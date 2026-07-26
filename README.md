---
title: VectorMind Intelligent Retrieval & RAG Platform
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
---

# VectorMind: Intelligent Retrieval & RAG Platform

VectorMind is a production-grade, portfolio-quality intelligent retrieval and RAG search platform. It merges dense vector retrieval with sparse keyword matching (BM25), reciprocal rank fusion (RRF), Cross-Encoder reranking, and grounded Retrieval-Augmented Generation (RAG) to upgrade traditional semantic search systems.

The platform includes real-time topic clustering visualizations (t-SNE), system telemetry analytics, and standard Information Retrieval (IR) benchmarking dashboards.

---

## Architecture Overview

VectorMind implements a multi-stage hybrid search pipeline to deliver highly accurate, contextual search results and grounded answers:

1. **Query Processing & Expansion**: Input queries are cleaned and expanded with technical and scientific synonyms to bridge the vocabulary gap.
2. **Hybrid Search (Sparse + Dense)**:
   * **Semantic Search (Dense)**: Computes dense sentence embeddings using SentenceTransformers (`all-MiniLM-L6-v2`) and retrieves candidates via a FAISS vector index.
   * **Keyword Search (Sparse)**: Evaluates query token matches using an optimized Okapi BM25 index over the corpus.
3. **Reciprocal Rank Fusion (RRF)**: Merges dense and sparse candidates by rank to combine lexical and semantic matching capabilities.
4. **Cross-Encoder Reranking**: Re-evaluates the top candidates with `cross-encoder/ms-marco-MiniLM-L-6-v2` to return the most relevant documents.
5. **Grounded Generation**: Generates contextual answers based strictly on the retrieved document contexts using Hugging Face's serverless inference APIs (falling back to a local `google/flan-t5-small` model offline).

---

## Directory Structure

```
VectorMind
├── backend
│   ├── api                  # FastAPI web server and endpoints
│   ├── cache                # Semantic cache for query acceleration
│   ├── clustering           # GMM topic clustering models
│   ├── data                 # Persisted indices, analytics, and data loader
│   ├── embeddings           # Dense vector models and Cross-Encoder rerankers
│   ├── preprocessing        # Text normalization and preprocessing pipelines
│   └── utils                # Evaluation metrics, configuration, and generator
├── docs                     # Technical documentation and deployment guides
├── frontend
│   ├── app                  # Next.js dashboard UI
│   ├── components           # React UI components
│   └── styles               # CSS theme styling
├── tests                    # System verification and API test scripts
├── Dockerfile               # Hugging Face Spaces Docker build configuration
├── requirements.txt         # Python dependencies
└── railway.json             # Infrastructure configuration
```

---

## Installation & Startup

### Prerequisites
* Python 3.10 or higher
* Node.js 18 or higher (for the frontend)

### 1. Run the Backend Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Garima-ji/VectorMind.git
   cd VectorMind
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify startup configuration:**
   ```bash
   python tests/verify_startup.py
   ```

4. **Start the FastAPI backend server:**
   ```bash
   python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
   ```

### 2. Run the Frontend Locally

1. **Navigate to the frontend folder:**
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   Create a `.env.local` file in the `frontend` folder:
   ```env
   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
   ```

4. **Start the Next.js development server:**
   ```bash
   npm run dev
   ```

---

## Running Tests

Verify API endpoints using the testing suite:
```bash
python tests/test_api.py
```

---

## Production Deployment

This project is pre-configured for dual-service deployment:

* **Backend (Hugging Face Spaces)**: Built using the root [Dockerfile](Dockerfile). Set the SDK to **Docker** in Hugging Face and configure the container port to `7860`.
* **Frontend (Vercel)**: Point your Vercel deployment to the `frontend` directory. Add the environment variable `NEXT_PUBLIC_API_URL` set to your Hugging Face Space URL (e.g. `https://<username>-<space-name>.hf.space`).
