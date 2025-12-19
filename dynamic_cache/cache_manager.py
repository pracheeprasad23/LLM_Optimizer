"""
Semantic cache manager with FAISS integration
"""
import faiss
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
import logging
from models import CacheEntry, CacheMetrics
from embedding_service import EmbeddingService
from cache_policy import CacheDecisionPolicy
from config import config

logger = logging.getLogger(__name__)


class SemanticCacheManager:
    """
    Main cache manager with FAISS-based semantic search and intelligent eviction
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.cache_policy = CacheDecisionPolicy()
        
        # FAISS index for semantic similarity (using Inner Product for cosine similarity)
        self.index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
        
        # Cache storage (maps index position to cache entry)
        self.cache_entries: List[CacheEntry] = []
        
        # Metrics tracking
        self.metrics = CacheMetrics()
        
        # Eviction history tracking
        self.eviction_history: List[Dict[str, Any]] = []
        
        # Dynamic thresholds (can be adjusted by optimizer)
        self.current_thresholds = {
            "short": config.THRESHOLD_SHORT_QUERY,
            "medium": config.THRESHOLD_MEDIUM_QUERY,
            "long": config.THRESHOLD_LONG_QUERY,
        }
    
    def get_adaptive_threshold(self, query: str) -> float:
        """
        Get adaptive similarity threshold based on query characteristics
        
        Args:
            query: Input query
            
        Returns:
            Similarity threshold
        """
        query_length = len(query)
        
        if query_length < config.SHORT_QUERY_MAX_LENGTH:
            return self.current_thresholds["short"]
        elif query_length < config.MEDIUM_QUERY_MAX_LENGTH:
            return self.current_thresholds["medium"]
        else:
            return self.current_thresholds["long"]
    
    async def search(self, query: str) -> Tuple[Optional[CacheEntry], float, float]:
        """
        Search for similar cached query
        
        Args:
            query: Input query
            
        Returns:
            Tuple of (cache_entry or None, similarity_score, threshold_used)
        """
        if self.index.ntotal == 0:
            return None, 0.0, self.get_adaptive_threshold(query)
        
        # Get query embedding
        query_embedding = await self.embedding_service.embed_query(query)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, k=1)
        
        best_similarity = float(distances[0][0])
        best_index = int(indices[0][0])
        
        # Get adaptive threshold
        threshold = self.get_adaptive_threshold(query)
        
        # Check if similarity meets threshold
        if best_similarity >= threshold:
            cache_entry = self.cache_entries[best_index]
            logger.info(f"CACHE HIT: similarity={best_similarity:.4f}, threshold={threshold:.4f}")
            return cache_entry, best_similarity, threshold
        
        logger.info(f"CACHE MISS: similarity={best_similarity:.4f}, threshold={threshold:.4f}")
        return None, best_similarity, threshold
    
    async def add(
        self,
        query: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        best_similarity: Optional[float] = None
    ) -> bool:
        """
        Add entry to cache if it passes the decision policy
        
        Args:
            query: Original query
            response: LLM response
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            cost: Cost of the LLM call
            best_similarity: Similarity to closest existing entry
            
        Returns:
            True if cached, False otherwise
        """
        total_tokens = input_tokens + output_tokens
        
        # Apply cache decision policy
        should_cache = self.cache_policy.should_cache(
            response_text=response,
            tokens_used=total_tokens,
            best_similarity_score=best_similarity,
            estimated_cost=cost
        )
        
        if not should_cache:
            return False
        
        # Check if cache is full and evict if needed
        if len(self.cache_entries) >= config.MAX_CACHE_SIZE:
            self._evict_entries()
        
        # Get embedding for the query
        query_embedding = await self.embedding_service.embed_query(query)
        
        # Create cache entry
        entry = CacheEntry(
            query=query,
            response=response,
            embedding=query_embedding.tolist(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost
        )
        
        # Add to FAISS index
        self.index.add(query_embedding.reshape(1, -1))
        
        # Add to cache storage
        self.cache_entries.append(entry)
        
        # Update metrics
        self.metrics.cache_size = len(self.cache_entries)
        
        logger.info(f"Added to cache: '{query[:50]}...' (total entries: {len(self.cache_entries)})")
        return True
    
    def update_hit(self, entry: CacheEntry, similarity: float, tokens_saved: int, cost_saved: float):
        """
        Update cache entry on hit
        
        Args:
            entry: Cache entry that was hit
            similarity: Similarity score of the hit
            tokens_saved: Tokens saved by using cache
            cost_saved: Cost saved by using cache
        """
        entry.hits += 1
        entry.last_access = datetime.utcnow()
        
        # Update average similarity (moving average)
        entry.avg_similarity = (
            (entry.avg_similarity * (entry.hits - 1) + similarity) / entry.hits
        )
        
        entry.llm_tokens_saved += tokens_saved
        
        # Update metrics
        self.metrics.llm_tokens_saved += tokens_saved
        self.metrics.total_cost_saved += cost_saved
    
    def _evict_entries(self):
        """
        Evict low-value entries when cache is full
        Uses intelligent value-based eviction, NOT simple LRU
        """
        num_to_evict = max(1, int(len(self.cache_entries) * config.EVICTION_PERCENTAGE))
        
        logger.info(f"🗑️ Cache full ({len(self.cache_entries)} entries), evicting {num_to_evict} entries")
        
        # Calculate value scores for all entries
        now = datetime.utcnow()
        entry_values = []
        
        for idx, entry in enumerate(self.cache_entries):
            age_seconds = (now - entry.created_at).total_seconds()
            value = self.cache_policy.calculate_cache_value(
                hits=entry.hits,
                age_seconds=age_seconds,
                avg_similarity=entry.avg_similarity,
                tokens_saved=entry.llm_tokens_saved
            )
            entry_values.append((idx, value, entry))
        
        # Sort by value (ascending) to get lowest value entries
        entry_values.sort(key=lambda x: x[1])
        
        # Get indices to evict
        indices_to_evict = [idx for idx, _, _ in entry_values[:num_to_evict]]
        indices_to_evict.sort(reverse=True)  # Remove from end to avoid index shifting
        
        # Log evictions with full details
        for idx in indices_to_evict:
            entry = self.cache_entries[idx]
            age_hours = (now - entry.created_at).total_seconds() / 3600
            value_score = entry_values[[i for i, (ei, _, _) in enumerate(entry_values) if ei == idx][0]][1]
            
            # Store in history
            self.eviction_history.append({
                "timestamp": now.isoformat(),
                "query": entry.query,
                "response": entry.response[:100],
                "hits": entry.hits,
                "age_hours": round(age_hours, 2),
                "value_score": round(value_score, 4),
                "avg_similarity": round(entry.avg_similarity, 4),
                "tokens_saved": entry.llm_tokens_saved,
                "reason": "Low value score"
            })
            
            logger.warning(
                f"🗑️ EVICTING: '{entry.query[:60]}...' | "
                f"Hits: {entry.hits} | Age: {age_hours:.1f}h | "
                f"Value: {value_score:.4f} | Similarity: {entry.avg_similarity:.4f} | "
                f"Tokens Saved: {entry.llm_tokens_saved}"
            )
        
        # Remove from cache_entries and rebuild FAISS index
        for idx in indices_to_evict:
            del self.cache_entries[idx]
        
        # Rebuild FAISS index
        self._rebuild_index()
        
        # Update metrics
        self.metrics.evictions += num_to_evict
        self.metrics.cache_size = len(self.cache_entries)
    
    def _rebuild_index(self):
        """Rebuild FAISS index from current cache entries"""
        self.index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
        
        if len(self.cache_entries) > 0:
            embeddings = np.array([entry.embedding for entry in self.cache_entries], dtype=np.float32)
            self.index.add(embeddings)
        
        logger.info(f"FAISS index rebuilt with {len(self.cache_entries)} entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get detailed cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        if len(self.cache_entries) == 0:
            return {
                "total_entries": 0,
                "avg_hits_per_entry": 0,
                "avg_age_seconds": 0,
                "top_queries": [],
                "value_distribution": {},
            }
        
        now = datetime.utcnow()
        total_hits = sum(entry.hits for entry in self.cache_entries)
        total_age = sum((now - entry.created_at).total_seconds() for entry in self.cache_entries)
        
        # Get top queries by hits
        sorted_entries = sorted(self.cache_entries, key=lambda e: e.hits, reverse=True)
        top_queries = [
            {
                "query": entry.query[:100],
                "hits": entry.hits,
                "tokens_saved": entry.llm_tokens_saved,
                "avg_similarity": round(entry.avg_similarity, 4),
            }
            for entry in sorted_entries[:5]
        ]
        
        # Value distribution
        value_scores = []
        for entry in self.cache_entries:
            age_seconds = (now - entry.created_at).total_seconds()
            value = self.cache_policy.calculate_cache_value(
                hits=entry.hits,
                age_seconds=age_seconds,
                avg_similarity=entry.avg_similarity,
                tokens_saved=entry.llm_tokens_saved
            )
            value_scores.append(value)
        
        value_distribution = {
            "min": round(min(value_scores), 4) if value_scores else 0,
            "max": round(max(value_scores), 4) if value_scores else 0,
            "avg": round(sum(value_scores) / len(value_scores), 4) if value_scores else 0,
        }
        
        return {
            "total_entries": len(self.cache_entries),
            "avg_hits_per_entry": round(total_hits / len(self.cache_entries), 2),
            "avg_age_seconds": round(total_age / len(self.cache_entries), 0),
            "top_queries": top_queries,
            "value_distribution": value_distribution,
        }
    
    def clear(self):
        """Clear all cache entries and reset metrics"""
        self.index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
        self.cache_entries = []
        self.metrics = CacheMetrics()
        self.eviction_history = []
        logger.info("Cache cleared")
    
    def get_eviction_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent eviction history"""
        return self.eviction_history[-limit:]
