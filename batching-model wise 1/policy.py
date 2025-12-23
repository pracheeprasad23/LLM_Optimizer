from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from model_catalog import get_model_info


@dataclass(frozen=True)
class BatchingPolicy:
    """Batching thresholds.

    Any of these can close a batch:
    - max_wait_ms: max time since the batch's first request
    - max_batch_size: max number of requests
    - max_batch_tokens: max token budget (sum of effective tokens)
    """

    max_wait_ms: int
    max_batch_size: int
    max_batch_tokens: int


@dataclass(frozen=True)
class AdaptiveBatchingConfig:
    """Interactive (chat-like) defaults + adaptive behavior."""

    # Baseline (medium latency tolerance)
    base_wait_ms: int = 80

    # Clamp for adaptive wait
    min_wait_ms: int = 40
    max_wait_ms: int = 120

    # Default caps
    default_max_batch_size: int = 8
    default_max_batch_tokens: int = 3000


def output_length_factor(expected_output_length: Optional[str]) -> float:
    """Approximate output cost/latency using a multiplier.

    We only have input token_count from Prompt_Optimizer.
    This helps avoid overloading a batch with prompts likely to produce long outputs.
    """

    if expected_output_length == "short":
        return 0.2
    if expected_output_length == "long":
        return 1.2
    return 0.6  # medium / unknown


def effective_tokens(token_count: int, analysis_json: Dict[str, Any]) -> int:
    expected = analysis_json.get("expected_output_length")
    factor = output_length_factor(expected)
    # effective = input + reserved output-ish budget
    eff = int(round(token_count * (1.0 + factor)))
    return max(1, eff)


def adaptive_wait_ms(latency_tolerance: Optional[str], cfg: AdaptiveBatchingConfig) -> int:
    """Adaptive waiting: low tolerance => shorter wait, high => longer wait."""

    if latency_tolerance == "low":
        wait = 50
    elif latency_tolerance == "high":
        wait = 120
    else:
        wait = cfg.base_wait_ms

    return max(cfg.min_wait_ms, min(cfg.max_wait_ms, wait))


def policy_for_model(
    model_name: str,
    analysis_json: Dict[str, Any],
    cfg: Optional[AdaptiveBatchingConfig] = None,
) -> BatchingPolicy:
    """Return batching thresholds for a request.

    Uses:
    - adaptive wait based on request latency_tolerance
    - per-model tuning based on catalog latency/cost tiers (if available)

    Note: This is a conservative interactive policy.
    """

    cfg = cfg or AdaptiveBatchingConfig()

    # Start with defaults
    wait_ms = adaptive_wait_ms(analysis_json.get("latency_tolerance"), cfg)
    max_size = cfg.default_max_batch_size
    max_tokens = cfg.default_max_batch_tokens

    info = get_model_info(model_name)

    # If the model catalog knows the model, tune caps.
    if info:
        latency_tier = info.get("latency_tier")
        cost_tier = info.get("cost_tier")

        # Fast models: allow larger batches, but keep wait small.
        if latency_tier == "low":
            max_size = max(max_size, 12)
            max_tokens = max(max_tokens, 4500)
            wait_ms = min(wait_ms, 80)

        # Slower models: keep batches smaller to reduce tail latency.
        if latency_tier == "medium":
            max_size = min(max_size, 8)
            max_tokens = min(max_tokens, 5000)

        # Very cheap models: can batch more aggressively (size/tokens), but still interactive.
        if cost_tier in {"very-low", "low"}:
            max_tokens = max(max_tokens, 5000)

        # Expensive models: keep batches tighter.
        if cost_tier in {"high"}:
            max_size = min(max_size, 6)
            max_tokens = min(max_tokens, 3500)

    return BatchingPolicy(max_wait_ms=wait_ms, max_batch_size=max_size, max_batch_tokens=max_tokens)
