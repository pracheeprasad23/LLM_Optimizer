from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from model_catalog import MODEL_CATALOG


_COST_RANK = {
    "very-low": 0,
    "low": 1,
    "medium": 2,
    "medium-high": 3,
    "high": 4,
}

_LATENCY_RANK = {
    "low": 0,
    "medium": 1,
    "high": 2,
}


@dataclass(frozen=True)
class SelectionConfig:
    """Cost-first (threshold-based) selection configuration.

    The key idea:
    - pick the cheapest/fastest model that meets a minimum capability threshold
    - only escalate to expensive models when needed (complexity/compliance)

    This produces more realistic multi-model routing than purely scoring by strength.
    """

    # Strength thresholds (per intent) by complexity.
    # Values match the MODEL_CATALOG strength scale (~2.0 to 5.0).
    low_min_strength: float = 2.2
    medium_min_strength: float = 2.8
    high_min_strength: float = 4.0

    # Additional required strength when compliance is needed.
    compliance_bonus: float = 0.6

    # When multiple candidates tie (cost/latency), pick among top N for diversity.
    diversity_top_n: int = 5


def _normalize_intent(intent_type: Optional[str]) -> str:
    if not intent_type:
        return "general"
    if intent_type in {"coding", "reasoning", "summarization"}:
        return intent_type
    if intent_type in {"data_analysis"}:
        return "reasoning"
    return "general"


def _strength(model: Dict[str, Any], intent: str) -> float:
    s = model.get("strength") or {}
    return float(s.get(intent, s.get("general", 0.0)))


def _rank_cost(model: Dict[str, Any]) -> int:
    return _COST_RANK.get(str(model.get("cost_tier", "medium")), 2)


def _rank_latency(model: Dict[str, Any]) -> int:
    return _LATENCY_RANK.get(str(model.get("latency_tier", "medium")), 1)


def _required_strength(complexity_level: Optional[str], cfg: SelectionConfig) -> float:
    if complexity_level == "high":
        return cfg.high_min_strength
    if complexity_level == "medium":
        return cfg.medium_min_strength
    return cfg.low_min_strength


def _provider_preference_boost(model: Dict[str, Any], intent: str, complexity_level: Optional[str]) -> float:
    """Small tie-breakers to avoid always picking one provider.

    Keeps the core rule (cheapest that meets threshold) intact.
    Only used as a final tie-break.
    """

    name = str(model.get("name", ""))
    provider = str(model.get("provider", ""))

    boost = 0.0
    if intent == "reasoning" and provider == "deepseek" and "reasoner" in name:
        boost += 0.2
    # DeepSeek chat is very cost-effective for many coding tasks.
    if intent == "coding" and provider == "deepseek" and "chat" in name and complexity_level in {"low", "medium"}:
        boost += 0.15
    if intent == "summarization" and provider == "anthropic" and "haiku" in name:
        boost += 0.15
    if intent == "coding" and provider == "google" and "flash" in name and complexity_level != "high":
        boost += 0.1
    # Grok mini is a reasonable low-latency option; use as a mild tie-break.
    if provider == "xai" and "mini" in name and complexity_level in {"low", "medium"}:
        boost += 0.08
    return boost


def select_model_from_catalog(
    analysis_json: Dict[str, Any],
    *,
    cfg: Optional[SelectionConfig] = None,
    catalog: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Select a model using the expanded MODEL_CATALOG.

    Rule (professional + cost-first):
    1) determine required capability threshold from request metadata
    2) keep only models meeting the threshold
    3) among candidates, choose lowest cost tier; break ties by latency tier
    4) if still tied, pick among top N for provider diversity (deterministic)

    Returns (model_name, debug_info).
    """

    cfg = cfg or SelectionConfig()
    cat = MODEL_CATALOG if catalog is None else catalog

    intent = _normalize_intent(analysis_json.get("intent_type"))
    complexity = analysis_json.get("complexity_level")
    latency_tol = analysis_json.get("latency_tolerance")
    compliance_needed = bool(analysis_json.get("compliance_needed"))

    required = _required_strength(complexity, cfg)
    if compliance_needed:
        required += cfg.compliance_bonus

    # If user needs low latency, tighten the threshold slightly to avoid weak models producing retries.
    if latency_tol == "low" and complexity in {"medium", "high"}:
        required += 0.2

    candidates: List[Dict[str, Any]] = []
    for m in cat:
        if _strength(m, intent) >= required:
            candidates.append(m)

    # If nothing meets threshold, fall back to the strongest models (rare).
    if not candidates:
        candidates = sorted(cat, key=lambda m: _strength(m, intent), reverse=True)[:5]

    # Sort by (cost, latency, -strength) then apply a small provider tie-break.
    ranked: List[Tuple[Tuple[float, float, float, float], Dict[str, Any]]] = []
    for m in candidates:
        cost = float(_rank_cost(m))
        lat = float(_rank_latency(m))
        strength = _strength(m, intent)
        boost = _provider_preference_boost(m, intent, complexity)
        # Lower tuple is better.
        ranked.append(((cost, lat, -strength, -boost), m))

    ranked.sort(key=lambda x: x[0])

    # Diversity: pick among top N candidates.
    # This is intentionally not restricted to equal (cost,latency) because many catalogs
    # have a single cheapest option which would otherwise dominate.
    top_n = max(1, int(cfg.diversity_top_n))
    top = [m for _, m in ranked[:top_n]]

    # Deterministic choice based on request features.
    key = f"{intent}|{complexity}|{latency_tol}|{int(compliance_needed)}"
    idx = sum(ord(c) for c in key) % len(top)
    chosen = top[idx]

    debug = {
        "intent": intent,
        "complexity_level": complexity,
        "latency_tolerance": latency_tol,
        "compliance_needed": compliance_needed,
        "required_strength": round(required, 2),
        "candidates": len(candidates),
        "top_5": [
            {
                "name": m["name"],
                "cost_tier": m.get("cost_tier"),
                "latency_tier": m.get("latency_tier"),
                "strength": _strength(m, intent),
            }
            for _, m in ranked[:5]
        ],
        "chosen": {
            "name": chosen["name"],
            "cost_tier": chosen.get("cost_tier"),
            "latency_tier": chosen.get("latency_tier"),
            "strength": _strength(chosen, intent),
        },
    }

    return chosen["name"], debug
