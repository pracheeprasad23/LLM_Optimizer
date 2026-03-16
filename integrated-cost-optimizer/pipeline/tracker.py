"""
Query Tracker
Tracks each query's journey through the pipeline
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque
import uuid
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from models import QueryTrackingInfo, PromptAnalysis


class QueryTracker:
    """Tracks query processing through the pipeline"""
    
    def __init__(self, max_recent: int = None):
        self.max_recent = max_recent or config.MAX_RECENT_QUERIES
        self._recent_queries: deque = deque(maxlen=self.max_recent)
        self._total_queries = 0
        self._total_time_ms = 0.0
        self._total_cost = 0.0
        self._total_cost_saved = 0.0
    
    def create_tracking(self, original_prompt: str) -> QueryTrackingInfo:
        """Create new tracking info for a query"""
        self._total_queries += 1
        return QueryTrackingInfo(
            query_id=f"q-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow(),
            original_prompt=original_prompt,
            optimized_prompt=original_prompt,  # Will be updated
        )
    
    def record_completed(self, tracking: QueryTrackingInfo):
        """Record a completed query"""
        self._recent_queries.append(tracking)
        self._total_time_ms += tracking.total_time_ms
        self._total_cost += tracking.llm_cost
        self._total_cost_saved += tracking.cost_saved
    
    def get_recent_queries(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent queries with tracking info"""
        queries = list(self._recent_queries)
        if limit:
            queries = queries[-limit:]
        return [q.to_dict() for q in reversed(queries)]  # Most recent first
    
    def get_recent_queries_detailed(self, limit: Optional[int] = None) -> List[QueryTrackingInfo]:
        """Get recent queries as full objects"""
        queries = list(self._recent_queries)
        if limit:
            queries = queries[-limit:]
        return list(reversed(queries))
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Get aggregated tracking metrics"""
        return {
            "total_queries": self._total_queries,
            "avg_response_time_ms": round(self._total_time_ms / self._total_queries, 2) if self._total_queries > 0 else 0,
            "total_cost": round(self._total_cost, 6),
            "total_cost_saved": round(self._total_cost_saved, 6),
            "recent_queries_count": len(self._recent_queries),
        }
    
    def clear(self):
        """Clear all tracking data"""
        self._recent_queries.clear()
        self._total_queries = 0
        self._total_time_ms = 0.0
        self._total_cost = 0.0
        self._total_cost_saved = 0.0
