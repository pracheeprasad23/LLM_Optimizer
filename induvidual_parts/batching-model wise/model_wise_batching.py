from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

MODEL_CATALOG: List[Dict] = [
    # OpenAI
    {
        "name": "gpt-3.5-turbo",
        "provider": "openai",
        "family": "chat",
        "cost_tier": "very-low",
        "latency_tier": "low",
        "context": 16_000,
        "strength": {"coding": 2, "reasoning": 2, "summarization": 3, "general": 3},
    },
    {
        "name": "gpt-4o-mini",
        "provider": "openai",
        "family": "chat",
        "cost_tier": "low",
        "latency_tier": "low",
        "context": 131_072,
        "strength": {"coding": 3, "reasoning": 3, "summarization": 3, "general": 3},
    },
    {
        "name": "gpt-4o",
        "provider": "openai",
        "family": "chat",
        "cost_tier": "medium",
        "latency_tier": "medium",
        "context": 131_072,
        "strength": {"coding": 4, "reasoning": 4, "summarization": 4, "general": 4},
    },
    {
        "name": "gpt-4.1",
        "provider": "openai",
        "family": "chat",
        "cost_tier": "medium-high",
        "latency_tier": "medium",
        "context": 200_000,
        "strength": {"coding": 5, "reasoning": 5, "summarization": 4, "general": 5},
    },
    # Anthropic
    {
        "name": "claude-3-haiku",
        "provider": "anthropic",
        "family": "chat",
        "cost_tier": "low",
        "latency_tier": "low",
        "context": 200_000,
        "strength": {"coding": 3, "reasoning": 2, "summarization": 3, "general": 3},
    },
    {
        "name": "claude-3.5-sonnet",
        "provider": "anthropic",
        "family": "chat",
        "cost_tier": "medium",
        "latency_tier": "medium",
        "context": 200_000,
        "strength": {"coding": 4, "reasoning": 4, "summarization": 4, "general": 4},
    },
    {
        "name": "claude-3-opus",
        "provider": "anthropic",
        "family": "chat",
        "cost_tier": "high",
        "latency_tier": "medium",
        "context": 200_000,
        "strength": {"coding": 5, "reasoning": 5, "summarization": 5, "general": 5},
    },
    # Google Gemini
    {
        "name": "models/gemini-1.5-flash",
        "provider": "google",
        "family": "chat",
        "cost_tier": "low",
        "latency_tier": "low",
        "context": 1_000_000,
        "strength": {"coding": 3, "reasoning": 3, "summarization": 3, "general": 3},
    },
    {
        "name": "models/gemini-1.5-pro",
        "provider": "google",
        "family": "chat",
        "cost_tier": "medium",
        "latency_tier": "medium",
        "context": 1_000_000,
        "strength": {"coding": 4, "reasoning": 4, "summarization": 4, "general": 4},
    },
    {
        "name": "models/gemini-2.5-flash",
        "provider": "google",
        "family": "chat",
        "cost_tier": "low",
        "latency_tier": "low",
        "context": 1_000_000,
        "strength": {"coding": 3, "reasoning": 3, "summarization": 3, "general": 3},
    },
    {
        "name": "models/gemini-2.5-pro",
        "provider": "google",
        "family": "chat",
        "cost_tier": "medium-high",
        "latency_tier": "medium",
        "context": 2_000_000,
        "strength": {"coding": 4, "reasoning": 5, "summarization": 4, "general": 4},
    },
    # DeepSeek
    {
        "name": "deepseek-chat",
        "provider": "deepseek",
        "family": "chat",
        "cost_tier": "very-low",
        "latency_tier": "low",
        "context": 32_000,
        "strength": {"coding": 2.5, "reasoning": 3.0, "summarization": 2.5, "general": 2.5},
    },
    {
        "name": "deepseek-reasoner",
        "provider": "deepseek",
        "family": "reasoning",
        "cost_tier": "medium",
        "latency_tier": "medium",
        "context": 64_000,
        "strength": {"coding": 3.5, "reasoning": 4.5, "summarization": 3.0, "general": 3.5},
    },
    # Grok
    {
        "name": "grok-2-mini",
        "provider": "xai",
        "family": "chat",
        "cost_tier": "low",
        "latency_tier": "low",
        "context": 128_000,
        "strength": {"coding": 3.0, "reasoning": 2.8, "summarization": 3.0, "general": 3.0},
    },
    {
        "name": "grok-2",
        "provider": "xai",
        "family": "chat",
        "cost_tier": "medium",
        "latency_tier": "medium",
        "context": 128_000,
        "strength": {"coding": 3.8, "reasoning": 3.8, "summarization": 3.6, "general": 3.7},
    },
]

