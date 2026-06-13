"""Analytics tracking module to store and persist search telemetry."""
import os
import json
import threading
from collections import Counter

class AnalyticsTracker:
    """Thread-safe search telemetry tracker with local JSON file backup."""
    
    def __init__(self, filepath="backend/data/analytics.json"):
        """Initialize and load existing analytics from disk."""
        self.filepath = filepath
        self.lock = threading.Lock()
        
        # In-memory statistics structure
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "total_latency": 0.0,
            "query_terms": {},
            "cluster_hits": {},
            "latencies": []  # List of recent latencies (last 1000)
        }
        
        self._load_stats()
        
    def _load_stats(self):
        """Load stats from local JSON file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    disk_stats = json.load(f)
                    # Verify structure matches expectations
                    for key in self.stats:
                        if key in disk_stats:
                            self.stats[key] = disk_stats[key]
            except Exception as e:
                print(f"Error loading analytics file: {e}")
                
    def _save_stats(self):
        """Save stats to disk."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving analytics file: {e}")
            
    def record_query(self, query, cache_hit, latency, cluster_id):
        """
        Record search query telemetry.
        
        Args:
            query: The user query string
            cache_hit: Boolean indicating if cache hit occurred
            latency: Time taken to process the query in seconds
            cluster_id: Dominant cluster ID of the query
        """
        with self.lock:
            self.stats["total_queries"] += 1
            if cache_hit:
                self.stats["cache_hits"] += 1
            self.stats["total_latency"] += latency
            
            # Record query frequency (limit terms to lowercase)
            q_clean = query.strip().lower()
            if q_clean:
                self.stats["query_terms"][q_clean] = self.stats["query_terms"].get(q_clean, 0) + 1
                
            # Record cluster ID occurrences
            c_str = str(cluster_id)
            self.stats["cluster_hits"][c_str] = self.stats["cluster_hits"].get(c_str, 0) + 1
            
            # Record latency history
            self.stats["latencies"].append(float(latency))
            if len(self.stats["latencies"]) > 1000:
                self.stats["latencies"].pop(0)
                
            self._save_stats()
            
    def get_analytics(self):
        """
        Compute and return analytics.
        
        Returns:
            Dict of retrieval statistics and metrics.
        """
        with self.lock:
            total = self.stats["total_queries"]
            hits = self.stats["cache_hits"]
            
            cache_hit_rate = round(hits / total, 4) if total > 0 else 0.0
            avg_latency = round(self.stats["total_latency"] / total, 4) if total > 0 else 0.0
            
            # Find top queries
            sorted_queries = sorted(self.stats["query_terms"].items(), key=lambda x: x[1], reverse=True)[:10]
            top_queries = [{"query": k, "count": v} for k, v in sorted_queries]
            
            # format cluster distribution
            cluster_dist = {int(k): v for k, v in self.stats["cluster_hits"].items()}
            
            return {
                "total_queries": total,
                "cache_hit_rate": cache_hit_rate,
                "average_latency_ms": round(avg_latency * 1000, 2),
                "top_queries": top_queries,
                "cluster_distribution": cluster_dist,
                "recent_latencies": self.stats["latencies"][-20:] # Return last 20 for charts
            }
            
    def clear(self):
        """Clear all analytics."""
        with self.lock:
            self.stats = {
                "total_queries": 0,
                "cache_hits": 0,
                "total_latency": 0.0,
                "query_terms": {},
                "cluster_hits": {},
                "latencies": []
            }
            self._save_stats()
