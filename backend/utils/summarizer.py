"""AI summary generation utilities."""

def generate_summary(results):
    """
    Generate a summary from top search results.
    
    Args:
        results: List of search result dictionaries
    
    Returns:
        Summary string (max 300 characters)
    """
    if not results:
        return ""
    
    texts = [r["document"] for r in results[:3]]
    combined = " ".join(texts)
    
    return combined[:300]
