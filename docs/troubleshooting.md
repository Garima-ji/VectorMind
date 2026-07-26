# VectorMind Troubleshooting Guide

## Site Not Working - Common Issues & Solutions

### 1. **Frontend Shows "Failed to fetch search results" Error**

**Cause:** The frontend cannot connect to the backend API.

**Solutions:**

#### a) **For Local Development**
1. Ensure both backend and frontend are running:
   ```bash
   # Terminal 1: Start backend
   cd VectorMind
   pip install -r requirements.txt
   python verify_startup.py
   python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
   
   # Terminal 2: Start frontend
   cd frontend
   npm install
   npm run dev
   ```

2. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "embedding_model": "ready",
     "cache": "ready",
     ...
   }
   ```

3. Check frontend environment variable:
   - Ensure `frontend/.env.local` exists with:
     ```
     NEXT_PUBLIC_API_URL=http://localhost:8000
     ```

#### b) **For Production (Vercel Deployment)**
1. Deploy backend to **Hugging Face Spaces** or **Railway**
2. Get the backend URL (e.g., `https://your-backend.hf.space`)
3. In Vercel project settings → Environment Variables, add:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.hf.space
   ```
4. Redeploy the frontend

---

### 2. **Backend Takes Forever to Start (Stuck on Initialization)**

**Cause:** First startup downloads models and processes the dataset.

**Solution:**
- Models (~500MB) are auto-downloaded on first run
- 20newsgroups dataset processing takes **2-5 minutes**
- **Wait for the message:** `"VectorMind API initialization completed. Server is READY!"`
- Check logs for progress:
  ```
  [INFO] Loading newsgroups dataset...
  [INFO] Preprocessing documents...
  [INFO] Generating dense vector embeddings...
  [INFO] Adding documents to FAISS index...
  [INFO] Fitting fuzzy clustering (GMM) model...
  [INFO] Saving index and model to disk...
  ```

---

### 3. **Memory Issues or Out of Disk Space**

**Models & Data Size:**
- SentenceTransformer model: ~170MB
- Cross-Encoder model: ~150MB
- T5 Generator model: ~250MB
- FAISS + GMM models: ~50MB
- **Total: ~620MB**

**Solutions:**
```bash
# Check disk space
df -h

# Clear old model cache (if needed)
rm -rf ~/.cache/huggingface/
rm -rf ~/.cache/torch/

# Run with less memory (set lower batch sizes in code)
```

---

### 4. **Port Already in Use (Port 8000 or 3000)**

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001
```

---

### 5. **Docker/Container Issues**

**Building the Docker image:**
```bash
docker build -t vectormind .
docker run -p 8000:7860 vectormind
```

**Common Docker issues:**
- Models re-download inside container (adds 5min startup)
- Use BuildKit for faster builds: `docker buildx build -t vectormind .`
- Mount volume to persist models:
  ```bash
  docker run -p 8000:7860 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -v ~/.cache/torch:/root/.cache/torch \
    vectormind
  ```

---

### 6. **CORS or Requests Being Blocked**

**Issue:** Frontend gets CORS errors even though backend allows it.

**Check:**
1. Backend has `allow_origins=["*"]` ✓
2. Frontend is making requests to correct URL
3. Browser console shows CORS error

**Fix in backend if needed:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✓ Already set
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 7. **API Endpoints Return Errors**

**Test each endpoint:**

```bash
# Health check
curl http://localhost:8000/health

# Simple query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning"}'

# Analytics
curl http://localhost:8000/analytics

# Clusters visualization
curl http://localhost:8000/clusters/visualization

# Evaluation
curl http://localhost:8000/evaluate?k=5
```

**Common errors:**
- **503 Service Unavailable:** Components not initialized (wait for startup)
- **400 Bad Request:** Empty query string
- **500 Server Error:** Check backend logs for stack trace

---

### 8. **Cluster Visualization Not Loading**

**Issue:** "Calculating t-SNE projections..." spins forever

**Solution:**
- t-SNE can be slow on first run (~30-60 seconds)
- If stuck > 2 minutes, restart backend
- Check RAM: t-SNE needs ~500MB for 20newsgroups

**Debug:**
```python
# In backend/api/main.py, add timeout
tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=1000)
```

---

### 9. **Verify Full Setup With Test Script**

Run the included test suite:
```bash
# Terminal with backend running on port 8000
python test_api.py
```

Should output:
```
Testing health endpoint...
Status: 200
Response: {'status': 'running', 'embedding_model': 'loaded', ...}

Testing query endpoint...
Status: 200
...

All tests completed successfully!
```

---

### 10. **Still Not Working? Debug Checklist**

- [ ] Backend runs without errors: `python verify_startup.py`
- [ ] Backend is accessible: `curl http://localhost:8000/health` returns 200
- [ ] Frontend `.env.local` has correct API URL
- [ ] Browser console shows actual error (not just loading)
- [ ] Network tab shows API requests (not blocked)
- [ ] Firewall allows port 8000 (local) or backend is public (production)
- [ ] Models are fully downloaded (~5-10 minutes first time)
- [ ] 2GB+ RAM available (check with `free -h` or `top`)
- [ ] Fresh npm install in frontend: `rm -rf node_modules && npm install`

---

## Quick Start for Local Testing

```bash
# Setup backend
git clone https://github.com/Garima-ji/VectorMind.git
cd VectorMind
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python verify_startup.py

# In one terminal - start backend
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000

# In another terminal - start frontend
cd frontend
npm install
npm run dev

# Visit http://localhost:3000
```

---

## For Production (Vercel + HF Spaces)

1. **Deploy Backend to Hugging Face Spaces:**
   - Create new Space
   - Select "Docker" runtime
   - Upload Dockerfile + code
   - Space URL: `https://username-vectormind.hf.space`

2. **Deploy Frontend to Vercel:**
   - Connect GitHub repo
   - Root directory: `frontend`
   - Environment variables:
     - `NEXT_PUBLIC_API_URL=https://username-vectormind.hf.space`
   - Deploy

3. **Share your Vercel URL!**

---

## Need More Help?

- Check backend logs: `docker logs <container_id>` (if using Docker)
- Check browser console: F12 → Console tab
- Test API directly: Postman or Insomnia
- Review API source: `backend/api/main.py`
