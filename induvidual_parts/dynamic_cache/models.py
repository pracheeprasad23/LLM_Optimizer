"""
Data models for cache entries and metrics
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import numpy as np


class CacheEntry(BaseModel):
    """Schema for a cache entry"""
    
    query: str
    response: str
    embedding: List[float]
    hits: int = 0
    avg_similarity: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_access: datetime = Field(default_factory=datetime.utcnow)
    llm_tokens_saved: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    
    class Config:
        arbitrary_types_allowed = True
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "query": self.query,
            "response": self.response,
            "embedding": self.embedding,
            "hits": self.hits,
            "avg_similarity": self.avg_similarity,
            "created_at": self.created_at.isoformat(),
            "last_access": self.last_access.isoformat(),
            "llm_tokens_saved": self.llm_tokens_saved,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
        }


class CacheMetrics(BaseModel):
    """Global cache metrics"""
    
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    llm_tokens_used: int = 0
    llm_tokens_saved: int = 0
    total_cost: float = 0.0
    total_cost_saved: float = 0.0
    cache_size: int = 0
    evictions: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
    
    @property
    def cost_reduction(self) -> float:
        """Calculate cost reduction percentage"""
        total_potential_cost = self.total_cost + self.total_cost_saved
        if total_potential_cost == 0:
            return 0.0
        return (self.total_cost_saved / total_potential_cost) * 100
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": round(self.hit_rate, 4),
            "llm_tokens_used": self.llm_tokens_used,
            "llm_tokens_saved": self.llm_tokens_saved,
            "total_cost": round(self.total_cost, 6),
            "total_cost_saved": round(self.total_cost_saved, 6),
            "cost_reduction_percent": round(self.cost_reduction, 2),
            "cache_size": self.cache_size,
            "evictions": self.evictions,
        }


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    
    query: str
    max_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.7


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    
    response: str
    cached: bool
    similarity_score: Optional[float] = None
    tokens_used: int
    tokens_saved: int
    cost: float
    cost_saved: float
    latency_ms: float
    threshold_used: float


class CacheStats(BaseModel):
    """Detailed cache statistics"""
    
    total_entries: int
    avg_hits_per_entry: float
    avg_age_seconds: float
    top_queries: List[dict]
    value_distribution: dict
