# batching-model wise 1 (Batching Simulation)

This folder implements **model-wise batching** for an LLM middleware pipeline.

Scope (as requested):
- Builds batches from incoming requests (cache-miss) **without calling any LLM**.
- Uses upstream metadata (`analysis_json`) and token counts (`token_count`) coming from `Prompt_Optimizer`.
- Keeps `LLM_Optimizer/LLM_Optimizer` unchanged.

## What batching does
- Groups requests by `selected_model` (one open batch per model)
- Closes a batch when any threshold is hit:
  - `max_wait_ms` (time window)
  - `max_batch_size` (count)
  - `max_batch_tokens` (token budget)

For interactive systems, this implementation uses **latency-first defaults** plus an **adaptive rule** based on `analysis_json["latency_tolerance"]`.

## Files
- `model_catalog.py` — expanded `MODEL_CATALOG` (no dependency on LLM_Optimizer config)
- `policy.py` — batching policy + adaptive wait rule
- `batcher.py` — online model-wise batcher
- `simulate.py` — offline driver that simulates arrivals and prints batches

## Run the simulation
From the repository root (folder that contains `LLM_Optimizer/`):

```bash
python "LLM_Optimizer/batching-model wise 1/simulate.py"
```

You can also pass a custom input file:

```bash
python "LLM_Optimizer/batching-model wise 1/simulate.py" --input "path/to/prompts_batch.json"
```

Examples (this repo):

```bash
python "LLM_Optimizer/batching-model wise 1/simulate.py" --input "LLM_Optimizer/batching-model wise 1/prompts_batch.json"
python "LLM_Optimizer/batching-model wise 1/simulate.py" --input "LLM_Optimizer/batching-model wise 1/prompts_batch_coding_100.json"
```

You should see:
- generated example prompts + their selected models
- created batches with model name, size, token totals, close reasons, and wait times

The default input file is `prompts_batch.json` in this folder.

### Input JSON formats supported

1) List of strings:

```json
["prompt one", "prompt two"]
```

2) List of objects (recommended for batching demos):

```json
[
  {"request_id":"r1","created_at_ms":0,"prompt":"Summarize this email..."},
  {"request_id":"r2","created_at_ms":35,"prompt":"Write Python code..."}
]
```

In production, the middleware ingress layer generates `request_id` and `created_at_ms` when a user prompt arrives.

## Input shape expected by the batcher
Each request should include:
- `request_id: str`
- `created_at_ms: int`
- `shortened_query: str`
- `analysis_json: dict` (must contain the keys used in your pipeline)
- `token_count: int` (from Prompt_Optimizer)
- `selected_model: str` (from your model-selection stage)
