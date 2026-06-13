"""Query translation and expansion using standard domain-specific synonym vocabularies."""
import re

# Dictionary of domain-specific synonyms focusing on 20 Newsgroups topics
SYNONYM_VOCABULARY = {
    "space": ["nasa", "orbit", "satellite", "shuttle", "mission", "cosmic"],
    "moon": ["apollo", "lunar", "landing", "orbit"],
    "graphics": ["card", "gpu", "vga", "drivers", "display", "3d", "rendering"],
    "computer": ["pc", "machine", "hardware", "software", "system", "processor"],
    "ai": ["artificial intelligence", "machine learning", "neural networks", "deep learning"],
    "ml": ["machine learning", "algorithms", "data science"],
    "crypto": ["cryptography", "encryption", "security", "clipper", "key", "privacy"],
    "encryption": ["crypto", "cryptography", "cipher", "security", "key"],
    "security": ["crypto", "encryption", "auth", "privacy", "hacker"],
    "medicine": ["health", "medical", "disease", "drug", "treatment", "therapy", "clinical"],
    "disease": ["illness", "cancer", "sickness", "medical", "symptoms"],
    "hockey": ["nhl", "game", "puck", "team", "playoffs", "player"],
    "politics": ["government", "policy", "law", "senate", "congress", "elections"],
    "religion": ["god", "faith", "christian", "bible", "church", "theology", "belief"]
}

def expand_query(query):
    """
    Expand query with relevant synonyms to improve document recall.
    
    Args:
        query: Original query string
        
    Returns:
        Expanded query string
    """
    if not query:
        return ""
        
    # Standardize and pull lowercase words
    query_cleaned = query.lower()
    words = re.findall(r'[a-z0-9]+', query_cleaned)
    
    expansions = []
    
    # 1. Match individual words
    for word in words:
        if word in SYNONYM_VOCABULARY:
            expansions.extend(SYNONYM_VOCABULARY[word])
            
    # 2. Match multi-word phrases (e.g., 'artificial intelligence')
    for phrase, synonyms in SYNONYM_VOCABULARY.items():
        if len(phrase.split()) > 1 and phrase in query_cleaned:
            expansions.extend(synonyms)
            
    # De-duplicate synonyms and remove words already in query
    unique_expansions = []
    original_words_set = set(words)
    
    for word in expansions:
        if word not in original_words_set and word not in unique_expansions:
            unique_expansions.append(word)
            
    # If synonyms are found, append them to the original query
    if unique_expansions:
        expanded_query = f"{query} {' '.join(unique_expansions)}"
        return expanded_query
        
    return query
