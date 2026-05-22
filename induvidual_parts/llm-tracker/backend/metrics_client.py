import httpx
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class MetricsClient:
    """
    Client SDK for sending metrics to the LLM Optimization Hub
    
    Usage in your model selection module:
    
    client = MetricsClient(base_url="http://localhost:8000")
    
    # When a request completes:
    client.track_request(
        model="models/gemini-2.5-flash",
        prompt_tokens=100,
        output_tokens=1746,
        total_tokens=2999,
        latency_ms=13596.617,
        user_id="user@example.com",
        team_alias="internal-chatbot-team"
    )
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 10.0
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def track_request(
        self,
        model: str,
        prompt_tokens: int,
        output_tokens: int,
        total_tokens: int,
        latency_ms: float,
        user_id: str = "anonymous",
        request_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Track a request
        
        Args:
            model: Model name (e.g., 'models/gemini-2.5-flash')
            prompt_tokens: Number of prompt tokens
            output_tokens: Number of output tokens
            total_tokens: Total tokens used
            latency_ms: Request latency in milliseconds
            user_id: User identifier
            request_id: Unique request ID (auto-generated if not provided)
            **kwargs: Additional metadata (team_alias, cache_hit, etc.)
        
        Returns:
            Response from metrics API
        """
        
        payload = {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "latency_ms": latency_ms,
            "user_id": user_id,
            "request_id": request_id or str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/metrics/track",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error tracking metrics: {str(e)}")
            raise
    
    async def track_cache_metrics(
        self,
        cache_hit: int,
        cache_miss: int,
        avg_lookup_time_ms: float,
        team_alias: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track cache performance metrics"""
        
        payload = {
            "cache_hit": cache_hit,
            "cache_miss": cache_miss,
            "avg_lookup_time_ms": avg_lookup_time_ms,
            "team_alias": team_alias
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/metrics/cache",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error tracking cache metrics: {str(e)}")
            raise
    
    async def track_batch(
        self,
        batch_id: str,
        batch_size: int,
        total_tokens: int,
        batch_cost: float,
        batch_latency_ms: float,
        status: str = "completed",
        team_alias: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track batch processing metrics"""
        
        payload = {
            "batch_id": batch_id,
            "batch_size": batch_size,
            "total_tokens": total_tokens,
            "batch_cost": batch_cost,
            "batch_latency_ms": batch_latency_ms,
            "status": status,
            "team_alias": team_alias
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/metrics/batch",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error tracking batch metrics: {str(e)}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()


class SyncMetricsClient:
    """
    Synchronous wrapper for MetricsClient
    
    Usage in your model selection module:
    
    client = SyncMetricsClient(base_url="http://localhost:8000")
    
    # When a request completes:
    client.track_request(
        model="models/gemini-2.5-flash",
        prompt_tokens=100,
        output_tokens=1746,
        total_tokens=2999,
        latency_ms=13596.617,
        user_id="user@example.com"
    )
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
    
    def track_request(
        self,
        model: str,
        prompt_tokens: int,
        output_tokens: int,
        total_tokens: int,
        latency_ms: float,
        user_id: str = "anonymous",
        request_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Track a request (synchronous)
        
        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            output_tokens: Number of output tokens
            total_tokens: Total tokens
            latency_ms: Latency in milliseconds
            user_id: User identifier
            request_id: Request ID (auto-generated if not provided)
            **kwargs: Additional metadata
        """
        
        payload = {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "latency_ms": latency_ms,
            "user_id": user_id,
            "request_id": request_id or str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        try:
            response = httpx.post(
                f"{self.base_url}/api/v1/metrics/track",
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error tracking metrics: {str(e)}")
            raise
    
    def track_cache_metrics(
        self,
        cache_hit: int,
        cache_miss: int,
        avg_lookup_time_ms: float,
        team_alias: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track cache performance metrics (synchronous)"""
        
        payload = {
            "cache_hit": cache_hit,
            "cache_miss": cache_miss,
            "avg_lookup_time_ms": avg_lookup_time_ms,
            "team_alias": team_alias
        }
        
        try:
            response = httpx.post(
                f"{self.base_url}/api/v1/metrics/cache",
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error tracking cache metrics: {str(e)}")
            raise
    
    def track_batch(
        self,
        batch_id: str,
        batch_size: int,
        total_tokens: int,
        batch_cost: float,
        batch_latency_ms: float,
        status: str = "completed",
        team_alias: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track batch processing metrics (synchronous)"""
        
        payload = {
            "batch_id": batch_id,
            "batch_size": batch_size,
            "total_tokens": total_tokens,
            "batch_cost": batch_cost,
            "batch_latency_ms": batch_latency_ms,
            "status": status,
            "team_alias": team_alias
        }
        
        try:
            response = httpx.post(
                f"{self.base_url}/api/v1/metrics/batch",
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error tracking batch metrics: {str(e)}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers


# Example usage
if __name__ == "__main__":
    # Synchronous example (simpler for your use case)
    client = SyncMetricsClient(base_url="http://localhost:8000")
    
    try:
        result = client.track_request(
            model="models/gemini-2.5-flash",
            prompt_tokens=10,
            output_tokens=1746,
            total_tokens=1756,
            latency_ms=13596.617,
            user_id="krrish@berri.ai",
            team_alias="internal-chatbot-team",
            cache_hit=False
        )
        print("✅ Metrics tracked:", result)
    except Exception as e:
        print("❌ Error:", e)
