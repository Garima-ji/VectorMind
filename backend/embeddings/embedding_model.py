"""Sentence embedding generation using SentenceTransformers."""
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    """Wrapper for SentenceTransformer model."""

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the SentenceTransformer model
        """
        try:
            self.model = SentenceTransformer(model_name, device="cpu")
            self.model_name = model_name
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model '{model_name}': {e}")

    def encode(self, texts, batch_size=8, normalize=True):
        """
        Generate embeddings for texts.

        Args:
            texts: Single text string or list of texts
            batch_size: Batch size for encoding
            normalize: Whether to normalize embeddings

        Returns:
            numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )
            return embeddings
        except Exception as e:
            raise RuntimeError(f"Failed to encode texts: {e}")

    def get_embedding_dim(self):
        """Return the dimension of embeddings."""
        return self.model.get_sentence_embedding_dimension()
