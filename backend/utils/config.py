"""Configuration settings for the semantic search system."""

# Model configuration
# JUSTIFICATION FOR EMBEDDING MODEL:
# We selected the 'all-MiniLM-L6-v2' model because it represents an optimal balance 
# between speed and accuracy for a lightweight semantic search system. It generates 
# 384-dimensional dense vectors, keeping memory and CPU footprint small, which fits 
# perfectly for in-memory operations and low-latency cache retrievals on standard machines.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Cache configuration
# JUSTIFICATION FOR CACHE SIMILARITY THRESHOLD:
# A threshold of 0.95 is selected. In semantic caching, a lower threshold (e.g. < 0.9) 
# risks matching queries that are semantically distinct (false cache hits), while a higher
# threshold (> 0.97) behaves too much like exact keyword matching, reducing the cache hit rate.
# 0.95 ensures that queries with minor syntactic differences or close synonyms hit the cache safely.
CACHE_SIMILARITY_THRESHOLD = 0.95

# Search configuration
TOP_K_RESULTS = 5
TOP_K_MIN = 1
TOP_K_MAX = 100

# Persistence configuration
# JUSTIFICATION FOR VECTOR DATABASE (FAISS / Fallback):
# FAISS (specifically FlatIP index) is selected as the vector store because it provides 
# extremely fast, optimized C++ vector similarity searches using inner product / cosine distance.
# We also implement a pure NumPy fallback in faiss_index.py to ensure zero-dependency startup
# robustness in environments where compiled FAISS binaries cannot be loaded.
INDEX_PATH = "backend/data/index_store/faiss_index.bin"
DOCS_PATH = "backend/data/index_store/documents.json"
GMM_PATH = "backend/data/index_store/gmm_model.pkl"
ANALYTICS_PATH = "backend/data/analytics.json"

# JUSTIFICATION FOR CLUSTER COUNT:
# The 20 Newsgroups dataset has 20 ground-truth target classes (e.g., sci.med, rec.autos, alt.atheism).
# To model the natural semantic structure of the dataset, we configure the clustering algorithm
# to find exactly 20 clusters. We use a Gaussian Mixture Model (GMM) instead of K-Means 
# because soft assignments are crucial: a document about gun legislation can overlap with both 
# politics and firearms, and a GMM naturally produces a probability distribution over the clusters.
n_clusters = 20  # Standard GMM cluster components

# Advanced models
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
GENERATOR_MODEL = "google/flan-t5-small"
HF_API_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
