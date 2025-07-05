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
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['VOICE_PROFILES_FOLDER'] = 'voice_profiles'

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VOICE_PROFILES_FOLDER'], exist_ok=True)

# Initialize voice methods
voice_methods = VoiceMethods()

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
    """Train voice recognition for better accuracy"""
    try:
        data = request.get_json()
        user_name = data.get('user_name', 'default')
        training_text = data.get('training_text', '')
        
        result = voice_methods.train_voice_profile(user_name, training_text)
        
        return jsonify({
            'success': True,
            'message': f'Voice training completed for {user_name}',
            'accuracy_improvement': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-transcript', methods=['POST'])
def export_transcript():
    """Export transcript to file"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        export_format = data.get('format', 'txt')
        
        if session_id not in transcript_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = transcript_sessions[session_id]
        file_path = voice_methods.export_transcript(
            session_data['transcript'],
            session_data.get('summary', ''),
            export_format,
            session_id
        )
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
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

if __name__ == '__main__':
    app.run(host='localhost', port=6922, debug=True)