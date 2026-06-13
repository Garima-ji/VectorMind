"""FastAPI service for semantic search."""
import os
import time
import psutil
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from backend.embeddings.embedding_model import EmbeddingModel
from backend.cache.semantic_cache import SemanticCache
from backend.vector_db.faiss_index import FAISSIndex
from backend.clustering.fuzzy_clustering import FuzzyClustering
from backend.preprocessing.text_cleaner import clean_text
from backend.preprocessing.preprocess_pipeline import preprocess_documents
from backend.utils.query_intent import detect_query_intent
from backend.utils.summarizer import generate_summary
from backend.utils.cluster_analysis import analyze_clusters
from backend.data.load_dataset import load_newsgroups_data
from backend.utils import config

app = FastAPI(title="VectorMind Semantic Search API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system components
embedding_model = None
semantic_cache = None
faiss_index = None
fuzzy_clustering = None
tfidf_vectorizer = None
tfidf_matrix = None

# Custom Logger
def log_info(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [INFO] {msg}")

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = config.TOP_K_RESULTS
    hybrid: Optional[bool] = True
    alpha: Optional[float] = 0.7  # Weight of semantic search in hybrid mode

class SearchResultItem(BaseModel):
    document: str
    similarity_score: float
    cluster: int
    match_type: str  # "semantic", "keyword", or "hybrid"

class QueryResponse(BaseModel):
    query: str
    intent: str
    cache_hit: bool
    matched_query: Optional[str] = None
    similarity_score: float
    result: str
    results: List[SearchResultItem]
    dominant_cluster: int
    cluster_probability: float
    processing_time: float

@app.on_event("startup")
async def startup_event():
    """Initialize system components, load persisted models, or index dataset on startup."""
    global embedding_model, semantic_cache, faiss_index, fuzzy_clustering, tfidf_vectorizer, tfidf_matrix
    
    try:
        log_info("Initializing embedding model (all-MiniLM-L6-v2)...")
        embedding_model = EmbeddingModel(model_name=config.EMBEDDING_MODEL)
        
        log_info("Initializing semantic cache...")
        semantic_cache = SemanticCache(similarity_threshold=config.CACHE_SIMILARITY_THRESHOLD)
        
        log_info("Initializing FAISS Vector Index...")
        dimension = embedding_model.get_embedding_dim()
        faiss_index = FAISSIndex(dimension=dimension)
        
        log_info("Initializing Fuzzy Clustering (GMM)...")
        fuzzy_clustering = FuzzyClustering(n_clusters=config.n_clusters)
        
        # Check if persistent database and clustering files exist
        has_index = os.path.exists(config.INDEX_PATH) or os.path.exists(config.INDEX_PATH + ".npy")
        has_docs = os.path.exists(config.DOCS_PATH)
        has_gmm = os.path.exists(config.GMM_PATH)
        
        if has_index and has_docs and has_gmm:
            log_info("Loading persisted FAISS index and GMM model...")
            try:
                faiss_index.load(config.INDEX_PATH, config.DOCS_PATH)
                fuzzy_clustering.load(config.GMM_PATH)
                log_info("Persisted index and model loaded successfully!")
            except Exception as e:
                log_info(f"Failed to load persisted files: {e}. Rebuilding instead.")
                build_and_persist_index()
        else:
            log_info("Persisted store files not found. Rebuilding index...")
            build_and_persist_index()
            
        # Fit TF-IDF Vectorizer on documents list for Keyword Search
        fit_tfidf_search()
        
        log_info("VectorMind API initialization completed. Server is READY!")
    except Exception as e:
        log_info(f"Startup error: {e}")
        # Gracefully proceed so API doesn't crash entirely
        pass

def build_and_persist_index():
    """Build and fit the index/model from raw dataset, then persist them."""
    global embedding_model, faiss_index, fuzzy_clustering
    
    log_info("Loading newsgroups dataset...")
    raw_data, targets, target_names = load_newsgroups_data()
    
    log_info("Preprocessing documents...")
    cleaned_docs = preprocess_documents(raw_data)
    
    log_info("Generating dense vector embeddings...")
    embeddings = embedding_model.encode(cleaned_docs)
    
    log_info("Adding documents to FAISS index...")
    faiss_index.add_documents(embeddings, raw_data)
    
    log_info("Fitting fuzzy clustering (GMM) model...")
    fuzzy_clustering.fit(embeddings)
    
    log_info("Saving index and model to disk...")
    faiss_index.save(config.INDEX_PATH, config.DOCS_PATH)
    fuzzy_clustering.save(config.GMM_PATH)
    log_info("Persisted stores saved successfully!")

def fit_tfidf_search():
    """Fit TF-IDF on indexed documents for hybrid search fallback/keyword match."""
    global tfidf_vectorizer, tfidf_matrix, faiss_index
    if faiss_index and faiss_index.documents:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(faiss_index.documents)
        log_info("TF-IDF vectorizer fitted successfully on index documents.")

@app.get("/")
async def root():
    """Simple API root check."""
    return {
        "message": "VectorMind Semantic Search API",
        "status": "running",
        "embedding_model": "loaded" if embedding_model else "not loaded",
        "faiss_index": f"loaded ({len(faiss_index.documents)} docs)" if faiss_index else "not loaded"
    }

@app.post("/query", response_model=QueryResponse)
async def query_search(request: QueryRequest):
    """Perform hybrid semantic-keyword search with cache checks and cluster detection."""
    start_time = time.time()
    
    if not embedding_model or not faiss_index or not fuzzy_clustering:
        raise HTTPException(status_code=503, detail="System components not fully initialized")
        
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")
        
    try:
        # Preprocess and intent classification
        cleaned_query = clean_text(request.query)
        intent = detect_query_intent(request.query)
        
        # Vector embedding generation
        query_embedding = embedding_model.encode([cleaned_query])[0]
        
        # Predict cluster probabilities
        cluster_id, cluster_prob = fuzzy_clustering.get_dominant_cluster(query_embedding)
        
        # Check cache
        cached_result, matched_query, cache_similarity = semantic_cache.get(query_embedding, query_cluster=cluster_id)
        if cached_result:
            processing_time = time.time() - start_time
            return QueryResponse(
                query=request.query,
                intent=intent,
                cache_hit=True,
                matched_query=matched_query,
                similarity_score=float(cache_similarity),
                result=cached_result,
                results=[SearchResultItem(
                    document=cached_result,
                    similarity_score=float(cache_similarity),
                    cluster=cluster_id,
                    match_type="cache"
                )],
                dominant_cluster=cluster_id,
                cluster_probability=cluster_prob,
                processing_time=round(processing_time, 4)
            )
            
        # 1. Semantic Search (FAISS)
        semantic_results = faiss_index.search(query_embedding, k=max(20, request.top_k * 2))
        semantic_dict = {doc: score for doc, score, idx in semantic_results}
        
        # 2. Keyword Search (TF-IDF Cosine Similarity)
        keyword_scores = {}
        if tfidf_vectorizer and tfidf_matrix is not None:
            query_tfidf = tfidf_vectorizer.transform([cleaned_query])
            cosine_sims = (tfidf_matrix * query_tfidf.T).toarray().flatten()
            top_k_indices = np.argsort(cosine_sims)[-request.top_k:][::-1]
            for idx in top_k_indices:
                if cosine_sims[idx] > 0.0:
                    doc = faiss_index.documents[idx]
                    keyword_scores[doc] = float(cosine_sims[idx])
                    
        # 3. Hybrid Rank Fusion (Linear Combination of normalized scores)
        combined_scores = {}
        all_docs = set(semantic_dict.keys()).union(set(keyword_scores.keys()))
        
        for doc in all_docs:
            sem_score = semantic_dict.get(doc, 0.0)
            key_score = keyword_scores.get(doc, 0.0)
            
            if request.hybrid:
                # Combined score calculation
                score = request.alpha * sem_score + (1.0 - request.alpha) * key_score
                match_type = "hybrid"
            else:
                score = sem_score
                match_type = "semantic"
                
            combined_scores[doc] = (score, match_type)
            
        # Rank by score
        ranked_docs = sorted(combined_scores.items(), key=lambda x: x[1][0], reverse=True)[:request.top_k]
        
        results_list = []
        for doc, (score, m_type) in ranked_docs:
            results_list.append(SearchResultItem(
                document=doc,
                similarity_score=score,
                cluster=cluster_id,
                match_type=m_type
            ))
            
        # If no results matched, fall back to pure semantic top-K or default
        if not results_list and semantic_results:
            for doc, score, idx in semantic_results[:request.top_k]:
                results_list.append(SearchResultItem(
                    document=doc,
                    similarity_score=score,
                    cluster=cluster_id,
                    match_type="semantic"
                ))
                
        # Generate summary
        results_raw = [{"document": item.document} for item in results_list]
        summary = generate_summary(results_raw) if results_raw else f"No results found for '{request.query}'."
        
        # Save to Cache
        semantic_cache.set(query_embedding, request.query, summary, cluster_id)
        
        processing_time = time.time() - start_time
        top_score = results_list[0].similarity_score if results_list else 0.0
        
        return QueryResponse(
            query=request.query,
            intent=intent,
            cache_hit=False,
            matched_query=None,
            similarity_score=float(top_score),
            result=summary,
            results=results_list,
            dominant_cluster=cluster_id,
            cluster_probability=cluster_prob,
            processing_time=round(processing_time, 4)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/cache/stats")
async def get_cache_stats():
    """Return semantic cache stats."""
    if not semantic_cache:
        raise HTTPException(status_code=503, detail="Cache not initialized")
    return semantic_cache.get_stats()

@app.delete("/cache")
async def clear_cache():
    """Clear the cache."""
    if not semantic_cache:
        raise HTTPException(status_code=503, detail="Cache not initialized")
    semantic_cache.clear()
    return {"message": "Cache cleared successfully"}

@app.get("/system/stats")
async def get_system_stats():
    """Detailed health check and system performance metrics."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    
    return {
        "status": "healthy",
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_usage_mb": round(mem_info.rss / (1024 * 1024), 2),
        "embedding_model": config.EMBEDDING_MODEL,
        "indexed_documents_count": len(faiss_index.documents) if faiss_index else 0,
        "cache_size": semantic_cache.size() if semantic_cache else 0,
        "has_faiss": faiss_index.using_faiss if faiss_index else False,
    }

@app.get("/clusters")
async def get_clusters():
    """Cluster analytics with top representative documents per cluster."""
    if not faiss_index or not fuzzy_clustering or not embedding_model:
        raise HTTPException(status_code=503, detail="Clustering module not fully initialized")
        
    try:
        documents = faiss_index.documents
        if not documents:
            return {"clusters": {}}
            
        # Fast encoding
        embeddings = embedding_model.encode(documents)
        memberships = fuzzy_clustering.predict_proba(embeddings)
        
        # Analyze clusters
        analysis = analyze_clusters(documents, memberships, fuzzy_clustering.n_clusters)
        
        # Convert keys to string JSON serialization compatibility
        formatted_analysis = {str(k): v for k, v in analysis.items()}
        
        return {
            "n_clusters": fuzzy_clustering.n_clusters,
            "clusters": formatted_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cluster analysis: {str(e)}")

@app.get("/health")
async def health_check():
    """Basic service diagnostics."""
    return {
        "status": "healthy",
        "embedding_model": "ready" if embedding_model else "not ready",
        "cache": "ready" if semantic_cache else "not ready",
        "vector_index": "ready" if faiss_index else "not ready",
        "clustering": "ready" if fuzzy_clustering else "not ready"
    }
