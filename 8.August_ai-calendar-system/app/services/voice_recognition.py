import speech_recognition as sr
import pyaudio
from pydub import AudioSegment
import io
import tempfile
import os

class VoiceRecognitionService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def listen_for_command(self, timeout=10, phrase_time_limit=5):
        """Listen for voice command and return text"""
        try:
            with self.microphone as source:
                print("Listening for command...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return "Timeout - no speech detected"
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Error with speech recognition service: {e}"
    
    def process_audio_file(self, audio_file):
        """Process uploaded audio file and return text"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                audio_file.save(tmp_file.name)
                
                # Load and process audio
                with sr.AudioFile(tmp_file.name) as source:
                    audio = self.recognizer.record(source)
                
                # Convert to text
                text = self.recognizer.recognize_google(audio)
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
                
                return text
                
        except Exception as e:
            return f"Error processing audio file: {str(e)}"
    
    def start_continuous_listening(self, callback_function):
        """Start continuous listening mode"""
        def listen_continuously():
            while True:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    text = self.recognizer.recognize_google(audio)
                    
                    # Check for wake word (e.g., "Hey Calendar")
                    if "hey calendar" in text.lower():
                        callback_function(text)
                        
                except sr.WaitTimeoutError:
                    pass  # Normal timeout, continue listening
                except sr.UnknownValueError:
                    pass  # Couldn't understand, continue listening
                except Exception as e:
                    print(f"Error in continuous listening: {e}")
                    break
        
        # Start listening in a separate thread
        import threading
        listening_thread = threading.Thread(target=listen_continuously, daemon=True)
        listening_thread.start()
        return listening_thread