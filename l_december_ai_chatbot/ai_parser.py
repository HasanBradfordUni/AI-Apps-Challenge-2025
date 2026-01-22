import os
import json
from google import genai
from google.genai import Client

class AIIntegrationService:
    """Integration with Google Generative AI"""
    
    def _initialize_client(self):
        """Initialize Google GenAI client"""
        try:
            self.client = Client(vertexai=True, project="generalpurposeai", location="us-central1")
            print("AI Integration Service initialized successfully")
        except Exception as e:
            print(f"Warning: AI service not available: {e}")
            self.client = None
    
    def generate_response(self, user_message, system_prompt, conversation_history=None, available_apps=None):
        """Generate AI response with app context"""
        if not self.client:
            return "AI service is currently unavailable."
        
        try:
            # Build context with available apps
            context_parts = [system_prompt]
            
            if available_apps:
                apps_info = "\n\nAvailable Applications:\n"
                for app_id, app_info in available_apps.items():
                    if app_info['available']:
                        apps_info += f"- {app_info['name']}: {app_info['description']}\n"
                context_parts.append(apps_info)
            
            # Add conversation history
            if conversation_history:
                history_text = "\n\nPrevious Conversation:\n"
                for msg in conversation_history[-5:]:  # Last 5 messages
                    history_text += f"User: {msg['user_message']}\n"
                    history_text += f"Assistant: {msg['ai_response']}\n"
                context_parts.append(history_text)
            
            # Add current user message
            context_parts.append(f"\n\nUser: {user_message}\nAssistant:")
            
            full_prompt = "".join(context_parts)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            
            return response.text
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return f"I encountered an error: {str(e)}"
    
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