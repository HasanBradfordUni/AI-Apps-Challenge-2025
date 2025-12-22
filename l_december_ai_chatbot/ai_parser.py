import os
import json
from google import genai
from google.genai import Client

class AIIntegrationService:
    """Integration with Google Generative AI"""
    
    def __init__(self):
        self.client = None
        self.model_name = "gemini-2.0-flash"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google GenAI client"""
        try:
            self.client = Client(vertexai=True, project="generalpurposeai", location="us-central1")
            print("AI Integration Service initialized successfully")
        except Exception as e:
            print(f"Warning: AI service not available: {e}")
            self.client = None
    
    def generate_response(self, user_message, system_prompt, context=None):
        """Generate AI response to user message"""
        if not self.client:
            return "I apologize, but AI services are currently unavailable."
        
        try:
            # Build conversation context
            full_prompt = system_prompt + "\n\n"
            
            if context:
                full_prompt += "Recent conversation:\n"
                for msg in context[-5:]:  # Last 5 messages for context
                    full_prompt += f"User: {msg['user_message']}\n"
                    full_prompt += f"Assistant: {msg['ai_response']}\n"
                full_prompt += "\n"
            
            full_prompt += f"User: {user_message}\nAssistant:"
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[full_prompt]
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}"
    
    def analyze_intent(self, message):
        """Analyze user intent from message"""
        if not self.client:
            return None
        
        try:
            prompt = f"""
            Analyze the user's intent from this message: "{message}"
            
            Classify into one of these categories:
            - question: User is asking a question
            - task: User wants to perform a task
            - app_request: User wants to use a specific app
            - general: General conversation
            
            Return only the category name.
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            
            return response.text.strip().lower()
            
        except Exception as e:
            return None