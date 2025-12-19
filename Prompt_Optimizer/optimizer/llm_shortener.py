import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it before running.")
genai.configure(api_key=api_key)

def shorten_prompt_with_llm(text: str) -> str:
    """Shorten the prompt using Gemini while keeping meaning intact."""
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash-lite-preview-09-2025")
        prompt = f"""
        Shorten this prompt without changing meaning or context.
        Remove redundant words, politeness, and filler phrases.
        Keep the structure clear and concise.
        Original prompt: {text}
        Return only the shortened version.
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini error:", e)
        return text  # fallback to original prompt