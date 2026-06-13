---
title: VectorMind Intelligent Retrieval & RAG Platform
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
---

# VectorMind – Production-Grade Intelligent Retrieval & RAG Platform

VectorMind is a production-grade, portfolio-quality intelligent retrieval and RAG search platform. It upgrades traditional semantic search by combining dense vector retrieval with sparse keyword search, reciprocal rank fusion (RRF), Cross-Encoder reranking, and grounded Retrieval-Augmented Generation (RAG).

The system features real-time 2D topic cluster visualizations, system telemetry analytics, and standard Information Retrieval (IR) benchmarking dashboard.

---

## Key Features

* **Hybrid Retrieval Engine**
  * **Semantic Vector Search (Dense):** Converts queries and documents into dense embeddings using SentenceTransformers (`all-MiniLM-L6-v2`) and searches using FAISS.
  * **Keyword Search (Sparse):** Implements an optimized Okapi BM25 index matching query tokens, filtering out stop-words, and weighting term frequencies.
  * **Reciprocal Rank Fusion (RRF):** Merges dense and sparse candidates by rank to leverage both semantic and keyword signals.

* **Cross-Encoder Reranking**
  * Uses `cross-encoder/ms-marco-MiniLM-L-6-v2` to evaluate retrieved candidates under a binary classification reranker.
  * Returns the top 5 most relevant documents from a candidate set of 20.

* **Grounded RAG Answers**
  * Generates grounded text answers based strictly on retrieved candidate contexts.
  * **Serverless API Support:** Connects to Hugging Face Serverless APIs using `meta-llama/Meta-Llama-3-8B-Instruct`.
  * **Local Fallback:** Automatically runs offline inference locally using `google/flan-t5-small` if API token is absent or rate-limited.

* **Query Expansion & Explanations**
  * **Synonym Expansion:** Translates input terms to equivalent technical and scientific synonyms.
  * **Search Explanations:** Explains exactly why each document was retrieved, showing keyword overlaps, semantic cosine similarity, and RRF rank fusion weights.

* **Telemetry Analytics & IR Evaluation**
  * **System Telemetry:** Logs cache hit rates, average query latencies, top search queries, and active cluster usage.
  * **Evaluation Suite:** Benchmark search precision using **Precision@K**, **Recall@K**, **MRR**, and **NDCG@K** over a 10-query synthetic benchmarking suite.
  * **t-SNE Coordinate Clusters:** Computes 2D t-SNE coordinate projections dynamically to render document cluster maps.

* **Sleek Next.js Dashboard Frontend**
  * Responsive, modern UI including tabs for: Search & RAG, t-SNE Cluster Mapping, System Telemetry Analytics, and Quality Evaluation Benchmarks.

---

## Tech Stack

* **Backend:** FastAPI, SentenceTransformers, FAISS, PyTorch, Scikit-learn, NumPy, PSUtil, Uvicorn
* **Frontend:** Next.js, TailwindCSS (for visual styles), Lucide React, SVG Charting
* **Deployment:** Docker, Hugging Face Spaces / Railway

---

## Project Structure

```
VectorMind-main
├── backend
│   ├── api
│   │   └── main.py             # FastAPI App & Endpoints
│   ├── cache
│   │   └── semantic_cache.py   # Semantic cache for query acceleration
│   ├── clustering
│   │   └── fuzzy_clustering.py # Fuzzy clustering using GMM models
│   ├── data
│   │   └── load_dataset.py     # Loader for Newsgroups dataset
│   ├── embeddings
│   │   ├── embedding_model.py  # Dense vector embeddings wrapper
│   │   └── reranker.py         # Cross-Encoder candidate reranker
│   ├── preprocessing
│   │   ├── preprocess_pipeline.py
│   │   └── text_cleaner.py
│   ├── utils
│   │   ├── analytics.py        # Thread-safe telemetry tracker
│   │   ├── config.py           # Configuration configurations
│   │   ├── evaluator.py        # IR evaluation benchmark calculator
│   │   └── generator.py        # RAG answer generator
│   └── vector_db
│       ├── bm25.py             # Sparse keyword retriever
│       └── faiss_index.py      # Dense FAISS vector storage index
├── frontend
│   ├── app
│   │   ├── page.tsx            # Beautiful redesigned user dashboard
│   │   └── layout.tsx
│   └── package.json
├── verify_startup.py           # ASCII-safe system startup verification
├── test_api.py                 # Endpoint integration verification
├── requirements.txt            # Python dependencies list
└── Dockerfile                  # Hugging Face Spaces build instructions
```

---

## Installation & Startup

### Clone and Install Backend

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Garima-ji/VectorMind.git
   cd VectorMind
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify compilation:**
   ```bash
   py verify_startup.py
   ```

4. **Start the FastAPI backend server:**
   ```bash
   py -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
   ```

5. **Run test integration check:**
   ```bash
   py test_api.py
   ```

---

## Main API Endpoints

### `POST /query`
Performs synonym-expanded hybrid search, Reciprocal Rank Fusion, Cross-Encoder reranking, and grounded RAG answer generation.
* **Payload:**
  ```json
  {
    "query": "machine learning algorithms",
    "top_k": 5,
    "hybrid": true
  }
  ```
* **Response:**
  ```json
  {
    "query": "machine learning algorithms",
    "intent": "informative",
    "cache_hit": false,
    "similarity_score": -9.19,
    "result": "Machine learning algorithms learn patterns from data...",
    "results": [
      {
        "document": "Machine learning uses statistical models...",
        "similarity_score": -9.19,
        "cluster": 3,
        "match_type": "reranked",
        "semantic_score": 0.23,
        "keyword_score": 4.45,
        "rrf_score": 0.015,
        "explanation": "Ranked #1 after Cross-Encoder reranking (score: -9.19). Initially matched via HYBRID search...",
        "index": 184
      }
    ],
    "dominant_cluster": 3,
    "cluster_probability": 1.0,
    "processing_time": 0.28,
    "expanded_query": "machine learning algorithms neural networks AI ML",
    "sources": ["Source 1"]
  }
  ```

### `GET /analytics`
Returns aggregate telemetry including hit rates, latency sparklines, and cluster distributions.

### `GET /evaluate`
Executes IR benchmarking calculations. Returns precision, recall, MRR, and NDCG rates.

### `GET /clusters/visualization`
Generates 2D t-SNE coordinate projections for interactive topic cluster mapping.

### `POST /reindex`
Triggers rebuilding the FAISS vector store, BM25 indices, and GMM models from scratch.

---

## Deploying

VectorMind is pre-configured for deployment:
* **Backend:** Deploy to **Hugging Face Spaces** or **Railway** using the provided `Dockerfile`.
* **Frontend:** Deploy to **Vercel** with the Root Directory set to `frontend` and the `NEXT_PUBLIC_API_URL` env variable pointing to your deployed backend.

---

## Author
Garima Patel
