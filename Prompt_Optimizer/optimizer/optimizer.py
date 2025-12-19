from .llm_shortener import shorten_prompt_with_llm
from .structural_cleaner import clean_prompt
from .complexity_analyzer import analyze_complexity
from .token_counter import count_tokens

from .llm_shortener import shorten_prompt_with_llm
from .structural_cleaner import clean_prompt
from .complexity_analyzer import analyze_complexity
from .token_counter import count_tokens

def optimize_prompt(user_prompt: str):
    cleaned = clean_prompt(user_prompt)
    shortened = shorten_prompt_with_llm(cleaned)

    complexity_info = analyze_complexity(shortened)
    token_count = count_tokens(shortened)

    return {
        "shortened_query": shortened,
        **complexity_info,
        "token_count": token_count
    }