"""
Continuous optimization module for adaptive cache behavior
"""
import logging
from typing import Dict, Any
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)


class CacheOptimizer:
    """
    Continuously optimizes cache behavior based on observed metrics
    """
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.optimization_count = 0
        self.optimization_history = []
        self.last_optimization_time = None
    
    def should_optimize(self) -> bool:
        """
        Determine if optimization should run
        
        Returns:
            True if optimization should run
        """
        total_requests = self.cache_manager.metrics.total_requests
        return total_requests > 0 and total_requests % config.OPTIMIZATION_INTERVAL == 0
    
    def optimize(self) -> Dict[str, Any]:
        """
        Run optimization based on current metrics
        
        Returns:
            Dictionary describing optimization actions taken
        """
        self.optimization_count += 1
        self.last_optimization_time = datetime.now().isoformat()
        metrics = self.cache_manager.metrics
        
        logger.info(f"=== Running Optimization #{self.optimization_count} ===")
        
        actions = {
            "optimization_number": self.optimization_count,
            "current_hit_rate": metrics.hit_rate,
            "target_hit_rate": config.TARGET_HIT_RATE,
            "threshold_adjustments": {},
            "recommendations": [],
        }
        
        # Analyze hit rate and adjust thresholds
        hit_rate = metrics.hit_rate
        
        if hit_rate < config.TARGET_HIT_RATE - 0.05:
            # Hit rate too low - relax thresholds to increase hits
            self._relax_thresholds(actions)
        elif hit_rate > config.TARGET_HIT_RATE + 0.10:
            # Hit rate too high - tighten thresholds for better quality
            self._tighten_thresholds(actions)
        else:
            actions["recommendations"].append("Hit rate is within target range - no threshold adjustment needed")
        
        # Analyze cache efficiency
        self._analyze_cache_efficiency(actions)
        
        # Store optimization history
        self.optimization_history.append({
            "optimization_number": self.optimization_count,
            "hit_rate": hit_rate,
            "cache_size": metrics.cache_size,
            "total_requests": metrics.total_requests,
        })
        
        logger.info(f"Optimization complete: {actions}")
        return actions
    
    def _relax_thresholds(self, actions: Dict[str, Any]):
        """
        Relax similarity thresholds to increase cache hits
        
        Args:
            actions: Actions dictionary to update
        """
        thresholds = self.cache_manager.current_thresholds
        
        # Decrease thresholds (more lenient matching)
        for key in thresholds:
            old_value = thresholds[key]
            new_value = max(0.70, old_value - config.THRESHOLD_ADJUSTMENT_STEP)
            thresholds[key] = new_value
            
            actions["threshold_adjustments"][key] = {
                "old": round(old_value, 4),
                "new": round(new_value, 4),
                "change": "relaxed"
            }
        
        actions["recommendations"].append(
            "Thresholds relaxed to increase cache hit rate"
        )
        logger.info("Thresholds relaxed to increase hits")
    
    def _tighten_thresholds(self, actions: Dict[str, Any]):
        """
        Tighten similarity thresholds to improve match quality
        
        Args:
            actions: Actions dictionary to update
        """
        thresholds = self.cache_manager.current_thresholds
        
        # Increase thresholds (stricter matching)
        for key in thresholds:
            old_value = thresholds[key]
            new_value = min(0.98, old_value + config.THRESHOLD_ADJUSTMENT_STEP)
            thresholds[key] = new_value
            
            actions["threshold_adjustments"][key] = {
                "old": round(old_value, 4),
                "new": round(new_value, 4),
                "change": "tightened"
            }
        
        actions["recommendations"].append(
            "Thresholds tightened to improve match quality"
        )
        logger.info("Thresholds tightened to improve quality")
    
    def _analyze_cache_efficiency(self, actions: Dict[str, Any]):
        """
        Analyze cache efficiency and provide recommendations
        
        Args:
            actions: Actions dictionary to update
        """
        metrics = self.cache_manager.metrics
        
        # Check eviction rate
        if metrics.evictions > 0:
            eviction_rate = metrics.evictions / metrics.cache_size if metrics.cache_size > 0 else 0
            if eviction_rate > 0.5:
                actions["recommendations"].append(
                    f"High eviction rate ({eviction_rate:.2%}) - consider increasing MAX_CACHE_SIZE"
                )
        
        # Check cost savings
        if metrics.total_cost_saved > 0:
            cost_reduction = metrics.cost_reduction
            actions["recommendations"].append(
                f"Cost reduction: {cost_reduction:.2f}% (${metrics.total_cost_saved:.6f} saved)"
            )
        
        # Check average hits per entry
        if metrics.cache_size > 0:
            avg_hits = metrics.cache_hits / metrics.cache_size
            if avg_hits < 1.5:
                actions["recommendations"].append(
                    f"Low average hits per entry ({avg_hits:.2f}) - cache policy may be too lenient"
                )
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """
        Get summary of optimization history
        
        Returns:
            Summary dictionary
        """
        total_requests = self.cache_manager.metrics.total_requests
        requests_since_last = total_requests % config.OPTIMIZATION_INTERVAL
        
        return {
            "optimization_count": self.optimization_count,
            "last_optimization_time": self.last_optimization_time or "Never",
            "requests_since_last_optimization": requests_since_last,
            "next_optimization_at": total_requests + (config.OPTIMIZATION_INTERVAL - requests_since_last),
            "current_thresholds": self.cache_manager.current_thresholds,
            "recent_history": self.optimization_history[-5:] if self.optimization_history else [],
        }
