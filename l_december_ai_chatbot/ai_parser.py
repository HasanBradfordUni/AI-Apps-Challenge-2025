import os
import json
from google import genai
from google.genai import types
import google.auth
import time
import random

class AIIntegrationService:
    """Service for AI integration using Google's Gemini API"""
    
    def __init__(self):
        """Initialize the AI service with Gemini client"""
        try:
            # Get credentials
            credentials, project_id = google.auth.default()
            
            # Initialize the Gemini client
            self.client = genai.Client(
                vertexai=True,
                project="generalpurposeai",
                location="us-central1"
            )
            
            self.model_id = "gemini-2.0-flash-exp"
            self.max_retries = 3
            self.retry_delay = 2  # seconds
            print(f"✓ AIIntegrationService initialized with model: {self.model_id}")
            
        except Exception as e:
            print(f"✗ AIIntegrationService initialization failed: {e}")
            self.client = None
            self.model_id = None
            self.max_retries = 0
            self.retry_delay = 0
    
    def _exponential_backoff_retry(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                    if attempt < self.max_retries - 1:
                        # Exponential backoff with jitter
                        wait_time = (2 ** attempt) * self.retry_delay + random.uniform(0, 1)
                        print(f"Rate limit hit. Retrying in {wait_time:.2f} seconds... (Attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"Max retries reached. Rate limit still active.")
                        raise Exception("API rate limit exceeded. Please try again in a few minutes.")
                else:
                    # Not a rate limit error, raise immediately
                    raise
        
        raise Exception("Failed after maximum retries")
    
    def generate_response(self, user_message, system_prompt, conversation_history=None, available_apps=None):
        """Generate AI response using Gemini with retry logic"""
        try:
            if not self.client:
                return "AI service is not available. Please check configuration."
            
            # Build the full prompt with context
            full_prompt = f"{system_prompt}\n\n"
            
            # Add available apps context if provided
            if available_apps:
                apps_list = "\n".join([
                    f"- {app['name']} ({app['icon']}): {app['description']} - {'Available' if app['available'] else 'Not Available'}"
                    for app in available_apps.values()
                ])
                full_prompt += f"Available Apps:\n{apps_list}\n\n"
            
            # Add conversation history if provided
            if conversation_history:
                history_text = "\n".join([
                    f"User: {msg['user_message']}\nAssistant: {msg['ai_response']}"
                    for msg in conversation_history[-5:]  # Last 5 messages
                ])
                full_prompt += f"Conversation History:\n{history_text}\n\n"
            
            # Add current user message
            full_prompt += f"User: {user_message}\n\nAssistant:"
            
            # Define the API call function
            def make_api_call():
                return self.client.models.generate_content(
                    model=self.model_id,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=2048,
                    )
                )
            
            # Call with retry logic
            response = self._exponential_backoff_retry(make_api_call)
            
            # Extract response text
            if response and response.text:
                return response.text.strip()
            else:
                return "I couldn't generate a response. Please try again."
            
        except Exception as e:
            error_message = str(e)
            print(f"Error generating AI response: {error_message}")
            import traceback
            print(traceback.format_exc())
            
            # Return user-friendly error message
            if '429' in error_message or 'RESOURCE_EXHAUSTED' in error_message:
                return "⚠️ I'm currently experiencing high demand. Please try again in a few minutes, or rephrase your question to use fewer resources."
            elif 'quota' in error_message.lower():
                return "⚠️ The daily API quota has been reached. Please try again tomorrow or contact the administrator."
            else:
                return f"I encountered an error while processing your request. Please try again or rephrase your question."
    
    def detect_app_intent(self, message, available_apps):
        """Use AI to detect which app the user wants to use"""
        try:
            if not self.client:
                return None
            
            apps_description = "\n".join([
                f"{app_id}: {app['name']} - {app['description']}"
                for app_id, app in available_apps.items()
                if app['available']
            ])
            
            prompt = f"""Based on the user's message, determine which app they want to use.
            
Available apps:
{apps_description}

User message: "{message}"

If the user wants to use a specific app, respond with just the app_id (e.g., 'document_search').
If no specific app is mentioned, respond with 'none'.
Do not include any explanation, just the app_id or 'none'."""

            def make_api_call():
                return self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=50,
                    )
                )
            
            response = self._exponential_backoff_retry(make_api_call)
            
            if response and response.text:
                app_id = response.text.strip().lower()
                if app_id in available_apps and available_apps[app_id]['available']:
                    return {
                        'app_id': app_id,
                        'app_name': available_apps[app_id]['name'],
                        'description': available_apps[app_id]['description'],
                        'confidence': 0.9
                    }
            
            return None
            
        except Exception as e:
            print(f"Error detecting app intent: {e}")
            # Return None silently for intent detection failures
            return None
    
    def enhance_prompt_for_mode(self, message, mode_config):
        """Enhance user message based on prompt mode"""
        try:
            if not self.client:
                return message
            
            system_context = mode_config.get('system_prompt', '')
            
            prompt = f"""Given this conversation mode context:
{system_context}

Enhance this user message to align with the mode while preserving the original intent:
"{message}"

Provide only the enhanced message, no explanation."""

            def make_api_call():
                return self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.5,
                        max_output_tokens=200,
                    )
                )
            
            response = self._exponential_backoff_retry(make_api_call)
            
            if response and response.text:
                return response.text.strip()
            
            return message
            
        except Exception as e:
            print(f"Error enhancing prompt: {e}")
            # Return original message if enhancement fails
            return message