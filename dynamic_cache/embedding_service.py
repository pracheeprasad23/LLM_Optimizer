"""
Embedding service for query vectorization
"""
import numpy as np
from typing import List, Optional
import google.generativeai as genai
from config import config


class EmbeddingService:
    """Handles text embedding using Google Gemini API"""
    
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = config.EMBEDDING_MODEL
        self.dimension = config.EMBEDDING_DIM
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize input text for consistent embeddings
        
        Args:
            text: Raw input text
            
        Returns:
            Normalized text
        """
        # Convert to lowercase, strip whitespace, collapse multiple spaces
        normalized = " ".join(text.lower().strip().split())
        return normalized
    
    async def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query
        
        Args:
            query: Input query text
            
        Returns:
            Embedding vector as float32 numpy array
        """
        normalized_query = self.normalize_text(query)
        
        result = genai.embed_content(
            model=self.model,
            content=normalized_query,
            task_type="retrieval_query"
        )
        
        embedding = np.array(result['embedding'], dtype=np.float32)
        
        # Normalize for cosine similarity (L2 normalization)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    async def embed_queries(self, queries: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple queries (batch)
        
        Args:
            queries: List of input queries
            
        Returns:
            Array of embeddings (N x dimension)
        """
        normalized_queries = [self.normalize_text(q) for q in queries]
        
        # Gemini batch embedding
        result = genai.embed_content(
            model=self.model,
            content=normalized_queries,
            task_type="retrieval_query"
        )
        
        embeddings = np.array(result['embedding'], dtype=np.float32)
        
        # Handle single vs multiple embeddings
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Normalize each embedding
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        return embeddings
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Since embeddings are already normalized, dot product = cosine similarity
        similarity = float(np.dot(embedding1, embedding2))
        return similarity
