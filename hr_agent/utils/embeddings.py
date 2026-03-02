import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine

class EmbeddingEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.fitted = False
        self.corpus = []
        
    def fit(self, texts):
        """Fit the vectorizer on a corpus of texts."""
        self.corpus = texts
        self.vectorizer.fit(texts)
        self.fitted = True
        
    def get_embedding(self, text):
        """Get embedding for a single text."""
        if not self.fitted:
            raise ValueError("Vectorizer not fitted. Call fit() first.")
        return self.vectorizer.transform([text]).toarray()[0]
    
    def similarity(self, text1, text2):
        """Compute cosine similarity between two texts."""
        if not self.fitted:
            raise ValueError("Vectorizer not fitted. Call fit() first.")
        
        vec1 = self.get_embedding(text1)
        vec2 = self.get_embedding(text2)
        
        # Handle zero vectors
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        
        return 1 - cosine(vec1, vec2)
    
    def batch_similarity(self, text1, texts2):
        """Compute similarities between one text and multiple texts."""
        vec1 = self.get_embedding(text1)
        
        if np.linalg.norm(vec1) == 0:
            return [0.0] * len(texts2)
        
        similarities = []
        for text2 in texts2:
            vec2 = self.get_embedding(text2)
            if np.linalg.norm(vec2) == 0:
                similarities.append(0.0)
            else:
                similarities.append(1 - cosine(vec1, vec2))
        
        return similarities
