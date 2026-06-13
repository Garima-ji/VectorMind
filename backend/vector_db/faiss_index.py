"""FAISS vector index for similarity search."""
import os
import json
import numpy as np

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

class FAISSIndex:
    """FAISS index wrapper for document embeddings with NumPy fallback."""
    
    def __init__(self, dimension):
        """
        Initialize index.
        
        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        self.documents = []
        self.using_faiss = HAS_FAISS
        
        if self.using_faiss:
            try:
                self.index = faiss.IndexFlatIP(dimension)  # Cosine similarity via Inner Product
            except Exception as e:
                print(f"Warning: Failed to initialize FAISS index: {e}. Falling back to NumPy flat index.")
                self.using_faiss = False
                self.embeddings = np.empty((0, dimension), dtype='float32')
        else:
            self.embeddings = np.empty((0, dimension), dtype='float32')

    def add_documents(self, embeddings, documents):
        """
        Add documents and their embeddings to the index.
        
        Args:
            embeddings: numpy array of embeddings (normalized)
            documents: List of document texts
        """
        if len(embeddings) == 0:
            return
            
        embeddings_float = embeddings.astype('float32')
        # Normalize embeddings for cosine similarity
        norm = np.linalg.norm(embeddings_float, axis=1, keepdims=True)
        norm[norm == 0] = 1.0
        normalized_embeddings = embeddings_float / norm
        
        if self.using_faiss:
            try:
                self.index.add(normalized_embeddings)
            except Exception as e:
                print(f"Error adding to FAISS index: {e}. Switching to NumPy fallback.")
                self.using_faiss = False
                self.embeddings = np.vstack([self.embeddings, normalized_embeddings])
        else:
            self.embeddings = np.vstack([self.embeddings, normalized_embeddings])
            
        self.documents.extend(documents)
    
    def search(self, query_embedding, k=5):
        """
        Search for top-k similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
        
        Returns:
            List of tuples (document, similarity_score, index)
        """
        if not self.documents:
            return []
            
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
            
        k = min(k, len(self.documents))
        
        if self.using_faiss:
            try:
                scores, indices = self.index.search(query_embedding, k)
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx >= 0 and idx < len(self.documents):
                        results.append((self.documents[idx], float(score), int(idx)))
                return results
            except Exception as e:
                print(f"FAISS search failed: {e}. Falling back to NumPy search.")
        
        # NumPy search fallback (Cosine similarity: dot product of normalized vectors)
        if len(self.embeddings) == 0:
            return []
        scores = np.dot(self.embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(scores)[-k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append((self.documents[idx], float(scores[idx]), int(idx)))
        return results

    def save(self, index_path, docs_path):
        """
        Persist the FAISS index / NumPy embeddings and documents list.
        """
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        os.makedirs(os.path.dirname(docs_path), exist_ok=True)
        
        # Save documents
        with open(docs_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
            
        # Save index
        if self.using_faiss:
            try:
                faiss.write_index(self.index, index_path)
                meta_path = index_path + ".meta"
                with open(meta_path, 'w') as f:
                    f.write("faiss")
            except Exception as e:
                print(f"Error saving FAISS index: {e}. Attempting numpy save.")
                np.save(index_path + ".npy", self.embeddings)
        else:
            np.save(index_path + ".npy", self.embeddings)

    def load(self, index_path, docs_path):
        """
        Load persisted index and documents.
        """
        if not os.path.exists(docs_path):
            raise FileNotFoundError(f"Documents file not found: {docs_path}")
            
        with open(docs_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
            
        if self.using_faiss and os.path.exists(index_path) and os.path.exists(index_path + ".meta"):
            try:
                self.index = faiss.read_index(index_path)
                self.using_faiss = True
                return
            except Exception as e:
                print(f"Error reading FAISS index: {e}. Trying numpy load.")
                
        # Fallback NumPy loading
        npy_path = index_path + ".npy"
        if os.path.exists(npy_path):
            self.embeddings = np.load(npy_path)
            self.using_faiss = False
        else:
            raise FileNotFoundError(f"Persisted index file not found: {index_path} or {npy_path}")

