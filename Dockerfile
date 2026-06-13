FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SentenceTransformer model to cache in Docker layer
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Pre-download scikit-learn newsgroups dataset to cache in Docker layer
RUN python -c "from sklearn.datasets import fetch_20newsgroups; fetch_20newsgroups(subset='train')"

COPY . .

CMD uvicorn backend.api.main:app --host 0.0.0.0 --port 7860