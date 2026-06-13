"""Cluster analysis utilities."""
import numpy as np

def analyze_clusters(documents, memberships, n_clusters):
    """
    Analyze clusters and find representative documents.
    
    Args:
        documents: List of document texts
        memberships: Cluster membership probabilities (n_samples, n_clusters)
        n_clusters: Number of clusters
    
    Returns:
        Dictionary mapping cluster_id to representative documents
    """
    cluster_examples = {}
    
    for cluster_id in range(n_clusters):
        # Get membership probabilities for this cluster
        cluster_probs = memberships[:, cluster_id]
        
        # Get top 3 documents with highest membership probability
        top_indices = np.argsort(cluster_probs)[-3:][::-1]
        
        examples = []
        for idx in top_indices:
            examples.append({
                "document": documents[idx][:200] + "...",  # Preview
                "probability": round(float(cluster_probs[idx]), 4)
            })
        
        cluster_examples[cluster_id] = examples
    
    return cluster_examples
