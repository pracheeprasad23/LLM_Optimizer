"""
Unified Configuration for Integrated LLM Cost Optimizer
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for the integrated cost optimizer"""
    
    # ==========================================================================
    # API Configuration
    # ==========================================================================
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    
    # Simulation Mode - Both true by default for demo without API keys
    SIMULATE_LLM: bool = os.getenv("SIMULATE_LLM", "true").lower() == "true"
    SIMULATE_EMBEDDINGS: bool = os.getenv("SIMULATE_EMBEDDINGS", "true").lower() == "true"
    
    # ==========================================================================
    # Cache Configuration
    # ==========================================================================
    MAX_CACHE_SIZE: int = int(os.getenv("MAX_CACHE_SIZE", "50"))
    EMBEDDING_DIM: int = 3072
    
    # Adaptive Threshold Configuration (based on query length)
    THRESHOLD_SHORT_QUERY: float = 0.85  # < 50 chars (lowered from 0.92)
    THRESHOLD_MEDIUM_QUERY: float = 0.80  # 50-200 chars (lowered from 0.88)
    THRESHOLD_LONG_QUERY: float = 0.75   # > 200 chars (lowered from 0.84)
    
    SHORT_QUERY_MAX_LENGTH: int = 50
    MEDIUM_QUERY_MAX_LENGTH: int = 200
    
    # Cost Configuration (per 1M tokens) - Gemini Flash
    EMBEDDING_COST_PER_1M: float = 0.00  # Free tier
    LLM_INPUT_COST_PER_1M: float = 0.075
    LLM_OUTPUT_COST_PER_1M: float = 0.30
    
    # Cache Decision Policy
    MIN_TOKENS_TO_CACHE: int = 10
    MAX_TOKENS_TO_CACHE: int = 4000
    MIN_COST_TO_CACHE: float = 0.000001
    SIMILARITY_COVERAGE_THRESHOLD: float = 0.98
    
    # Value Scoring Weights (for eviction)
    WEIGHT_FREQUENCY: float = 0.35
    WEIGHT_RECENCY: float = 0.20
    WEIGHT_SIMILARITY: float = 0.25
    WEIGHT_TOKENS_SAVED: float = 0.20
    
    # Eviction Configuration
    EVICTION_PERCENTAGE: float = 0.10
    
    # Optimization Configuration
    OPTIMIZATION_INTERVAL: int = int(os.getenv("OPTIMIZATION_INTERVAL", "50"))
    TARGET_HIT_RATE: float = 0.40
    THRESHOLD_ADJUSTMENT_STEP: float = 0.02
    
    # ==========================================================================
    # Batching Configuration
    # ==========================================================================
    BATCH_BASE_WAIT_MS: int = 80
    BATCH_MIN_WAIT_MS: int = 40
    BATCH_MAX_WAIT_MS: int = 120
    BATCH_DEFAULT_MAX_SIZE: int = 8
    BATCH_DEFAULT_MAX_TOKENS: int = 3000
    
    # ==========================================================================
    # Query Tracking Configuration
    # ==========================================================================
    MAX_RECENT_QUERIES: int = 20
    
    # ==========================================================================
    # Helper Methods
    # ==========================================================================
    @classmethod
    def get_adaptive_threshold(cls, query_length: int) -> float:
        """Get similarity threshold based on query length"""
        if query_length < cls.SHORT_QUERY_MAX_LENGTH:
            return cls.THRESHOLD_SHORT_QUERY
        elif query_length < cls.MEDIUM_QUERY_MAX_LENGTH:
            return cls.THRESHOLD_MEDIUM_QUERY
        else:
            return cls.THRESHOLD_LONG_QUERY
    
    @classmethod
    def calculate_cost(cls, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost of an LLM call"""
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
            "simulate_llm": cls.SIMULATE_LLM,
            "simulate_embeddings": cls.SIMULATE_EMBEDDINGS,
            "thresholds": {
                "short_query": cls.THRESHOLD_SHORT_QUERY,
                "medium_query": cls.THRESHOLD_MEDIUM_QUERY,
                "long_query": cls.THRESHOLD_LONG_QUERY,
            },
            "batching": {
                "base_wait_ms": cls.BATCH_BASE_WAIT_MS,
                "max_batch_size": cls.BATCH_DEFAULT_MAX_SIZE,
                "max_batch_tokens": cls.BATCH_DEFAULT_MAX_TOKENS,
            }
        }


config = Config()
