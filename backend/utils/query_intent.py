"""Query intent detection utilities."""

def detect_query_intent(query: str):
    """
    Detect the intent of a search query.
    
    Args:
        query: Search query string
    
    Returns:
        Intent type: 'how-to', 'comparison', 'list', or 'informational'
    """
    query_lower = query.lower()
    
    if query_lower.startswith("how"):
        return "how-to"
    elif " vs " in query_lower or " versus " in query_lower:
        return "comparison"
    elif query_lower.startswith("best") or query_lower.startswith("top"):
        return "list"
    else:
        return "informational"
