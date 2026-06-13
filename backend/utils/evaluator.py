"""Evaluation framework for information retrieval (IR) metrics."""
import math

# Define 10 evaluation queries with keyword mapping to dynamically identify relevant documents
EVALUATION_QUERIES = [
    {
        "query": "space orbit mission launch",
        "keywords": ["space", "orbit", "nasa", "satellite", "shuttle", "mission", "lunar", "moon"]
    },
    {
        "query": "encryption key cryptography security",
        "keywords": ["encrypt", "crypto", "clipper", "key", "secure", "cipher", "pgp"]
    },
    {
        "query": "graphics card computer gpu drivers",
        "keywords": ["graphics", "card", "gpu", "driver", "vga", "3d", "display", "rendering"]
    },
    {
        "query": "nhl game hockey team playoffs",
        "keywords": ["hockey", "nhl", "game", "puck", "team", "playoffs", "goalie", "score"]
    },
    {
        "query": "medical disease treatment health cancer",
        "keywords": ["medical", "disease", "treatment", "health", "cancer", "doctor", "drug", "medicine"]
    },
    {
        "query": "god faith christian bible church",
        "keywords": ["god", "faith", "christian", "bible", "church", "religion", "christ", "sin"]
    },
    {
        "query": "government gun laws congressional senate",
        "keywords": ["gun", "law", "government", "senate", "congress", "politics", "weapon"]
    },
    {
        "query": "motorcycle engine ride helmet bike",
        "keywords": ["motorcycle", "bike", "ride", "helmet", "honda", "yamaha", "engine"]
    },
    {
        "query": "sale price sell condition offer shipping",
        "keywords": ["sale", "price", "sell", "condition", "offer", "shipping", "buy", "asking"]
    },
    {
        "query": "windows driver display card visual",
        "keywords": ["windows", "driver", "display", "microsoft", "os", "file", "visual"]
    }
]

def get_ground_truth_relevance(documents, keywords):
    """Find document indices that contain any of the relevance keywords."""
    relevant_set = set()
    for idx, doc in enumerate(documents):
        doc_lower = doc.lower()
        if any(kw in doc_lower for kw in keywords):
            relevant_set.add(idx)
    return relevant_set

def compute_precision_at_k(retrieved_indices, relevant_indices, k):
    """Calculate Precision at K (P@K)."""
    if k <= 0:
        return 0.0
    top_retrieved = retrieved_indices[:k]
    relevant_retrieved = sum(1 for idx in top_retrieved if idx in relevant_indices)
    return relevant_retrieved / k

def compute_recall_at_k(retrieved_indices, relevant_indices, k):
    """Calculate Recall at K (R@K)."""
    if not relevant_indices:
        return 0.0
    top_retrieved = retrieved_indices[:k]
    relevant_retrieved = sum(1 for idx in top_retrieved if idx in relevant_indices)
    return relevant_retrieved / len(relevant_indices)

def compute_mrr(retrieved_indices, relevant_indices):
    """Calculate Reciprocal Rank (RR)."""
    for rank, idx in enumerate(retrieved_indices):
        if idx in relevant_indices:
            return 1.0 / (rank + 1)
    return 0.0

def compute_ndcg_at_k(retrieved_indices, relevant_indices, k):
    """Calculate Normalized Discounted Cumulative Gain at K (NDCG@K)."""
    if k <= 0:
        return 0.0
    
    top_retrieved = retrieved_indices[:k]
    
    # Calculate DCG@K
    dcg = 0.0
    for rank, idx in enumerate(top_retrieved):
        rel = 1.0 if idx in relevant_indices else 0.0
        dcg += rel / math.log2(rank + 2)
        
    # Calculate IDCG@K (Ideal sorting of relevant documents)
    idcg = 0.0
    num_relevant_in_top_k = min(len(relevant_indices), k)
    for rank in range(num_relevant_in_top_k):
        idcg += 1.0 / math.log2(rank + 2)
        
    if idcg == 0.0:
        return 0.0
        
    return dcg / idcg

def evaluate_system(documents, search_fn, k=5):
    """
    Evaluate the retrieval system across all standard queries.
    
    Args:
        documents: Complete list of document strings in index
        search_fn: Function that takes a query string and returns a list of result dicts/tuples
                   (which must contain original document indices)
        k: Threshold parameter for evaluation (default 5)
        
    Returns:
        Dict of average evaluation scores.
    """
    if not documents:
        return {"precision_at_k": 0.0, "recall_at_k": 0.0, "mrr": 0.0, "ndcg_at_k": 0.0}
        
    total_queries = len(EVALUATION_QUERIES)
    sum_precision = 0.0
    sum_recall = 0.0
    sum_mrr = 0.0
    sum_ndcg = 0.0
    
    query_reports = []
    
    for eval_item in EVALUATION_QUERIES:
        query = eval_item["query"]
        keywords = eval_item["keywords"]
        
        # Get ground truth relevant indices
        relevant_indices = get_ground_truth_relevance(documents, keywords)
        
        # Run search query on system
        results = search_fn(query)
        
        # Extract returned document indices in rank order
        retrieved_indices = []
        for res in results:
            # Handle list of dicts (from reranked search) or list of tuples (from FAISS index)
            if isinstance(res, dict) and "index" in res:
                retrieved_indices.append(res["index"])
            elif isinstance(res, tuple) and len(res) >= 3:
                retrieved_indices.append(res[2])
                
        # Compute metrics
        p = compute_precision_at_k(retrieved_indices, relevant_indices, k)
        r = compute_recall_at_k(retrieved_indices, relevant_indices, k)
        mrr = compute_mrr(retrieved_indices, relevant_indices)
        ndcg = compute_ndcg_at_k(retrieved_indices, relevant_indices, k)
        
        sum_precision += p
        sum_recall += r
        sum_mrr += mrr
        sum_ndcg += ndcg
        
        query_reports.append({
            "query": query,
            "relevant_count": len(relevant_indices),
            "retrieved_count": len(retrieved_indices),
            "precision_at_k": round(p, 4),
            "recall_at_k": round(r, 4),
            "mrr": round(mrr, 4),
            "ndcg_at_k": round(ndcg, 4)
        })
        
    return {
        "k": k,
        "precision_at_k": round(sum_precision / total_queries, 4),
        "recall_at_k": round(sum_recall / total_queries, 4),
        "mrr": round(sum_mrr / total_queries, 4),
        "ndcg_at_k": round(sum_ndcg / total_queries, 4),
        "query_reports": query_reports
    }
