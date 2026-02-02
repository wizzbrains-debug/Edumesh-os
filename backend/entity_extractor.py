import json
from typing import Dict, Any, List
from .gemini_client import EduMeshGemini

class EntityExtractor:
    """
    Role: Sociographic Data Analyst
    Extracts structured data from raw text.
    """
    def __init__(self, gemini: EduMeshGemini):
        self.gemini = gemini
        self.thought_signature_label = "edumesh-mapping-v1"

    def extract(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        Role: Sociographic Data Analyst ({self.thought_signature_label})
        Task: Analyze the following survey text and extract structured entities.
        
        Input Text: "{text}"
        
        Output Schema (JSON):
        {{
            "people": [{{ "name": "str", "role": "str", "bio": "str" }}],
            "skills": [{{ "name": "str", "level": "Beginner|Intermediate|Expert" }}],
            "needs": [{{ "name": "str", "type": "Learning|Mentorship|Collaboration" }}],
            "relationships": [{{ "from": "name", "to": "name", "type": "str" }}]
        }}
        """
        
        return self.gemini.generate_json(prompt, thinking_level="HIGH")
