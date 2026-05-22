from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import MetricsEntry, CacheMetrics, BatchMetrics, ModelMetrics, DailyAggregates
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class QueryType(str, Enum):
    FAQ = "faq"
    REASONING = "reasoning"
    CREATIVE = "creative"
    CODE = "code"
    GENERAL = "general"

class QueryComplexity(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class MetricsTracker:
    """
    Core metrics tracking service
    Receives metrics from model selection module and stores them
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def track_request(
        self,
        model: str,
        prompt_tokens: int,
        output_tokens: int,
        total_tokens: int,
        latency_ms: float,
        request_id: str,
        user_id: str,
        **kwargs
    ) -> MetricsEntry:
        """
        Main method to track a request from model selection module
        
        Args:
            model: Model name (e.g., 'models/gemini-2.5-flash')
            prompt_tokens: Number of prompt tokens
            output_tokens: Number of output tokens
            total_tokens: Total tokens
            latency_ms: Latency in milliseconds
            request_id: Unique request identifier
            user_id: User identifier
            **kwargs: Additional metadata
        
        Returns:
            MetricsEntry: Stored metrics entry
        """
        
        try:
            # Extract additional metadata
            end_user = kwargs.get('end_user', user_id)
            team_alias = kwargs.get('team_alias', 'default')
            organization_alias = kwargs.get('organization_alias', 'default')
            key_alias = kwargs.get('key_alias', 'default')
            
            # Calculate costs (mock pricing - replace with actual pricing)
            response_cost = self._calculate_cost(model, prompt_tokens, output_tokens)
            prompt_cost = self._calculate_prompt_cost(model, prompt_tokens)
            output_cost = response_cost - prompt_cost
            
            # Determine query type and complexity
            query_type = kwargs.get('query_type', QueryType.GENERAL)
            query_complexity = kwargs.get('query_complexity', self._estimate_complexity(total_tokens))
            
            # Cache information
            cache_hit = kwargs.get('cache_hit', False)
            cache_similarity_score = kwargs.get('cache_similarity_score', None)
            
            # Batch information
            is_batched = kwargs.get('is_batched', False)
            batch_id = kwargs.get('batch_id', None)
            batch_size = kwargs.get('batch_size', 1 if not is_batched else None)
            
            # Model tier
            model_tier = kwargs.get('model_tier', self._get_model_tier(model))
            
            # Time to first token (optional)
            time_to_first_token_ms = kwargs.get('time_to_first_token_ms', None)
            
            # Status
            status = kwargs.get('status', 'success')
            error_message = kwargs.get('error_message', None)
            
            # Create metrics entry
            metrics_entry = MetricsEntry(
                timestamp=datetime.utcnow(),
                model=model,
                model_tier=model_tier,
                prompt_tokens=prompt_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                response_cost=response_cost,
                prompt_cost=prompt_cost,
                output_cost=output_cost,
                latency_ms=latency_ms,
                time_to_first_token_ms=time_to_first_token_ms,
                cache_hit=cache_hit,
                cache_similarity_score=cache_similarity_score,
                is_batched=is_batched,
                batch_id=batch_id,
                batch_size=batch_size,
                request_id=request_id,
                user_id=user_id,
                end_user=end_user,
                team_alias=team_alias,
                organization_alias=organization_alias,
                key_alias=key_alias,
                query_type=query_type,
                query_complexity=query_complexity,
                batchable=kwargs.get('batchable', True),
                status=status,
                error_message=error_message,
                additional_usage_values=kwargs.get('additional_usage_values', {}),
                metadata=kwargs.get('metadata', {})
            )
            
            self.db.add(metrics_entry)
            self.db.commit()
            self.db.refresh(metrics_entry)
            
            logger.info(f"Tracked request {request_id} - Cost: ${response_cost:.6f}, Tokens: {total_tokens}, Latency: {latency_ms}ms")
            
            return metrics_entry
            
        except Exception as e:
            logger.error(f"Error tracking request: {str(e)}")
            self.db.rollback()
            raise
    
    def track_cache_metrics(
        self,
        cache_hit: int,
        cache_miss: int,
        avg_lookup_time_ms: float,
        team_alias: str = "default"
    ) -> CacheMetrics:
        """Track cache performance metrics"""
        
        try:
            cache_metric = CacheMetrics(
                timestamp=datetime.utcnow(),
                cache_hit=cache_hit,
                cache_miss=cache_miss,
                avg_cache_lookup_time_ms=avg_lookup_time_ms,
                total_cached_queries=cache_hit + cache_miss,
                team_alias=team_alias
            )
            
            self.db.add(cache_metric)
            self.db.commit()
            
            return cache_metric
        except Exception as e:
            logger.error(f"Error tracking cache metrics: {str(e)}")
            self.db.rollback()
            raise
    
    def track_batch(
        self,
        batch_id: str,
        batch_size: int,
        total_tokens: int,
        batch_cost: float,
        batch_latency_ms: float,
        status: str = "completed",
        team_alias: str = "default"
    ) -> BatchMetrics:
        """Track batch processing metrics"""
        
        try:
            avg_cost_per_query_batched = batch_cost / batch_size
            
            batch_metric = BatchMetrics(
                timestamp=datetime.utcnow(),
                batch_id=batch_id,
                batch_size=batch_size,
                total_tokens_in_batch=total_tokens,
                batch_cost=batch_cost,
                batch_latency_ms=batch_latency_ms,
                avg_cost_per_query_batched=avg_cost_per_query_batched,
                status=status,
                team_alias=team_alias
            )
            
            self.db.add(batch_metric)
            self.db.commit()
            
            logger.info(f"Tracked batch {batch_id} - Size: {batch_size}, Cost: ${batch_cost:.6f}")
            
            return batch_metric
        except Exception as e:
            logger.error(f"Error tracking batch: {str(e)}")
            self.db.rollback()
            raise
    
    # Helper Methods
    
    def _calculate_cost(self, model: str, prompt_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model pricing"""
        
        # Mock pricing - replace with actual pricing
        pricing = {
            "models/gemini-2.5-flash": {"prompt": 0.000075, "output": 0.0003},
            "gpt-4": {"prompt": 0.00003, "output": 0.0006},
            "gpt-4-turbo": {"prompt": 0.00001, "output": 0.00003},
            "gpt-3.5-turbo": {"prompt": 0.0000005, "output": 0.0000015},
            "claude-3-opus": {"prompt": 0.000015, "output": 0.000075},
            "claude-3-sonnet": {"prompt": 0.000003, "output": 0.000015},
        }
        
        model_key = model.lower()
        rates = pricing.get(model_key, {"prompt": 0.00001, "output": 0.00003})
        
        return (prompt_tokens * rates["prompt"]) + (output_tokens * rates["output"])
    
    def _calculate_prompt_cost(self, model: str, prompt_tokens: int) -> float:
        """Calculate prompt-only cost"""
        
        pricing = {
            "models/gemini-2.5-flash": 0.000075,
            "gpt-4": 0.00003,
            "gpt-4-turbo": 0.00001,
            "gpt-3.5-turbo": 0.0000005,
            "claude-3-opus": 0.000015,
            "claude-3-sonnet": 0.000003,
        }
        
        model_key = model.lower()
        rate = pricing.get(model_key, 0.00001)
        
        return prompt_tokens * rate
    
    def _estimate_complexity(self, total_tokens: int) -> str:
        """Estimate query complexity based on token count"""
        if total_tokens < 200:
            return QueryComplexity.SIMPLE
        elif total_tokens < 1000:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.COMPLEX
    
    def _get_model_tier(self, model: str) -> str:
        """Determine model tier"""
        model_lower = model.lower()
        
        if "flash" in model_lower or "3.5" in model_lower or "sonnet" in model_lower:
            return "budget"
        elif "gpt-4-turbo" in model_lower or "opus" in model_lower:
            return "standard"
        else:
            return "premium"


class MetricsAggregator:
    """
    Aggregates metrics for reporting and analysis
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_metrics(
        self,
        time_range_hours: int = 24,
        team_alias: Optional[str] = None,
        model_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get metrics for dashboard display"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        query = self.db.query(MetricsEntry).filter(
            MetricsEntry.timestamp >= cutoff_time,
            MetricsEntry.status == 'success'
        )
        
        if team_alias:
            query = query.filter(MetricsEntry.team_alias == team_alias)
        if model_filter:
            query = query.filter(MetricsEntry.model == model_filter)
        
        entries = query.all()
        
        if not entries:
            return self._empty_metrics()
        
        total_cost = sum(e.response_cost for e in entries)
        total_tokens = sum(e.total_tokens for e in entries)
        avg_latency = sum(e.latency_ms for e in entries) / len(entries)
        cache_hits = sum(1 for e in entries if e.cache_hit)
        cache_hit_rate = (cache_hits / len(entries)) * 100 if entries else 0
        
        # Model distribution
        model_usage = {}
        for entry in entries:
            if entry.model not in model_usage:
                model_usage[entry.model] = {"count": 0, "tokens": 0, "cost": 0}
            model_usage[entry.model]["count"] += 1
            model_usage[entry.model]["tokens"] += entry.total_tokens
            model_usage[entry.model]["cost"] += entry.response_cost
        
        # Hourly trend
        hourly_trend = {}
        for entry in entries:
            hour_key = entry.timestamp.strftime("%Y-%m-%d %H:00")
            if hour_key not in hourly_trend:
                hourly_trend[hour_key] = {"cost": 0, "count": 0}
            hourly_trend[hour_key]["cost"] += entry.response_cost
            hourly_trend[hour_key]["count"] += 1
        
        return {
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_requests": len(entries),
            "avg_latency_ms": avg_latency,
            "cache_hit_rate": cache_hit_rate,
            "error_rate": 0,
            "model_usage": model_usage,
            "hourly_trend": hourly_trend,
            "time_range_hours": time_range_hours
        }
    
    def get_recent_requests(
        self,
        limit: int = 50,
        team_alias: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent requests"""
        
        query = self.db.query(MetricsEntry).order_by(MetricsEntry.timestamp.desc())
        
        if team_alias:
            query = query.filter(MetricsEntry.team_alias == team_alias)
        
        entries = query.limit(limit).all()
        
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "model": e.model,
                "prompt_tokens": e.prompt_tokens,
                "output_tokens": e.output_tokens,
                "total_tokens": e.total_tokens,
                "cost": e.response_cost,
                "latency_ms": e.latency_ms,
                "status": e.status,
                "team": e.team_alias,
                "user": e.end_user,
                "cache_hit": e.cache_hit,
                "request_id": e.request_id
            }
            for e in entries
        ]
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            "total_cost": 0,
            "total_tokens": 0,
            "total_requests": 0,
            "avg_latency_ms": 0,
            "cache_hit_rate": 0,
            "error_rate": 0,
            "model_usage": {},
            "hourly_trend": {}
        }
