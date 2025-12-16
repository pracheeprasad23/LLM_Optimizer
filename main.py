# main.py

from selector import select_model
from gemini_logger import run_gemini_and_log

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
# GEMINI EXECUTION + METRICS
# ------------------------------------------------------------------

response, metrics = run_gemini_and_log(
    api_key=GEMINI_API_KEY,
    model_name=selected_model,
    prompt=shortened_query
)

# ------------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------------

print("\n=== RESPONSE ===\n")
print(response)

print("\n=== METRICS ===\n")
print(metrics)
