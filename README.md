---
title: VectorMind Intelligent Retrieval & RAG Platform
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 8000
---

# VectorMind: Intelligent Semantic Search, Cache & RAG Platform

> **Live Demo Platform**: [https://garimap20-vectormind-api.hf.space/ui/](https://garimap20-vectormind-api.hf.space/ui/)

![VectorMind Dashboard UI](https://raw.githubusercontent.com/Garima-ji/VectorMind/main/docs/assets/dashboard.png)

VectorMind is a production-grade, portfolio-quality intelligent retrieval and RAG search platform. It is fully aligned with the **Trademarkia - AI&ML Engineer Task** specifications, implementing semantic search over the **20 Newsgroups corpus** using FAISS, a Gaussian Mixture Model (GMM) fuzzy clustering layer, and a custom cluster-aware semantic cache built from first principles.

The platform also includes a Next.js web application for real-time topic visualizations (t-SNE coordinates), telemetry analytics, and standard Information Retrieval (IR) benchmarking dashboards.

---

## 🚀 Trademarkia Assignment Architecture

VectorMind implements all four core components requested in the specifications:

### 1. Preprocessing & FAISS Vector DB (Part 1)
* **Pre-processing**: Noisy headers, quoting replies, and signatures are stripped using scikit-learn standard filters to keep search focused on pure message body semantics.
* **Embeddings**: Text is encoded into 384-dimensional dense vectors using the SentenceTransformers `all-MiniLM-L6-v2` model.
* **Vector Index**: Uses a **FAISS** (Facebook AI Similarity Search) FlatIP index for fast cosine similarity lookups, backed by a zero-dependency **NumPy fallback** for environment flexibility.

### 2. GMM Fuzzy Clustering & Boundary Analysis (Part 2)
* **Soft Assignment**: Implements a Gaussian Mixture Model (GMM) clustering layer. Instead of hard categorizing, it returns a probability distribution mapping documents to multiple overlapping topics.
* **Number of Clusters**: Configured to **20 clusters** to naturally capture the 20 newsgroups categories.
* **Boundary Analysis**: Dynamically extracts boundary/uncertain documents—specifically locating items where the probability gap between the top two assigned clusters is lowest.

### 3. Custom Semantic Cache (Part 3)
* **First Principles**: Built entirely using NumPy and scikit-learn cosine similarity (without Redis, Memcached, or external caching middleware).
* **Cluster-Aware Lookups**: Groups cache entries using their GMM dominant cluster. When a new query is run, the cache only searches entries in the matching cluster, preventing search latencies from scaling as the cache grows.
* **Tunable Parameter**: Employs a similarity threshold of `0.95`, balancing search accuracy (precision) against query acceleration (recall).

### 4. FastAPI Service & State Management (Part 4)
Exposes clean REST endpoints on port **8000**:
* `POST /query`: Accepts a query, checks the cluster-aware semantic cache, falls back to a hybrid FAISS+BM25 and Cross-Encoder reranker on a cache miss, and generates grounded RAG answers.
* `GET /cache/stats`: Returns cache metrics (`total_entries`, `hit_count`, `miss_count`, `hit_rate`).
* `DELETE /cache`: Resets and flushes all cache entries and statistics (requires `X-Admin-Token` header).
* `GET /reindex/status`: Check progress of background index jobs.
* `/ui/`: Serves the integrated static frontend dashboard directly from uvicorn, unifying backend and frontend on a single port.

---

## 📂 Directory Structure

```
VectorMind
├── backend
│   ├── api                  # FastAPI web server, routes, and endpoints
│   ├── cache                # Semantic cache and cluster filtering logic
│   ├── clustering           # GMM clustering models and fitting pipelines
│   ├── data                 # Analytics store, data loaders, and saved indices
│   ├── embeddings           # SentenceTransformer and Cross-Encoder models
│   ├── preprocessing        # Text cleaners and newsgroup stripping filters
│   └── utils                # Analytics, config, and generator utilities
├── frontend
│   ├── app                  # Next.js UI dashboard
│   ├── components           # React UI components
│   └── styles               # CSS theme styling
├── tests                    # Startup and API verification scripts
├── Dockerfile               # Port 8000 production container build
├── requirements.txt         # Python backend dependencies
└── README.md                # General system documentation
```

---

## 🛠️ Quick Start & Local Run

### Prerequisites
* Python 3.10 or higher
* Node.js 18 or higher (only if using the Next.js UI dashboard)

### 1. Run the FastAPI Backend

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Startup Configuration**:
   ```bash
   python tests/verify_startup.py
   ```

3. **Start the Uvicorn Server**:
   ```bash
   python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
   ```

### 2. View the Integrated UI Dashboard (No Node.js process needed!)

Since Next.js is compiled and served statically from FastAPI:
1. Open the local address: `http://localhost:8000/ui/` in your browser.
2. The UI dashboard runs immediately, fetching queries and metrics directly.

*(Optional Development Mode: Navigate to `cd frontend`, run `npm install && npm run dev` to start hot-reloading dev mode on `http://localhost:3000`).*

---

## 🐳 Docker Deployment (Port 8000)

VectorMind is containerized and configured to start on port **8000**:

1. **Build the container image**:
   ```bash
   docker build -t vectormind:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 vectormind:latest
   ```

---

## 🧪 Testing the Pipeline

To run the API validation suite and trigger index rebuilding over the full 20 Newsgroups corpus:

```bash
python tests/test_api.py
```
This script validates health routes, checks caching thresholds, retrieves cluster distributions, evaluates system precision/NDCG metrics, and invokes the `/reindex` pipeline.
