"""Fuzzy clustering using Gaussian Mixture Model."""
import pickle
import os
from sklearn.mixture import GaussianMixture
import numpy as np

class FuzzyClustering:
    """GMM-based fuzzy clustering for document embeddings."""
    
    def __init__(self, n_clusters=20, random_state=42):
        """
        Initialize GMM clustering.
        
        Args:
            n_clusters: Number of clusters
            random_state: Random seed
        """
        self.n_clusters = n_clusters
        self.gmm = GaussianMixture(n_components=n_clusters, random_state=random_state)
        self.is_fitted = False
    
    def fit(self, embeddings):
        """
        Fit GMM on embeddings.
        
        Args:
            embeddings: numpy array of embeddings
        """
        self.gmm.fit(embeddings)
        self.is_fitted = True
    
    def predict_proba(self, embeddings):
        """
        Get probability distribution across clusters.
        
        Args:
            embeddings: numpy array of embeddings
        
        Returns:
            Probability matrix (n_samples, n_clusters)
        """
        if not self.is_fitted:
            # Fallback to uniform distribution
            return np.ones((len(embeddings), self.n_clusters)) / self.n_clusters
        try:
            return self.gmm.predict_proba(embeddings)
        except Exception as e:
            print(f"Clustering prediction failed: {e}. Falling back to uniform probabilities.")
            return np.ones((len(embeddings), self.n_clusters)) / self.n_clusters
    
    def get_dominant_cluster(self, embedding):
        """
        Get the dominant cluster for a single embedding.
        
        Args:
            embedding: Single embedding vector
        
        Returns:
            Tuple (cluster_id, probability)
        """
        try:
            probs = self.predict_proba(embedding.reshape(1, -1))[0]
            dominant_cluster = int(np.argmax(probs))
            return dominant_cluster, float(probs[dominant_cluster])
        except Exception as e:
            print(f"Error getting dominant cluster: {e}. Defaulting to cluster 0.")
            return 0, 1.0

    def save(self, path):
        """Save GMM model to path."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'gmm': self.gmm,
                'is_fitted': self.is_fitted,
                'n_clusters': self.n_clusters
            }, f)

    def load(self, path):
        """Load GMM model from path."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Clustering model file not found: {path}")
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.gmm = data['gmm']
            self.is_fitted = data['is_fitted']
            self.n_clusters = data['n_clusters']

