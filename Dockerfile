FROM python:3.10-slim

# Create a non-root user (UID 1000) as required by Hugging Face Spaces
RUN useradd -m -u 1000 user

# Set up working directory inside the user's home
WORKDIR /home/user/app
RUN chown -R user:user /home/user/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Switch to the non-root user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Pre-download models inside the user's home directory cache so they are available at runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"
RUN python -c "from transformers import pipeline; pipeline('text2text-generation', model='google/flan-t5-small')"
RUN python -c "from sklearn.datasets import fetch_20newsgroups; fetch_20newsgroups(subset='train')"

# Copy project files with ownership set to the non-root user
COPY --chown=user . .

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/')" || exit 1

CMD uvicorn backend.api.main:app --host 0.0.0.0 --port 7860
