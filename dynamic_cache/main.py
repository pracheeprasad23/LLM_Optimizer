"""
FastAPI application for Adaptive Semantic Cache System
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
import random
from typing import Dict, Any

from models import QueryRequest, QueryResponse, CacheMetrics, CacheStats
from cache_manager import SemanticCacheManager
from llm_service import LLMService
from optimizer import CacheOptimizer
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
cache_manager = None
llm_service = None
optimizer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global cache_manager, llm_service, optimizer
    
    logger.info("Starting Adaptive Semantic Cache System...")
    
    # Initialize services
    cache_manager = SemanticCacheManager()
    llm_service = LLMService()
    optimizer = CacheOptimizer(cache_manager)
    
    logger.info("System initialized successfully")
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title="Adaptive Semantic Cache System",
    description="Dynamic, Cost-Aware LLM Caching with Semantic Similarity",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "system": "Adaptive Semantic Cache System",
        "version": "1.0.0"
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Main query endpoint with semantic caching
    
    Args:
        request: Query request
        
    Returns:
        Query response with caching information
    """
    start_time = time.time()
    
    logger.info(f"Received query: '{request.query[:100]}...'")
    
    # Update metrics
    cache_manager.metrics.total_requests += 1
    
    # Search cache for similar query
    cache_entry, similarity_score, threshold_used = await cache_manager.search(request.query)
    
    if cache_entry is not None:
        # CACHE HIT
        cache_manager.metrics.cache_hits += 1
        
        # Calculate tokens and cost that would have been used
        estimated_tokens = cache_entry.input_tokens + cache_entry.output_tokens
        estimated_cost = cache_entry.cost
        
        # Update cache entry
        cache_manager.update_hit(
            entry=cache_entry,
            similarity=similarity_score,
            tokens_saved=estimated_tokens,
            cost_saved=estimated_cost
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"CACHE HIT - similarity: {similarity_score:.4f}, "
            f"tokens saved: {estimated_tokens}, cost saved: ${estimated_cost:.6f}"
        )
        
        response = QueryResponse(
            response=cache_entry.response,
            cached=True,
            similarity_score=similarity_score,
            tokens_used=0,
            tokens_saved=estimated_tokens,
            cost=0.0,
            cost_saved=estimated_cost,
            latency_ms=latency_ms,
            threshold_used=threshold_used
        )
    else:
        # CACHE MISS - Call LLM
        cache_manager.metrics.cache_misses += 1
        
        logger.info("CACHE MISS - calling LLM")
        
        # Generate response using LLM
        ##Main LLM Call##
        # llm_response, input_tokens, output_tokens, cost = await llm_service.generate_response(
        #     query=request.query,
        #     max_tokens=request.max_tokens,
        #     temperature=request.temperature
        # )
        
        ##Test LLM Call with Realistic Random Simulation##
        # Generate realistic varied responses
        query_len = len(request.query)
        input_tokens = random.randint(8, 20)  # Realistic input token range
        output_tokens = random.randint(15, 150)  # Varied output lengths
        
        # Realistic Gemini costs: $0.075/1M input, $0.30/1M output
        cost = (input_tokens * 0.075 + output_tokens * 0.30) / 1_000_000
        
        # Generate varied responses to make embeddings different
        response_templates = [
            f"The answer to your question is: {random.randint(1, 1000)}. This is a simulated response.",
            f"Based on the query, here's what I found: Information {random.randint(1, 1000)}. Hope this helps!",
            f"Let me explain: {random.randint(1, 1000)} is the key point here. Does that answer your question?",
            f"Interesting question! The response is {random.randint(1, 1000)}. Let me know if you need more details.",
            f"Here's a detailed answer: Point {random.randint(1, 1000)} covers your question comprehensively."
        ]
        llm_response = random.choice(response_templates)
        
        total_tokens = input_tokens + output_tokens
        
        # Update metrics
        cache_manager.metrics.llm_tokens_used += total_tokens
        cache_manager.metrics.total_cost += cost
        
        # Try to add to cache
        cached = await cache_manager.add(
            query=request.query,
            response=llm_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            best_similarity=similarity_score if similarity_score > 0 else None
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"LLM response - tokens: {total_tokens}, cost: ${cost:.6f}, "
            f"cached: {cached}, latency: {latency_ms:.2f}ms"
        )
        
        response = QueryResponse(
            response=llm_response,
            cached=False,
            similarity_score=None,
            tokens_used=total_tokens,
            tokens_saved=0,
            cost=cost,
            cost_saved=0.0,
            latency_ms=latency_ms,
            threshold_used=threshold_used
        )
    
    # Check if optimization should run
    if optimizer.should_optimize():
        optimization_result = optimizer.optimize()
        logger.info(f"Optimization triggered: {optimization_result}")
    
    return response


@app.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get global cache metrics
    
    Returns:
        Cache metrics dictionary
    """
    return {
        "metrics": cache_manager.metrics.to_dict(),
        "optimizer": optimizer.get_optimization_summary(),
        "config": config.to_dict()
    }


@app.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get detailed cache statistics
    
    Returns:
        Cache statistics
    """
    stats = cache_manager.get_stats()
    return {
        "stats": stats,
        "metrics": cache_manager.metrics.to_dict()
    }


@app.post("/cache/clear")
async def clear_cache() -> Dict[str, str]:
    """
    Clear all cache entries (admin endpoint)
    
    Returns:
        Success message
    """
    cache_manager.clear()
    return {"status": "success", "message": "Cache cleared"}


@app.get("/cache/entries")
async def get_cache_entries() -> Dict[str, Any]:
    """
    Get all cache entries (for debugging)
    
    Returns:
        List of cache entries
    """
    entries = [
        {
            "query": entry.query[:100],
            "response": entry.response[:100],
            "hits": entry.hits,
            "avg_similarity": round(entry.avg_similarity, 4),
            "tokens_saved": entry.llm_tokens_saved,
            "created_at": entry.created_at.isoformat(),
        }
        for entry in cache_manager.cache_entries[:20]  # Limit to first 20
    ]
    
    return {
        "total_entries": len(cache_manager.cache_entries),
        "showing": len(entries),
        "entries": entries
    }


@app.get("/optimizer/history")
async def get_optimizer_history() -> Dict[str, Any]:
    """
    Get optimization history
    
    Returns:
        Optimization history and details
    """
    return {
        "optimization_count": optimizer.optimization_count,
        "last_optimization": optimizer.last_optimization_time,
        "requests_since_last": cache_manager.metrics.total_requests % config.OPTIMIZATION_INTERVAL,
        "next_optimization_at": ((cache_manager.metrics.total_requests // config.OPTIMIZATION_INTERVAL) + 1) * config.OPTIMIZATION_INTERVAL
    }


@app.get("/evictions/history")
async def get_eviction_history(limit: int = 100) -> Dict[str, Any]:
    """
    Get eviction history
    
    Args:
        limit: Maximum number of evictions to return
        
    Returns:
        Eviction history
    """
    history = cache_manager.get_eviction_history(limit)
    return {
        "total_evictions": cache_manager.metrics.evictions,
        "history_count": len(history),
        "evictions": history
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
