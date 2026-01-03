# executor.py
# Provider-agnostic model execution and metrics collection
# Currently supports Gemini, structured for easy extension to other providers

import time
import json
from typing import Dict, Tuple, Optional
from config import MODEL_METADATA

def _is_gemini_model(model_name: str) -> bool:
    """Check if model is a Gemini model."""
    model_lower = model_name.lower()
    return "gemini" in model_lower or (model_name.startswith("models/") and "gemini" in model_lower)


def _calculate_cost(model_name: str, prompt_tokens: int, output_tokens: int) -> Optional[float]:
    """Calculate actual cost based on model pricing and token usage."""
    if model_name not in MODEL_METADATA:
        return None
    
    metadata = MODEL_METADATA[model_name]
    input_cost = metadata.get("input_cost_per_1m", 0)
    output_cost = metadata.get("output_cost_per_1m", 0)
    
    if input_cost == 0 and output_cost == 0:
        return None
    
    # Calculate cost: (tokens / 1,000,000) * cost_per_1m
    input_cost_total = (prompt_tokens / 1_000_000) * input_cost
    output_cost_total = (output_tokens / 1_000_000) * output_cost
    
    return round(input_cost_total + output_cost_total, 6)


def _calculate_throughput(total_tokens: int, latency_sec: float) -> Optional[float]:
    """Calculate tokens per second throughput."""
    if latency_sec <= 0:
        return None
    return round(total_tokens / latency_sec, 2)


def execute_and_log(
    model_name: str,
    prompt: str,
    api_key: str,
    analysis_json: Optional[Dict] = None
) -> Tuple[Optional[str], Dict]:
    """
    Execute query with selected model and return comprehensive metrics.
    
    Args:
        model_name: Selected model identifier
        prompt: Query prompt to execute
        api_key: API key for the provider
        analysis_json: Original query metadata (for context)
    
    Returns:
        Tuple of (response_text, metrics_dict)
        - response_text: Model response (None if error or non-Gemini)
        - metrics_dict: Comprehensive metrics in JSON-ready format
    """
    metrics = {
        "model": model_name,
        "provider": _get_provider(model_name),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "query_metadata": analysis_json or {},
        "status": "success",
        "error": None
    }
    
    # Handle non-Gemini models (return model name only, no metrics)
    if not _is_gemini_model(model_name):
        metrics["status"] = "unsupported_provider"
        metrics["error"] = f"Provider not yet implemented. Model '{model_name}' selected but only Gemini is currently supported."
        return None, metrics
    
    # Execute Gemini model
    try:
        from gemini_executor import execute_gemini
        
        response_text, execution_metrics = execute_gemini(
            api_key=api_key,
            model_name=model_name,
            prompt=prompt
        )
        
        # Merge execution metrics
        metrics.update(execution_metrics)
        
        # Calculate additional metrics
        prompt_tokens = execution_metrics.get("prompt_tokens", 0)
        output_tokens = execution_metrics.get("output_tokens", 0)
        total_tokens = execution_metrics.get("total_tokens", 0)
        latency_sec = execution_metrics.get("latency_sec", 0)
        
        # Cost calculation
        actual_cost = _calculate_cost(model_name, prompt_tokens, output_tokens)
        if actual_cost is not None:
            metrics["actual_cost_usd"] = actual_cost
        
        # Throughput calculation
        throughput = _calculate_throughput(total_tokens, latency_sec)
        if throughput is not None:
            metrics["throughput_tokens_per_sec"] = throughput
        
        # Response metadata
        if response_text:
            metrics["response_length_chars"] = len(response_text)
            metrics["response_length_words"] = len(response_text.split())
        
        return response_text, metrics
        
    except Exception as e:
        # Error handling
        metrics["status"] = "error"
        metrics["error"] = str(e)
        metrics["error_type"] = type(e).__name__
        return None, metrics


def _get_provider(model_name: str) -> str:
    """Determine provider from model name."""
    if _is_gemini_model(model_name):
        return "google"
    elif "gpt" in model_name.lower() or "openai" in model_name.lower():
        return "openai"
    elif "claude" in model_name.lower():
        return "anthropic"
    elif "llama" in model_name.lower() or "gemma" in model_name.lower():
        return "meta"
    elif "grok" in model_name.lower():
        return "xai"
    elif "kimi" in model_name.lower():
        return "moonshot"
    elif "nova" in model_name.lower():
        return "cohere"
    else:
        return "unknown"

