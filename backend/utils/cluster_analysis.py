"""Cluster analysis utilities."""
import numpy as np

def analyze_clusters(documents, memberships, n_clusters):
    """
    Analyze clusters, find representative documents, and extract boundary/uncertain cases.
    
    Args:
        documents: List of document texts
        memberships: Cluster membership probabilities (n_samples, n_clusters)
        n_clusters: Number of clusters
    
    Returns:
        Dictionary with:
            - 'representative_docs': Map of cluster_id to representative documents
            - 'boundary_cases': List of documents sitting on the boundaries of multiple clusters
    """
    cluster_examples = {}
    
    # 1. Extract representative documents (highest probability for each cluster)
    for cluster_id in range(n_clusters):
        cluster_probs = memberships[:, cluster_id]
        top_indices = np.argsort(cluster_probs)[-3:][::-1]
        
        examples = []
        for idx in top_indices:
            examples.append({
                "document": documents[idx][:200] + "...",  # Preview
                "probability": round(float(cluster_probs[idx]), 4)
            })
        cluster_examples[cluster_id] = examples
    
    # 2. Extract boundary cases (uncertainty where top two cluster probabilities are closest)
    boundary_cases = []
    for idx, probs in enumerate(memberships):
        sorted_indices = np.argsort(probs)[::-1]
        top_idx = int(sorted_indices[0])
        top_p = float(probs[top_idx])
        sec_idx = int(sorted_indices[1])
        sec_p = float(probs[sec_idx])
        
        margin = top_p - sec_p
        boundary_cases.append({
            "index": idx,
            "document": documents[idx][:250] + "...",
            "margin": round(margin, 4),
            "top_cluster": top_idx,
            "top_probability": round(top_p, 4),
            "secondary_cluster": sec_idx,
            "secondary_probability": round(sec_p, 4)
        })
    
    # Sort boundary cases by margin ascending (closest sharing / highest uncertainty first)
    boundary_cases = sorted(boundary_cases, key=lambda x: x["margin"])[:10]
    
    return {
        "representative_docs": cluster_examples,
        "boundary_cases": boundary_cases
    }
