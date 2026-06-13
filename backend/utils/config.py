"""Configuration settings for the semantic search system."""

# Model configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Cache configuration
CACHE_SIMILARITY_THRESHOLD = 0.95

# Search configuration
TOP_K_RESULTS = 5

# Persistence configuration
INDEX_PATH = "backend/data/index_store/faiss_index.bin"
DOCS_PATH = "backend/data/index_store/documents.json"
GMM_PATH = "backend/data/index_store/gmm_model.pkl"
n_clusters = 5  # Standard GMM cluster components

