"""Cross-Encoder reranking model to re-score candidate documents against a query."""
try:
    from sentence_transformers import CrossEncoder
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class CrossEncoderReranker:
    """Lazy-loaded Cross-Encoder model wrapper for precise query-document relevance scoring."""
    
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize the reranker.
        
        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.model = None
        self.using_cross_encoder = HAS_SENTENCE_TRANSFORMERS
        
    def _load_model(self):
        """Lazy load model to optimize memory usage at startup."""
        if self.model is None and self.using_cross_encoder:
            try:
                print(f"Loading Cross-Encoder model: {self.model_name}...")
                self.model = CrossEncoder(self.model_name)
            except Exception as e:
                print(f"Error loading Cross-Encoder model: {e}. Falling back to pass-through.")
                self.using_cross_encoder = False
                
    def rerank(self, query, candidates, top_k=5):
        """
        Rerank a list of candidate documents.
        
        Args:
            query: The user query string
            candidates: List of tuples (document_text, base_score, original_index)
            top_k: Number of documents to return after reranking
            
        Returns:
            List of dicts containing document details with base and rerank scores.
        """
        if not candidates:
            return []
            
        self._load_model()
        
        if not self.using_cross_encoder or not self.model:
            # Fallback: return top_k candidates directly based on base score
            sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:top_k]
            return [
                {
                  "document": cand[0],
                  "base_score": cand[1],
                  "rerank_score": cand[1],
                  "index": cand[2]
                }
                for cand in sorted_candidates
            ]
            
        # Format input pairs for Cross-Encoder: [[query, doc1], [query, doc2], ...]
        pairs = [[query, cand[0]] for cand in candidates]
        
        try:
            # Predict scores (typically logit or sigmoid values depending on model)
            scores = self.model.predict(pairs)
            
            # Map back to structured results
            reranked_results = []
            for score, cand in zip(scores, candidates):
                reranked_results.append({
                    "document": cand[0],
                    "base_score": cand[1],
                    "rerank_score": float(score),
                    "index": cand[2]
                })
                
            # Sort by rerank score descending
            reranked_results.sort(key=lambda x: x["rerank_score"], reverse=True)
            return reranked_results[:top_k]
            
        except Exception as e:
            print(f"Reranking error: {e}. Falling back to default candidates.")
            sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:top_k]
            return [
                {
                  "document": cand[0],
                  "base_score": cand[1],
                  "rerank_score": cand[1],
                  "index": cand[2]
                }
                for cand in sorted_candidates
            ]
