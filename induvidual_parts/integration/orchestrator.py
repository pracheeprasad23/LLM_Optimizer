"""
Unified LLM Optimization Pipeline Orchestrator

Coordinates all optimization modules while keeping them independent.
"""

import sys
import time
import logging
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
import importlib.util

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)


class OptimizationOrchestrator:
    """
    Main orchestrator that coordinates all optimization modules.
    Each module remains independent and can be modified separately.
    """
    
    def __init__(
        self,
        enable_batching: bool = False,
        enable_cache: bool = True,
        enable_metrics: bool = False,
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize orchestrator with feature flags.
        
        Args:
            enable_batching: Enable batch processing (default: False)
            enable_cache: Enable dynamic caching (default: True)
            enable_metrics: Enable metrics tracking (default: False)
            gemini_api_key: API key for Gemini models (required for execution)
        """
        self.enable_batching = enable_batching
        self.enable_cache = enable_cache
        self.enable_metrics = enable_metrics
        # Use provided key or load from .env file
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        
        # Store base path (project root, one level up from integration/)
        self.base_path = Path(__file__).parent.parent
        
        # Lazy import modules (only when needed)
        self._prompt_optimizer = None
        self._model_selector = None
        self._batcher = None
        self._cache_manager = None
        self._executor = None
        
        # Initialize cache if enabled
        if self.enable_cache:
            self._init_cache()
            
        # Initialize batcher if enabled
        if self.enable_batching:
            self._init_batcher()
    
    def _init_cache(self):
        """Initialize cache manager (lazy import)"""
        try:
            cache_path = self.base_path / "dynamic_cache"
            sys.path.insert(0, str(cache_path))
            try:
                from cache_manager import SemanticCacheManager
                self._cache_manager = SemanticCacheManager()
                logger.info("✓ Cache manager initialized")
            finally:
                if str(cache_path) in sys.path:
                    sys.path.remove(str(cache_path))
        except Exception as e:
            logger.warning(f"Cache initialization failed: {e}")
            self.enable_cache = False
    
    def _init_batcher(self):
        """Initialize batcher (lazy import)"""
        try:
            batcher_path = self.base_path / "batching-model wise 1"
            sys.path.insert(0, str(batcher_path))
            try:
                from batcher import ModelWiseBatcher
                self._batcher = ModelWiseBatcher()
                logger.info("✓ Batcher initialized")
            finally:
                if str(batcher_path) in sys.path:
                    sys.path.remove(str(batcher_path))
        except Exception as e:
            logger.warning(f"Batcher initialization failed: {e}")
            self.enable_batching = False
    
    def _import_optimizer_module(self):
        """Import optimize_prompt function by changing working directory"""
        original_cwd = os.getcwd()
        prompt_opt_dir = self.base_path / "Prompt_Optimizer"
        os.chdir(str(prompt_opt_dir))
        try:
            # Now we're in Prompt_Optimizer, so optimizer.optimizer works
            sys.path.insert(0, str(prompt_opt_dir))
            try:
                from optimizer.optimizer import optimize_prompt
                return optimize_prompt
            finally:
                if str(prompt_opt_dir) in sys.path:
                    sys.path.remove(str(prompt_opt_dir))
        finally:
            os.chdir(original_cwd)
    
    def _import_model_selection_module(self, module_name):
        """Import model selection modules by changing working directory and clearing config cache"""
        original_cwd = os.getcwd()
        model_sel_dir = self.base_path / "model_selection_and_logging"
        os.chdir(str(model_sel_dir))
        try:
            # Clear config from cache to avoid conflict with dynamic_cache/config.py
            if 'config' in sys.modules:
                del sys.modules['config']
            
            # Now we're in model_selection_and_logging, so config.py is found correctly
            sys.path.insert(0, str(model_sel_dir))
            try:
                module = __import__(module_name)
                return module
            finally:
                if str(model_sel_dir) in sys.path:
                    sys.path.remove(str(model_sel_dir))
        finally:
            os.chdir(original_cwd)
    
    async def process_query(
        self,
        user_prompt: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete optimization pipeline.
        
        Args:
            user_prompt: Raw user input prompt
            user_id: Optional user identifier
            request_id: Optional request identifier
            
        Returns:
            Dictionary with response and all optimization metadata
        """
        stages_timing = {}
        start_time = time.time()
        
        # ============================================================
        # STAGE 1: Prompt Optimization
        # ============================================================
        logger.info("\n" + "="*60)
        logger.info("[STAGE 1] Prompt Optimization")
        logger.info("="*60)
        
        stage_start = time.time()
        try:
            optimize_prompt = self._import_optimizer_module()
            optimization_result = optimize_prompt(user_prompt)
            
            shortened_query = optimization_result["shortened_query"]
            analysis_json = {
                "intent_type": optimization_result.get("intent_type"),
                "complexity_level": optimization_result.get("complexity_level"),
                "expected_output_length": optimization_result.get("expected_output_length"),
                "latency_tolerance": optimization_result.get("latency_tolerance"),
                "compliance_needed": optimization_result.get("compliance_needed", False)
            }
            token_count = optimization_result.get("token_count", 0)
            
            logger.info(f"✓ Input length: {len(user_prompt)} chars")
            logger.info(f"✓ Optimized length: {len(shortened_query)} chars")
            logger.info(f"✓ Intent: {analysis_json['intent_type']}, Complexity: {analysis_json['complexity_level']}")
            logger.info(f"✓ Tokens: {token_count}")
            
            stages_timing["prompt_optimization_ms"] = (time.time() - stage_start) * 1000
            
        except Exception as e:
            logger.error(f"✗ Prompt optimization failed: {e}")
            # Fallback to original prompt
            shortened_query = user_prompt
            analysis_json = {"intent_type": "general", "complexity_level": "medium"}
            token_count = len(user_prompt.split()) * 1.3  # Rough estimate
            stages_timing["prompt_optimization_ms"] = (time.time() - stage_start) * 1000
        
        # ============================================================
        # STAGE 2: Model Selection
        # ============================================================
        logger.info("\n" + "="*60)
        logger.info("[STAGE 2] Model Selection")
        logger.info("="*60)
        
        stage_start = time.time()
        try:
            selector_module = self._import_model_selection_module("selector")
            selected_model = selector_module.select_model(analysis_json)
            
            logger.info(f"✓ Selected model: {selected_model}")
            logger.info(f"✓ Selection rationale: Based on intent={analysis_json['intent_type']}, complexity={analysis_json['complexity_level']}")
            
            stages_timing["model_selection_ms"] = (time.time() - stage_start) * 1000
            
        except Exception as e:
            logger.error(f"✗ Model selection failed: {e}")
            selected_model = "models/gemini-2.5-flash"  # Fallback
            stages_timing["model_selection_ms"] = (time.time() - stage_start) * 1000
        
        # ============================================================
        # STAGE 3: Cache Lookup (if enabled)
        # ============================================================
        cache_hit = False
        cache_similarity = None
        cached_response = None
        
        if self.enable_cache and self._cache_manager:
            logger.info("\n" + "="*60)
            logger.info("[STAGE 3] Cache Lookup")
            logger.info("="*60)
            
            stage_start = time.time()
            try:
                cache_entry, similarity_score, threshold = await self._cache_manager.search(shortened_query)
                
                if cache_entry:
                    cache_hit = True
                    cached_response = cache_entry.response
                    cache_similarity = similarity_score
                    logger.info(f"✓ CACHE HIT - Similarity: {similarity_score:.4f}, Threshold: {threshold:.4f}")
                else:
                    logger.info(f"✓ CACHE MISS - Best similarity: {similarity_score:.4f}")
                
                stages_timing["cache_lookup_ms"] = (time.time() - stage_start) * 1000
                
            except Exception as e:
                logger.warning(f"Cache lookup failed: {e}")
                stages_timing["cache_lookup_ms"] = (time.time() - stage_start) * 1000
        
        # ============================================================
        # STAGE 4: LLM Execution (if not cached)
        # ============================================================
        llm_response = None
        execution_metrics = {}
        
        if not cache_hit:
            logger.info("\n" + "="*60)
            logger.info("[STAGE 4] LLM Execution")
            logger.info("="*60)
            
            stage_start = time.time()
            try:
                if self.gemini_api_key:
                    logger.info(f"Selected model: {selected_model}")
                    logger.info(f"API key available: {bool(self.gemini_api_key)}")
                    
                    executor_module = self._import_model_selection_module("executor")
                    
                    response_text, metrics = executor_module.execute_and_log(
                        model_name=selected_model,
                        prompt=shortened_query,
                        api_key=self.gemini_api_key,
                        analysis_json=analysis_json
                    )
                    
                    logger.info(f"Execution status: {metrics.get('status', 'unknown')}")
                    logger.info(f"Execution error: {metrics.get('error', 'none')}")
                    
                    if response_text:
                        llm_response = response_text
                        execution_metrics = {
                            "prompt_tokens": metrics.get("prompt_tokens", 0),
                            "output_tokens": metrics.get("output_tokens", 0),
                            "total_tokens": metrics.get("total_tokens", 0),
                            "cost_usd": metrics.get("actual_cost_usd", 0),
                            "latency_ms": metrics.get("latency_ms", 0),
                            "status": metrics.get("status", "success")
                        }
                        
                        logger.info(f"✓ Execution successful")
                        logger.info(f"✓ Tokens: {execution_metrics['prompt_tokens']} in, {execution_metrics['output_tokens']} out")
                        logger.info(f"✓ Cost: ${execution_metrics['cost_usd']:.6f}")
                        logger.info(f"✓ Latency: {execution_metrics['latency_ms']:.2f}ms")
                    else:
                        logger.warning(f"✗ Execution returned no response")
                        logger.warning(f"   Status: {metrics.get('status', 'unknown')}")
                        logger.warning(f"   Error: {metrics.get('error', 'No error message')}")
                        logger.warning(f"   Provider: {metrics.get('provider', 'unknown')}")
                        execution_metrics = {"status": metrics.get("status", "unsupported_provider"), "error": metrics.get("error")}
                else:
                    logger.warning("✗ No Gemini API key provided - skipping execution")
                    execution_metrics = {"status": "no_api_key", "error": "API key required for execution"}
                    
            except Exception as e:
                logger.error(f"✗ LLM execution failed: {e}")
                execution_metrics = {"status": "error", "error": str(e)}
            
            stages_timing["llm_execution_ms"] = (time.time() - stage_start) * 1000
        
        # Use cached response if available
        final_response = cached_response if cache_hit else llm_response
        
        # ============================================================
        # STAGE 5: Cache Storage (if miss and execution successful)
        # ============================================================
        cache_stored = False
        if self.enable_cache and self._cache_manager and not cache_hit and final_response:
            logger.info("\n" + "="*60)
            logger.info("[STAGE 5] Cache Storage")
            logger.info("="*60)
            
            try:
                stored = await self._cache_manager.add(
                    query=shortened_query,
                    response=final_response,
                    input_tokens=execution_metrics.get("prompt_tokens", token_count),
                    output_tokens=execution_metrics.get("output_tokens", 0),
                    cost=execution_metrics.get("cost_usd", 0),
                    best_similarity=cache_similarity
                )
                cache_stored = stored
                logger.info(f"✓ Cache storage: {'SUCCESS' if stored else 'SKIPPED (policy)'}")
            except Exception as e:
                logger.warning(f"Cache storage failed: {e}")
        
        # ============================================================
        # STAGE 6: Response Assembly
        # ============================================================
        total_time = (time.time() - start_time) * 1000
        
        result = {
            "response": final_response,
            "optimization": {
                "original_prompt_length": len(user_prompt),
                "optimized_prompt_length": len(shortened_query),
                "tokens_saved_in_prompt": max(0, token_count - execution_metrics.get("prompt_tokens", token_count)),
                "analysis": analysis_json
            },
            "model": {
                "selected": selected_model,
                "rationale": f"Selected based on intent={analysis_json['intent_type']}, complexity={analysis_json['complexity_level']}"
            },
            "cache": {
                "hit": cache_hit,
                "similarity_score": cache_similarity,
                "stored": cache_stored
            },
            "metrics": execution_metrics if execution_metrics else {
                "status": "cached" if cache_hit else "no_execution",
                "prompt_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0,
                "latency_ms": 0
            },
            "stages": {
                **stages_timing,
                "total_ms": total_time
            },
            "request_id": request_id,
            "user_id": user_id
        }
        
        logger.info("\n" + "="*60)
        logger.info("[RESULT] Pipeline Complete")
        logger.info("="*60)
        logger.info(f"✓ Total latency: {total_time:.2f}ms")
        logger.info(f"✓ Cache: {'HIT' if cache_hit else 'MISS'}")
        logger.info(f"✓ Response length: {len(final_response) if final_response else 0} chars")
        
        return result


# Convenience function for easy usage
async def process_query(
    user_prompt: str,
    gemini_api_key: Optional[str] = None,
    enable_cache: bool = True,
    enable_batching: bool = False,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to process a query through the optimization pipeline.
    
    Args:
        user_prompt: Raw user input
        gemini_api_key: API key for Gemini models
        enable_cache: Enable caching (default: True)
        enable_batching: Enable batching (default: False)
        user_id: Optional user identifier
        
    Returns:
        Dictionary with response and optimization metadata
    """
    orchestrator = OptimizationOrchestrator(
        enable_cache=enable_cache,
        enable_batching=enable_batching,
        gemini_api_key=gemini_api_key
    )
    
    return await orchestrator.process_query(user_prompt, user_id=user_id)
