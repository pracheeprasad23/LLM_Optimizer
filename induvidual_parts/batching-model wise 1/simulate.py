from __future__ import annotations

import argparse
import json
import os
import random
from typing import Any, Dict, List

from batcher import ModelWiseBatcher, PromptRequest
from catalog_selector import select_model_from_catalog


def estimate_token_count(text: str) -> int:
    # Lightweight heuristic for simulation/demo only.
    return max(1, (len(text) // 4) + 8)


def estimate_analysis_json(prompt: str) -> Dict[str, Any]:
    """Heuristic metadata extractor (no LLM calls).

    Produces the same keys your pipeline expects:
    - intent_type
    - complexity_level
    - expected_output_length
    - latency_tolerance
    - compliance_needed
    """

    p = (prompt or "").strip()
    lowered = p.lower()

    # Intent
    if any(k in lowered for k in ["code", "python", "javascript", "bug", "function", "class", "api", "test", "refactor"]):
        intent = "coding"
    elif any(k in lowered for k in ["summarize", "summary", "tl;dr", "tldr", "bullet", "action items"]):
        intent = "summarization"
    elif any(k in lowered for k in ["explain", "why", "analyze", "reason", "prove", "derive", "intuition"]):
        intent = "reasoning"
    elif any(k in lowered for k in ["dataset", "csv", "plot", "chart", "visualize", "dashboard"]):
        intent = "data_analysis"
    else:
        intent = "general"

    # Complexity (word-count heuristic)
    wc = len(p.split())
    if wc < 15:
        complexity = "low"
    elif wc < 45:
        complexity = "medium"
    else:
        complexity = "high"

    # Expected output length
    if any(k in lowered for k in ["brief", "short", "tldr", "tl;dr"]):
        expected = "short"
    elif any(k in lowered for k in ["step-by-step", "detailed", "comprehensive", "in depth"]):
        expected = "long"
    else:
        expected = "medium"

    # Latency tolerance (interactive proxy)
    # If user wants brief output, they probably want lower latency.
    if expected == "short":
        latency_tol = "low"
    elif expected == "long":
        latency_tol = "high"
    else:
        latency_tol = "medium"

    # Compliance
    compliance = any(k in lowered for k in ["privacy", "pii", "gdpr", "confidential", "sensitive", "policy", "compliance"])

    return {
        "intent_type": intent,
        "complexity_level": complexity,
        "expected_output_length": expected,
        "latency_tolerance": latency_tol,
        "compliance_needed": compliance,
    }


def load_requests_from_json(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list")

    out: List[Dict[str, Any]] = []
    for i, item in enumerate(data, start=1):
        if isinstance(item, str):
            out.append({"request_id": f"r{i}", "created_at_ms": None, "prompt": item})
        elif isinstance(item, dict):
            prompt = item.get("prompt") or item.get("shortened_query")
            if not prompt:
                raise ValueError(f"Item {i} must include 'prompt' (or 'shortened_query')")
            out.append({
                "request_id": item.get("request_id") or f"r{i}",
                "created_at_ms": item.get("created_at_ms"),
                "prompt": prompt,
                "user_id": item.get("user_id"),
            })
        else:
            raise ValueError(f"Item {i} must be a string or an object")
    return out


def build_prompt_requests(raw: List[Dict[str, Any]]) -> List[PromptRequest]:
    # If created_at_ms is missing, generate synthetic arrivals.
    now = 0
    out: List[PromptRequest] = []

    for item in raw:
        created_at_ms = item.get("created_at_ms")
        if created_at_ms is None:
            created_at_ms = now
            now += random.randint(0, 60)
        else:
            # Keep now tracking for future synthetic items.
            now = max(now, int(created_at_ms))

        prompt = str(item["prompt"])
        analysis_json = estimate_analysis_json(prompt)
        token_count = estimate_token_count(prompt)

        selected_model, _debug = select_model_from_catalog(analysis_json)

        out.append(
            PromptRequest(
                request_id=str(item.get("request_id")),
                created_at_ms=int(created_at_ms),
                shortened_query=prompt,
                analysis_json=analysis_json,
                token_count=token_count,
                selected_model=selected_model,
                user_id=item.get("user_id"),
            )
        )

    out.sort(key=lambda r: r.created_at_ms)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Batching simulation (no LLM calls)")
    default_path = os.path.join(os.path.dirname(__file__), "prompts_batch.json")
    parser.add_argument(
        "--input",
        default=default_path,
        help="Path to JSON file (list of prompt strings or objects with request_id/created_at_ms/prompt)",
    )
    args = parser.parse_args()

    random.seed(7)  # stable synthetic timestamps if needed

    raw = load_requests_from_json(args.input)
    requests = build_prompt_requests(raw)
    batcher = ModelWiseBatcher()

    print("=== REQUESTS (loaded from JSON + selected models) ===")
    print("id   t(ms) user intent         complexity latency tok   model                       prompt")
    print("---- ----- ---- ------------   ---------- ------- ----- --------------------------  ------")
    for r in requests:
        intent = (r.analysis_json.get("intent_type") or "").ljust(12)
        complexity = (r.analysis_json.get("complexity_level") or "").ljust(10)
        latency = (r.analysis_json.get("latency_tolerance") or "").ljust(7)
        model = (r.selected_model[:26]).ljust(26)
        prompt_snip = (r.shortened_query.replace("\n", " ")[:60] + ("..." if len(r.shortened_query) > 60 else ""))
        print(f"{r.request_id.ljust(4)} {str(r.created_at_ms).rjust(5)} {str(r.user_id or '').ljust(4)} {intent} {complexity} {latency} {str(r.token_count).rjust(5)} {model}  {prompt_snip}")

    print("\n=== BATCHES ===")
    all_batches = []
    for r in requests:
        all_batches.extend(batcher.add(r, now_ms=r.created_at_ms))

    # Flush remaining at end
    end_ms = requests[-1].created_at_ms if requests else 0
    all_batches.extend(batcher.flush_all(now_ms=end_ms))

    def _batch_num(batch_id: str) -> int:
        try:
            return int(batch_id.split("-")[-1])
        except Exception:
            return 0

    all_batches.sort(key=lambda b: (b.created_at_ms, _batch_num(b.batch_id)))

    print("batch    model                       size tok_in tok_eff created closed wait reason ids")
    print("-------  --------------------------  ---- ------ ------- ------- ------ ---- ------ ---")
    for b in all_batches:
        ids = ",".join(req.request_id for req in b.requests)
        model = (b.model_name[:26]).ljust(26)
        created = str(b.created_at_ms).rjust(5)
        closed = str(b.closed_at_ms if b.closed_at_ms is not None else "").rjust(5)
        print(
            f"{b.batch_id.ljust(7)}  {model}  {str(b.size).rjust(4)} {str(b.total_input_tokens).rjust(6)} {str(b.total_effective_tokens).rjust(7)} {created} {closed} {str(b.max_wait_ms).rjust(4)} {str(b.close_reason).ljust(6)} {ids}"
        )


if __name__ == "__main__":
    main()
