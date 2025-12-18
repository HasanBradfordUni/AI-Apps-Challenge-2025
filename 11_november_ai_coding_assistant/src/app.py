from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
import markdown
from datetime import datetime
from utils.code_processor import CodeProcessor
from utils.forms import CodeAssistantForm
from ai.geminiPrompt import (
    generate_code_suggestion, 
    explain_error, 
    generate_documentation, 
    complete_code,
    analyze_code_quality,
    generate_test_cases, 
    generate_code_completions,
    generate_hover_info,    
    explain_code_functionality
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
folder_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config['UPLOAD_FOLDER'] = os.path.join(folder_path, 'uploads')
app.config['CODE_SESSIONS_FOLDER'] = os.path.join(folder_path, 'code_sessions')

# Add markdown filter
@app.template_filter('markdown')
def markdown_filter(text):
    if not text:
        return ""
    return markdown.markdown(text, extensions=['fenced_code', 'tables', 'toc'])

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CODE_SESSIONS_FOLDER'], exist_ok=True)

# Initialize code processor
code_processor = CodeProcessor()

# Global variables for coding sessions
coding_sessions = {}
current_code = ""
current_language = "python"

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with code editor and AI assistance"""
    form = CodeAssistantForm()
    suggestion_result = ""
    session_id = None
    
    if form.validate_on_submit():
        # Process code assistance request
        if form.code_input.data:
            try:
                code_content = form.code_input.data
                language = form.programming_language.data
                assistance_type = form.assistance_type.data
                
                # Generate AI assistance based on type
                if assistance_type == 'suggestion':
                    suggestion_result = generate_code_suggestion(
                        code_content, 
                        language,
                        form.context.data
                    )
                elif assistance_type == 'error_explanation':
                    suggestion_result = explain_error(
                        code_content,
                        form.error_message.data,
                        language
                    )
                elif assistance_type == 'documentation':
                    suggestion_result = generate_documentation(
                        code_content,
                        language,
                        form.doc_type.data
                    )
                elif assistance_type == 'completion':
                    suggestion_result = complete_code(
                        code_content,
                        language,
                        form.context.data
                    )
                
                # Save session
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                session_id = f"code_{timestamp}"
                coding_sessions[session_id] = {
                    'code_content': code_content,
                    'language': language,
                    'suggestion': suggestion_result,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'code_assistance',
                    'assistance_settings': {
                        'type': assistance_type,
                        'context': form.context.data,
                        'error_message': form.error_message.data,
                        'doc_type': form.doc_type.data
                    }
                }
                
                flash('Code assistance generated successfully!', 'success')
                
            except Exception as e:
                flash(f'Error processing code: {str(e)}', 'error')
    
    return render_template('index.html', 
                         form=form, 
                         suggestion_result=suggestion_result,
                         session_id=session_id)

@app.route('/api/code-suggestion', methods=['POST'])
def get_code_suggestion():
    """Generate AI code suggestions"""
    try:
        data = request.get_json()
        code_content = data.get('code', '')
        language = data.get('language', 'python')
        context = data.get('context', '')
        
        if not code_content:
            return jsonify({'error': 'No code provided'}), 400
        
        # Generate suggestion
        suggestion = generate_code_suggestion(code_content, language, context)
        
        # Save session
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = f"code_{timestamp}"
        coding_sessions[session_id] = {
            'code_content': code_content,
            'language': language,
            'suggestion': suggestion,
            'timestamp': datetime.now().isoformat(),
            'type': 'code_suggestion',
            'assistance_settings': {
                'type': 'suggestion',
                'context': context
            }
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'suggestion': suggestion,
            'language': language,
            'code_length': len(code_content)
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/explain-error', methods=['POST'])
def explain_code_error():
    """Explain coding errors with AI assistance"""
    try:
        data = request.get_json()
        code_content = data.get('code', '')
        error_message = data.get('error', '')
        language = data.get('language', 'python')
        
        if not error_message:
            return jsonify({'error': 'No error message provided'}), 400
        
        # Generate error explanation
        explanation = explain_error(code_content, error_message, language)
        
        # Save session
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = f"error_{timestamp}"
        coding_sessions[session_id] = {
            'code_content': code_content,
            'language': language,
            'suggestion': explanation,
            'timestamp': datetime.now().isoformat(),
            'type': 'error_explanation',
            'assistance_settings': {
                'type': 'error_explanation',
                'error_message': error_message
            }
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'explanation': explanation,
            'language': language
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/generate-docs', methods=['POST'])
def generate_code_documentation():
    """Generate documentation for code"""
    try:
        data = request.get_json()
        code_content = data.get('code', '')
        language = data.get('language', 'python')
        doc_type = data.get('doc_type', 'docstring')
        
        if not code_content:
            return jsonify({'error': 'No code provided'}), 400
        
        # Generate documentation
        documentation = generate_documentation(code_content, language, doc_type)
        
        # Save session
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = f"docs_{timestamp}"
        coding_sessions[session_id] = {
            'code_content': code_content,
            'language': language,
            'suggestion': documentation,
            'timestamp': datetime.now().isoformat(),
            'type': 'documentation',
            'assistance_settings': {
                'type': 'documentation',
                'doc_type': doc_type
            }
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'documentation': documentation,
            'language': language
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/complete-code', methods=['POST'])
def complete_user_code():
    """Complete partial code with AI assistance"""
    try:
        data = request.get_json()
        code_content = data.get('code', '')
        language = data.get('language', 'python')
        context = data.get('context', '')
        
        if not code_content:
            return jsonify({'error': 'No code provided'}), 400
        
        # Generate code completion
        completion = complete_code(code_content, language, context)
        
        # Save session
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = f"completion_{timestamp}"
        coding_sessions[session_id] = {
            'code_content': code_content,
            'language': language,
            'suggestion': completion,
            'timestamp': datetime.now().isoformat(),
            'type': 'code_completion',
            'assistance_settings': {
                'type': 'completion',
                'context': context
            }
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'completion': completion,
            'language': language
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/export-code', methods=['POST'])
def export_code():
    """Export code to file"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        session_id = data.get('session_id')
        export_format = data.get('format', 'txt')
        
        if session_id not in coding_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = coding_sessions[session_id]
        
        file_path = code_processor.export_code(
            session_data['code_content'],
            session_data['suggestion'],
            session_data['language'],
            export_format,
            session_id,
            session_data.get('assistance_settings', {})
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

@app.route('/api/export-code-only', methods=['POST'])
def export_code_only():
    """Export only the current code in the editor as the specified file type"""
    try:
        data = request.get_json()
        code_content = data.get('code', '')
        language = data.get('language', 'python')
        session_id = data.get('session_id', f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if not code_content.strip():
            return jsonify({'error': 'No code content to export'}), 400
        
        # Export only the code
        file_path = code_processor.export_code_only(code_content, language, session_id)
        
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

@app.route('/api/get-supported-file-types', methods=['GET'])
def get_supported_file_types():
    """Get list of all supported file types for export dropdown"""
    try:
        file_types = code_processor.get_supported_file_types()
        return jsonify({
            'success': True,
            'file_types': file_types
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-session/<session_id>')
def download_session(session_id):
    """Download a specific session as a plaintext summary"""
    try:
        print(f"Download session request - Session ID: {session_id}")
        
        if session_id not in coding_sessions:
            print(f"Session {session_id} not found in {list(coding_sessions.keys())}")
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = coding_sessions[session_id]
        print(f"Session data found: {session_data.keys()}")
        
        file_path = code_processor.download_session_summary(
            session_data['code_content'],
            session_data['suggestion'],
            session_data['language'],
            session_id,
            'txt',  # Default to txt format
            session_data.get('assistance_settings', {})
        )
        
        print(f"Download file path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"File not found at: {file_path}")
            return jsonify({'error': 'Download file was not created successfully'}), 500
        
        print(f"File size: {os.path.getsize(file_path)} bytes")
        filename = os.path.basename(file_path)
        print(f"Sending file: {filename}")
        
        return send_file(
            file_path, 
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    
    except Exception as e:
        print(f"Download session error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-session/<session_id>/<export_format>')
def download_session_format(session_id, export_format):
    """Download a specific session with specified format (txt or markdown)"""
    try:
        print(f"Download session request - Session ID: {session_id}, Format: {export_format}")
        
        if session_id not in coding_sessions:
            print(f"Session {session_id} not found in {list(coding_sessions.keys())}")
            return jsonify({'error': 'Session not found'}), 404
        
        # Only allow txt and markdown formats for session downloads
        if export_format not in ['txt', 'markdown', 'md']:
            return jsonify({'error': 'Invalid format. Only txt and markdown are supported for session downloads'}), 400
        
        session_data = coding_sessions[session_id]
        print(f"Session data found: {session_data.keys()}")
        
        file_path = code_processor.download_session_summary(
            session_data['code_content'],
            session_data['suggestion'],
            session_data['language'],
            session_id,
            export_format,
            session_data.get('assistance_settings', {})
        )
        
        print(f"Download file path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"File not found at: {file_path}")
            return jsonify({'error': 'Download file was not created successfully'}), 500
        
        print(f"File size: {os.path.getsize(file_path)} bytes")
        filename = os.path.basename(file_path)
        print(f"Sending file: {filename}")
        
        # Set appropriate mimetype
        mimetype = 'text/markdown' if export_format in ['markdown', 'md'] else 'text/plain'
        
        return send_file(
            file_path, 
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    
    except Exception as e:
        print(f"Download session error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Update the legacy export_code_direct to redirect to new functions
@app.route('/api/export-code/<session_id>/<export_format>')
def export_code_direct(session_id, export_format):
    """Legacy export route - redirects to appropriate new route"""
    try:
        if export_format in ['txt', 'markdown', 'md']:
            # Redirect to session download
            return redirect(url_for('download_session_format', session_id=session_id, export_format=export_format))
        else:
            # This is a code-only export, handle differently
            if session_id not in coding_sessions:
                return jsonify({'error': 'Session not found'}), 404
            
            session_data = coding_sessions[session_id]
            file_path = code_processor.export_code_only(
                session_data['code_content'],
                export_format,  # Use export_format as language
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-sessions', methods=['GET'])
def get_sessions():
    """Get all coding sessions"""
    try:
        return jsonify({
            'success': True,
            'sessions': coding_sessions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a specific session"""
    try:
        if session_id in coding_sessions:
            del coding_sessions[session_id]
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get a specific session"""
    try:
        if session_id in coding_sessions:
            return jsonify({
                'success': True,
                'session': coding_sessions[session_id]
            })
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-coding-stats', methods=['GET'])
def get_coding_stats():
    """Get coding statistics"""
    try:
        total_sessions = len(coding_sessions)
        languages = [session['language'] for session in coding_sessions.values()]
        most_used_language = max(set(languages), key=languages.count) if languages else 'None'
        
        return jsonify({
            'success': True,
            'stats': {
                'total_sessions': total_sessions,
                'most_used_language': most_used_language,
                'total_lines': sum(len(session['code_content'].split('\n')) for session in coding_sessions.values())
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-completions', methods=['POST'])
def get_ai_completions():
    """Get AI-powered code completions for Monaco Editor"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        line = data.get('line', 1)
        column = data.get('column', 1)
        context = data.get('context', '')
        
        # Get the current line content for better context
        lines = code.split('\n')
        current_line = lines[line-1] if line <= len(lines) else ''
        
        # Enhanced AI completions with more context
        completions = generate_code_completions(
            code, 
            language, 
            context, 
            line, 
            column,
            current_line_content=current_line,
            previous_lines=lines[:line-1] if line > 1 else [],
            full_context=True
        )
        
        return jsonify({
            'success': True,
            'completions': completions
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'completions': []
        }), 200  # Return 200 to avoid breaking Monaco

@app.route('/api/ai-hover', methods=['POST'])
def get_ai_hover():
    """Get AI-powered hover information"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        word = data.get('word', '')
        line = data.get('line', 1)
        language = data.get('language', 'python')
        
        # Generate AI hover info
        info = generate_hover_info(code, word, language, line)
        
        return jsonify({
            'success': True,
            'info': info
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 200

@app.route('/api/explain-code', methods=['POST'])
def explain_code_snippet():
    """Explain a specific code snippet"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code.strip():
            return jsonify({'error': 'No code provided'}), 400
        
        # Generate explanation
        explanation = explain_code_functionality(code, language)
        
        return jsonify({
            'success': True,
            'explanation': explanation
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/download-session-summary/<session_id>')
def download_session_summary(session_id):
    """Download session summary with all details"""
    try:
        if session_id not in coding_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = coding_sessions[session_id]
        
        # Create comprehensive session summary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_filename = f"session_summary_{session_id}_{timestamp}.txt"
        summary_path = os.path.join(app.config['CODE_SESSIONS_FOLDER'], summary_filename)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("AI CODING ASSISTANT - SESSION SUMMARY\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Date: {session_data.get('timestamp', 'Unknown')}\n")
            f.write(f"Programming Language: {session_data.get('language', 'Unknown')}\n")
            f.write(f"Assistance Type: {session_data.get('type', 'Unknown')}\n\n")
            
            # Session configuration
            settings = session_data.get('assistance_settings', {})
            if settings:
                f.write("SESSION CONFIGURATION:\n")
                f.write("-" * 40 + "\n")
                for key, value in settings.items():
                    if value:
                        f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                f.write("\n")
            
            # Original code
            f.write("ORIGINAL CODE:\n")
            f.write("-" * 40 + "\n")
            f.write(session_data.get('code_content', 'No code available') + "\n\n")
            
            # AI response
            f.write("AI RESPONSE:\n")
            f.write("-" * 40 + "\n")
            f.write(session_data.get('suggestion', 'No suggestion available') + "\n\n")
            
            f.write("="*80 + "\n")
            f.write("Generated by AI Coding Assistant\n")
            f.write("="*80 + "\n")
        
        return send_file(
            summary_path,
            as_attachment=True,
            download_name=summary_filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-session-markdown/<session_id>')
def download_session_markdown(session_id):
    """Download session summary as markdown"""
    try:
        if session_id not in coding_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = coding_sessions[session_id]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_filename = f"session_summary_{session_id}_{timestamp}.md"
        summary_path = os.path.join(app.config['CODE_SESSIONS_FOLDER'], summary_filename)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# AI Coding Assistant - Session Summary\n\n")
            
            f.write("## Session Details\n")
            f.write(f"- **Session ID:** {session_id}\n")
            f.write(f"- **Date:** {session_data.get('timestamp', 'Unknown')}\n")
            f.write(f"- **Programming Language:** {session_data.get('language', 'Unknown')}\n")
            f.write(f"- **Assistance Type:** {session_data.get('type', 'Unknown')}\n\n")
            
            # Session configuration
            settings = session_data.get('assistance_settings', {})
            if settings:
                f.write("## Session Configuration\n")
                for key, value in settings.items():
                    if value:
                        f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
                f.write("\n")
            
            # Original code
            f.write("## Original Code\n")
            f.write(f"```{session_data.get('language', 'text')}\n")
            f.write(session_data.get('code_content', 'No code available'))
            f.write("\n```\n\n")
            
            # AI response
            f.write("## AI Response\n")
            f.write(session_data.get('suggestion', 'No suggestion available'))
            f.write("\n\n")
            
            f.write("---\n")
            f.write("*Generated by AI Coding Assistant*\n")
        
        return send_file(
            summary_path,
            as_attachment=True,
            download_name=summary_filename,
            mimetype='text/markdown'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=6922, debug=True)