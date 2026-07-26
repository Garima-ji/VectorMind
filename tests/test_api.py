"""Test script for VectorMind API."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_query():
    """Test query endpoint."""
    print("Testing query endpoint...")
    payload = {"query": "machine learning algorithms", "top_k": 3}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_cache_stats():
    """Test cache stats endpoint."""
    print("Testing cache stats endpoint...")
    response = requests.get(f"{BASE_URL}/cache/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_cached_query():
    """Test cached query."""
    print("Testing cached query (should hit cache)...")
    payload = {"query": "machine learning algorithms", "top_k": 3}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Cache Hit: {response.json()['cache_hit']}")
    print()

def test_system_stats():
    """Test system stats endpoint."""
    print("Testing system stats endpoint...")
    response = requests.get(f"{BASE_URL}/system/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_clusters():
    """Test clusters endpoint."""
    print("Testing clusters endpoint...")
    response = requests.get(f"{BASE_URL}/clusters")
    print(f"Status: {response.status_code}")
    # Show truncated output for clusters representation
    clusters_data = response.json()
    print(f"Number of clusters: {clusters_data.get('n_clusters')}")
    print(f"Sample Cluster 0 Keys: {list(clusters_data.get('clusters', {}).keys())[:5] if clusters_data.get('clusters') else 'None'}")
    print()

def test_analytics():
    """Test analytics endpoint."""
    print("Testing analytics endpoint...")
    response = requests.get(f"{BASE_URL}/analytics")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_evaluate():
    """Test evaluate endpoint."""
    print("Testing evaluate endpoint...")
    response = requests.get(f"{BASE_URL}/evaluate?k=5")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Precision@5: {data.get('precision_at_k')}")
    print(f"NDCG@5: {data.get('ndcg_at_k')}")
    print()

def test_clusters_visualization():
    """Test clusters visualization endpoint."""
    print("Testing clusters visualization endpoint...")
    response = requests.get(f"{BASE_URL}/clusters/visualization")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Number of points: {len(data.get('points', []))}")
    if data.get('points'):
        print(f"Sample point 0: {data['points'][0]}")
    print()

def test_reindex():
    """Test reindexing endpoint."""
    print("Testing reindexing endpoint...")
    response = requests.post(f"{BASE_URL}/reindex")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    try:
        test_health()
        test_query()
        test_cache_stats()
        test_cached_query()
        test_system_stats()
        test_clusters()
        test_analytics()
        test_evaluate()
        test_clusters_visualization()
        test_reindex()
        print("All tests completed successfully!")
    except Exception as e:
        print(f"Error connecting to server or executing tests: {e}")

