from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
import os, json, shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from .models import (create_connection, create_tables, create_or_get_user, save_user_template, 
                    get_user_templates, save_directory_analysis, get_user_recent_analyses, delete_user_template)
from .services.directory_analyzer import DirectoryAnalyzer
from .services.file_parser import FileParser
from .services.template_matcher import TemplateMatcher
from .services.ai_parser import AISummarizer

main_bp = Blueprint('main', __name__)

# Database setup
db_path = os.path.join(os.path.dirname(__file__), 'static', 'directory_summariser.db')
connection = create_connection(db_path)
create_tables(connection)

# Initialize services
directory_analyzer = DirectoryAnalyzer()
file_parser = FileParser()
template_matcher = TemplateMatcher()
ai_summarizer = AISummarizer()

def login_required(f):
    """Decorator to check if user is logged in"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@main_bp.route('/')
def index():
    """Redirect to login or dashboard based on session"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login/registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        
        if not username or not email:
            flash('Please provide both username and email.', 'error')
            return render_template('login.html')
        
        try:
            # Create or get user
            user = create_or_get_user(connection, username, email)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing directory analysis overview"""
    user_id = session['user_id']
    
    # Get user templates
    user_templates = get_user_templates(connection, user_id)
    
    # Get recent analyses for this user
    recent_summaries = get_user_recent_analyses(connection, user_id, limit=5)
    
    # Get current analysis from session
    current_analysis = session.get('current_analysis')
    
    return render_template('index.html', 
                         user_templates=user_templates,
                         recent_summaries=recent_summaries,
                         current_analysis=current_analysis)

@main_bp.route('/analyze_directory', methods=['POST'])
@login_required
def analyze_directory():
    """Analyze a directory and generate comprehensive summary"""
    directory_path = request.form.get('directory_path', '').strip()
    user_id = session['user_id']
    
    if not directory_path:
        flash('Please provide a valid directory path.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        flash('Directory path does not exist or is not accessible.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Analyze directory structure
        analysis_result = directory_analyzer.analyze_directory(directory_path)
        
        # Parse files for content analysis
        content_analysis = file_parser.analyze_directory_content(directory_path)
        
        # Generate AI summary
        ai_insights = ai_summarizer.generate_directory_insights(analysis_result, content_analysis)
        
        # Prepare analysis data
        analysis_data = {
            'directory_path': directory_path,
            'total_files': analysis_result.get('total_files', 0),
            'total_size': analysis_result.get('total_size', 0),
            'file_type_categories': analysis_result.get('file_type_categories', {}),
            'ai_insights': ai_insights,
            'content_analysis': content_analysis
        }
        
        # Save to database
        analysis_id = save_directory_analysis(connection, user_id, directory_path, analysis_data)
        
        # Store in session
        session['current_analysis'] = analysis_data
        session['current_analysis']['id'] = analysis_id
        
        flash(f'Successfully analyzed directory: {directory_path}', 'success')
        return redirect(url_for('main.view_analysis'))
        
    except Exception as e:
        flash(f'Error analyzing directory: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/view_analysis')
@login_required
def view_analysis():
    """Display detailed analysis results"""
    if 'current_analysis' not in session:
        flash('No analysis data available. Please analyze a directory first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    analysis_data = session['current_analysis']
    template_matches = session.get('template_matches', [])
    
    return render_template('results.html', 
                         analysis=analysis_data,
                         template_matches=template_matches)

@main_bp.route('/templates', methods=['GET'])
@login_required
def templates():
    """Template management page"""
    user_id = session['user_id']
    user_templates = get_user_templates(connection, user_id)
    current_analysis = session.get('current_analysis')
    
    return render_template('templates.html',
                         user_templates=user_templates,
                         current_analysis=current_analysis)

@main_bp.route('/upload_templates', methods=['POST'])
@login_required
def upload_templates():
    """Handle template file uploads for similarity matching"""
    uploaded_files = request.files.getlist('template_files')
    template_category = request.form.get('category', 'General')
    user_id = session['user_id']
    
    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
        flash('Please select at least one template file.', 'error')
        return redirect(url_for('main.templates'))
    
    try:
        upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'user_templates', str(user_id))
        os.makedirs(upload_folder, exist_ok=True)
        
        uploaded_count = 0
        for file in uploaded_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                # Read file content for database storage
                with open(filepath, 'rb') as f:
                    file_content = f.read()
                
                # Save to database
                save_user_template(connection, user_id, template_category, filename, file_content)
                uploaded_count += 1
        
        flash(f'Successfully uploaded {uploaded_count} template files in category "{template_category}".', 'success')
        
    except Exception as e:
        flash(f'Error uploading templates: {str(e)}', 'error')
    
    return redirect(url_for('main.templates'))

@main_bp.route('/delete_template/<int:template_id>', methods=['POST'])
@login_required
def delete_template(template_id):
    """Delete a user template"""
    user_id = session['user_id']
    
    try:
        if delete_user_template(connection, template_id, user_id):
            flash('Template deleted successfully.', 'success')
        else:
            flash('Template not found or access denied.', 'error')
    except Exception as e:
        flash(f'Error deleting template: {str(e)}', 'error')
    
    return redirect(url_for('main.templates'))

@main_bp.route('/template_matching', methods=['POST'])
@login_required
def template_matching():
    """Perform template matching against directory contents"""
    if 'current_analysis' not in session:
        flash('Please analyze a directory first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user_id = session['user_id']
    user_templates = get_user_templates(connection, user_id)
    
    if not user_templates:
        flash('Please upload template files first.', 'error')
        return redirect(url_for('main.templates'))
    
    try:
        analysis_data = session['current_analysis']
        directory_path = analysis_data['directory_path']
        
        # Prepare templates for matching
        templates = []
        for template in user_templates:
            templates.append({
                'category': template[1],  # category
                'filename': template[2],  # filename
                'id': template[0]         # template id
            })
        
        # Perform template matching
        matching_results = template_matcher.find_similar_files(directory_path, templates)
        
        # Store results in session
        session['template_matches'] = matching_results
        
        flash(f'Template matching completed. Found matches across {len(matching_results)} categories.', 'success')
        return redirect(url_for('main.view_analysis'))
        
    except Exception as e:
        flash(f'Error performing template matching: {str(e)}', 'error')
        return redirect(url_for('main.templates'))

@main_bp.route('/export_analysis/<format>')
@login_required
def export_analysis(format):
    """Export analysis results in different formats"""
    if 'current_analysis' not in session:
        flash('No analysis data to export.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        analysis_data = session['current_analysis']
        
        if format == 'json':
            response = make_response(json.dumps(analysis_data, indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=directory_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            return response
            
        elif format == 'csv':
            # Generate CSV export
            csv_content = file_parser.export_to_csv(analysis_data)
            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=directory_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            return response
            
        else:
            flash('Unsupported export format.', 'error')
            return redirect(url_for('main.view_analysis'))
            
    except Exception as e:
        flash(f'Error exporting analysis: {str(e)}', 'error')
        return redirect(url_for('main.view_analysis'))

@main_bp.route('/batch_analyze', methods=['POST'])
@login_required
def batch_analyze():
    """Analyze multiple directories in batch"""
    directory_paths = request.form.get('directory_paths', '').strip()
    user_id = session['user_id']
    
    if not directory_paths:
        flash('Please provide directory paths (one per line).', 'error')
        return redirect(url_for('main.dashboard'))
    
    paths = [path.strip() for path in directory_paths.split('\n') if path.strip()]
    
    try:
        batch_results = []
        for path in paths:
            if os.path.exists(path) and os.path.isdir(path):
                analysis_result = directory_analyzer.analyze_directory(path)
                content_analysis = file_parser.analyze_directory_content(path)
                
                # Save individual analysis
                analysis_data = {
                    'directory_path': path,
                    'total_files': analysis_result.get('total_files', 0),
                    'total_size': analysis_result.get('total_size', 0),
                    'file_type_categories': analysis_result.get('file_type_categories', {}),
                    'content_analysis': content_analysis
                }
                
                save_directory_analysis(connection, user_id, path, analysis_data)
                
                batch_results.append({
                    'path': path,
                    'analysis': analysis_result,
                    'content': content_analysis
                })
            else:
                batch_results.append({
                    'path': path,
                    'error': 'Directory not found or inaccessible'
                })
        
        session['batch_results'] = batch_results
        flash(f'Batch analysis completed for {len(batch_results)} directories.', 'success')
        return render_template('batch_results.html', results=batch_results)
        
    except Exception as e:
        flash(f'Error in batch analysis: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/api/directory_stats/<path:directory_path>')
@login_required
def get_directory_stats(directory_path):
    """API endpoint to get quick directory statistics"""
    try:
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return jsonify({'error': 'Directory not found'}), 404
        
        stats = directory_analyzer.get_quick_stats(directory_path)
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/clear_session')
@login_required
def clear_session():
    """Clear current analysis session"""
    session.pop('current_analysis', None)
    session.pop('template_matches', None)
    session.pop('batch_results', None)
    flash('Session cleared successfully.', 'success')
    return redirect(url_for('main.dashboard'))