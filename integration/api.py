"""
FastAPI API for Unified LLM Optimization Pipeline

Provides REST endpoints for the integrated optimization system.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from orchestrator import OptimizationOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Optimization Pipeline API",
    description="Unified API for prompt optimization, model selection, caching, and execution",
    version="1.0.0"
)

# Initialize orchestrator (lazy, can be reconfigured)
_orchestrator: Optional[OptimizationOrchestrator] = None


# Pydantic models
class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    prompt: str = Field(..., description="User prompt to process")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    request_id: Optional[str] = Field(None, description="Optional request identifier")
    enable_cache: Optional[bool] = Field(True, description="Enable caching")
    enable_batching: Optional[bool] = Field(False, description="Enable batching")


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    response: Optional[str]
    optimization: Dict[str, Any]
    model: Dict[str, Any]
    cache: Dict[str, Any]
    metrics: Dict[str, Any]
    stages: Dict[str, Any]
    request_id: Optional[str] = None
    user_id: Optional[str] = None


def get_orchestrator() -> OptimizationOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    
    if _orchestrator is None:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        _orchestrator = OptimizationOrchestrator(
            enable_cache=True,
            enable_batching=False,
            gemini_api_key=gemini_api_key
        )
        logger.info("Orchestrator initialized")
    
    return _orchestrator


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "LLM Optimization Pipeline",
        "version": "1.0.0",
        "modules": {
            "prompt_optimizer": "enabled",
            "model_selection": "enabled",
            "batching": "configurable",
            "cache": "enabled",
            "executor": "enabled (Gemini only)"
        }
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    try:
        orchestrator = get_orchestrator()
        return {
            "status": "healthy",
            "cache_enabled": orchestrator.enable_cache,
            "batching_enabled": orchestrator.enable_batching,
            "has_api_key": orchestrator.gemini_api_key is not None
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    Main endpoint to process a query through the optimization pipeline.
    
    Processes the query through:
    1. Prompt Optimization
    2. Model Selection
    3. Cache Lookup (if enabled)
    4. LLM Execution (if cache miss)
    5. Cache Storage (if miss and successful)
    
    Returns unified response with all optimization metadata.
    """
    try:
        # Get API key from env or use orchestrator's default
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Create orchestrator with request-specific settings
        orchestrator = OptimizationOrchestrator(
            enable_cache=request.enable_cache,
            enable_batching=request.enable_batching,
            gemini_api_key=gemini_api_key
        )
        
        # Process query
        result = await orchestrator.process_query(
            user_prompt=request.prompt,
            user_id=request.user_id,
            request_id=request.request_id
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics (if cache is enabled)"""
    try:
        orchestrator = get_orchestrator()
        if not orchestrator.enable_cache or not orchestrator._cache_manager:
            return {"error": "Cache is not enabled"}
        
        stats = orchestrator._cache_manager.get_stats()
        metrics = orchestrator._cache_manager.metrics.to_dict()
        
        return {
            "stats": stats,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cache/clear")
async def clear_cache():
    """Clear cache (if enabled)"""
    try:
        orchestrator = get_orchestrator()
        if not orchestrator.enable_cache or not orchestrator._cache_manager:
            return {"error": "Cache is not enabled"}
        
        orchestrator._cache_manager.clear()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

