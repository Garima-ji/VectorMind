"""FastAPI service for semantic search, hybrid retrieval, reranking, and RAG."""
import os
import time
import re
import psutil
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
from fastapi.staticfiles import StaticFiles
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

# Import advanced retrieval components
from backend.vector_db.bm25 import BM25Retriever
from backend.embeddings.reranker import CrossEncoderReranker
from backend.utils.generator import RAGGenerator
from backend.utils.query_expansion import expand_query
from backend.utils.analytics import AnalyticsTracker
from backend.utils.evaluator import evaluate_system

app = FastAPI(title="VectorMind Semantic Search API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Next.js static production bundle UI at /ui
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "out"))
if os.path.exists(frontend_dir):
    app.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="ui")
    print(f"[INFO] Static frontend UI successfully mounted at /ui from {frontend_dir}")
else:
    print(f"[WARNING] Static frontend directory not found at: {frontend_dir}. UI route is disabled.")

# Global system components
embedding_model = None
semantic_cache = None
faiss_index = None
fuzzy_clustering = None
tfidf_vectorizer = None
tfidf_matrix = None

# Advanced retrieval global components
bm25_retriever = None
reranker = None
rag_generator = None
analytics_tracker = None

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
    match_type: str  # "semantic", "keyword", "hybrid", "reranked"
    # New detailed retrieval fields
    semantic_score: Optional[float] = None
    keyword_score: Optional[float] = None
    rrf_score: Optional[float] = None
    explanation: Optional[str] = None
    index: Optional[int] = None

