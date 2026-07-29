"""Analytics tracking module to store and persist search telemetry using SQLite."""
import os
import sqlite3
import threading

class AnalyticsTracker:
    """Process-safe and thread-safe search telemetry tracker using SQLite."""
    
    def __init__(self, filepath="backend/data/analytics.db"):
        """Initialize and create table schema if it does not exist."""
        self.filepath = filepath
        self.lock = threading.Lock()
        
        # Ensure parent folder exists
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self._init_db()
        
    def _get_connection(self):
        """Create a connection to SQLite database."""
        # Disable same-thread check so we can use a connection across threads safely inside the lock
        return sqlite3.connect(self.filepath, timeout=10.0)
        
    def _init_db(self):
        """Create the query telemetry table if not present."""
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS queries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT,
                        cache_hit INTEGER,
                        latency REAL,
                        cluster_id INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            except Exception as e:
                print(f"Error initializing SQLite database: {e}")
            finally:
                conn.close()
                
    def record_query(self, query, cache_hit, latency, cluster_id):
        """
        Record search query telemetry into the SQLite database.
        
        Args:
            query: The user query string
            cache_hit: Boolean indicating if cache hit occurred
            latency: Time taken to process the query in seconds
            cluster_id: Dominant cluster ID of the query
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO queries (query, cache_hit, latency, cluster_id) VALUES (?, ?, ?, ?)",
                    (query.strip().lower(), 1 if cache_hit else 0, float(latency), int(cluster_id))
                )
                conn.commit()
            except Exception as e:
                print(f"Error saving query to database: {e}")
            finally:
                conn.close()
                
    def get_analytics(self):
        """
        Compute and return analytics from the database logs.
        
        Returns:
            Dict of retrieval statistics and metrics.
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                
                # Fetch total queries, hits, and latencies
                cursor.execute("SELECT COUNT(*), SUM(cache_hit), SUM(latency) FROM queries")
                row = cursor.fetchone()
                total = row[0] or 0
                hits = row[1] or 0
                total_latency = row[2] or 0.0
                
                # Fetch top queries
                cursor.execute("SELECT query, COUNT(*) as c FROM queries WHERE query != '' GROUP BY query ORDER BY c DESC LIMIT 10")
                top_queries = [{"query": r[0], "count": r[1]} for r in cursor.fetchall()]
                
                # Fetch cluster hits distribution
                cursor.execute("SELECT cluster_id, COUNT(*) FROM queries GROUP BY cluster_id")
                cluster_dist = {int(r[0]): r[1] for r in cursor.fetchall()}
                
                # Fetch recent latencies (last 20 for graphs, and limit history)
                cursor.execute("SELECT latency FROM queries ORDER BY id DESC LIMIT 1000")
                recent_latencies = [float(r[0]) for r in cursor.fetchall()][::-1]
                
                cache_hit_rate = round(hits / total, 4) if total > 0 else 0.0
                avg_latency = round(total_latency / total, 4) if total > 0 else 0.0
                
                return {
                    "total_queries": total,
                    "cache_hit_rate": cache_hit_rate,
                    "average_latency_ms": round(avg_latency * 1000, 2),
                    "top_queries": top_queries,
                    "cluster_distribution": cluster_dist,
                    "recent_latencies": recent_latencies[-20:] # Return last 20 for charts
                }
            except Exception as e:
                print(f"Error reading analytics from database: {e}")
                return {
                    "total_queries": 0,
                    "cache_hit_rate": 0.0,
                    "average_latency_ms": 0.0,
                    "top_queries": [],
                    "cluster_distribution": {},
                    "recent_latencies": []
                }
            finally:
                conn.close()
                
    def clear(self):
        """Clear all analytics database entries."""
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM queries")
                conn.commit()
            except Exception as e:
                print(f"Error clearing database: {e}")
            finally:
                conn.close()
