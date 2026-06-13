"""Verify all imports and dependencies."""
import sys

def verify_imports():
    """Verify all required imports."""
    print("Verifying imports...")
    
    try:
        print("✓ Importing FastAPI...")
        from fastapi import FastAPI, HTTPException
        
        print("✓ Importing Pydantic...")
        from pydantic import BaseModel
        
        print("✓ Importing CORS...")
        from fastapi.middleware.cors import CORSMiddleware
        
        print("✓ Importing SentenceTransformers...")
        from sentence_transformers import SentenceTransformer
        
        print("✓ Importing NumPy...")
        import numpy as np
        
        print("✓ Importing scikit-learn...")
        from sklearn.metrics.pairwise import cosine_similarity
        
        print("✓ Importing backend modules...")
        from backend.embeddings.embedding_model import EmbeddingModel
        from backend.cache.semantic_cache import SemanticCache
        
        print("\n✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        return False

def test_embedding_model():
    """Test embedding model initialization."""
    print("\nTesting embedding model...")
    try:
        from backend.embeddings.embedding_model import EmbeddingModel
        model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        print(f"✓ Model loaded: {model.model_name}")
        print(f"✓ Embedding dimension: {model.get_embedding_dim()}")
        
        # Test encoding
        test_text = "Hello world"
        embedding = model.encode([test_text])[0]
        print(f"✓ Encoding works: shape {embedding.shape}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_cache():
    """Test semantic cache."""
    print("\nTesting semantic cache...")
    try:
        from backend.cache.semantic_cache import SemanticCache
        import numpy as np
        
        cache = SemanticCache(similarity_threshold=0.95)
        print("✓ Cache initialized")
        
        # Test cache operations
        dummy_embedding = np.random.rand(384)
        cache.set(dummy_embedding, "test query", "test result", 0)
        print("✓ Cache set works")
        
        stats = cache.get_stats()
        print(f"✓ Cache stats: {stats}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
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
        print("✓ All checks passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("✗ Some checks failed. Please fix errors before deploying.")
        sys.exit(1)
