"""
Configuration module for Adaptive Semantic Cache System
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for the cache system"""
    
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")  # For both LLM and embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    
    # Cache Configuration
    MAX_CACHE_SIZE: int = int(os.getenv("MAX_CACHE_SIZE", "25"))  # Reduced for easier testing
    EMBEDDING_DIM: int = 768  # text-embedding-004 dimension
    
    # Adaptive Threshold Configuration
    # Thresholds based on query length (in characters)
    THRESHOLD_SHORT_QUERY: float = 0.92  # < 50 chars
    THRESHOLD_MEDIUM_QUERY: float = 0.88  # 50-200 chars
    THRESHOLD_LONG_QUERY: float = 0.84  # > 200 chars
    
    SHORT_QUERY_MAX_LENGTH: int = 50
    MEDIUM_QUERY_MAX_LENGTH: int = 200
    
    # Cost Configuration (per 1M tokens)
    EMBEDDING_COST_PER_1M: float = 0.00  # FREE (Gemini embeddings are free up to quota)
    LLM_INPUT_COST_PER_1M: float = 0.075  # $0.075 per 1M tokens (Gemini 1.5 Flash)
    LLM_OUTPUT_COST_PER_1M: float = 0.30  # $0.30 per 1M tokens (Gemini 1.5 Flash)
    
    # Cache Decision Policy
    MIN_TOKENS_TO_CACHE: int = 10  # Don't cache very short responses (lowered for Gemini)
    MAX_TOKENS_TO_CACHE: int = 4000  # Don't cache very long responses
    MIN_COST_TO_CACHE: float = 0.000001  # Minimum cost threshold in dollars (lowered for Gemini)
    SIMILARITY_COVERAGE_THRESHOLD: float = 0.98  # Skip if very similar exists (relaxed for testing)
    
    # Value Scoring Weights
    WEIGHT_FREQUENCY: float = 0.35
    WEIGHT_RECENCY: float = 0.20
    WEIGHT_SIMILARITY: float = 0.25
    WEIGHT_TOKENS_SAVED: float = 0.20
    
    # Eviction Configuration
    EVICTION_PERCENTAGE: float = 0.10  # Evict 10% (2-3 entries when cache has 25)
    MIN_HITS_TO_RETAIN: int = 2  # Entries with < 2 hits are prime for eviction
    
    # Optimization Configuration
    OPTIMIZATION_INTERVAL: int = int(os.getenv("OPTIMIZATION_INTERVAL", "50"))
    TARGET_HIT_RATE: float = 0.40  # Target 40% hit rate
    THRESHOLD_ADJUSTMENT_STEP: float = 0.02
    
    @classmethod
    def get_adaptive_threshold(cls, query_length: int) -> float:
        """
        Determine similarity threshold based on query characteristics
        
        Args:
            query_length: Length of the query in characters
            
        Returns:
            Similarity threshold (0.0 to 1.0)
        """
        if query_length < cls.SHORT_QUERY_MAX_LENGTH:
            return cls.THRESHOLD_SHORT_QUERY
        elif query_length < cls.MEDIUM_QUERY_MAX_LENGTH:
            return cls.THRESHOLD_MEDIUM_QUERY
        else:
            return cls.THRESHOLD_LONG_QUERY
    
    @classmethod
    def calculate_cost(cls, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the cost of an LLM call
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in dollars
        """
        input_cost = (input_tokens / 1_000_000) * cls.LLM_INPUT_COST_PER_1M
        output_cost = (output_tokens / 1_000_000) * cls.LLM_OUTPUT_COST_PER_1M
        return input_cost + output_cost
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            "embedding_model": cls.EMBEDDING_MODEL,
            "llm_model": cls.LLM_MODEL,
            "max_cache_size": cls.MAX_CACHE_SIZE,
            "thresholds": {
                "short_query": cls.THRESHOLD_SHORT_QUERY,
                "medium_query": cls.THRESHOLD_MEDIUM_QUERY,
                "long_query": cls.THRESHOLD_LONG_QUERY,
            },
            "weights": {
                "frequency": cls.WEIGHT_FREQUENCY,
                "recency": cls.WEIGHT_RECENCY,
                "similarity": cls.WEIGHT_SIMILARITY,
                "tokens_saved": cls.WEIGHT_TOKENS_SAVED,
            }
        }


config = Config()
