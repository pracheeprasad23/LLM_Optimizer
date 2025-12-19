"""
Adaptive cache decision policy module
"""
from typing import Optional
from config import config
import logging

logger = logging.getLogger(__name__)


class CacheDecisionPolicy:
    """
    Determines whether to cache a response based on multiple factors
    """
    
    def __init__(self):
        self.min_tokens = config.MIN_TOKENS_TO_CACHE
        self.max_tokens = config.MAX_TOKENS_TO_CACHE
        self.min_cost = config.MIN_COST_TO_CACHE
        self.coverage_threshold = config.SIMILARITY_COVERAGE_THRESHOLD
    
    def should_cache(
        self,
        response_text: str,
        tokens_used: int,
        best_similarity_score: Optional[float],
        estimated_cost: float
    ) -> bool:
        """
        Decide whether to cache a response
        
        Args:
            response_text: The LLM response
            tokens_used: Total tokens (input + output)
            best_similarity_score: Similarity to closest existing cache entry (None if first)
            estimated_cost: Cost of the LLM call
            
        Returns:
            True if should cache, False otherwise
        """
        logger.info(f"Cache decision check: tokens={tokens_used}, cost=${estimated_cost:.8f}, similarity={best_similarity_score}")
        
        # Rule 1: Skip very short responses (likely not valuable)
        if tokens_used < self.min_tokens:
            logger.info(f"Skip cache: too short ({tokens_used} < {self.min_tokens} tokens)")
            return False
        
        # Rule 2: Skip very long responses (memory concerns)
        if tokens_used > self.max_tokens:
            logger.info(f"Skip cache: too long ({tokens_used} > {self.max_tokens} tokens)")
            return False
        
        # Rule 3: Skip cheap responses (not worth the memory)
        if estimated_cost < self.min_cost:
            logger.info(f"Skip cache: too cheap (${estimated_cost:.8f} < ${self.min_cost:.8f})")
            return False
        
        # Rule 4: Skip if very similar coverage already exists
        if best_similarity_score is not None and best_similarity_score >= self.coverage_threshold:
            logger.info(f"Skip cache: similar coverage exists ({best_similarity_score:.4f} >= {self.coverage_threshold})")
            return False
        
        # Rule 5: Cache if it passes all checks
        logger.info(f"Cache decision: YES (tokens={tokens_used}, cost=${estimated_cost:.8f})")
        return True
    
    def calculate_cache_value(
        self,
        hits: int,
        age_seconds: float,
        avg_similarity: float,
        tokens_saved: int
    ) -> float:
        """
        Calculate value score for a cache entry
        
        Args:
            hits: Number of cache hits
            age_seconds: Age of the entry in seconds
            avg_similarity: Average similarity of hits
            tokens_saved: Total tokens saved by this entry
            
        Returns:
            Value score (higher is better)
        """
        # Normalize metrics
        # Frequency component (hits)
        frequency_score = min(hits / 10.0, 1.0)  # Cap at 10 hits
        
        # Recency component (inverse of age, with decay)
        max_age = 86400  # 24 hours in seconds
        recency_score = max(0, 1.0 - (age_seconds / max_age))
        
        # Similarity component (how well it matches queries)
        similarity_score = avg_similarity
        
        # Tokens saved component
        tokens_score = min(tokens_saved / 10000.0, 1.0)  # Cap at 10k tokens
        
        # Weighted combination
        value = (
            config.WEIGHT_FREQUENCY * frequency_score +
            config.WEIGHT_RECENCY * recency_score +
            config.WEIGHT_SIMILARITY * similarity_score +
            config.WEIGHT_TOKENS_SAVED * tokens_score
        )
        
        return value
