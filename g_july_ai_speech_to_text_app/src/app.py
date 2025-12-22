from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from utils.voice_methods import VoiceMethods
from utils.forms import SpeechToTextForm
from ai.geminiPrompt import generate_transcript_summary, generate_voice_command_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Get the correct folder paths
folder_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config['UPLOAD_FOLDER'] = os.path.join(folder_path, 'uploads')
app.config['VOICE_PROFILES_FOLDER'] = os.path.join(folder_path, 'voice_profiles')

print(f"App folder path: {folder_path}")
print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
print(f"Voice profiles folder: {app.config['VOICE_PROFILES_FOLDER']}")

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VOICE_PROFILES_FOLDER'], exist_ok=True)

# Initialize voice methods with correct folder paths
voice_methods = VoiceMethods(
    upload_folder=app.config['UPLOAD_FOLDER'],
    voice_profiles_folder=app.config['VOICE_PROFILES_FOLDER']
)

# Global variables for real-time transcription
transcription_active = False
current_transcript = ""
transcript_sessions = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with all functionality"""
    form = SpeechToTextForm()
    ai_summary = ""
    
    if form.validate_on_submit():
        # Process uploaded audio file
        if form.audio_file.data:
            filename = secure_filename(form.audio_file.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.audio_file.data.save(filepath)
            
            # Transcribe audio
            transcript = voice_methods.transcribe_audio_file(filepath)
            
            # Generate AI summary
            ai_summary = generate_transcript_summary(transcript, form.summary_type.data)
            
            # Save session
            session_id = f"upload_{timestamp}"
            transcript_sessions[session_id] = {
                'transcript': transcript,
                'summary': ai_summary,
                'timestamp': datetime.now().isoformat(),
                'filename': filename,
                'type': 'upload'
            }
    
    return render_template('index.html', form=form, ai_summary=ai_summary)

@app.route('/api/start-recording', methods=['POST'])
def start_recording():
    """Start real-time audio recording and transcription"""
    global transcription_active, current_transcript
    
    try:
        if transcription_active:
            return jsonify({'error': 'Recording already in progress'}), 400
        
        transcription_active = True
        current_transcript = ""
        
        # Start recording
        voice_methods.start_real_time_recording()
        
        return jsonify({
            'success': True,
            'message': 'Recording started',
            'session_id': f"live_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop-recording', methods=['POST'])
def stop_recording():
    """Stop real-time recording and return transcript"""
    global transcription_active, current_transcript
    
    try:
        if not transcription_active:
            return jsonify({'error': 'No recording in progress'}), 400
        
        transcription_active = False
        current_transcript = voice_methods.stop_recording()
        
        # Generate summary if requested
        data = request.get_json() or {}
        include_summary = data.get('include_summary', False)
        summary = generate_transcript_summary(current_transcript, "meeting") if include_summary else ""
        
        # Save session
        session_id = f"live_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        transcript_sessions[session_id] = {
            'transcript': current_transcript,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'type': 'live'
        }
        
        return jsonify({
            'success': True,
            'transcript': current_transcript,
            'summary': summary,
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-transcript', methods=['GET'])
def get_current_transcript():
    """Get current transcript during live recording"""
    global current_transcript, transcription_active
    
    if transcription_active:
        current_transcript = voice_methods.get_current_transcript()
    
    return jsonify({
        'transcript': current_transcript,
        'is_recording': transcription_active,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/voice-command', methods=['POST'])
def process_voice_command():
    """Process voice commands"""
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
        # Use AI to understand and respond to voice commands
        response = generate_voice_command_response(command)
        
        # Execute command actions based on AI response
        if 'start_recording' in response.lower():
            return start_recording()
        elif 'stop_recording' in response.lower():
            return stop_recording()
        elif 'summarize' in response.lower():
            if current_transcript:
                summary = generate_transcript_summary(current_transcript, "quick")
                return jsonify({'success': True, 'summary': summary, 'response': response})
            else:
                return jsonify({'error': 'No transcript available to summarize', 'response': response}), 400
        
        return jsonify({'success': True, 'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train-voice', methods=['POST'])
def train_voice():
    """Train voice recognition with proper timing"""
    try:
        data = request.get_json()
        user_name = data.get('user_name', 'default')
        training_text = data.get('training_text', '')
        duration = data.get('duration', 15)  # Get duration from frontend
        
        # Simulate proper training duration
        import time
        time.sleep(duration)  # Actually wait for the specified duration
        
        result = voice_methods.train_voice_profile(user_name, training_text)
        
        return jsonify({
            'success': True,
            'message': f'Voice training completed for {user_name} in {duration} seconds',
            'accuracy_improvement': result,
            'training_duration': duration
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-transcript', methods=['POST'])
def export_transcript():
    """Export transcript to file"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        session_id = data.get('session_id')
        export_format = data.get('format', 'txt')
        
        print(f"Export request - Session ID: {session_id}, Format: {export_format}")
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        if session_id not in transcript_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = transcript_sessions[session_id]
        print(f"Session data found: {session_data.keys()}")
        
        file_path = voice_methods.export_transcript(
            session_data['transcript'],
            session_data.get('summary', ''),
            export_format,
            session_id
        )
        
        print(f"Export file path: {file_path}")
        
        # Check if file exists before sending
        if not os.path.exists(file_path):
            return jsonify({'error': 'Export file was not created successfully'}), 500
        
        # Get the filename for download
        filename = os.path.basename(file_path)
        
        return send_file(
            file_path, 
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        print(f"Export error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Add a new route for direct exports with URL parameters
@app.route('/api/export-transcript/<session_id>/<export_format>')
def export_transcript_direct(session_id, export_format):
    """Direct export with URL parameters"""
    try:
        print(f"Direct export - Session ID: {session_id}, Format: {export_format}")
        
        if session_id not in transcript_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = transcript_sessions[session_id]
        
        file_path = voice_methods.export_transcript(
            session_data['transcript'],
            session_data.get('summary', ''),
            export_format,
            session_id
        )
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Export file was not created successfully'}), 500
        
        filename = os.path.basename(file_path)
        
        return send_file(
            file_path, 
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        print(f"Direct export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-sessions', methods=['GET'])
def get_sessions():
    """Get all transcript sessions"""
    return jsonify({
        'sessions': [
            {
                'id': session_id,
                'timestamp': data['timestamp'],
                'type': data['type'],
                'filename': data.get('filename', ''),
                'has_summary': bool(data.get('summary'))
            }
            for session_id, data in transcript_sessions.items()
        ]
    })

@app.route('/api/delete-session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a transcript session"""
    if session_id not in transcript_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    del transcript_sessions[session_id]
    return jsonify({'success': True, 'message': 'Session deleted'})

@app.route('/api/upload-audio', methods=['POST'])
def upload_audio():
    """Handle audio file upload with optimized processing"""
    try:
        print("=== Enhanced Upload Audio Debug ===")
        print(f"Request files: {list(request.files.keys())}")
        
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not voice_methods.validate_audio_file(file):
            return jsonify({'error': 'Invalid audio file format'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"File saved: {filepath}, Size: {file_size_mb:.2f} MB")
        
        # Optimized transcription strategy
        transcript = ""
        transcription_method = "standard"
        
        if file_size_mb > 25:  # Very large files
            print("Very large file detected, using chunked transcription...")
            transcript = voice_methods.transcribe_audio_chunks(filepath, chunk_duration=15)
            transcription_method = "chunked_optimized"
        elif file_size_mb > 5:  # Medium files
            print("Medium file detected, using chunked transcription...")
            transcript = voice_methods.transcribe_audio_chunks(filepath, chunk_duration=20)
            transcription_method = "chunked_standard"
        else:  # Small files
            print("Small file detected, using standard transcription...")
            transcript = voice_methods.transcribe_audio_file(filepath)
            transcription_method = "standard"
        
        # Improve transcription quality
        transcript = voice_methods.improve_transcription_quality(transcript)
        
        if not transcript or transcript.startswith("Error"):
            return jsonify({'error': f'Transcription failed: {transcript}'}), 500
        
        # Generate summary efficiently
        summary_type = request.form.get('summary_type', 'conversation')
        summary = generate_transcript_summary(transcript, summary_type)
        
        # Save session
        session_id = f"upload_{timestamp}"
        transcript_sessions[session_id] = {
            'transcript': transcript,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'type': 'upload',
            'file_size_mb': round(file_size_mb, 2),
            'transcription_method': transcription_method,
            'word_count': len(transcript.split()) if transcript else 0,
            'processing_time': 'optimized'
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'transcript': transcript,
            'summary': summary,
            'filename': filename,
            'file_size_mb': round(file_size_mb, 2),
            'transcription_method': transcription_method,
            'word_count': len(transcript.split()) if transcript else 0
        })
    
    except Exception as e:
        print(f"Error in upload_audio: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/get-session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session data"""
    if session_id not in transcript_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'success': True,
        'session': transcript_sessions[session_id]
    })

if __name__ == '__main__':
    app.run(host='localhost', port=6922, debug=True)