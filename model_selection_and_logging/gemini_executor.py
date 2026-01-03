# gemini_executor.py
# Gemini-specific execution logic

import time
import google.generativeai as genai
from typing import Tuple, Dict


def execute_gemini(api_key: str, model_name: str, prompt: str) -> Tuple[str, Dict]:
    """
    Execute query using Gemini API and capture execution metrics.
    
    Args:
        api_key: Gemini API key
        model_name: Gemini model identifier (e.g., "models/gemini-2.5-flash")
        prompt: Query prompt
    
    Returns:
        Tuple of (response_text, metrics_dict)
    
    Raises:
        Exception: If API call fails
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # Capture timing metrics
    start_time = time.time()
    
    try:
        # Generate content
        response = model.generate_content(prompt)
        
        # Calculate latency
        end_time = time.time()
        total_latency_sec = end_time - start_time
        
        # Extract usage metadata
        usage = response.usage_metadata if hasattr(response, 'usage_metadata') else None
        
        # Get response text
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        # Build metrics
        metrics = {
            "prompt_tokens": usage.prompt_token_count if usage else 0,
            "output_tokens": usage.candidates_token_count if usage else 0,
            "total_tokens": usage.total_token_count if usage else 0,
            "latency_sec": round(total_latency_sec, 3),
            "latency_ms": round(total_latency_sec * 1000, 3),
            "time_to_first_token_sec": None,  # Gemini API doesn't provide this directly
            "finish_reason": None,  # Can be extracted from response if available
        }
        
        # Try to extract finish reason from response
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                metrics["finish_reason"] = candidate.finish_reason
        
        return response_text, metrics
        
    except Exception as e:
        # Re-raise with context
        raise Exception(f"Gemini API error: {str(e)}") from e

