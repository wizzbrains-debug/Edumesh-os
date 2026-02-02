import os
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load environment variables
load_dotenv()

class EduMeshGemini:
    """
    Core client for interacting with Gemini 3 Pro.
    Maintains persistent thought signature across calls.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-pro-preview" 
        self.thought_signature: List[str] = [] 
        
    def _add_thought_context(self, prompt: str) -> str:
        """Injects previous thought signatures into the current prompt context."""
        if not self.thought_signature:
            return prompt
        
        signature_block = "\n".join([f"Previous Thought: {t}" for t in self.thought_signature[-3:]]) # Keep last 3
        return f"{prompt}\n\n[SYSTEM: PREVIOUS THOUGHT SIGNATURES]\n{signature_block}\n[END SYSTEM]"

    def generate_text(self, prompt: str, thinking_level: str = "HIGH") -> str:
        """
        Generates text with thinking capabilities.
        thinking_level: "HIGH" (simulated via strict instruction or config)
        """
        # Enhance prompt with thought history
        full_prompt = self._add_thought_context(prompt)

        # map "HIGH" to specific config if API supports it, essentially ensuring include_thoughts is True
        # and potentially setting a higher token budget for thoughts if that were an option.
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt,
            config=config
        )
        
        # Capture thoughts if available to persist signature
        if hasattr(response, 'candidates') and response.candidates:
             for part in response.candidates[0].content.parts:
                 if part.thought:
                     if part.thought not in self.thought_signature:
                        self.thought_signature.append(part.thought)
        
        return response.text

    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None, thinking_level: str = "HIGH") -> Dict[str, Any]:
        """
        Generates structured JSON output.
        """
        full_prompt = self._add_thought_context(prompt)
        json_prompt = f"{full_prompt}\n\nIMPORTANT: Output ONLY valid JSON."
        
        config = types.GenerateContentConfig(
             response_mime_type="application/json",
             thinking_config=types.ThinkingConfig(include_thoughts=True)
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=json_prompt,
            config=config
        )

        # Persist thought similarly
        if hasattr(response, 'candidates') and response.candidates:
             for part in response.candidates[0].content.parts:
                 if hasattr(part, 'thought') and part.thought: # Check attribute existence
                     self.thought_signature.append(part.thought)

        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {response.text}")
            return {}

    def generate_multimodal(self, prompt: str, image_path: str, thinking_level: str = "HIGH") -> str:
        """
        Generates content based on text and image.
        """
        full_prompt = self._add_thought_context(prompt)
        
        try:
            image = Image.open(image_path)
        except Exception as e:
            return f"Error loading image: {e}"

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[full_prompt, image],
            config=config
        )
        
        # Persist thought
        if hasattr(response, 'candidates') and response.candidates:
             for part in response.candidates[0].content.parts:
                 if hasattr(part, 'thought') and part.thought:
                     self.thought_signature.append(part.thought)
                     
        return response.text
    
    def get_thought_signature(self) -> List[str]:
        return self.thought_signature
