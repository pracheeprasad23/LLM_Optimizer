"""
Cost Optimizer Pipeline Orchestrator
Coordinates the entire flow: Prompt Optimization → Cache → Batching → LLM
"""
import time
import logging
from typing import Dict, Any, Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from models import QueryRequest, QueryResponse, PromptAnalysis, QueryTrackingInfo
from prompt_optimizer import clean_prompt, shorten_prompt, analyze_complexity, count_tokens
from cache import SemanticCacheManager
from batching import ModelWiseBatcher, select_model
from batching.batcher import BatchRequest
from llm import LLMService
from pipeline.tracker import QueryTracker

logger = logging.getLogger(__name__)


class CostOptimizerPipeline:
    """Main pipeline orchestrating all cost optimization stages"""
    
    def __init__(self):
        self.cache_manager = SemanticCacheManager()
        self.batcher = ModelWiseBatcher()
        self.llm_service = LLMService()
        self.query_tracker = QueryTracker()
        
        logger.info("Cost Optimizer Pipeline initialized")
    
    async def process_query(
        self,
        request: QueryRequest
    ) -> QueryResponse:
        """Process a query through the entire pipeline"""
        
        start_time = time.time()
        
        # Create tracking info
        tracking = self.query_tracker.create_tracking(request.query)
        
        try:
            # =================================================================
            # STAGE 1: Prompt Optimization
            # =================================================================
            opt_start = time.time()
            
            # Clean the prompt
            cleaned_prompt = clean_prompt(request.query)
            
            # Shorten the prompt (may use LLM)
            shortened_prompt = shorten_prompt(cleaned_prompt)
            
            # Analyze complexity
            analysis_dict = analyze_complexity(shortened_prompt)
            analysis = PromptAnalysis(**analysis_dict)
            
            # Count tokens
            original_tokens = count_tokens(request.query)
            optimized_tokens = count_tokens(shortened_prompt)
            
            # Update tracking
            tracking.optimized_prompt = shortened_prompt
            tracking.prompt_analysis = analysis
            tracking.original_tokens = original_tokens
            tracking.optimized_tokens = optimized_tokens
            tracking.optimization_time_ms = (time.time() - opt_start) * 1000
            
            logger.info(f"Prompt optimized: {original_tokens} → {optimized_tokens} tokens")
            
            # =================================================================
            # STAGE 2: Semantic Cache Lookup
            # =================================================================
            cache_start = time.time()
            
            self.cache_manager.metrics.total_requests += 1
            cache_entry, similarity_score, threshold_used = await self.cache_manager.search(shortened_prompt)
            
            tracking.cache_lookup_time_ms = (time.time() - cache_start) * 1000
            tracking.cache_threshold_used = threshold_used
            tracking.cache_similarity_score = similarity_score if similarity_score > 0 else None
            
            if cache_entry is not None:
                # CACHE HIT
                tracking.cache_hit = True
                self.cache_manager.metrics.cache_hits += 1
                
                # Calculate savings
                estimated_tokens = cache_entry.input_tokens + cache_entry.output_tokens
                estimated_cost = cache_entry.cost
                
                # Update cache entry
                self.cache_manager.update_hit(
                    entry=cache_entry,
                    similarity=similarity_score,
                    tokens_saved=estimated_tokens,
                    cost_saved=estimated_cost
                )
                
                # Update tracking
                tracking.llm_response = cache_entry.response
                tracking.cost_saved = estimated_cost
                tracking.tokens_saved = estimated_tokens
                tracking.total_time_ms = (time.time() - start_time) * 1000
                tracking.status = "completed"
                
                # Record tracking
                self.query_tracker.record_completed(tracking)
                
                logger.info(f"CACHE HIT - similarity: {similarity_score:.4f}")
                
                return QueryResponse(
                    response=cache_entry.response,
                    cached=True,
                    similarity_score=similarity_score,
                    tokens_used=0,
                    tokens_saved=estimated_tokens,
                    cost=0.0,
                    cost_saved=estimated_cost,
                    latency_ms=(time.time() - start_time) * 1000,
                    threshold_used=threshold_used,
                    tracking_id=tracking.query_id
                )
            
            # CACHE MISS
            tracking.cache_hit = False
            self.cache_manager.metrics.cache_misses += 1
            
            logger.info(f"CACHE MISS - similarity: {similarity_score:.4f}")
            
            # =================================================================
            # STAGE 3: Model Selection
            # =================================================================
            selected_model, selection_debug = select_model(analysis_dict)
            tracking.selected_model = selected_model
            tracking.model_selection_reason = str(selection_debug.get("chosen", {}))
            
            logger.info(f"Selected model: {selected_model}")
            
            # =================================================================
            # STAGE 4: Batching (for tracking purposes)
            # =================================================================
            now_ms = int(time.time() * 1000)
            batch_request = BatchRequest(
                request_id=tracking.query_id,
                created_at_ms=now_ms,
                optimized_prompt=shortened_prompt,
                analysis_json=analysis_dict,
                token_count=optimized_tokens,
                selected_model=selected_model,
                user_id=request.user_id
            )
            
            closed_batches = self.batcher.add(batch_request, now_ms=now_ms)
            
            # For simplicity in this demo, we process immediately
            # In production, batches would be held and processed together
            if closed_batches:
                tracking.batch_id = closed_batches[-1].batch_id
                tracking.batch_size = closed_batches[-1].size
            
            # =================================================================
            # STAGE 5: LLM Response Generation
            # =================================================================
            llm_start = time.time()
            
            llm_response, input_tokens, output_tokens, cost = await self.llm_service.generate_response(
                query=shortened_prompt,
                model_name=selected_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            tracking.llm_response = llm_response
            tracking.llm_input_tokens = input_tokens
            tracking.llm_output_tokens = output_tokens
            tracking.llm_cost = cost
            tracking.llm_response_time_ms = (time.time() - llm_start) * 1000
            
            # Update cache metrics
            total_tokens = input_tokens + output_tokens
            self.cache_manager.metrics.llm_tokens_used += total_tokens
            self.cache_manager.metrics.total_cost += cost
            
            logger.info(f"LLM response: {total_tokens} tokens, ${cost:.6f}")
            
            # =================================================================
            # STAGE 6: Cache the Response
            # =================================================================
            cached = await self.cache_manager.add(
                query=shortened_prompt,
                response=llm_response,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                best_similarity=similarity_score if similarity_score > 0 else None
            )
            
            logger.info(f"Cached: {cached}")
            
            # Finalize tracking
            tracking.total_time_ms = (time.time() - start_time) * 1000
            tracking.status = "completed"
            
            # Record tracking
            self.query_tracker.record_completed(tracking)
            
            return QueryResponse(
                response=llm_response,
                cached=False,
                similarity_score=similarity_score if similarity_score > 0 else None,
                tokens_used=total_tokens,
                tokens_saved=0,
                cost=cost,
                cost_saved=0.0,
                latency_ms=(time.time() - start_time) * 1000,
                threshold_used=threshold_used,
                selected_model=selected_model,
                batch_id=tracking.batch_id,
                tracking_id=tracking.query_id
            )
            
        except Exception as e:
            tracking.status = "error"
            tracking.error_message = str(e)
            tracking.total_time_ms = (time.time() - start_time) * 1000
            self.query_tracker.record_completed(tracking)
            
            logger.error(f"Pipeline error: {e}")
            raise
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        return {
            "cache": self.cache_manager.metrics.to_dict(),
            "cache_stats": self.cache_manager.get_stats(),
            "batching": self.batcher.get_stats(),
            "tracking": self.query_tracker.get_aggregated_metrics(),
            "config": config.to_dict(),
        }
    
    def get_recent_queries(self, limit: int = 20) -> list:
        """Get recent queries with tracking"""
        return self.query_tracker.get_recent_queries(limit)
    
    def clear_all(self):
        """Clear all caches and tracking"""
        self.cache_manager.clear()
        self.query_tracker.clear()
        logger.info("All data cleared")
