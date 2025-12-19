import google.generativeai as genai
import os
from .intent_classifier import classify_intent

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_complexity(prompt: str) -> dict:
    """
    Hybrid analyzer:
    - Uses rule-based classifier first (fast)
    - Falls back to Gemini if intent_type == 'other'
    """
    base_result = classify_intent(prompt)

    # If intent confidently classified, skip Gemini call
    if base_result["intent_type"] != "other":
        return base_result

    # Otherwise, use Gemini for deeper analysis
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash-lite-preview-09-2025")
        query = f"""
        Analyze the following user prompt and classify it into JSON:
        {{
          "intent_type": ["reasoning","summarization","coding","data_analysis","creative_writing","factual_answering","conversation","classification","other"],
          "complexity_level": ["low","medium","high"],
          "expected_output_length": ["short","medium","long"],
          "latency_tolerance": ["high","medium","low"],
          "compliance_needed": boolean
        }}

        Prompt: {prompt}
        """
        response = model.generate_content(query)
        import json, re
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            gemini_json = json.loads(match.group(0))
            return gemini_json
    except Exception as e:
        print("⚠️ Gemini error:", e)

    # Fallback to rule-based output
    return base_result