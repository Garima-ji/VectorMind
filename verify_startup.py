"""Verify all imports and dependencies."""
import sys

def verify_imports():
    """Verify all required imports."""
    print("Verifying imports...")
    
    try:
        print("[OK] Importing FastAPI...")
        from fastapi import FastAPI, HTTPException
        
        print("[OK] Importing Pydantic...")
        from pydantic import BaseModel
        
        print("[OK] Importing CORS...")
        from fastapi.middleware.cors import CORSMiddleware
        
        print("[OK] Importing SentenceTransformers...")
        from sentence_transformers import SentenceTransformer
        
        print("[OK] Importing NumPy...")
        import numpy as np
        
        print("[OK] Importing scikit-learn...")
        from sklearn.metrics.pairwise import cosine_similarity
        
        print("[OK] Importing backend modules...")
        from backend.embeddings.embedding_model import EmbeddingModel
        from backend.cache.semantic_cache import SemanticCache
        from backend.vector_db.bm25 import BM25Retriever
        from backend.embeddings.reranker import CrossEncoderReranker
        from backend.utils.generator import RAGGenerator
        from backend.utils.query_expansion import expand_query
        from backend.utils.analytics import AnalyticsTracker
        from backend.utils.evaluator import evaluate_system
        
        print("\n[OK] All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n[ERROR] Import error: {e}")
        return False

def test_embedding_model():
    """Test embedding model initialization."""
    print("\nTesting embedding model...")
    try:
        from backend.embeddings.embedding_model import EmbeddingModel
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        print(f"[OK] Model loaded: {model.model_name}")
        print(f"[OK] Embedding dimension: {model.get_embedding_dim()}")
        
        # Test encoding
        test_text = "Hello world"
        embedding = model.encode([test_text])[0]
        print(f"[OK] Encoding works: shape {embedding.shape}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_cache():
    """Test semantic cache."""
    print("\nTesting semantic cache...")
    try:
        from backend.cache.semantic_cache import SemanticCache
        import numpy as np
        
        cache = SemanticCache(similarity_threshold=0.95)
        print("[OK] Cache initialized")
        
        # Test cache operations
        dummy_embedding = np.random.rand(384)
        cache.set(dummy_embedding, "test query", "test result", 0)
        print("[OK] Cache set works")
        
        stats = cache.get_stats()
        print(f"[OK] Cache stats: {stats}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("VectorMind API Startup Verification")
    print("=" * 50)
    
    success = True
    success = verify_imports() and success
    success = test_embedding_model() and success
    success = test_cache() and success
    
    print("\n" + "=" * 50)
    if success:
        print("[OK] All checks passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("[ERROR] Some checks failed. Please fix errors before deploying.")
        sys.exit(1)
