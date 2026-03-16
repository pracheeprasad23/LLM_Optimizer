"""
Unified LLM Service
Handles LLM calls with simulation mode support
"""
import random
from typing import Tuple
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config


class LLMService:
    """Handles LLM calls with simulation support"""
    
    def __init__(self):
        self._model = None
        
        if not config.SIMULATE_LLM:
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                self._genai = genai
                self._model = genai.GenerativeModel(config.LLM_MODEL)
            except ImportError:
                self._genai = None
        else:
            self._genai = None
    
    async def generate_response(
        self,
        query: str,
        model_name: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Tuple[str, int, int, float]:
        """
        Generate response using LLM.
        
        Returns: (response_text, input_tokens, output_tokens, cost)
        """
        if config.SIMULATE_LLM or self._model is None:
            return self._simulate_response(query, model_name, max_tokens)
        
        try:
            generation_config = self._genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            response = self._model.generate_content(
                query,
                generation_config=generation_config
            )
            
            response_text = response.text
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count
            cost = config.calculate_cost(input_tokens, output_tokens)
            
            return response_text, input_tokens, output_tokens, cost
            
        except Exception as e:
            print(f"LLM error: {e}")
            return self._simulate_response(query, model_name, max_tokens)
    
    def _simulate_response(
        self,
        query: str,
        model_name: str = None,
        max_tokens: int = 500
    ) -> Tuple[str, int, int, float]:
        """Generate simulated response for testing"""
        
        # Simulate realistic token counts
        input_tokens = len(query) // 4 + 5
        output_tokens = random.randint(50, min(max_tokens, 200))
        
        # Calculate simulated cost based on model
        cost = config.calculate_cost(input_tokens, output_tokens)
        
        # Generate varied simulated responses
        response_templates = [
            f"Based on your query about '{query[:30]}...', here's what I found: "
            f"This is a comprehensive response that addresses the key points. "
            f"The main aspects to consider are: 1) Understanding the context, "
            f"2) Analyzing the requirements, and 3) Providing actionable insights. "
            f"For more details, consider exploring related topics.",
            
            f"Thank you for your question. Let me provide a detailed answer: "
            f"The topic you mentioned involves several important considerations. "
            f"First, it's essential to understand the fundamentals. "
            f"Second, practical application is key. "
            f"Finally, continuous learning will help you master this subject.",
            
            f"Here's a structured response to your inquiry: "
            f"Understanding '{query[:20]}...' requires examining multiple factors. "
            f"Key insight #1: Context matters significantly. "
            f"Key insight #2: Implementation varies by use case. "
            f"Key insight #3: Best practices evolve over time.",
            
            f"Great question! Let me break this down: "
            f"Your query touches on important concepts in this domain. "
            f"The short answer is that it depends on your specific requirements. "
            f"However, I can offer some general guidance that should be helpful. "
            f"Would you like me to elaborate on any specific aspect?",
            
            f"I've analyzed your request and here are my findings: "
            f"This topic has multiple dimensions worth exploring. "
            f"From a technical perspective, the approach should be systematic. "
            f"From a practical standpoint, focus on measurable outcomes. "
            f"Let me know if you need clarification on any points.",
        ]
        
        response_text = random.choice(response_templates)
        
        # Add model info to simulated response
        if model_name:
            response_text = f"[Simulated response from {model_name}] " + response_text
        
        return response_text, input_tokens, output_tokens, cost
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation"""
        return len(text) // 4 + 1
