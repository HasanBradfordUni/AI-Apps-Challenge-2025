import vertexai
from vertexai.generative_models import GenerativeModel
import json
import re
from datetime import datetime, timedelta

# Initialize Vertex AI
vertexai.init(project="generalpurposeai", location="us-central1")
model = GenerativeModel(model_name="gemini-2.0-flash")

class AICommandParser:
    def __init__(self):
        self.model = model
    
    def parse_email_scheduling_request(self, email_subject, email_body):
        """Parse email content for scheduling instructions"""
        prompt = f"""
        Parse this email for scheduling instructions and return a JSON response:
        
        Subject: {email_subject}
        Body: {email_body}
        
        Extract the following information and return as JSON:
        {{
            "action": "create|update|cancel|reschedule",
            "event_title": "extracted meeting title",
            "date": "YYYY-MM-DD",
            "start_time": "HH:MM",
            "end_time": "HH:MM",
            "duration_minutes": number,
            "location": "location if mentioned",
            "attendees": ["email1@example.com", "email2@example.com"],
            "description": "additional details",
            "priority": "high|medium|low",
            "confidence": 0.0-1.0
        }}
        
        Return only valid JSON without any additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean and parse JSON response
            json_text = self._extract_json(response.text)
            return json.loads(json_text)
        except Exception as e:
            print(f"Error parsing email: {str(e)}")
            return {"action": "unknown", "confidence": 0.0}
    
    def parse_voice_command(self, voice_text):
        """Parse voice command for calendar actions"""
        prompt = f"""
        Parse this voice command for calendar actions:
        
        Command: "{voice_text}"
        
        Return JSON with:
        {{
            "intent": "create_event|check_schedule|cancel_event|reschedule_event|get_summary",
            "action_details": {{
                "event_title": "title if creating event",
                "date": "YYYY-MM-DD or 'today'|'tomorrow'|'next week'",
                "time": "HH:MM or 'morning'|'afternoon'|'evening'",
                "duration": "duration in minutes if specified",
                "location": "location if mentioned"
            }},
            "confidence": 0.0-1.0
        }}
        
        Return only valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_text = self._extract_json(response.text)
            return json.loads(json_text)
        except Exception as e:
            print(f"Error parsing voice command: {str(e)}")
            return {"intent": "unknown", "confidence": 0.0}
    
    def suggest_meeting_times(self, existing_events, meeting_duration_minutes=60):
        """Suggest optimal meeting times based on existing schedule"""
        prompt = f"""
        Based on these existing calendar events, suggest 3 optimal meeting times for a {meeting_duration_minutes}-minute meeting:
        
        Existing Events: {json.dumps(existing_events, indent=2)}
        
        Consider:
        - Avoid conflicts
        - Prefer business hours (9 AM - 5 PM)
        - Leave buffer time between meetings
        - Prefer morning slots when possible
        
        Return JSON:
        {{
            "suggestions": [
                {{
                    "date": "YYYY-MM-DD",
                    "start_time": "HH:MM",
                    "end_time": "HH:MM",
                    "reasoning": "why this time is optimal"
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_text = self._extract_json(response.text)
            return json.loads(json_text)
        except Exception as e:
            print(f"Error suggesting meeting times: {str(e)}")
            return {"suggestions": []}
    
    def generate_daily_summary(self, events, date):
        """Generate AI-powered daily agenda summary"""
        prompt = f"""
        Create a professional daily agenda summary for {date}:
        
        Events: {json.dumps(events, indent=2)}
        
        Generate a brief, executive-style summary including:
        - Number of meetings
        - Key meetings/priorities
        - Potential conflicts or tight scheduling
        - Preparation suggestions
        
        Keep it concise and actionable.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return "Unable to generate summary at this time."
    
    def _extract_json(self, text):
        """Extract JSON from AI response"""
        # Try to find JSON in the response
        json_match = re.search(r'({[\s\S]*})', text)
        if json_match:
            return json_match.group(1)
        else:
            # If no JSON found, try cleaning the response
            cleaned = re.sub(r'```json|```', '', text).strip()
            return cleaned