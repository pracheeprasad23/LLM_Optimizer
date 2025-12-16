# selector.py

import time
import math
from config import MODEL_LIST

def select_model(analysis_json):
    intent     = analysis_json["intent_type"]
    complexity = analysis_json["complexity_level"]
    latency    = analysis_json["latency_tolerance"]
    compliance = analysis_json["compliance_needed"]

    scores = {model: 0 for model in MODEL_LIST}

    for model in MODEL_LIST:
        score = 0

        # Complexity handling
        if complexity == "low":
            score += 3 if "flash" in model else 1
        elif complexity == "medium":
            score += 3 if "flash" in model else 2
        else:  # high
            score += 4 if "pro" in model else 1

        # Intent handling
        if intent in ["coding", "reasoning", "data_analysis"]:
            if "pro" in model:
                score += 2

        # Latency preference
        if latency == "low":
            if "flash" in model:
                score += 2
            else:
                score -= 1

        # Compliance
        if compliance:
            if "pro" in model:
                score += 3
            else:
                score -= 2

        # Light load balancing
        score += 0.05 * math.sin(time.time())
        scores[model] = score

    return max(scores, key=scores.get)
