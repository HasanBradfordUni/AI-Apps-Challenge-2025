import speech_recognition as sr
import os
import json
import threading
import time
from datetime import datetime
import tempfile

class VoiceMethods:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_recording = False
        self.current_transcript = ""
        self.voice_profiles = {}
        self.load_voice_profiles()
        
        # Initialize microphone with error handling
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
            self.microphone = None
    
    def transcribe_audio_file(self, file_path):
        """Transcribe audio from uploaded file using SpeechRecognition"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return "Error: Audio file not found"
            
            # Use SpeechRecognition for file transcription
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition (free but requires internet)
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Could not understand audio - please try speaking more clearly"
            except sr.RequestError as e:
                return f"Could not request results from speech recognition service: {e}"
                
        except Exception as e:
            return f"Error transcribing audio file: {str(e)}"
    
    def start_real_time_recording(self):
        """Start real-time audio recording"""
        if not self.microphone:
            raise Exception("Microphone not available")
            
        self.is_recording = True
        self.current_transcript = ""
        
        # Start transcription in a separate thread
        threading.Thread(target=self._transcribe_continuously, daemon=True).start()
    
    def _transcribe_continuously(self):
        """Continuously transcribe audio"""
        print("Starting continuous transcription...")
        
        while self.is_recording:
            try:
                if not self.microphone:
                    break
                    
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio)
                    if text.strip():
                        self.current_transcript += text + " "
                        print(f"Transcribed: {text}")
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    continue
                except sr.RequestError:
                    # API was unreachable or unresponsive
                    continue
                    
            except sr.WaitTimeoutError:
                # No speech detected within timeout
                continue
            except Exception as e:
                print(f"Error in continuous transcription: {e}")
                time.sleep(1)
    
    def stop_recording(self):
        """Stop recording and return final transcript"""
        self.is_recording = False
        time.sleep(0.5)  # Give time for last transcription
        return self.current_transcript.strip()
    
    def get_current_transcript(self):
        """Get current transcript during recording"""
        return self.current_transcript.strip()
    
    def process_voice_command(self, command):
        """Process voice commands using basic text matching"""
        command = command.lower().strip()
        
        # Basic command recognition
        if any(word in command for word in ['start', 'begin', 'record', 'recording']):
            return "start_recording"
        elif any(word in command for word in ['stop', 'end', 'finish', 'pause']):
            return "stop_recording"
        elif any(word in command for word in ['summary', 'summarize', 'sum up']):
            return "summarize"
        elif any(word in command for word in ['clear', 'reset', 'delete', 'remove']):
            return "clear_transcript"
        elif any(word in command for word in ['export', 'save', 'download']):
            return "export_transcript"
        else:
            return "unknown_command"
    
    def train_voice_profile(self, user_name, training_text):
        """Train voice profile for better recognition"""
        try:
            if not self.microphone:
                return "Microphone not available for voice training"
            
            # Simulate voice training with basic profile storage
            self.voice_profiles[user_name] = {
                'created_at': datetime.now().isoformat(),
                'training_text': training_text,
                'samples_count': 3  # Simulate 3 training samples
            }
            
            self.save_voice_profiles()
            return f"Voice profile created for {user_name}"
            
        except Exception as e:
            return f"Error training voice profile: {str(e)}"
    
    def load_voice_profiles(self):
        """Load existing voice profiles"""
        try:
            profiles_path = 'voice_profiles/profiles.json'
            if os.path.exists(profiles_path):
                with open(profiles_path, 'r') as f:
                    self.voice_profiles = json.load(f)
            else:
                self.voice_profiles = {}
        except Exception as e:
            print(f"Error loading voice profiles: {e}")
            self.voice_profiles = {}
    
    def save_voice_profiles(self):
        """Save voice profiles to file"""
        try:
            os.makedirs('voice_profiles', exist_ok=True)
            with open('voice_profiles/profiles.json', 'w') as f:
                json.dump(self.voice_profiles, f, indent=2)
        except Exception as e:
            print(f"Error saving voice profiles: {e}")
    
    def export_transcript(self, transcript, summary, format_type, session_id):
        """Export transcript to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format_type == 'txt':
                filename = f"transcript_{session_id}_{timestamp}.txt"
                filepath = os.path.join("uploads", filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Transcript - {session_id}\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write("TRANSCRIPT:\n")
                    f.write(transcript if transcript else "No transcript available")
                    f.write("\n\n" + "=" * 50 + "\n\n")
                    if summary:
                        f.write("AI SUMMARY:\n")
                        f.write(summary)
            
            elif format_type == 'json':
                filename = f"transcript_{session_id}_{timestamp}.json"
                filepath = os.path.join("uploads", filename)
                
                data = {
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'transcript': transcript if transcript else "",
                    'summary': summary if summary else ""
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting transcript: {str(e)}")
    
    def validate_audio_file(self, file):
        """Validate uploaded audio file"""
        if not file:
            return False
        
        allowed_extensions = ['mp3', 'wav', 'm4a', 'mp4', 'ogg', 'flac']
        filename = file.filename.lower()
        
        return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions
    
    def get_microphone_status(self):
        """Get microphone availability status"""
        return {
            'available': self.microphone is not None,
            'is_recording': self.is_recording,
            'current_transcript_length': len(self.current_transcript)
        }