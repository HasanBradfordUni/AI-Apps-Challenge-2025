import speech_recognition as sr
import os
import json
import threading
import time
from datetime import datetime
import tempfile
import subprocess
import queue

class VoiceMethods:
    def __init__(self, upload_folder=None, voice_profiles_folder=None):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_recording = False
        self.current_transcript = ""
        self.voice_profiles = {}
        self.transcript_queue = queue.Queue()
        self.recording_thread = None
        
        # Use provided folder paths or defaults
        self.upload_folder = upload_folder or "uploads"
        self.voice_profiles_folder = voice_profiles_folder or "voice_profiles"
        
        # Ensure directories exist
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.voice_profiles_folder, exist_ok=True)
        
        self.load_voice_profiles()
        
        # Enhanced recognizer settings for better accuracy
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
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

    def load_voice_profiles(self):
        """Load voice profiles from file"""
        try:
            profiles_file = os.path.join(self.voice_profiles_folder, "profiles.json")
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    self.voice_profiles = json.load(f)
                print(f"Loaded {len(self.voice_profiles)} voice profiles from {profiles_file}")
            else:
                self.voice_profiles = {}
                print(f"No existing voice profiles found at {profiles_file}")
        except Exception as e:
            print(f"Error loading voice profiles: {e}")
            self.voice_profiles = {}

    def save_voice_profiles(self):
        """Save voice profiles to file"""
        try:
            profiles_file = os.path.join(self.voice_profiles_folder, "profiles.json")
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_profiles, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.voice_profiles)} voice profiles to {profiles_file}")
        except Exception as e:
            print(f"Error saving voice profiles: {e}")

    def train_voice_profile(self, user_name, training_text):
        """Train a voice profile for a user"""
        try:
            # Simulate voice training (in a real implementation, this would use actual ML)
            profile_data = {
                'user_name': user_name,
                'training_text': training_text,
                'created_at': datetime.now().isoformat(),
                'accuracy_improvement': 15,  # Simulated improvement percentage
                'training_sessions': self.voice_profiles.get(user_name, {}).get('training_sessions', 0) + 1
            }
            
            self.voice_profiles[user_name] = profile_data
            self.save_voice_profiles()
            
            return profile_data['accuracy_improvement']
        except Exception as e:
            print(f"Error training voice profile: {e}")
            return 0

    def get_current_transcript(self):
        """Get the current transcript during live recording"""
        return self.current_transcript

    def improve_transcription_quality(self, transcript):
        """Improve transcription quality with post-processing"""
        if not transcript or transcript.startswith("Error"):
            return transcript
        
        try:
            # Basic text cleaning and formatting
            improved = transcript.strip()
            
            # Remove duplicate words
            words = improved.split()
            cleaned_words = []
            for i, word in enumerate(words):
                if i == 0 or word.lower() != words[i-1].lower():
                    cleaned_words.append(word)
            
            improved = ' '.join(cleaned_words)
            
            # Basic punctuation improvements
            improved = improved.replace(' , ', ', ')
            improved = improved.replace(' . ', '. ')
            improved = improved.replace(' ? ', '? ')
            improved = improved.replace(' ! ', '! ')
            
            # Capitalize first letter
            if improved:
                improved = improved[0].upper() + improved[1:]
            
            return improved
        except Exception as e:
            print(f"Error improving transcription: {e}")
            return transcript

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
                    '-ar', '16000',  # Sample rate
                    '-ac', '1',      # Mono
                    '-c:a', 'pcm_s16le',  # PCM codec
                    '-af', 'highpass=f=80,lowpass=f=8000,volume=1.5',  # Audio filters
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
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    if text.strip():
                        transcription_results.append(text.strip())
                        print(f"Google recognition successful: {text[:50]}...")

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Google Speech Recognition error: {e}")
            
            # Method 2: Google Speech Recognition with enhanced settings
            try:
                with sr.AudioFile(processed_file) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(
                        audio, 
                        language='en-US',
                        show_all=False
                    )
                    if text.strip() and text not in transcription_results:
                        transcription_results.append(text.strip())
                        print(f"Enhanced Google recognition: {text[:50]}...")
            except Exception as e:
                print(f"Enhanced recognition error: {e}")
            
            # Method 3: Whisper API (if available)
            try:
                whisper_result = self.transcribe_with_whisper(processed_file)
                if whisper_result and whisper_result not in transcription_results:
                    transcription_results.append(whisper_result)
                    print(f"Whisper recognition: {whisper_result[:50]}...")
            except Exception as e:
                print(f"Whisper error: {e}")
            
            # Clean up processed file if it's different from original
            if processed_file != file_path:
                try:
                    os.remove(processed_file)
                except:
                    pass
            
            # Return the best transcription
            if transcription_results:
                # Return the longest transcription as it's likely the most complete
                best_result = max(transcription_results, key=len)
                return self.improve_transcription_quality(best_result)
            else:
                return "Error: Could not transcribe audio. Please check audio quality and try again."
                
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
    
    def start_real_time_recording(self):
        """Start real-time audio recording with improved stability"""
        if not self.microphone:
            raise Exception("Microphone not available")
            
        self.is_recording = True
        self.current_transcript = ""
        
        # Clear any existing queue items
        while not self.transcript_queue.empty():
            try:
                self.transcript_queue.get_nowait()
            except queue.Empty:
                break
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._record_audio_continuously, daemon=True)
        self.recording_thread.start()
        
        # Start transcription thread
        threading.Thread(target=self._process_audio_continuously, daemon=True).start()
    
    def _record_audio_continuously(self):
        """Record audio continuously and add to queue"""
        print("Starting continuous audio recording...")
        
        while self.is_recording:
            try:
                with self.microphone as source:
                    # Adjust for ambient noise periodically
                    if len(self.current_transcript) % 100 == 0:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Listen for audio with shorter timeout for better responsiveness
                    audio = self.recognizer.listen(source, timeout=0.5, phrase_time_limit=5)
                    
                    # Add audio to queue for processing
                    if not self.transcript_queue.full():
                        self.transcript_queue.put(audio)
                
            except sr.WaitTimeoutError:
                # No speech detected within timeout - this is normal
                continue
            except Exception as e:
                print(f"Error in audio recording: {e}")
                time.sleep(0.1)
    
    def _process_audio_continuously(self):
        """Process audio from queue and transcribe"""
        print("Starting continuous transcription...")
        
        while self.is_recording or not self.transcript_queue.empty():
            try:
                # Get audio from queue with timeout
                audio = self.transcript_queue.get(timeout=1)
                
                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    if text.strip():
                        # Add space before new text if needed
                        if self.current_transcript and not self.current_transcript.endswith(' '):
                            self.current_transcript += " "
                        self.current_transcript += text.strip()
                        print(f"Transcribed: {text}")
                except sr.UnknownValueError:
                    # Speech was unintelligible - continue
                    continue
                except sr.RequestError as e:
                    print(f"Recognition service error: {e}")
                    continue
                    
            except queue.Empty:
                # No audio in queue - continue
                continue
            except Exception as e:
                print(f"Error in transcription processing: {e}")
                time.sleep(0.1)
    
    def stop_recording(self):
        """Stop recording and return final transcript"""
        self.is_recording = False
        
        # Wait for processing to complete
        time.sleep(1)
        
        # Process any remaining audio in queue
        while not self.transcript_queue.empty():
            try:
                audio = self.transcript_queue.get_nowait()
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    if text.strip():
                        if self.current_transcript and not self.current_transcript.endswith(' '):
                            self.current_transcript += " "
                        self.current_transcript += text.strip()
                except:
                    continue
            except queue.Empty:
                break
        
        return self.current_transcript.strip()
    
    def transcribe_audio_chunks(self, file_path, chunk_duration=20):
        """Split audio into smaller chunks for better transcription coverage"""
        try:
            import pydub
            
            print(f"Starting chunked transcription for file: {file_path}")
            
            # Load audio file
            audio = pydub.AudioSegment.from_file(file_path)
            total_duration = len(audio) / 1000  # Duration in seconds
            print(f"Total audio duration: {total_duration:.2f} seconds")
            
            # Use smaller chunks for better coverage
            chunk_length_ms = chunk_duration * 1000
            overlap_ms = 2000  # 2 second overlap to avoid missing words at boundaries
            
            transcriptions = []
            temp_dir = tempfile.gettempdir()
            
            # Create overlapping chunks
            start = 0
            chunk_num = 0
            
            while start < len(audio):
                end = min(start + chunk_length_ms, len(audio))
                chunk = audio[start:end]
                
                chunk_file = os.path.join(temp_dir, f"chunk_{chunk_num}_{os.getpid()}.wav")
                chunk.export(chunk_file, format="wav", parameters=["-ar", "16000", "-ac", "1"])
                
                print(f"Processing chunk {chunk_num + 1}, duration: {len(chunk)/1000:.2f}s")
                
                # Transcribe chunk with multiple attempts
                chunk_transcript = None
                for attempt in range(2):
                    chunk_transcript = self.transcribe_audio_file(chunk_file)
                    if chunk_transcript and not chunk_transcript.startswith("Error"):
                        break
                    time.sleep(0.5)  # Brief pause between attempts
                
                if chunk_transcript and not chunk_transcript.startswith("Error"):
                    transcriptions.append(chunk_transcript.strip())
                    print(f"Chunk {chunk_num + 1} transcribed: {chunk_transcript[:50]}...")
                else:
                    print(f"Failed to transcribe chunk {chunk_num + 1}")
                
                # Clean up chunk file
                try:
                    os.remove(chunk_file)
                except:
                    pass
                
                # Move to next chunk with overlap
                if end >= len(audio):
                    break
                start = end - overlap_ms
                chunk_num += 1
            
            # Combine transcriptions and remove duplicates from overlaps
            if transcriptions:
                combined = self._combine_overlapping_transcripts(transcriptions)
                print(f"Final combined transcript length: {len(combined)} characters")
                return combined
            else:
                return "No audio could be transcribed from any chunks"
            
        except ImportError:
            print("pydub not available - install with: pip install pydub")
            return self.transcribe_audio_file(file_path)
        except Exception as e:
            print(f"Chunk transcription error: {e}")
            return self.transcribe_audio_file(file_path)
    
    def _combine_overlapping_transcripts(self, transcriptions):
        """Combine overlapping transcripts and remove duplicates"""
        if not transcriptions:
            return ""
        
        if len(transcriptions) == 1:
            return transcriptions[0]
        
        combined = transcriptions[0]
        
        for i in range(1, len(transcriptions)):
            current = transcriptions[i]
            
            # Find potential overlap by checking if the end of combined matches the start of current
            overlap_found = False
            for overlap_len in range(min(50, len(combined), len(current)), 5, -1):
                combined_end = combined[-overlap_len:].strip().lower()
                current_start = current[:overlap_len].strip().lower()
                
                if combined_end == current_start:
                    # Remove the overlapping part from current and append
                    combined += " " + current[overlap_len:].strip()
                    overlap_found = True
                    break
            
            if not overlap_found:
                # No overlap found, just append with space
                combined += " " + current.strip()
        
        return combined.strip()
    
    def export_transcript(self, transcript, summary, format_type, session_id):
        """Export transcript to file with improved error handling"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Use the configured upload folder
            uploads_dir = self.upload_folder
            
            # Generate filename
            if format_type == 'txt':
                filename = f"transcript_{session_id}_{timestamp}.txt"
                filepath = os.path.join(uploads_dir, filename)
                
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
                filepath = os.path.join(uploads_dir, filename)
                
                data = {
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'transcript': transcript if transcript else "",
                    'summary': summary if summary else "",
                    'export_format': format_type,
                    'word_count': len(transcript.split()) if transcript else 0,
                    'character_count': len(transcript) if transcript else 0
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            else:
                raise Exception(f"Unsupported export format: {format_type}")
            
            # Verify file was created and has content
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print(f"Export successful: {filepath}")
                return filepath
            else:
                raise Exception("File was not created successfully or is empty")
            
        except Exception as e:
            print(f"Export error details: {str(e)}")
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