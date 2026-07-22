# VectorMind - Quick Fix Guide

## 🔴 Problem: Frontend Can't Connect to Backend

Your frontend at `https://vector-mind-gp.vercel.app/` is showing:
```
"Failed to fetch search results. Verify that your backend container is running."
```

## ✅ Solution: Add Environment Variable to Vercel

### Step 1: Get Your Backend URL
- Backend is deployed on Hugging Face Spaces
- URL format: `https://garima-ji-vectormind.hf.space`
- **Go to:** https://huggingface.co/spaces to find your exact Space URL

### Step 2: Add to Vercel Environment

1. Go to: **https://vercel.com/dashboard**
2. Click on your **VectorMind** project
3. Navigate to: **Settings → Environment Variables**
4. Add new variable:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://garima-ji-vectormind.hf.space
   ```
   (Replace with your actual HF Space URL)
5. Click "Save"
6. Go to **Deployments** and click **Redeploy** on the latest deployment

### Step 3: Wait for Redeployment
- Vercel will rebuild and redeploy automatically
- Takes about 2-3 minutes

### Step 4: Test
- Visit: https://vector-mind-gp.vercel.app/
- Try searching for "machine learning"
- ✅ Should now work!

---

## For Local Testing

If you want to test locally with the local backend:

```bash
# Terminal 1: Start backend
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev

# Visit: http://localhost:3000
```

The `frontend/.env.local` file already has the correct local URL.

---

## 🐛 Troubleshooting

### Backend URL is wrong?
```bash
# Test if backend is running by visiting this URL in your browser:
https://garima-ji-vectormind.hf.space/health
```

If it shows:
```json
{"status": "healthy", ...}
```
✅ Backend is working!

If it doesn't work, check:
1. Is your HF Space still running?
2. Is the URL correct?
3. Check HF Spaces dashboard for any errors

### Still not working after setting env var?
1. Hard refresh browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. Clear browser cache
3. Wait 5 minutes for Vercel redeploy to complete
4. Check browser Network tab (F12) for actual error

---

## API Endpoints Available

Your backend supports these endpoints:

- `/` - Health check
- `/query` - Search + RAG
- `/analytics` - Telemetry
- `/clusters/visualization` - 2D visualization
- `/evaluate` - Benchmarking

---

## Need Help?

Check these files:
- `SETUP.md` - Complete setup guide
- `TROUBLESHOOTING.md` - Detailed troubleshooting
- `backend/api/main.py` - API endpoints
- `frontend/app/page.tsx` - Frontend code
