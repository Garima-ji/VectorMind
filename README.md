# VectorMind – Semantic Search System

VectorMind is a lightweight **semantic search engine** that retrieves relevant documents based on meaning rather than simple keyword matching.
The system uses **sentence embeddings, FAISS vector indexing, fuzzy clustering, and semantic caching** to deliver fast and intelligent search results.

This project demonstrates the use of **modern NLP techniques and vector databases** to build scalable semantic search systems.

---

## Key Features

* **Text Preprocessing**

  * Lowercasing
  * Special character removal
  * Whitespace normalization

* **Sentence Embeddings**

  * Uses SentenceTransformers (`all-MiniLM-L6-v2`)
  * Converts text into dense semantic vectors

* **FAISS Vector Index**

  * Fast similarity search
  * Efficient vector storage and retrieval
  * Cosine similarity search

* **Fuzzy Clustering**

  * Gaussian Mixture Model (GMM)
  * Assigns documents to clusters probabilistically

* **Semantic Cache**

  * Stores previous query results
  * Retrieves cached results for highly similar queries
  * Reduces computation time

* **FastAPI Backend**

  * RESTful API endpoints
  * Real-time semantic search queries
  * Cache monitoring and management

---

## Tech Stack

* Python
* FastAPI
* SentenceTransformers
* FAISS
* Scikit-learn
* NumPy
* Uvicorn

---

## Project Architecture

Text Query
→ Text Preprocessing
→ Sentence Embedding
→ FAISS Vector Search
→ Fuzzy Clustering (GMM)
→ Semantic Cache Check
→ Return Top-K Similar Documents

---

## Project Structure

semantic-search-system

backend
│
├── data
│ └── load_dataset.py
│
├── preprocessing
│ ├── text_cleaner.py
│ └── preprocess_pipeline.py
│
├── embeddings
│ └── embedding_model.py
│
├── vector_db
│ └── faiss_index.py
│
├── clustering
│ └── fuzzy_clustering.py
│
├── cache
│ └── semantic_cache.py
│
├── api
│ └── main.py
│
└── utils
└── config.py

frontend

requirements.txt
README.md

---

## Installation

Clone the repository:

```
git clone https://github.com/Garima-ji/VectorMind.git
cd semantic-search-system
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Running the Server

Start the FastAPI server:

```
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Server will run at:

```
http://localhost:8000
```

---

## API Endpoints

### POST /query

Search semantically related documents.

Example request:

```
{
 "query": "artificial intelligence"
}
```

Example response:

```
{
 "query": "artificial intelligence",
 "results": [
  {
   "document": "AI is transforming modern industries...",
   "similarity_score": 0.87
  }
 ]
}
```

---

### GET /cache/stats

Returns semantic cache statistics.

---

### DELETE /cache

Clears cached search results.

---

## API Documentation

FastAPI automatically generates interactive API docs.

Open in browser:

```
http://localhost:8000/docs
```

---

## Dataset

This project uses a subset of the **20 Newsgroups dataset** for demonstration purposes.

The dataset is processed and embedded into vector representations for semantic retrieval.

---

## Future Improvements

* Hybrid keyword + vector search
* Scalable distributed vector database
* Frontend search interface
* Query ranking improvements
* Real-time indexing

---

## Author

Garima Patel



