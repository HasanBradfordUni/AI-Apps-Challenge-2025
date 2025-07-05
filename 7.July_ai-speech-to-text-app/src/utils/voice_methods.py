import speech_recognition as sr
import whisper
import pyaudio
import wave
import threading
import os
import json
from datetime import datetime
from pydub import AudioSegment
import tempfile

class VoiceMethods:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.whisper_model = None
        self.is_recording = False
        self.current_transcript = ""
        self.audio_frames = []
        self.voice_profiles = {}
        self.load_voice_profiles()
        
    def initialize_whisper(self):
        """Initialize Whisper model for offline transcription"""
        if not self.whisper_model:
            self.whisper_model = whisper.load_model("base")
    
    def transcribe_audio_file(self, file_path):
        """Transcribe audio from uploaded file"""
        try:
            # Convert to WAV if needed
            if not file_path.lower().endswith('.wav'):
                audio = AudioSegment.from_file(file_path)
                wav_path = file_path.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_path, format="wav")
                file_path = wav_path
            
            # Use Whisper for transcription
            self.initialize_whisper()
            result = self.whisper_model.transcribe(file_path)
            return result["text"]
        
        except Exception as e:
            # Fallback to SpeechRecognition
            try:
                with sr.AudioFile(file_path) as source:
                    audio = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio)
            except:
                return f"Error transcribing audio: {str(e)}"
    
    def start_real_time_recording(self):
        """Start real-time audio recording"""
        self.is_recording = True
        self.current_transcript = ""
        self.audio_frames = []
        
        # Start recording in a separate thread
        threading.Thread(target=self._record_audio, daemon=True).start()
        threading.Thread(target=self._transcribe_continuously, daemon=True).start()
    
    def _record_audio(self):
        """Record audio in chunks"""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
            
            while self.is_recording:
                data = stream.read(CHUNK)
                self.audio_frames.append(data)
            
            stream.stop_stream()
            stream.close()
        finally:
            p.terminate()
    
    def _transcribe_continuously(self):
        """Continuously transcribe audio chunks"""
        while self.is_recording:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.current_transcript += text + " "
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    continue
                    
            except sr.WaitTimeoutError:
                continue
    
    def stop_recording(self):
        """Stop recording and return final transcript"""
        self.is_recording = False
        
        # Save the recorded audio
        if self.audio_frames:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"recording_{timestamp}.wav"
            filepath = os.path.join("uploads", filename)
            
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()
        
        return self.current_transcript
    
    def get_current_transcript(self):
        """Get current transcript during recording"""
        return self.current_transcript
    
    def process_voice_command(self, command):
        """Process voice commands using speech recognition"""
        command = command.lower()
        
        # Basic command recognition
        if any(word in command for word in ['start', 'begin', 'record']):
            return "start_recording"
        elif any(word in command for word in ['stop', 'end', 'finish']):
            return "stop_recording"
        elif any(word in command for word in ['summary', 'summarize', 'sum up']):
            return "summarize"
        elif any(word in command for word in ['clear', 'reset', 'delete']):
            return "clear_transcript"
        else:
            return "unknown_command"
    
    def train_voice_profile(self, user_name, training_text):
        """Train voice profile for better recognition"""
        try:
            # Record training samples
            training_samples = []
            
            # Simulate voice training (in real implementation, you'd record actual audio)
            for i in range(3):  # 3 training samples
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=10)
                    
                # Save audio sample
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                sample_path = f"voice_profiles/{user_name}_sample_{i}_{timestamp}.wav"
                
                with open(sample_path, "wb") as f:
                    f.write(audio.get_wav_data())
                
                training_samples.append(sample_path)
            
            # Save voice profile
            self.voice_profiles[user_name] = {
                'training_samples': training_samples,
                'created_at': datetime.now().isoformat(),
                'training_text': training_text
            }
            
            self.save_voice_profiles()
            return "Voice profile trained successfully"
            
        except Exception as e:
            return f"Error training voice profile: {str(e)}"
    
    def load_voice_profiles(self):
        """Load existing voice profiles"""
        try:
            if os.path.exists('voice_profiles/profiles.json'):
                with open('voice_profiles/profiles.json', 'r') as f:
                    self.voice_profiles = json.load(f)
        except:
            self.voice_profiles = {}
    
    def save_voice_profiles(self):
        """Save voice profiles to file"""
        os.makedirs('voice_profiles', exist_ok=True)
        with open('voice_profiles/profiles.json', 'w') as f:
            json.dump(self.voice_profiles, f, indent=2)
    
    def export_transcript(self, transcript, summary, format_type, session_id):
        """Export transcript to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'txt':
            filename = f"transcript_{session_id}_{timestamp}.txt"
            filepath = os.path.join("uploads", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Transcript - {session_id}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write("TRANSCRIPT:\n")
                f.write(transcript)
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
                'transcript': transcript,
                'summary': summary
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def validate_audio_file(self, file):
        """Validate uploaded audio file"""
        if not file:
            return False
        
        allowed_extensions = ['mp3', 'wav', 'm4a', 'mp4', 'ogg', 'flac']
        filename = file.filename.lower()
        
        return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions
    
    def get_audio_duration(self, file_path):
        """Get audio file duration"""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000  # Convert to seconds
        except:
            return 0
    
    def chunk_audio_for_transcription(self, file_path, chunk_duration=60):
        """Split long audio files into chunks for better transcription"""
        try:
            audio = AudioSegment.from_file(file_path)
            duration = len(audio) / 1000  # seconds
            
            if duration <= chunk_duration:
                return [file_path]
            
            chunks = []
            for i in range(0, int(duration), chunk_duration):
                start_time = i * 1000
                end_time = min((i + chunk_duration) * 1000, len(audio))
                chunk = audio[start_time:end_time]
                
                chunk_filename = f"chunk_{i}_{file_path}"
                chunk.export(chunk_filename, format="wav")
                chunks.append(chunk_filename)
            
            return chunks
        except:
            return [file_path]