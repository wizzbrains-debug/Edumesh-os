import json
from typing import List, Dict, Any
from .gemini_client import EduMeshGemini

class GapDetector:
    """
    Role: Strategic Gap Analyst
    Detects skill gaps and arbitrage opportunities.
    """
    def __init__(self, gemini: EduMeshGemini):
        self.gemini = gemini
        self.thought_signature_label = "edumesh-gap-detector-v1"

    def detect_gaps(self, community_state: str) -> List[Dict[str, Any]]:
        # 1. Parse the raw state to extract lists for constraints
        try:
            state_data = json.loads(community_state)
            people = state_data.get("people", [])
            community_people = [p["name"] for p in people]
            
            # Extract all unique skills from everyone
            all_skills = set()
            for p in people:
                all_skills.update(p.get("skills", []))
            community_skills = list(all_skills)
            
        except json.JSONDecodeError:
            # Fallback if state is not valid JSON
            community_people = "Unknown"
            community_skills = "Unknown"

        prompt = f"""
        You are a community intelligence system.

        IMPORTANT RULES:
        - You may ONLY reference people from this list:
          {community_people}

        - You may ONLY reference skills from this list:
          {community_skills}

        DO NOT invent new names, roles, or skills.

        TASK:
        Analyze the community graph and identify strategic skill gaps
        and leadership opportunities using ONLY the provided people.
        
        Community Data:
        {community_state}

        Return a JSON array with:
        - title
        - severity (HIGH, MEDIUM, LOW)
        - suggested_intervention (mention real people by name)
        """
        
        result = self.gemini.generate_json(prompt, thinking_level="HIGH")
        # Ensure result is a list, generate_json might return a dict if the model wraps it
        if isinstance(result, dict) and "gaps" in result:
            return result["gaps"]
        if isinstance(result, list):
            return result
        return []
