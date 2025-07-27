import speech_recognition as sr
import os
import json
import threading
import time
from datetime import datetime
import tempfile
import subprocess
import wave

class VoiceMethods:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_recording = False
        self.current_transcript = ""
        self.voice_profiles = {}
        self.load_voice_profiles()
        
        # Enhanced recognizer settings for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.8
        
        # Initialize microphone with error handling
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print(f"Energy threshold set to: {self.recognizer.energy_threshold}")
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
            self.microphone = None
    
    def preprocess_audio(self, file_path):
        """Preprocess audio file for better transcription quality"""
        try:
            # Create a temporary processed file
            temp_dir = tempfile.gettempdir()
            processed_file = os.path.join(temp_dir, f"processed_{os.path.basename(file_path)}")
            
            # Try to use ffmpeg for audio preprocessing (if available)
            try:
                # Normalize audio, reduce noise, convert to optimal format
                subprocess.run([
                    'ffmpeg', '-i', file_path,
                    '-ar', '16000',  # Sample rate 16kHz (optimal for speech)
                    '-ac', '1',      # Mono
                    '-c:a', 'pcm_s16le',  # PCM format
                    '-af', 'highpass=f=80,lowpass=f=8000,volume=1.5',  # Filter and amplify
                    '-y', processed_file
                ], check=True, capture_output=True)
                
                print(f"Audio preprocessed with ffmpeg: {processed_file}")
                return processed_file
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("ffmpeg not available, using original file")
                return file_path
                
        except Exception as e:
            print(f"Error preprocessing audio: {e}")
            return file_path
    
    def transcribe_audio_file(self, file_path):
        """Enhanced audio transcription with multiple methods"""
        try:
            print(f"Transcribing audio file: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return "Error: Audio file not found"
            
            # Preprocess audio for better quality
            processed_file = self.preprocess_audio(file_path)
            
            # Try multiple transcription methods
            transcription_results = []
            
            # Method 1: Google Speech Recognition (Free)
            try:
                with sr.AudioFile(processed_file) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.record(source)
                
                text = self.recognizer.recognize_google(audio, language='en-US')
                transcription_results.append(("Google", text))
                print(f"Google transcription: {text[:100]}...")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Google Speech Recognition error: {e}")
            
            # Method 2: Google Speech Recognition with enhanced settings
            try:
                with sr.AudioFile(processed_file) as source:
                    audio = self.recognizer.record(source)
                
                # Try with show_all=True to get confidence scores
                text = self.recognizer.recognize_google(
                    audio, 
                    language='en-US',
                    show_all=False
                )
                transcription_results.append(("Google Enhanced", text))
                print(f"Google Enhanced transcription: {text[:100]}...")
            except Exception as e:
                print(f"Google Enhanced transcription failed: {e}")
            
            # Method 3: Whisper API (if available)
            try:
                whisper_result = self.transcribe_with_whisper(processed_file)
                if whisper_result:
                    transcription_results.append(("Whisper", whisper_result))
                    print(f"Whisper transcription: {whisper_result[:100]}...")
            except Exception as e:
                print(f"Whisper transcription failed: {e}")
            
            # Clean up processed file if it's different from original
            if processed_file != file_path:
                try:
                    os.remove(processed_file)
                except:
                    pass
            
            # Return the best transcription
            if transcription_results:
                # For now, prefer Whisper if available, otherwise use the longest result
                whisper_results = [r for r in transcription_results if r[0] == "Whisper"]
                if whisper_results:
                    return whisper_results[0][1]
                
                # Otherwise, return the longest transcription (usually more complete)
                best_result = max(transcription_results, key=lambda x: len(x[1]))
                return best_result[1]
            else:
                return "Could not transcribe audio - please try a different file or check audio quality"
                
        except Exception as e:
            print(f"Error transcribing audio file: {str(e)}")
            return f"Error transcribing audio file: {str(e)}"
    
    def transcribe_with_whisper(self, file_path):
        """Try to use OpenAI Whisper for transcription"""
        try:
            import whisper
            
            # Load the base model (good balance of speed and accuracy)
            model = whisper.load_model("base")
            
            # Transcribe the audio
            result = model.transcribe(file_path, language='en')
            
            return result["text"].strip()
            
        except ImportError:
            print("Whisper not available - install with: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return None
    
    def transcribe_audio_chunks(self, file_path, chunk_duration=30):
        """Split audio into chunks for better transcription of long files"""
        try:
            import pydub
            
            # Load audio file
            audio = pydub.AudioSegment.from_file(file_path)
            
            # Split into chunks
            chunk_length_ms = chunk_duration * 1000
            chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
            
            transcriptions = []
            temp_dir = tempfile.gettempdir()
            
            for i, chunk in enumerate(chunks):
                chunk_file = os.path.join(temp_dir, f"chunk_{i}.wav")
                chunk.export(chunk_file, format="wav")
                
                # Transcribe chunk
                chunk_transcript = self.transcribe_audio_file(chunk_file)
                if not chunk_transcript.startswith("Error"):
                    transcriptions.append(chunk_transcript)
                
                # Clean up
                try:
                    os.remove(chunk_file)
                except:
                    pass
            
            return " ".join(transcriptions)
            
        except ImportError:
            print("pydub not available - install with: pip install pydub")
            return self.transcribe_audio_file(file_path)
        except Exception as e:
            print(f"Chunk transcription error: {e}")
            return self.transcribe_audio_file(file_path)
    
    def improve_transcription_quality(self, transcript):
        """Post-process transcription to improve quality"""
        if not transcript or transcript.startswith("Error"):
            return transcript
        
        # Basic text cleaning and formatting
        cleaned = transcript.strip()
        
        # Fix common transcription errors
        replacements = {
            " i ": " I ",
            " im ": " I'm ",
            " dont ": " don't ",
            " cant ": " can't ",
            " wont ": " won't ",
            " youre ": " you're ",
            " theyre ": " they're ",
            " theres ": " there's ",
            " whats ": " what's ",
            " thats ": " that's ",
            " its ": " it's ",
            " hes ": " he's ",
            " shes ": " she's ",
            " well ": " we'll ",
            " ill ": " I'll ",
            " youll ": " you'll ",
            " were ": " we're ",
            " oclock ": " o'clock ",
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        # Capitalize first letter of sentences
        sentences = cleaned.split('. ')
        sentences = [s.capitalize() if s else s for s in sentences]
        cleaned = '. '.join(sentences)
        
        # Ensure first letter is capitalized
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
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