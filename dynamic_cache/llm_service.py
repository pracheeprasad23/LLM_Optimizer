"""
LLM service for generating responses
"""
import google.generativeai as genai
from typing import Tuple, Dict, Any
from config import config


class LLMService:
    """Handles LLM calls and token counting"""
    
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.LLM_MODEL)
    
    async def generate_response(
        self,
        query: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Tuple[str, int, int, float]:
        """
        Generate response using LLM
        
        Args:
            query: User query
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Tuple of (response_text, input_tokens, output_tokens, cost)
        """
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        
        response = self.model.generate_content(
            query,
            generation_config=generation_config
        )
        
        response_text = response.text
        
        # Get token counts from usage metadata
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        
        # Calculate cost
        cost = config.calculate_cost(input_tokens, output_tokens)
        
        return response_text, input_tokens, output_tokens, cost
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation)
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
