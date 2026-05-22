from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import uuid

from database import get_db
from metrics_tracker import MetricsTracker, MetricsAggregator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="LLM Optimization Hub - Metrics Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import os
from dotenv import load_dotenv

load_dotenv()  # this will read backend/.env

DATABASE_URL = os.getenv("DATABASE_URL")

# ============================================
# PYDANTIC MODELS
# ============================================

class MetricsPayload(BaseModel):
    """Schema for incoming metrics from model selection module"""
    model: str = Field(..., description="Model name (e.g., 'models/gemini-2.5-flash')")
    prompt_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    timestamp: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    end_user: Optional[str] = None
    team_alias: Optional[str] = None
    organization_alias: Optional[str] = None
    key_alias: Optional[str] = None
    query_type: Optional[str] = None
    cache_hit: Optional[bool] = False
    cache_similarity_score: Optional[float] = None
    is_batched: Optional[bool] = False
    batch_id: Optional[str] = None
    batch_size: Optional[int] = None
    status: Optional[str] = "success"
    error_message: Optional[str] = None
    time_to_first_token_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class CacheMetricsPayload(BaseModel):
    """Schema for cache metrics"""
    cache_hit: int
    cache_miss: int
    avg_lookup_time_ms: float
    team_alias: Optional[str] = None

class BatchMetricsPayload(BaseModel):
    """Schema for batch metrics"""
    batch_id: str
    batch_size: int
    total_tokens: int
    batch_cost: float
    batch_latency_ms: float
    status: Optional[str] = "completed"
    team_alias: Optional[str] = None

class DashboardMetricsResponse(BaseModel):
    """Response schema for dashboard metrics"""
    total_cost: float
    total_tokens: int
    total_requests: int
    avg_latency_ms: float
    cache_hit_rate: float
    error_rate: float
    model_usage: Dict[str, Any]
    hourly_trend: Dict[str, Any]

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/metrics/track")
async def track_metrics(payload: MetricsPayload, db: Session = Depends(get_db)):
    """
    Track metrics from model selection module
    
    Expected input from model selection module:
    {
        'model': 'models/gemini-2.5-flash',
        'prompt_tokens': 10,
        'output_tokens': 1746,
        'total_tokens': 2999,
        'latency_ms': 13596.617,
        'timestamp': '2025-12-14 19:37:14'
    }
    """
    try:
        # Generate request ID if not provided
        request_id = payload.request_id or str(uuid.uuid4())
        user_id = payload.user_id or "anonymous"
        
        # Initialize tracker
        tracker = MetricsTracker(db)
        
        # Track the request
        metrics_entry = tracker.track_request(
            model=payload.model,
            prompt_tokens=payload.prompt_tokens,
            output_tokens=payload.output_tokens,
            total_tokens=payload.total_tokens,
            latency_ms=payload.latency_ms,
            request_id=request_id,
            user_id=user_id,
            end_user=payload.end_user,
            team_alias=payload.team_alias,
            organization_alias=payload.organization_alias,
            key_alias=payload.key_alias,
            query_type=payload.query_type,
            cache_hit=payload.cache_hit,
            cache_similarity_score=payload.cache_similarity_score,
            is_batched=payload.is_batched,
            batch_id=payload.batch_id,
            batch_size=payload.batch_size,
            status=payload.status,
            error_message=payload.error_message,
            time_to_first_token_ms=payload.time_to_first_token_ms,
            metadata=payload.metadata
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": "Metrics tracked successfully",
                "request_id": request_id,
                "cost": float(metrics_entry.response_cost),
                "tokens": metrics_entry.total_tokens
            }
        )
    
    except Exception as e:
        logger.error(f"Error tracking metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/metrics/cache")
async def track_cache_metrics(payload: CacheMetricsPayload, db: Session = Depends(get_db)):
    """Track cache performance metrics"""
    try:
        tracker = MetricsTracker(db)
        cache_metric = tracker.track_cache_metrics(
            cache_hit=payload.cache_hit,
            cache_miss=payload.cache_miss,
            avg_lookup_time_ms=payload.avg_lookup_time_ms,
            team_alias=payload.team_alias or "default"
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": "Cache metrics tracked",
                "cache_hit_rate": (payload.cache_hit / (payload.cache_hit + payload.cache_miss)) * 100
            }
        )
    
    except Exception as e:
        logger.error(f"Error tracking cache metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/metrics/batch")
async def track_batch_metrics(payload: BatchMetricsPayload, db: Session = Depends(get_db)):
    """Track batch processing metrics"""
    try:
        tracker = MetricsTracker(db)
        batch_metric = tracker.track_batch(
            batch_id=payload.batch_id,
            batch_size=payload.batch_size,
            total_tokens=payload.total_tokens,
            batch_cost=payload.batch_cost,
            batch_latency_ms=payload.batch_latency_ms,
            status=payload.status,
            team_alias=payload.team_alias or "default"
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": "Batch metrics tracked",
                "batch_id": payload.batch_id,
                "cost_per_query": payload.batch_cost / payload.batch_size
            }
        )
    
    except Exception as e:
        logger.error(f"Error tracking batch metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dashboard/metrics")
async def get_dashboard_metrics(
    time_range_hours: int = Query(24, ge=1, le=730),
    team_alias: Optional[str] = None,
    model_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregated metrics for dashboard
    
    Query parameters:
    - time_range_hours: Number of hours to look back (default: 24)
    - team_alias: Filter by team (optional)
    - model_filter: Filter by model (optional)
    """
    try:
        aggregator = MetricsAggregator(db)
        metrics = aggregator.get_dashboard_metrics(
            time_range_hours=time_range_hours,
            team_alias=team_alias,
            model_filter=model_filter
        )
        
        return JSONResponse(
            status_code=200,
            content=metrics
        )
    
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/requests/recent")
async def get_recent_requests(
    limit: int = Query(50, ge=1, le=500),
    team_alias: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get recent requests
    
    Query parameters:
    - limit: Number of requests to return (default: 50)
    - team_alias: Filter by team (optional)
    """
    try:
        aggregator = MetricsAggregator(db)
        requests = aggregator.get_recent_requests(
            limit=limit,
            team_alias=team_alias
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "count": len(requests),
                "requests": requests
            }
        )
    
    except Exception as e:
        logger.error(f"Error fetching recent requests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health/detailed")
async def health_detailed(db: Session = Depends(get_db)):
    """Get detailed system health information"""
    try:
        # Test database connection
        from database import MetricsEntry
        db.query(MetricsEntry).limit(1).all()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected",
                "version": "1.0.0"
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# ============================================
# STARTUP EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("LLM Optimization Hub - Metrics Backend Starting")
    logger.info("API Documentation available at /docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
