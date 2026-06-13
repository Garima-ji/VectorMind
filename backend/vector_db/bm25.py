"""BM25 search engine for keyword-based document retrieval."""
import math
import re
from collections import Counter

def tokenize(text):
    """Clean and tokenize text into words."""
    if not text:
        return []
    text = text.lower()
    # Replace special characters with spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.split()

class BM25Retriever:
    """Okapi BM25 ranking algorithm implementation."""
    
    def __init__(self, documents=None, k1=1.5, b=0.75):
        """
        Initialize BM25 with a corpus.
        
        Args:
            documents: List of document strings
            k1: Term frequency scaling parameter (typically 1.2 to 2.0)
            b: Document length scaling parameter (typically 0.75)
        """
        self.k1 = k1
        self.b = b
        self.documents = []
        self.doc_lengths = []
        self.avg_doc_len = 0
        self.doc_freqs = []
        self.term_df = Counter()
        self.idf = {}
        
        if documents:
            self.fit(documents)
            
    def fit(self, documents):
        """Fit BM25 parameters on a corpus of documents."""
        self.documents = documents
        self.doc_lengths = [len(tokenize(doc)) for doc in documents]
        self.avg_doc_len = sum(self.doc_lengths) / len(documents) if documents else 0
        
        self.doc_freqs = []
        self.term_df = Counter()
        
        for doc in documents:
            terms = tokenize(doc)
            self.doc_freqs.append(Counter(terms))
            for term in set(terms):
                self.term_df[term] += 1
                
        # Precompute IDF for all terms in vocabulary
        num_docs = len(documents)
        for term, df in self.term_df.items():
            # Smoothed IDF to prevent negative values
            self.idf[term] = math.log((num_docs - df + 0.5) / (df + 0.5) + 1.0)
            
    def get_score(self, doc_idx, query_terms):
        """Calculate BM25 score for a single document given a tokenized query."""
        score = 0.0
        doc_freq = self.doc_freqs[doc_idx]
        d_len = self.doc_lengths[doc_idx]
        
        for term in query_terms:
            if term not in self.idf:
                continue
            tf = doc_freq.get(term, 0)
            if tf == 0:
                continue
                
            idf = self.idf[term]
            # Okapi BM25 formula tf component
            tf_component = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * (d_len / self.avg_doc_len)))
            score += idf * tf_component
            
        return score
        
    def search(self, query, k=5):
        """
        Search for top-k similar documents.
        
        Args:
            query: Query string
            k: Number of top results to return
            
        Returns:
            List of tuples: (document, similarity_score, doc_index)
        """
        if not self.documents:
            return []
            
        query_terms = tokenize(query)
        if not query_terms:
            return []
            
        scores = []
        for idx in range(len(self.documents)):
            score = self.get_score(idx, query_terms)
            if score > 0.0:
                scores.append((self.documents[idx], float(score), idx))
                
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]
