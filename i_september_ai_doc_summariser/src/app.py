from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from utils.document_processor import DocumentProcessor
from utils.forms import DocumentSummaryForm
from ai.geminiPrompt import generate_document_summary, analyze_document_content
import markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
folder_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config['UPLOAD_FOLDER'] = os.path.join(folder_path, 'uploads')
app.config['SUMMARIES_FOLDER'] = os.path.join(folder_path, 'summaries')

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SUMMARIES_FOLDER'], exist_ok=True)

# Initialize document processor
doc_processor = DocumentProcessor()

# Global variables for document sessions
document_sessions = {}
current_document = ""
current_summary = ""

# Register markdown filter
@app.template_filter('markdown')
def markdown_filter(text):
    """Convert markdown text to HTML"""
    if not text:
        return ""
    return markdown.markdown(text, extensions=['extra', 'codehilite'])

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with document upload and summarization"""
    form = DocumentSummaryForm()
    summary_result = ""
    session_id = None
    
    if form.validate_on_submit():
        # Process uploaded document
        if form.document_file.data:
            try:
                filename = secure_filename(form.document_file.data.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.document_file.data.save(filepath)
                
                # Extract text from document
                document_text = doc_processor.extract_text_from_file(filepath)
                
                # Generate AI summary
                summary_result = generate_document_summary(
                    document_text, 
                    form.summary_type.data,
                    form.summary_length.data,
                    form.summary_tone.data
                )
                
                # Save session
                session_id = f"doc_{timestamp}"
                document_sessions[session_id] = {
                    'document_text': document_text,
                    'summary': summary_result,
                    'timestamp': datetime.now().isoformat(),
                    'filename': filename,
                    'type': 'document_upload',
                    'summary_settings': {
                        'type': form.summary_type.data,
                        'length': form.summary_length.data,
                        'tone': form.summary_tone.data
                    }
                }
                
                flash('Document processed successfully!', 'success')
                
            except Exception as e:
                flash(f'Error processing document: {str(e)}', 'error')
    
    return render_template('index.html', 
                         form=form, 
                         summary_result=summary_result,
                         session_id=session_id)

@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """Handle document file upload with text extraction"""
    try:
        if 'document_file' not in request.files:
            return jsonify({'error': 'No document file provided'}), 400
        
        file = request.files['document_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not doc_processor.validate_document_file(file):
            return jsonify({'error': 'Invalid document file format. Supported: PDF, DOCX, TXT'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        # Extract text from document
        document_text = doc_processor.extract_text_from_file(filepath)
        
        if not document_text or len(document_text.strip()) < 10:
            return jsonify({'error': 'Could not extract readable text from document'}), 500
        
        # Get summary settings from form
        summary_type = request.form.get('summary_type', 'general')
        summary_length = request.form.get('summary_length', 'medium')
        summary_tone = request.form.get('summary_tone', 'neutral')
        
        # Generate summary
        summary = generate_document_summary(document_text, summary_type, summary_length, summary_tone)
        
        # Save session
        session_id = f"doc_{timestamp}"
        document_sessions[session_id] = {
            'document_text': document_text,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'type': 'document_upload',
            'file_size_mb': round(file_size_mb, 2),
            'word_count': len(document_text.split()) if document_text else 0,
            'summary_settings': {
                'type': summary_type,
                'length': summary_length,
                'tone': summary_tone
            }
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'document_text': document_text[:500] + "..." if len(document_text) > 500 else document_text,
            'full_text_length': len(document_text),
            'summary': summary,
            'filename': filename,
            'file_size_mb': round(file_size_mb, 2),
            'word_count': len(document_text.split()) if document_text else 0
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/regenerate-summary', methods=['POST'])
def regenerate_summary():
    """Regenerate summary with different settings"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        summary_type = data.get('summary_type', 'general')
        summary_length = data.get('summary_length', 'medium')
        summary_tone = data.get('summary_tone', 'neutral')
        
        if session_id not in document_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = document_sessions[session_id]
        document_text = session_data['document_text']
        
        # Generate new summary
        new_summary = generate_document_summary(document_text, summary_type, summary_length, summary_tone)
        
        # Update session
        session_data['summary'] = new_summary
        session_data['summary_settings'] = {
            'type': summary_type,
            'length': summary_length,
            'tone': summary_tone
        }
        
        return jsonify({
            'success': True,
            'summary': new_summary,
            'settings': session_data['summary_settings']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-document', methods=['POST'])
def analyze_document():
    """Analyze document content for insights"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id not in document_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = document_sessions[session_id]
        document_text = session_data['document_text']
        
        # Perform document analysis
        analysis = analyze_document_content(document_text)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-summaries', methods=['POST'])
def compare_summaries():
    """Compare two different summary approaches"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        settings1 = data.get('settings1', {})
        settings2 = data.get('settings2', {})
        
        if session_id not in document_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = document_sessions[session_id]
        document_text = session_data['document_text']
        
        # Generate two different summaries
        summary1 = generate_document_summary(
            document_text,
            settings1.get('type', 'general'),
            settings1.get('length', 'medium'),
            settings1.get('tone', 'neutral')
        )
        
        summary2 = generate_document_summary(
            document_text,
            settings2.get('type', 'academic'),
            settings2.get('length', 'long'),
            settings2.get('tone', 'formal')
        )
        
        return jsonify({
            'success': True,
            'summary1': summary1,
            'summary2': summary2,
            'settings1': settings1,
            'settings2': settings2
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-summary', methods=['POST'])
def export_summary():
    """Export summary to file"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        session_id = data.get('session_id')
        export_format = data.get('format', 'txt')
        
        if session_id not in document_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = document_sessions[session_id]
        
        file_path = doc_processor.export_summary(
            session_data['document_text'],
            session_data['summary'],
            export_format,
            session_id,
            session_data.get('summary_settings', {})
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-summary/<session_id>/<export_format>')
def export_summary_direct(session_id, export_format):
    """Direct export with URL parameters"""
    try:
        print(f"Export request - Session ID: {session_id}, Format: {export_format}")
        
        if session_id not in document_sessions:
            print(f"Session {session_id} not found in {list(document_sessions.keys())}")
            return jsonify({'error': 'Session not found. Please upload a document first.'}), 404
        
        session_data = document_sessions[session_id]
        print(f"Session data found: {session_data.keys()}")
        
        # Validate export format
        if export_format not in ['txt', 'json', 'pdf']:
            return jsonify({'error': f'Invalid export format: {export_format}'}), 400
        
        # Check if document text exists
        if not session_data.get('document_text'):
            return jsonify({'error': 'No document text available in this session'}), 400
        
        # Check if summary exists
        if not session_data.get('summary'):
            return jsonify({'error': 'No summary available in this session'}), 400
        
        file_path = doc_processor.export_summary(
            session_data['document_text'],
            session_data['summary'],
            export_format,
            session_id,
            session_data.get('summary_settings', {})
        )
        
        print(f"Export file path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"File not found at: {file_path}")
            return jsonify({'error': 'Export file was not created successfully. Check server logs for details.'}), 500
        
        print(f"File size: {os.path.getsize(file_path)} bytes")
        filename = os.path.basename(file_path)
        print(f"Sending file: {filename}")
        
        # Set correct mimetype based on format
        mimetypes = {
            'txt': 'text/plain',
            'json': 'application/json',
            'pdf': 'application/pdf'
        }
        
        return send_file(
            file_path, 
            as_attachment=True,
            download_name=filename,
            mimetype=mimetypes.get(export_format, 'application/octet-stream')
        )
    
    except Exception as e:
        print(f"Export error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/get-sessions', methods=['GET'])
def get_sessions():
    """Get all document sessions"""
    return jsonify({
        'sessions': [
            {
                'id': session_id,
                'timestamp': data['timestamp'],
                'type': data['type'],
                'filename': data.get('filename', ''),
                'word_count': data.get('word_count', 0),
                'has_summary': bool(data.get('summary')),
                'summary_settings': data.get('summary_settings', {})
            }
            for session_id, data in document_sessions.items()
        ]
    })

@app.route('/api/delete-session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a document session"""
    if session_id not in document_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    del document_sessions[session_id]
    return jsonify({'success': True, 'message': 'Session deleted'})

@app.route('/api/get-session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session data"""
    if session_id not in document_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'success': True,
        'session': document_sessions[session_id]
    })

@app.route('/api/get-document-stats', methods=['GET'])
def get_document_stats():
    """Get statistics about processed documents"""
    total_documents = len(document_sessions)
    total_words = sum(session.get('word_count', 0) for session in document_sessions.values())
    
    # Summary type distribution
    summary_types = {}
    for session in document_sessions.values():
        settings = session.get('summary_settings', {})
        summary_type = settings.get('type', 'unknown')
        summary_types[summary_type] = summary_types.get(summary_type, 0) + 1
    
    return jsonify({
        'total_documents': total_documents,
        'total_words_processed': total_words,
        'summary_type_distribution': summary_types,
        'average_words_per_document': total_words / total_documents if total_documents > 0 else 0
    })

@app.route('/api/download-session/<session_id>', methods=['GET'])
def download_session(session_id):
    """Download complete session data as JSON"""
    try:
        if session_id not in document_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = document_sessions[session_id]
        
        # Create JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"session_{session_id}_{timestamp}.json"
        filepath = os.path.join(app.config['SUMMARIES_FOLDER'], filename)
        
        # Prepare session data for export
        export_data = {
            'session_id': session_id,
            'filename': session_data.get('filename', 'unknown'),
            'timestamp': session_data.get('timestamp', ''),
            'summary_settings': session_data.get('summary_settings', {}),
            'document_text': session_data.get('document_text', ''),
            'summary': session_data.get('summary', ''),
            'word_count': session_data.get('word_count', 0),
            'file_size_mb': session_data.get('file_size_mb', 0)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
    
    except Exception as e:
        print(f"Download session error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=6922, debug=True)