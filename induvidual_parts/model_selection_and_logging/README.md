# LLM_Optimizer in short
Selects the most suitable Large Language Model per query, based on metadata derived during prompt optimization, while capturing real execution metrics.

# LLM Optimizer – Cost & Resource Optimization for LLMs

## Overview
LLM Optimizer is a lightweight, modular framework designed to optimize cost and resource usage for Large Language Model (LLM) applications.  
It intelligently selects the most suitable model per query using metadata generated during prompt optimization and optionally logs real execution metrics using Gemini APIs.

The system focuses on per-query optimization and supports both single-query and batch-processing pipelines.

---

## System Architecture

```

User Query
↓
Prompt Optimization (external system)
→ shortened_query
→ analysis_json
↓
Batch / Single Query Decision (external system)
↓
Model Selection (this module)
↓
(Optional) Gemini Execution + Metrics Logging

````

---

## Key Features

- Smart, scoring-based model selection  
- Works for both batch and single-query flows  
- Uses real Gemini API usage metrics (tokens, latency)  
- No cost estimation or assumptions  
- Logging is optional and decoupled  
- Designed for cost-first LLM systems  

---

## Inputs

### From Prompt Optimization Module
```json
{
  "shortened_query": "Explain binary search in Python",
  "analysis_json": {
    "intent_type": "coding",
    "complexity_level": "medium",
    "expected_output_length": "medium",
    "latency_tolerance": "low",
    "compliance_needed": false
  }
}
````

### Input Description

* shortened_query: Final, optimized prompt sent to the LLM
* analysis_json: Metadata used only for model selection and routing

---

## Outputs

* Selected model name
* (Optional) Model response
* (Optional) Execution metrics:

  * Prompt tokens
  * Output tokens
  * Total tokens
  * Latency (ms)
  * Timestamp

---

## File Structure

```
llm_optimizer/
│
├── config.py          # Supported Gemini models
├── selector.py        # Model selection logic
├── gemini_logger.py   # Optional Gemini execution + logging
├── main.py            # Entry point
└── requirements.txt
```

---

## Model Selection Logic

Model selection is performed using a scoring-based algorithm.
Each available model is scored based on:

* Query complexity
* Intent type (coding, reasoning, summarization, etc.)
* Latency tolerance
* Compliance or safety requirements

The model with the highest score is selected.
This process is purely algorithmic and does not call any LLM.

---

## Supported Models

The system uses only Gemini models verified via `list_models()` for the provided API key, such as:

* models/gemini-2.5-flash
* models/gemini-2.5-pro

These models support the `generateContent` method.

---

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Add Gemini API key in `main.py`:

```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

3. Run:

```bash
python main.py
```

---

## Design Principles

* Separation of concerns between prompt optimization, model selection, and execution
* Cost-first design to minimize per-query spend
* Extensible architecture for future models and providers

---

## Use Cases

* Cost-aware AI assistants
* Multi-agent LLM systems
* High-throughput batch LLM processing
* LLM routing and optimization research

---

## Future Enhancements

* Batch execution with grouped Gemini calls
* Cost dashboards and analytics
* Reinforcement learning–based model routing
* Multi-provider LLM support

---

## Summary

LLM Optimizer provides a clean, production-ready foundation for building efficient, cost-aware LLM systems, ensuring every query is handled by the right model at the right cost.
