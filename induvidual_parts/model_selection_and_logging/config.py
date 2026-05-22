# config.py
# Model metadata from Vellum AI LLM Leaderboard (updated Nov 2025)

MODEL_METADATA = {
    # Fast & Cost-Effective Models
    "models/gemini-2.5-flash": {
        "context_window": 1000000,
        "input_cost_per_1m": 0.15,
        "output_cost_per_1m": 0.6,
        "speed_tokens_per_sec": 200,
        "latency_ttft_sec": 0.35,
        "benchmark_scores": {
            "coding": 0,  # Not in top 5
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "gpt-4o-mini": {
        "context_window": 128000,
        "input_cost_per_1m": 0.15,
        "output_cost_per_1m": 0.6,
        "speed_tokens_per_sec": 65,
        "latency_ttft_sec": 0.35,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "models/gemini-2.0-flash": {
        "context_window": 1000000,
        "input_cost_per_1m": 0.1,
        "output_cost_per_1m": 0.4,
        "speed_tokens_per_sec": 257,
        "latency_ttft_sec": 0.34,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    # High-Performance Coding Models
    "claude-sonnet-4.5": {
        "context_window": 200000,
        "input_cost_per_1m": 3.0,
        "output_cost_per_1m": 15.0,
        "speed_tokens_per_sec": 69,
        "latency_ttft_sec": 31.0,
        "benchmark_scores": {
            "coding": 82.0,  # Best in SWE Bench
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 89.1
        }
    },
    
    "claude-opus-4.5": {
        "context_window": 200000,
        "input_cost_per_1m": 5.0,
        "output_cost_per_1m": 25.0,
        "speed_tokens_per_sec": 0,  # Not available
        "latency_ttft_sec": 0,
        "benchmark_scores": {
            "coding": 80.9,  # 2nd in SWE Bench
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 378.0,  # Best in ARC-AGI 2
            "multilingual": 90.8
        }
    },
    
    "gpt-5.2": {
        "context_window": 400000,
        "input_cost_per_1m": 1.5,
        "output_cost_per_1m": 14.0,
        "speed_tokens_per_sec": 92,
        "latency_ttft_sec": 0.6,
        "benchmark_scores": {
            "coding": 80.0,  # 3rd in SWE Bench
            "reasoning": 92.4,  # Best in GPQA Diamond
            "overall": 0,
            "math": 100.0,  # Best in AIME 2025
            "visual": 53.0,
            "multilingual": 0
        }
    },
    
    # High-Performance Reasoning Models
    "models/gemini-3-pro": {
        "context_window": 10000000,
        "input_cost_per_1m": 2.0,
        "output_cost_per_1m": 12.0,
        "speed_tokens_per_sec": 128,
        "latency_ttft_sec": 30.3,
        "benchmark_scores": {
            "coding": 76.2,
            "reasoning": 91.9,  # 2nd in GPQA Diamond
            "overall": 45.8,  # Best in Humanity's Last Exam
            "math": 100.0,  # Best in AIME 2025
            "visual": 31.0,
            "multilingual": 91.8  # Best in MMMLU
        }
    },
    
    "models/gemini-2.5-pro": {
        "context_window": 1000000,
        "input_cost_per_1m": 1.25,
        "output_cost_per_1m": 10.0,
        "speed_tokens_per_sec": 191,
        "latency_ttft_sec": 30.0,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 21.6,
            "math": 0,
            "visual": 0,
            "multilingual": 89.2
        }
    },
    
    "gpt-5.1": {
        "context_window": 200000,
        "input_cost_per_1m": 1.25,
        "output_cost_per_1m": 10.0,
        "speed_tokens_per_sec": 0,
        "latency_ttft_sec": 0,
        "benchmark_scores": {
            "coding": 76.3,
            "reasoning": 88.1,
            "overall": 0,
            "math": 0,
            "visual": 18.0,
            "multilingual": 0
        }
    },
    
    # Balanced Models
    "gpt-4o": {
        "context_window": 128000,
        "input_cost_per_1m": 2.5,
        "output_cost_per_1m": 10.0,
        "speed_tokens_per_sec": 143,
        "latency_ttft_sec": 0.51,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "claude-3.5-sonnet": {
        "context_window": 200000,
        "input_cost_per_1m": 3.0,
        "output_cost_per_1m": 15.0,
        "speed_tokens_per_sec": 78,
        "latency_ttft_sec": 1.22,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "claude-3.5-haiku": {
        "context_window": 200000,
        "input_cost_per_1m": 0.8,
        "output_cost_per_1m": 4.0,
        "speed_tokens_per_sec": 66,
        "latency_ttft_sec": 0.88,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    # Ultra-Cheap Models (Cost-First Scenarios)
    "nova-micro": {
        "context_window": 0,  # Not specified
        "input_cost_per_1m": 0.04,
        "output_cost_per_1m": 0.14,
        "speed_tokens_per_sec": 0,  # Not available
        "latency_ttft_sec": 0.3,  # Lowest latency
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "gemma-3-27b": {
        "context_window": 128000,
        "input_cost_per_1m": 0.07,
        "output_cost_per_1m": 0.07,
        "speed_tokens_per_sec": 59,
        "latency_ttft_sec": 0.72,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "gpt-oss-20b": {
        "context_window": 131072,
        "input_cost_per_1m": 0.08,
        "output_cost_per_1m": 0.35,
        "speed_tokens_per_sec": 564,
        "latency_ttft_sec": 4.0,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 98.7,  # 4th in AIME 2025
            "visual": 0,
            "multilingual": 0
        }
    },
    
    # Ultra-Fast Models (Low Latency Critical)
    "llama-4-scout": {
        "context_window": 10000000,
        "input_cost_per_1m": 0.11,
        "output_cost_per_1m": 0.34,
        "speed_tokens_per_sec": 2600,  # Fastest
        "latency_ttft_sec": 0.33,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "llama-3.3-70b": {
        "context_window": 128000,
        "input_cost_per_1m": 0.59,
        "output_cost_per_1m": 0.7,
        "speed_tokens_per_sec": 2500,  # 2nd fastest
        "latency_ttft_sec": 0.52,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "llama-3.1-405b": {
        "context_window": 128000,
        "input_cost_per_1m": 3.5,
        "output_cost_per_1m": 3.5,
        "speed_tokens_per_sec": 969,
        "latency_ttft_sec": 0.73,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    # High-Performance Reasoning Models
    "kimi-k2-thinking": {
        "context_window": 256000,
        "input_cost_per_1m": 0.6,
        "output_cost_per_1m": 2.5,
        "speed_tokens_per_sec": 79,
        "latency_ttft_sec": 25.3,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 44.9,  # 2nd best overall
            "math": 99.1,  # 3rd in AIME 2025
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "grok-4": {
        "context_window": 256000,
        "input_cost_per_1m": 0,  # Not available
        "output_cost_per_1m": 0,
        "speed_tokens_per_sec": 52,
        "latency_ttft_sec": 13.3,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 87.5,  # 4th in GPQA Diamond
            "overall": 25.4,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "gpt-5": {
        "context_window": 400000,
        "input_cost_per_1m": 1.25,
        "output_cost_per_1m": 10.0,
        "speed_tokens_per_sec": 0,
        "latency_ttft_sec": 0,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 87.3,  # 5th in GPQA Diamond
            "overall": 35.2,
            "math": 0,
            "visual": 18.0,
            "multilingual": 0
        }
    },
    
    # Additional Claude Variants
    "claude-opus-4.1": {
        "context_window": 200000,
        "input_cost_per_1m": 15.0,
        "output_cost_per_1m": 75.0,
        "speed_tokens_per_sec": 0,
        "latency_ttft_sec": 0,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 89.5  # 3rd in MMMLU
        }
    },
    
    "claude-3.7-sonnet": {
        "context_window": 200000,
        "input_cost_per_1m": 3.0,
        "output_cost_per_1m": 15.0,
        "speed_tokens_per_sec": 78,
        "latency_ttft_sec": 0.91,  # Faster than 4.5
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    # Balanced Premium Models
    "nova-pro": {
        "context_window": 300000,
        "input_cost_per_1m": 1.0,
        "output_cost_per_1m": 4.0,
        "speed_tokens_per_sec": 128,
        "latency_ttft_sec": 0.64,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 0,
            "visual": 0,
            "multilingual": 0
        }
    },
    
    "openai-o3": {
        "context_window": 200000,
        "input_cost_per_1m": 10.0,
        "output_cost_per_1m": 40.0,
        "speed_tokens_per_sec": 94,
        "latency_ttft_sec": 28.0,
        "benchmark_scores": {
            "coding": 0,
            "reasoning": 0,
            "overall": 0,
            "math": 98.4,  # 5th in AIME 2025
            "visual": 0,
            "multilingual": 0
        }
    }
}

# List of available models
MODEL_LIST = list(MODEL_METADATA.keys())