COST_SCORES = {"very-low": 3.4, "low": 3, "medium": 2, "medium-high": 1, "high": 0}
LATENCY_SCORES = {"low": 3, "medium": 2, "high": 1}

WEIGHTS = {
    "cost": 1.4,
    "latency": 1.2,
    "intent_fit": 1.3,
    "complexity_fit": 1.1,
    "simplicity_bonus": 0.4,
    "compliance_bonus": 1.3,
    "compliance_penalty": -1.0,
}


def estimate_metadata(prompt: str) -> Dict:
    """Heuristic metadata extractor to keep the tool self-contained."""
    lowered = prompt.lower()

    intent = "general"
    if any(k in lowered for k in ["code", "python", "javascript", "bug", "function", "class", "api"]):
        intent = "coding"
    elif any(k in lowered for k in ["explain", "why", "analyze", "reason", "prove"]):
        intent = "reasoning"
    elif any(k in lowered for k in ["summarize", "summary", "tl;dr"]):
        intent = "summarization"

    length = len(prompt.split())
    if length < 20:
        complexity = "low"
    elif length < 80:
        complexity = "medium"
    else:
        complexity = "high"

    compliance_needed = any(k in lowered for k in ["policy", "safety", "compliance", "secure", "confidential"])

    return {
        "intent": intent,
        "complexity": complexity,
        "compliance_needed": compliance_needed,
    }


def _stable_jitter(name: str) -> float:
    return (sum(ord(c) for c in name) % 100) / 10000.0


def score_model(model: Dict, meta: Dict) -> float:
    """Score a model based on cost, latency, capability fit, and constraints."""
    cost_score = COST_SCORES.get(model["cost_tier"], 1)
    latency_score = LATENCY_SCORES.get(model["latency_tier"], 1)

    intent = meta["intent"]
    intent_strength = model["strength"].get(intent, model["strength"].get("general", 2))
    reasoning_strength = model["strength"].get("reasoning", model["strength"].get("general", 2))

    score = 0.0
    score += cost_score * WEIGHTS["cost"]
    score += latency_score * WEIGHTS["latency"]
    score += intent_strength * WEIGHTS["intent_fit"]

    if meta["complexity"] == "high":
        score += reasoning_strength * WEIGHTS["complexity_fit"]
    elif meta["complexity"] == "low":
        score += WEIGHTS["simplicity_bonus"]

    if meta["compliance_needed"]:
        if model["cost_tier"] in ["medium", "medium-high", "high"]:
            score += WEIGHTS["compliance_bonus"]
        else:
            score += WEIGHTS["compliance_penalty"]

    score += _stable_jitter(model["name"])
    return score


def select_model(prompt: str) -> Tuple[str, Dict]:
    meta = estimate_metadata(prompt)
    scored = []
    for m in MODEL_CATALOG:
        scored.append(
            {
                "name": m["name"],
                "score": score_model(m, meta),
                "cost": COST_SCORES.get(m["cost_tier"], 1),
                "latency": LATENCY_SCORES.get(m["latency_tier"], 1),
                "provider": m["provider"],
            }
        )
    scored.sort(key=lambda x: (-x["score"], -x["cost"], -x["latency"], x["name"]))
    best = scored[0]["name"]
    rationale = {
        "inferred_metadata": meta,
        "scores": scored,
    }
    return best, rationale


def load_prompts(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def batch_prompts(prompts: List[str]) -> Dict[str, List[Dict]]:
    """Run selection for each prompt and bucket them by chosen model."""
    batches: Dict[str, List[Dict]] = {}
    for prompt in prompts:
        model, rationale = select_model(prompt)
        top_score = rationale["scores"][0]["score"]
        batches.setdefault(model, []).append(
            {
                "prompt": prompt,
                "score": top_score,
                "intent": rationale["inferred_metadata"]["intent"],
                "complexity": rationale["inferred_metadata"]["complexity"],
                "compliance_needed": rationale["inferred_metadata"]["compliance_needed"],
            }
        )
    return batches


def main():
    data_path = Path(__file__).with_name("prompts_batch.json")
    prompts = load_prompts(data_path)
    batches = batch_prompts(prompts)

    print(f"Total prompts: {len(prompts)}")
    print(f"Models used: {len(batches)}")

    for model, items in batches.items():
        print(f"\n=== MODEL: {model} | prompts: {len(items)} ===")
        for item in items:
            print(f"- [{item['complexity']}] {item['prompt']}")


if __name__ == "__main__":
    main()
