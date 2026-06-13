"""Text cleaning utilities."""
import re

def clean_text(text):
    """
    Clean text by:
    - Converting to lowercase
    - Removing special characters
    - Removing extra whitespace
    
    Args:
        text: Input text string
    
    Returns:
        Cleaned text string
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
