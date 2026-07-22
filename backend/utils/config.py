"""Configuration settings for the semantic search system."""

# Model configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Cache configuration
CACHE_SIMILARITY_THRESHOLD = 0.95

# Search configuration
TOP_K_RESULTS = 5
TOP_K_MIN = 1
TOP_K_MAX = 100

# Persistence configuration
INDEX_PATH = "backend/data/index_store/faiss_index.bin"
DOCS_PATH = "backend/data/index_store/documents.json"
GMM_PATH = "backend/data/index_store/gmm_model.pkl"
ANALYTICS_PATH = "backend/data/analytics.json"
n_clusters = 5  # Standard GMM cluster components

# Advanced models
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
GENERATOR_MODEL = "google/flan-t5-small"
HF_API_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
