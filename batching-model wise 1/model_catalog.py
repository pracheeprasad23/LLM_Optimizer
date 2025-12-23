from __future__ import annotations

from typing import Dict, List, Optional


# NOTE:
# - This catalog lives outside `LLM_Optimizer/LLM_Optimizer` by design.
# - It can be extended without changing the selection module.

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


def index_by_name(catalog: Optional[List[Dict]] = None) -> Dict[str, Dict]:
    cat = MODEL_CATALOG if catalog is None else catalog
    return {m["name"]: m for m in cat}


def get_model_info(model_name: str, catalog: Optional[List[Dict]] = None) -> Optional[Dict]:
    return index_by_name(catalog).get(model_name)
