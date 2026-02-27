# llm_config.py
import os
from litellm import completion
import json
import re

class LLMConfig:
    """Centralized LLM configuration - change settings here only"""
    
    # Model settings - CHANGE ONLY HERE
    MODEL = "anthropic.claude-3-haiku-20240307-v1:0"
    TEMPERATURE = 0
    MAX_TOKENS = 2000
    
    @staticmethod
    def call_llm(prompt: str, max_tokens: int = None) -> str:
        """
        Centralized LLM call - all extractors use this
        """
        response = completion(
            model=LLMConfig.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=LLMConfig.TEMPERATURE,
            max_tokens=max_tokens or LLMConfig.MAX_TOKENS
        )
        return response.choices[0].message.content
    
    @staticmethod
    def extract_json(response_text: str) -> dict:
        """
        Centralized JSON extraction logic
        """
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try finding JSON in text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
