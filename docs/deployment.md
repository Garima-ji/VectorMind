# VectorMind Semantic Search API

FastAPI-based semantic search system using SentenceTransformers and semantic caching.

## Features

- Semantic search using SentenceTransformers (all-MiniLM-L6-v2)
- Semantic caching with cosine similarity
- FastAPI REST API
- Docker support
- Railway deployment ready

## API Endpoints

- `GET /` - Health check
- `POST /query` - Semantic search query
- `GET /cache/stats` - Cache statistics
- `DELETE /cache` - Clear cache
- `GET /health` - Detailed health check

## Local Development

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run server:
```bash
uvicorn backend.api.main:app --reload --port 8000
```

### Test API:
```bash
curl http://localhost:8000/
```

## Docker Deployment

### Build image:
```bash
docker build -t vectormind-api .
```

### Run container:
```bash
docker run -p 8000:8000 vectormind-api
```

## Railway Deployment

### Method 1: Using Railway CLI
```bash
railway login
railway init
railway up
```

### Method 2: GitHub Integration
1. Push code to GitHub
2. Connect repository to Railway
3. Railway will auto-detect Dockerfile
4. Deploy automatically

### Environment Variables (Optional)
- `PORT` - Server port (Railway sets automatically)

## API Usage

### Query Example:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning algorithms"}'
```

### Response:
```json
{
  "query": "machine learning algorithms",
  "cache_hit": false,
  "matched_query": null,
  "similarity_score": 1.0,
  "result": "Echo: machine learning algorithms",
  "results": [
    {
      "document": "Echo: machine learning algorithms",
      "similarity_score": 1.0
    }
  ],
  "dominant_cluster": 0
}
```

## Architecture

- **FastAPI**: Web framework
- **SentenceTransformers**: Embedding generation
- **Semantic Cache**: Query result caching
- **Docker**: Containerization

## Memory Optimization

- CPU-only inference (no GPU required)
- Lightweight model (all-MiniLM-L6-v2)
- No dataset loading at startup
- Lazy initialization where possible

## Troubleshooting

### Port binding issues:
Ensure Railway's `PORT` environment variable is used:
```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
```

### Memory issues:
- Use smaller batch sizes
- Reduce cache size
- Use CPU-only torch

### Import errors:
Ensure all imports use `backend.` prefix:
```python
from backend.embeddings.embedding_model import EmbeddingModel
```

## License

MIT
