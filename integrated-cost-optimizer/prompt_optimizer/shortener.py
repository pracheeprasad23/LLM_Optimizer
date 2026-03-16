"""
LLM-based Prompt Shortener
Uses Gemini API to intelligently shorten prompts while preserving meaning
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

# Only import Gemini if not in simulation mode
if not config.SIMULATE_LLM:
    try:
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
    except ImportError:
        pass


def shorten_prompt(text: str) -> str:
    """
    Shorten the prompt using Gemini while keeping meaning intact.
    Falls back to returning original text if API is unavailable or simulation mode.
    """
    # Simulation mode - just return the cleaned text
    if config.SIMULATE_LLM:
        # Simple simulation: remove common verbose patterns
        shortened = text
        verbose_patterns = [
            ("in order to", "to"),
            ("due to the fact that", "because"),
            ("at this point in time", "now"),
            ("in the event that", "if"),
            ("for the purpose of", "for"),
        ]
        for pattern, replacement in verbose_patterns:
            shortened = shortened.replace(pattern, replacement)
        return shortened
    
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
        print(f"LLM shortening error: {e}")
        return text  # fallback to original
