# main.py

import json
from selector import select_model
from executor import execute_and_log

# 🔑 PUT YOUR API KEY HERE
GEMINI_API_KEY = "###"

# ------------------------------------------------------------------
# RECEIVED FROM PROMPT OPTIMIZATION TEAM
# ------------------------------------------------------------------

shortened_query = "Explain binary search in Python with an example."

analysis_json = {
    "intent_type": "coding",
    "complexity_level": "medium",
    "expected_output_length": "medium",
    "latency_tolerance": "low",
    "compliance_needed": False
}

# ------------------------------------------------------------------
# MODEL SELECTION (after batch/single decision)
# ------------------------------------------------------------------

selected_model = select_model(analysis_json)
print("Selected model:", selected_model)

# ------------------------------------------------------------------
# MODEL EXECUTION + METRICS COLLECTION
# ------------------------------------------------------------------

response, metrics = execute_and_log(
    model_name=selected_model,
    prompt=shortened_query,
    api_key=GEMINI_API_KEY,
    analysis_json=analysis_json
)

# ------------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------------

print("\n=== RESPONSE ===\n")
if response:
    print(response)
else:
    print("No response (error or unsupported provider)")

print("\n=== METRICS (JSON-ready) ===\n")
print(json.dumps(metrics, indent=2))

# For dashboard team - this is the JSON to send
metrics_json = json.dumps(metrics)
print(f"\n=== JSON String (for dashboard) ===\n{metrics_json}")
