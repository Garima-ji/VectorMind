# Quick Start Guide - Railway Deployment

## 🚀 Deploy in 3 Steps

### Step 1: Verify Locally (Optional but Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Verify everything works
python verify_startup.py

# Start server
uvicorn backend.api.main:app --port 8000

# Test in another terminal
curl http://localhost:8000/
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 3: Deploy on Railway
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway auto-detects Dockerfile
6. Click "Deploy"
7. Wait ~2-3 minutes
8. Get your deployment URL

## ✅ Verify Deployment

### Test Health Endpoint
```bash
curl https://your-app.railway.app/
```

Expected response:
```json
{
  "message": "VectorMind Semantic Search API",
  "status": "running",
  "embedding_model": "loaded"
}
```

### Test Query Endpoint
```bash
curl -X POST https://your-app.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning"}'
```

Expected response:
```json
{
  "query": "machine learning",
  "cache_hit": false,
  "matched_query": null,
  "similarity_score": 1.0,
  "result": "Echo: machine learning",
  "results": [...],
  "dominant_cluster": 0
}
```

### Test Cache
```bash
# Same query again - should hit cache
curl -X POST https://your-app.railway.app/query \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning"}'
```

Expected: `"cache_hit": true`

## 🔧 Troubleshooting

### Build Fails
- Check Railway logs
- Verify Dockerfile syntax
- Ensure requirements.txt is valid

### Server Won't Start
- Check if PORT environment variable is set
- Verify uvicorn command in Dockerfile
- Check Railway startup logs

### Import Errors
- Run `python verify_startup.py` locally
- Check all imports use `backend.` prefix
- Verify requirements.txt has all dependencies

### Memory Issues
- Railway free tier: 512MB RAM
- Current app uses ~400MB
- Should work fine
- If issues, upgrade Railway plan

## 📊 Monitor Deployment

### Railway Dashboard
- View logs in real-time
- Check memory usage
- Monitor request metrics
- View deployment history

### Health Checks
```bash
# Basic health
curl https://your-app.railway.app/

# Detailed health
curl https://your-app.railway.app/health

# Cache stats
curl https://your-app.railway.app/cache/stats
```

## 🎯 What's Working

✅ FastAPI server
✅ Embedding model (all-MiniLM-L6-v2)
✅ Semantic caching
✅ Query endpoint
✅ Health checks
✅ CORS enabled

## 📝 What's Not Included (By Design)

❌ Dataset loading (causes deployment failures)
❌ FAISS index building (too memory intensive)
❌ Clustering (optional feature)

These can be added later as optional features with proper optimization.

## 🔗 Useful Links

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- FastAPI Docs: https://fastapi.tiangolo.com
- SentenceTransformers: https://www.sbert.net

## 💡 Tips

1. **First deployment takes longer** (~3-5 min) - downloading model
2. **Subsequent deploys are faster** (~1-2 min) - cached layers
3. **Monitor logs** during first deployment
4. **Test all endpoints** after deployment
5. **Check memory usage** in Railway dashboard

## 🎉 Success!

If you see this response, you're deployed:
```json
{
  "message": "VectorMind Semantic Search API",
  "status": "running",
  "embedding_model": "loaded"
}
```

Your API is now live and ready to use! 🚀
