# gemini_logger.py

import time
import google.generativeai as genai

def run_gemini_and_log(api_key, model_name, prompt):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name)

    start = time.time()
    response = model.generate_content(prompt)
    end = time.time()

    usage = response.usage_metadata

    metrics = {
        "model": model_name,
        "prompt_tokens": usage.prompt_token_count,
        "output_tokens": usage.candidates_token_count,
        "total_tokens": usage.total_token_count,
        "latency_ms": round((end - start) * 1000, 3),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    return response.text, metrics
