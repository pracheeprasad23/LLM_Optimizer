"""
Embedding Service for Semantic Cache
Supports both Gemini API and full simulation mode
"""
import numpy as np
import hashlib
from typing import List
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config


class EmbeddingService:
    """Handles text embedding using Gemini API or simulation"""
    
    def __init__(self):
        self.dimension = config.EMBEDDING_DIM
        self._genai = None
        
        # Only initialize Gemini if NOT simulating
        if not config.SIMULATE_EMBEDDINGS:
            try:
                import google.generativeai as genai
                if config.GEMINI_API_KEY:
                    genai.configure(api_key=config.GEMINI_API_KEY)
                    self._genai = genai
                    self.model = config.EMBEDDING_MODEL
            except ImportError:
                pass
    
    def normalize_text(self, text: str) -> str:
        """Normalize input text for consistent embeddings"""
        return " ".join(text.lower().strip().split())
    
    def _simulate_embedding(self, text: str) -> np.ndarray:
        """
        Generate a deterministic simulated embedding based on text hash.
        Same text always produces same embedding for cache matching.
        """
        normalized = self.normalize_text(text)
        
        # Create a deterministic seed from the text
        text_hash = hashlib.md5(normalized.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        
        # Generate deterministic random embedding
        rng = np.random.RandomState(seed)
        embedding = rng.randn(self.dimension).astype(np.float32)
        
        # L2 normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    async def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        
        # Always simulate if flag is set or no API configured
        if config.SIMULATE_EMBEDDINGS or self._genai is None:
            return self._simulate_embedding(query)
        
        try:
            normalized_query = self.normalize_text(query)
            result = self._genai.embed_content(
                model=self.model,
                content=normalized_query,
                task_type="retrieval_query"
            )
            embedding = np.array(result['embedding'], dtype=np.float32)
            
            # L2 normalize for cosine similarity
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
        except Exception as e:
            # Fallback to simulation on any error
            print(f"Embedding API error, using simulation: {e}")
            return self._simulate_embedding(query)
    
    async def embed_queries(self, queries: List[str]) -> np.ndarray:
        """Generate embeddings for multiple queries"""
        embeddings = []
        for query in queries:
            emb = await self.embed_query(query)
            embeddings.append(emb)
        return np.array(embeddings, dtype=np.float32)
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return float(np.dot(embedding1, embedding2))

