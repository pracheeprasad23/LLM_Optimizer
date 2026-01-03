# selector.py
# Enhanced model selection using leaderboard benchmark data, costs, and speeds

import time
import math
from config import MODEL_METADATA, MODEL_LIST

def select_model(analysis_json):
    """
    Selects the best model based on query metadata and leaderboard performance.
    
    Scoring factors:
    - Benchmark performance (coding, reasoning, overall)
    - Cost efficiency (input + output costs)
    - Speed and latency
    - Complexity requirements
    - Intent type matching
    - Latency tolerance
    - Compliance needs
    """
    intent     = analysis_json["intent_type"]
    complexity = analysis_json["complexity_level"]
    latency    = analysis_json["latency_tolerance"]
    compliance = analysis_json["compliance_needed"]
    output_length = analysis_json.get("expected_output_length", "medium")
    
    scores = {}
    
    # Get max benchmark scores for normalization
    max_coding = max(m["benchmark_scores"]["coding"] for m in MODEL_METADATA.values())
    max_reasoning = max(m["benchmark_scores"]["reasoning"] for m in MODEL_METADATA.values())
    max_overall = max(m["benchmark_scores"]["overall"] for m in MODEL_METADATA.values())
    max_speed = max(m["speed_tokens_per_sec"] or 1 for m in MODEL_METADATA.values())
    min_latency = min(m["latency_ttft_sec"] or 10 for m in MODEL_METADATA.values() if m["latency_ttft_sec"])
    max_cost = max((m["input_cost_per_1m"] + m["output_cost_per_1m"]) for m in MODEL_METADATA.values())
    
    for model_name in MODEL_LIST:
        metadata = MODEL_METADATA[model_name]
        score = 0
        
        # 1. BENCHMARK PERFORMANCE (0-40 points)
        # Intent-based benchmark scoring
        if intent == "coding":
            if max_coding > 0:
                score += 40 * (metadata["benchmark_scores"]["coding"] / max_coding)
        elif intent in ["reasoning", "data_analysis", "math"]:
            if max_reasoning > 0:
                score += 30 * (metadata["benchmark_scores"]["reasoning"] / max_reasoning)
            if intent == "math" and metadata["benchmark_scores"]["math"] > 0:
                score += 10 * (metadata["benchmark_scores"]["math"] / 100)  # Normalize to 100
        else:
            # For general queries, use overall score
            if max_overall > 0:
                score += 30 * (metadata["benchmark_scores"]["overall"] / max_overall)
        
        # 2. COMPLEXITY HANDLING (0-15 points)
        if complexity == "low":
            # Prefer fast, cheap models for simple tasks
            if metadata["speed_tokens_per_sec"] and metadata["speed_tokens_per_sec"] > 100:
                score += 10
            if (metadata["input_cost_per_1m"] + metadata["output_cost_per_1m"]) < 1.0:
                score += 5
        elif complexity == "medium":
            # Balanced approach
            if metadata["benchmark_scores"]["coding"] > 50 or metadata["benchmark_scores"]["reasoning"] > 50:
                score += 10
            if metadata["speed_tokens_per_sec"] and metadata["speed_tokens_per_sec"] > 50:
                score += 5
        else:  # high complexity
            # Prefer high-performance models
            if metadata["benchmark_scores"]["coding"] > 70 or metadata["benchmark_scores"]["reasoning"] > 80:
                score += 15
            elif metadata["benchmark_scores"]["overall"] > 30:
                score += 10
        
        # 3. COST EFFICIENCY (0-20 points)
        # Lower cost = higher score (inverted)
        total_cost = metadata["input_cost_per_1m"] + metadata["output_cost_per_1m"]
        if max_cost > 0:
            cost_score = 20 * (1 - (total_cost / max_cost))
            score += cost_score
        
        # Adjust for output length
        if output_length == "long":
            # Weight output cost more heavily
            if metadata["output_cost_per_1m"] < 5.0:
                score += 5
        
        # 4. SPEED & LATENCY (0-15 points)
        if latency == "low":
            # High weight on speed and low latency
            if metadata["speed_tokens_per_sec"]:
                speed_score = 10 * (metadata["speed_tokens_per_sec"] / max_speed)
                score += speed_score
            
            if metadata["latency_ttft_sec"] and min_latency > 0:
                latency_score = 5 * (1 - (metadata["latency_ttft_sec"] / (min_latency * 10)))
                score += max(0, latency_score)
        elif latency == "medium":
            # Moderate weight on speed
            if metadata["speed_tokens_per_sec"]:
                speed_score = 5 * (metadata["speed_tokens_per_sec"] / max_speed)
                score += speed_score
        # else: high latency tolerance, no speed bonus
        
        # 5. COMPLIANCE & SAFETY (0-10 points)
        if compliance:
            # Prefer models with better overall performance (proxy for safety)
            if metadata["benchmark_scores"]["overall"] > 20:
                score += 10
            elif metadata["benchmark_scores"]["reasoning"] > 80:
                score += 8
            elif "pro" in model_name.lower() or "opus" in model_name.lower():
                score += 5
        else:
            # No compliance needed, can use cheaper/faster models
            if total_cost < 1.0:
                score += 5
        
        # 6. CONTEXT WINDOW (0-5 points)
        # Bonus for large context if needed (could be enhanced with query length analysis)
        if metadata["context_window"] >= 1000000:
            score += 3
        elif metadata["context_window"] >= 200000:
            score += 2
        
        # 7. LOAD BALANCING (small random factor)
        score += 0.1 * math.sin(time.time() + hash(model_name) % 100)
        
        scores[model_name] = score
    
    # Return model with highest score
    selected = max(scores, key=scores.get)
    
    # Debug: print top 3 models (optional, can be removed)
    sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    print(f"\nTop 3 models:")
    for model, score in sorted_models[:3]:
        print(f"  {model}: {score:.2f}")
    
    return selected
