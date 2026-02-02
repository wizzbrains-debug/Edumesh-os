from typing import List, Dict, Any
from .gemini_client import EduMeshGemini

class LeadSelector:
    """
    Role: HR / Talent Scout
    Selects community leads based on trust and skill signals.
    """
    def __init__(self, gemini: EduMeshGemini):
        self.gemini = gemini

    def select_leads(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidate_str = json.dumps(candidates, indent=2)
        prompt = f"""
        Task: Select the top 3 candidates for "Community Lead" roles for a "Train-the-Trainer" program.
        Criteria: High skill level, willingness to share (mentorship signals), and diverse background.
        
        Candidates:
        {candidate_str}
        
        Output Schema (JSON List):
        [
             {{ "id": "user_id", "name": "str", "reason": "Why selected?" }}
        ]
        """
        
        result = self.gemini.generate_json(prompt, thinking_level="HIGH")
        if isinstance(result, dict) and "leads" in result:
            return result["leads"]
        if isinstance(result, list):
            return result
        return []

import json
