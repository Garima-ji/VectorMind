"""Semantic cache implementation with cosine similarity."""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SemanticCache:
    """Cluster-aware cache for storing query embeddings and results."""
    
    def __init__(self, similarity_threshold=0.95):
        """
        Initialize semantic cache.
        
        EXPLORATION OF THE TUNABLE SIMILARITY THRESHOLD PARAMETER:
        The `similarity_threshold` is the core tunable parameter of the semantic cache system.
        It defines the boundary for deciding whether a new query is semantically "close enough"
        to a cached query to reuse its result.
        
        Key trade-offs of this parameter:
        1. High values (e.g., 0.98 - 1.00):
           - Acts like an exact match cache. 
           - High precision: Almost zero chance of a false cache hit.
           - Low recall: Misses opportunities to accelerate queries that differ only by minor
             synonyms, word ordering, or punctuation.
        2. Low values (e.g., 0.80 - 0.90):
           - High recall: Accelerates a large number of query variants.
           - Low precision: High risk of false cache hits, returning answers that might be about 
             the same general topic (same cluster) but fail to answer the user's specific query.
        3. Configured default (0.95):
           - Empirically selected. It safely filters out semantically distinct queries while 
             consistently hitting for rephrased inputs or inputs with interchangeable synonyms.
        
        Args:
            similarity_threshold: Minimum similarity for cache hit
        """
        self.similarity_threshold = similarity_threshold
        self.cache_entries = []  # List of dicts with embedding, result, cluster
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, query_embedding, query_cluster=None):
        """
        Check cache for similar query, filtering by cluster.
        
        Args:
            query_embedding: Query embedding vector
            query_cluster: Dominant cluster ID (optional)
        
        Returns:
            Tuple (cached_result, matched_query, similarity_score) if found, (None, None, 0) otherwise
        """
        if not self.cache_entries:
            self.miss_count += 1
            return None, None, 0
        
        # Filter cache entries by cluster if provided
        if query_cluster is not None:
            filtered_entries = [e for e in self.cache_entries if e["cluster"] == query_cluster]
        else:
            filtered_entries = self.cache_entries
        
        if not filtered_entries:
            self.miss_count += 1
            return None, None, 0
        
        # Extract embeddings from filtered entries
        filtered_embeddings = np.array([e["embedding"] for e in filtered_entries])
        
        # Compute cosine similarity with filtered embeddings
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1),
            filtered_embeddings
        )[0]
        
        max_similarity = np.max(similarities)
        
        if max_similarity >= self.similarity_threshold:
            self.hit_count += 1
            best_match_idx = np.argmax(similarities)
            matched_entry = filtered_entries[best_match_idx]
            return matched_entry["result"], matched_entry.get("query", ""), float(max_similarity)
        
        self.miss_count += 1
        return None, None, 0
    
    def set(self, query_embedding, query, result, cluster):
        """
        Store query, embedding, result, and cluster in cache.
        
        Args:
            query_embedding: Query embedding vector
            query: Original query string
            result: Search result to cache
            cluster: Dominant cluster ID
        """
        self.cache_entries.append({
            "embedding": query_embedding,
            "query": query,
            "result": result,
            "cluster": cluster
        })
    
    def get_stats(self):
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0.0
        
        return {
            "total_entries": len(self.cache_entries),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": round(hit_rate, 4)
        }
    
    def clear(self):
        """Clear cache and reset statistics."""
        self.cache_entries = []
        self.hit_count = 0
        self.miss_count = 0
    
    def size(self):
        """Return the number of cached entries."""
        return len(self.cache_entries)
