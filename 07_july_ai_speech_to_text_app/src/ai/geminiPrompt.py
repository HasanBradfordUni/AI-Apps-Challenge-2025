from google import genai
from google.genai.types import GenerateContentConfig
from google.genai import Client
import google.auth

credentials, project_id = google.auth.default()

# Initialize the new client
client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")

def generate_transcript_summary(transcript, summary_type):
    """Generate an AI summary of the transcript based on type"""
    
    if summary_type == "meeting":
        prompt = f"""
        Please analyze the following meeting transcript and provide a comprehensive summary:
        
        Transcript: {transcript}
        
        Please provide:
        1. Meeting Overview (2-3 sentences)
        2. Key Discussion Points (bullet points)
        3. Action Items and Decisions Made
        4. Next Steps or Follow-ups
        5. Key Participants and Their Contributions
        
        Format the response clearly with proper headings and bullet points.
        """
    
    elif summary_type == "lecture":
        prompt = f"""
        Please analyze the following lecture transcript and provide an educational summary:
        
        Transcript: {transcript}
        
        Please provide:
        1. Lecture Topic and Main Theme
        2. Key Learning Points (bullet points)
        3. Important Concepts and Definitions
        4. Examples or Case Studies Mentioned
        5. Takeaways for Students
        
        Format the response as study notes with clear headings.
        """
    
    elif summary_type == "interview":
        prompt = f"""
        Please analyze the following interview transcript and provide a structured summary:
        
        Transcript: {transcript}
        
        Please provide:
        1. Interview Overview
        2. Key Questions Asked
        3. Main Responses and Insights
        4. Candidate/Interviewee Strengths Highlighted
        5. Important Quotes or Statements
        
        Format the response professionally with clear sections.
        """
    
    elif summary_type == "conversation":
        prompt = f"""
        Please analyze the following conversation transcript and provide a summary:
        
        Transcript: {transcript}
        
        Please provide:
        1. Conversation Overview
        2. Main Topics Discussed
        3. Key Points Made by Each Speaker
        4. Agreements or Disagreements
        5. Overall Tone and Outcome
        
        Format the response in a friendly, conversational style.
        """
    
    elif summary_type == "quick":
        prompt = f"""
        Please provide a quick, concise summary of the following transcript in 3-4 sentences:
        
        Transcript: {transcript}
        
        Focus on the most important points and main outcomes.
        """
    
    else:
        prompt = f"""
        Please provide a general summary of the following transcript:
        
        Transcript: {transcript}
        
        Include the main topics, key points, and any important conclusions.
        """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_voice_command_response(command):
    """Generate AI response to voice commands"""
    
    prompt = f"""
    You are a helpful voice assistant for a speech-to-text application. 
    A user has given you the following voice command: "{command}"
    
    Please analyze the command and provide:
    1. What action the user wants to perform
    2. A helpful response acknowledging their request
    3. Any additional guidance if needed
    
    Available actions in the app:
    - start_recording: Start recording audio
    - stop_recording: Stop recording audio
    - summarize: Generate a summary of the transcript
    - clear_transcript: Clear the current transcript
    - export_transcript: Export the transcript to a file
    - train_voice: Train voice recognition
    
    Respond in a friendly, conversational tone as if you're speaking to the user.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"I'm sorry, I couldn't process that command. Please try again. Error: {str(e)}"

def generate_transcription_tips(transcript_quality):
    """Generate tips for improving transcription quality"""
    
    prompt = f"""
    Based on the transcription quality assessment: {transcript_quality}
    
    Please provide helpful tips for improving speech-to-text accuracy:
    1. Audio quality improvements
    2. Speaking techniques
    3. Environment setup
    4. Recording best practices
    
    Make the tips practical and easy to follow.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return "Unable to generate tips at this time."

def analyze_transcript_sentiment(transcript):
    """Analyze the sentiment and tone of the transcript"""
    
    prompt = f"""
    Please analyze the sentiment and tone of the following transcript:
    
    Transcript: {transcript}
    
    Please provide:
    1. Overall sentiment (positive, negative, neutral)
    2. Emotional tone throughout the conversation
    3. Key emotional moments or shifts
    4. Professional vs casual tone assessment
    
    Keep the analysis objective and helpful.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return "Unable to analyze sentiment at this time."

def main():
    """Main function to demonstrate the AI functionality"""
    pass

if __name__ == '__main__':
    main()