class QueryResponse(BaseModel):
    query: str
    intent: str
    cache_hit: bool
    matched_query: Optional[str] = None
    similarity_score: float
    result: str  # Grounded RAG answer
    results: List[SearchResultItem]
    dominant_cluster: int
    cluster_probability: float
    processing_time: float
    # New advanced RAG/telemetry fields
    expanded_query: Optional[str] = None
    sources: Optional[List[str]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize system components, load persisted models, or index dataset on startup."""
    global embedding_model, semantic_cache, faiss_index, fuzzy_clustering, tfidf_vectorizer, tfidf_matrix
    global bm25_retriever, reranker, rag_generator, analytics_tracker
    
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
        
        # Initialize Advanced search components
        log_info("Initializing BM25 Retriever on loaded documents...")
        bm25_retriever = BM25Retriever(faiss_index.documents)
        
        log_info("Initializing Cross-Encoder Reranker...")
        reranker = CrossEncoderReranker(model_name=config.RERANKER_MODEL)
        
        log_info("Initializing RAG Generator...")
        rag_generator = RAGGenerator(local_model=config.GENERATOR_MODEL, hf_api_model=config.HF_API_MODEL)
        
        log_info("Initializing Analytics Tracker...")
        analytics_tracker = AnalyticsTracker(filepath=config.ANALYTICS_PATH)
        
        log_info("VectorMind API initialization completed. Server is READY!")
    except Exception as e:
        log_info(f"CRITICAL: Startup failed: {e}")
        raise

def build_and_persist_index():
    """Build and fit the index/model from raw dataset, then persist them."""
    global embedding_model, faiss_index, fuzzy_clustering, bm25_retriever
    
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
    
    # Re-fit BM25 on indexing
    if bm25_retriever:
        log_info("Re-fitting BM25 index...")
        bm25_retriever.fit(raw_data)

def fit_tfidf_search():
    """Fit TF-IDF on indexed documents for hybrid search fallback/keyword match."""
    global tfidf_vectorizer, tfidf_matrix, faiss_index
    if faiss_index and faiss_index.documents:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(faiss_index.documents)
        log_info("TF-IDF vectorizer fitted successfully on index documents.")

def reciprocal_rank_fusion(semantic_results, keyword_results, k_rrf=60):
    """
    Reciprocal Rank Fusion (RRF) to merge semantic and keyword search ranks.
    
    Fixed to avoid index corruption by using clean lookup maps instead of re-indexing.
    
    Args:
        semantic_results: List of tuples (doc, score, index)
        keyword_results: List of tuples (doc, score, index)
        k_rrf: Constant parameters for RRF (usually 60)
        
    Returns:
        List of dicts containing fused results.
    """
    rrf_scores = {}
    
    # Build clean index → document and index → score maps to avoid re-indexing errors
    sem_docs = {item[2]: item[0] for item in semantic_results}
    key_docs = {item[2]: item[0] for item in keyword_results}
    sem_scores = {item[2]: item[1] for item in semantic_results}
    key_scores = {item[2]: item[1] for item in keyword_results}
    
    # Map ranks (1-based index)
    sem_ranks = {item[2]: rank + 1 for rank, item in enumerate(semantic_results)}
    key_ranks = {item[2]: rank + 1 for rank, item in enumerate(keyword_results)}
    
    all_indices = set(sem_ranks.keys()).union(set(key_ranks.keys()))
    
    for idx in all_indices:
        sem_rank = sem_ranks.get(idx)
        key_rank = key_ranks.get(idx)
        
        score = 0.0
        if sem_rank is not None:
            score += 1.0 / (k_rrf + sem_rank)
        if key_rank is not None:
            score += 1.0 / (k_rrf + key_rank)
        
        # Use clean lookup maps instead of re-indexing
        doc = sem_docs.get(idx) or key_docs.get(idx)
        
        rrf_scores[idx] = {
            "document": doc,
            "rrf_score": score,
            "index": idx,
            "semantic_score": float(sem_scores.get(idx, 0.0)),
            "keyword_score": float(key_scores.get(idx, 0.0)),
            "match_type": "hybrid" if (sem_rank and key_rank) else ("semantic" if sem_rank else "keyword")
        }
        
    # Sort by RRF score descending
    sorted_rrf = sorted(rrf_scores.values(), key=lambda x: x["rrf_score"], reverse=True)
    return sorted_rrf

def get_matching_keywords(query, document):
    """Extract intersection of query and document terms, skipping common stop words."""
    query_words = set(re.findall(r'[a-z0-9]+', query.lower()))
    doc_words = set(re.findall(r'[a-z0-9]+', document.lower()))
    shared = query_words.intersection(doc_words)
    stopwords = {"the", "a", "an", "and", "or", "but", "if", "then", "of", "to", "in", "on", "for", "with", "is", "was", "it", "this", "that", "i", "you", "he", "she", "they", "we"}
    return [word for word in shared if word not in stopwords]

@app.get("/")
async def root():
    """Simple API root check."""
    return {
        "message": "VectorMind Intelligent Semantic Search & RAG API",
        "status": "running",
        "embedding_model": "loaded" if embedding_model else "not loaded",
        "faiss_index": f"loaded ({len(faiss_index.documents)} docs)" if faiss_index else "not loaded",
        "bm25_retriever": "ready" if bm25_retriever else "not ready",
        "reranker": "ready" if reranker else "not ready",
        "rag_generator": "ready" if rag_generator else "not ready"
    }

@app.post("/query", response_model=QueryResponse)
async def query_search(request: QueryRequest):
    """Perform synonym-expanded hybrid search, RRF rank merging, Cross-Encoder reranking, and RAG answer generation."""
    start_time = time.time()
    
    if not embedding_model or not faiss_index or not fuzzy_clustering or not bm25_retriever or not reranker or not rag_generator:
        raise HTTPException(status_code=503, detail="System components not fully initialized")
        
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")
    
    # Validate and constrain top_k
    top_k = request.top_k or config.TOP_K_RESULTS
    top_k = max(config.TOP_K_MIN, min(top_k, config.TOP_K_MAX))
        
    try:
        # 1. Query Expansion (synonym matching)
        expanded_q = expand_query(request.query)
        
        # Preprocess query for vectors and classifier
        cleaned_query = clean_text(request.query)
        intent = detect_query_intent(request.query)
        
        # 2. Vector embedding generation
        query_embedding = embedding_model.encode([cleaned_query])[0]
        
        # Predict GMM cluster probabilities
        cluster_id, cluster_prob = fuzzy_clustering.get_dominant_cluster(query_embedding)
        
        # 3. Check Semantic Cache
        cached_result, matched_query, cache_similarity = semantic_cache.get(query_embedding, query_cluster=cluster_id)
        if cached_result:
            processing_time = time.time() - start_time
            # Record analytics log (latency = ~0 for cache hit)
            if analytics_tracker:
                analytics_tracker.record_query(request.query, cache_hit=True, latency=processing_time, cluster_id=cluster_id)
                
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
                    match_type="cache",
                    explanation=f"Exact match fetched from semantic cache (matched query: '{matched_query}')"
                )],
                dominant_cluster=cluster_id,
                cluster_probability=cluster_prob,
                processing_time=round(processing_time, 4),
                expanded_query=expanded_q,
                sources=["Semantic Cache"]
            )
            
        # 4. Perform Candidate Retrieval (Hybrid Search)
        # Fetch top 20 candidates from FAISS dense vector search
        semantic_candidates = faiss_index.search(query_embedding, k=20)
        
        # Fetch top 20 candidates from BM25 sparse keyword search using expanded query
        keyword_candidates = bm25_retriever.search(expanded_q, k=20)
        
        # 5. Merge Candidate Lists via Reciprocal Rank Fusion (RRF)
        fused_candidates = reciprocal_rank_fusion(semantic_candidates, keyword_candidates, k_rrf=60)
        
        # Slice the top 20 candidates for rerank processing
        rerank_candidates = []
        for c in fused_candidates[:20]:
            rerank_candidates.append((c["document"], c["rrf_score"], c["index"]))
            
        # 6. Apply Cross-Encoder Reranking
        reranked_docs = reranker.rerank(request.query, rerank_candidates, top_k=top_k)
        
        # 7. Generate Grounded RAG Answer
        context_texts = [item["document"] for item in reranked_docs]
        rag_answer, rag_sources = rag_generator.generate_answer(request.query, context_texts)
        
        # Save generated RAG answer to Semantic Cache for future acceleration
        semantic_cache.set(query_embedding, request.query, rag_answer, cluster_id)
        
        # 8. Compile Search Explanations
        final_results = []
        for rank, item in enumerate(reranked_docs):
            doc = item["document"]
            idx = item["index"]
            rerank_score = item["rerank_score"]
            base_fused_score = item["base_score"]
            
            # Find the original match type and scores
            orig_match = "hybrid"
            sem_score = 0.0
            key_score = 0.0
            
            for orig in fused_candidates:
                if orig["index"] == idx:
                    orig_match = orig["match_type"]
                    sem_score = orig["semantic_score"]
                    key_score = orig["keyword_score"]
                    break
                    
            # Compute matching keyword overlaps
            matching_terms = get_matching_keywords(request.query, doc)
            
            # Form explanation text
            explanation = (
                f"Ranked #{rank+1} after Cross-Encoder reranking (score: {round(rerank_score, 2)}). "
                f"Initially matched via {orig_match.upper()} search. "
                f"Keyword Overlaps: {', '.join(matching_terms) if matching_terms else 'None'}. "
                f"Semantic Cosine: {round(sem_score * 100, 1)}% | BM25 Score: {round(key_score, 1)}."
            )
            
            # Predict cluster for this document
            doc_embedding = embedding_model.encode([doc])[0]
            doc_cluster, _ = fuzzy_clustering.get_dominant_cluster(doc_embedding)
            
            final_results.append(SearchResultItem(
                document=doc,
                similarity_score=rerank_score,
                cluster=doc_cluster,
                match_type="reranked",
                semantic_score=sem_score,
                keyword_score=key_score,
                rrf_score=base_fused_score,
                explanation=explanation,
                index=idx
            ))
            
        processing_time = time.time() - start_time
        top_score = final_results[0].similarity_score if final_results else 0.0
        
        # 9. Record Analytics Telemetry
        if analytics_tracker:
            analytics_tracker.record_query(request.query, cache_hit=False, latency=processing_time, cluster_id=cluster_id)
            
        return QueryResponse(
            query=request.query,
            intent=intent,
            cache_hit=False,
            matched_query=None,
            similarity_score=float(top_score),
            result=rag_answer,
            results=final_results,
            dominant_cluster=cluster_id,
            cluster_probability=cluster_prob,
            processing_time=round(processing_time, 4),
            expanded_query=expanded_q,
            sources=rag_sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution error: {str(e)}")

@app.get("/analytics")
async def get_analytics_dashboard():
    """Return dashboard analytics telemetry."""
    if not analytics_tracker:
        raise HTTPException(status_code=503, detail="Analytics component not initialized")
    return analytics_tracker.get_analytics()

# Global state tracking for reindexing progress
reindex_status = {
    "status": "idle", # "idle", "running", "completed", "failed"
    "message": "No active reindexing job.",
    "error": None,
    "last_run": None
}

def run_reindex_task():
    global reindex_status
    reindex_status["status"] = "running"
    reindex_status["message"] = "Reindexing full corpus and training GMM model..."
    reindex_status["error"] = None
    try:
        build_and_persist_index()
        fit_tfidf_search()
        reindex_status["status"] = "completed"
        reindex_status["message"] = "Reindexing successfully completed."
        reindex_status["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        reindex_status["status"] = "failed"
        reindex_status["message"] = "Reindexing failed."
        reindex_status["error"] = str(e)
        print(f"[ERROR] Reindexing background task error: {e}")

@app.post("/reindex")
async def rebuild_search_index(background_tasks: BackgroundTasks):
    """Trigger complete document reindexing and GMM model fit in the background."""
    global reindex_status
    if reindex_status["status"] == "running":
        return {"status": "running", "message": "Reindexing is already in progress."}
        
    background_tasks.add_task(run_reindex_task)
    return {"status": "accepted", "message": "Reindexing task started in the background."}

@app.get("/reindex/status")
async def get_reindex_status():
    """Check the status of the background reindexing task."""
    global reindex_status
    return reindex_status

@app.get("/evaluate")
async def run_system_evaluation(k: int = Query(5, description="Evaluation threshold parameter")):
    """Run standard IR precision, recall, MRR, and NDCG benchmark tests."""
    if not faiss_index or not faiss_index.documents:
        raise HTTPException(status_code=503, detail="Search documents index not loaded")
        
    def evaluation_search_pipeline(query_string: str):
        # Mini search pipeline for evaluation matching
        query_embedding = embedding_model.encode([query_string])[0]
        semantic_candidates = faiss_index.search(query_embedding, k=20)
        expanded_q = expand_query(query_string)
        keyword_candidates = bm25_retriever.search(expanded_q, k=20)
        fused = reciprocal_rank_fusion(semantic_candidates, keyword_candidates, k_rrf=60)
        rerank_candidates = [(item["document"], item["rrf_score"], item["index"]) for item in fused[:20]]
        reranked = reranker.rerank(query_string, rerank_candidates, top_k=k)
        return reranked
        
    try:
        report = evaluate_system(faiss_index.documents, evaluation_search_pipeline, k=k)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.get("/clusters/visualization")
async def get_clusters_visualization():
    """Generate 2D t-SNE coordinate projections for interactive frontend topic mapping."""
    if not faiss_index or not faiss_index.documents or not embedding_model or not fuzzy_clustering:
        raise HTTPException(status_code=503, detail="System components not fully loaded")
        
    try:
        from sklearn.manifold import TSNE
        documents = faiss_index.documents
        
        # Generate dense embeddings
        embeddings = embedding_model.encode(documents)
        
        # Fit t-SNE projection to 2D space
        perplexity_val = min(30, max(5, len(documents) // 5))
        try:
            tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity_val, max_iter=1000)
        except TypeError:
            tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity_val, n_iter=1000)
        embeddings_2d = tsne.fit_transform(embeddings)
        
        # Calculate cluster memberships
        memberships = fuzzy_clustering.predict_proba(embeddings)
        dominant_clusters = np.argmax(memberships, axis=1)
        
        points = []
        for idx, (x, y) in enumerate(embeddings_2d):
            # Clean snippet for easy JSON rendering
            snippet = documents[idx][:120].strip().replace("\n", " ")
            if len(documents[idx]) > 120:
                snippet += "..."
                
            points.append({
                "id": idx,
                "x": round(float(x), 4),
                "y": round(float(y), 4),
                "document": snippet,
                "cluster": int(dominant_clusters[idx]),
                "probability": round(float(memberships[idx][dominant_clusters[idx]]), 4)
            })
            
        return {
            "n_documents": len(documents),
            "points": points
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"t-SNE projection failed: {str(e)}")

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
        formatted_analysis = {str(k): v for k, v in analysis["representative_docs"].items()}
        
        return {
            "n_clusters": fuzzy_clustering.n_clusters,
            "clusters": formatted_analysis,
            "boundary_cases": analysis["boundary_cases"]
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
        "clustering": "ready" if fuzzy_clustering else "not ready",
        "bm25": "ready" if bm25_retriever else "not ready",
        "reranker": "ready" if reranker else "not ready",
        "rag": "ready" if rag_generator else "not ready"
    }
