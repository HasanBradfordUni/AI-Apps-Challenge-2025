from google import genai
from google.genai.types import GenerateContentConfig
from google.genai import Client
import google.auth
import json
import re
from datetime import datetime, timedelta

# Initialize Google Auth and Client
credentials, project_id = google.auth.default()
client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")

class AICommandParser:
    def __init__(self):
        self.client = client
        self.model_name = "gemini-2.0-flash"
    
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return "Unable to generate summary at this time."
    
    def generate_calendar_insights(self, events, time_period="week"):
        """Generate AI insights about calendar patterns and productivity"""
        prompt = f"""
        Analyze these calendar events for the past {time_period} and provide insights:
        
        Events: {json.dumps(events, indent=2)}
        
        Please provide:
        1. Meeting frequency and patterns
        2. Time management observations
        3. Productivity suggestions
        4. Schedule optimization recommendations
        
        Keep insights professional and actionable.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating insights: {str(e)}")
            return "Unable to generate insights at this time."
    
    def parse_natural_language_scheduling(self, user_input):
        """Parse natural language input for scheduling requests"""
        prompt = f"""
        Parse this natural language scheduling request:
        
        User Input: "{user_input}"
        
        Extract scheduling information and return JSON:
        {{
            "intent": "schedule|reschedule|cancel|find_time",
            "event_details": {{
                "title": "meeting title or subject",
                "date": "YYYY-MM-DD or relative like 'tomorrow'",
                "time": "HH:MM or relative like 'morning'",
                "duration": "duration in minutes",
                "attendees": ["list of people mentioned"],
                "location": "location if specified",
                "description": "additional context"
            }},
            "urgency": "high|medium|low",
            "confidence": 0.0-1.0
        }}
        
        Return only valid JSON.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            json_text = self._extract_json(response.text)
            return json.loads(json_text)
        except Exception as e:
            print(f"Error parsing natural language: {str(e)}")
            return {"intent": "unknown", "confidence": 0.0}
    
    def generate_meeting_agenda(self, meeting_title, attendees, duration_minutes):
        """Generate a meeting agenda based on title and participants"""
        prompt = f"""
        Generate a professional meeting agenda for:
        
        Meeting: {meeting_title}
        Attendees: {', '.join(attendees) if attendees else 'Not specified'}
        Duration: {duration_minutes} minutes
        
        Create a structured agenda with:
        1. Welcome and introductions (if applicable)
        2. Main discussion points
        3. Action items to cover
        4. Time allocations for each section
        5. Next steps/follow-up
        
        Make it professional and time-efficient.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating agenda: {str(e)}")
            return "Unable to generate meeting agenda at this time."
    
    def analyze_scheduling_conflicts(self, new_event, existing_events):
        """Analyze potential conflicts and suggest resolutions"""
        prompt = f"""
        Analyze potential scheduling conflicts:
        
        New Event: {json.dumps(new_event, indent=2)}
        Existing Events: {json.dumps(existing_events, indent=2)}
        
        Provide analysis in JSON format:
        {{
            "has_conflicts": true|false,
            "conflicts": [
                {{
                    "event_id": "conflicting event id",
                    "event_title": "title",
                    "conflict_type": "overlap|back_to_back|travel_time",
                    "severity": "high|medium|low"
                }}
            ],
            "suggestions": [
                {{
                    "action": "reschedule|shorten|move_location",
                    "reasoning": "why this suggestion makes sense",
                    "new_time": "HH:MM if applicable"
                }}
            ]
        }}
        
        Return only valid JSON.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            json_text = self._extract_json(response.text)
            return json.loads(json_text)
        except Exception as e:
            print(f"Error analyzing conflicts: {str(e)}")
            return {"has_conflicts": False, "conflicts": [], "suggestions": []}
    
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

# Additional utility functions for calendar AI features
def format_ai_response_for_user(ai_response, response_type="general"):
    """Format AI responses for better user presentation"""
    if response_type == "summary":
        return f"📅 **Daily Summary**\n\n{ai_response}"
    elif response_type == "suggestion":
        return f"💡 **AI Suggestion**\n\n{ai_response}"
    elif response_type == "conflict":
        return f"⚠️ **Schedule Conflict**\n\n{ai_response}"
    elif response_type == "insight":
        return f"📊 **Calendar Insights**\n\n{ai_response}"
    else:
        return ai_response

def validate_scheduling_data(scheduling_data):
    """Validate AI-parsed scheduling data before processing"""
    required_fields = ['intent', 'confidence']
    
    if not isinstance(scheduling_data, dict):
        return False, "Invalid data format"
    
    for field in required_fields:
        if field not in scheduling_data:
            return False, f"Missing required field: {field}"
    
    if scheduling_data.get('confidence', 0) < 0.5:
        return False, "Low confidence in AI parsing"
    
    return True, "Valid"

# Main function for testing
def main():
    """Test the AI parser functionality"""
    parser = AICommandParser()
    
    # Test email parsing
    test_email_subject = "Meeting Request: Project Review"
    test_email_body = "Can we schedule a meeting tomorrow at 2 PM to review the project status?"
    
    result = parser.parse_email_scheduling_request(test_email_subject, test_email_body)
    print("Email parsing result:", result)

if __name__ == '__main__':
    main()