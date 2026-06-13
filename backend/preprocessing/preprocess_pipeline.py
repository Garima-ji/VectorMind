"""Preprocessing pipeline for text data."""
from backend.preprocessing.text_cleaner import clean_text

def preprocess_documents(documents):
    """
    Apply preprocessing pipeline to a list of documents.
    
    Args:
        documents: List of text documents
    
    Returns:
        List of cleaned documents
    """
    return [clean_text(doc) for doc in documents]
