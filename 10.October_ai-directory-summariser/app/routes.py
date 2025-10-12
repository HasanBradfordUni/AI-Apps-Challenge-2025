from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
import os, json, shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from .models import (create_connection, create_tables, create_or_get_user, save_user_template, 
                    get_user_templates, save_directory_analysis, get_user_recent_analyses, 
                    delete_user_template, get_analysis_with_matches)
from .services.directory_analyzer import DirectoryAnalyzer
from .services.file_parser import FileParser
from .services.template_matcher import TemplateMatcher
from .services.ai_parser import AISummarizer


def register_routes(app):
    """Register all routes with the Flask app"""
    
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
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function

    @app.route('/')
    def index():
        """Redirect to login or dashboard based on session"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login/registration"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            
            if not username or not email:
                flash('Please provide both username and email.', 'error')
                return render_template('login.html')
            
            try:
                user = create_or_get_user(connection, username, email)
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                
                flash(f'Welcome, {username}!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                flash(f'Login error: {str(e)}', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        """Handle user logout"""
        session.clear()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard showing directory analysis overview"""
        user_id = session['user_id']
        
        try:
            user_templates = get_user_templates(connection, user_id)
            recent_summaries = get_user_recent_analyses(connection, user_id, limit=5)
            current_analysis = session.get('current_analysis')
            
            return render_template('index.html', 
                                 user_templates=user_templates or [],
                                 recent_summaries=recent_summaries or [],
                                 current_analysis=current_analysis)
                                 
        except Exception as e:
            flash(f'Error loading dashboard: {str(e)}', 'error')
            return render_template('index.html', 
                                 user_templates=[],
                                 recent_summaries=[],
                                 current_analysis=None)

    @app.route('/analyze_directory', methods=['POST'])
    @login_required
    def analyze_directory():
        """Analyze a directory and generate comprehensive summary"""
        directory_path = request.form.get('directory_path', '').strip()
        user_id = session['user_id']
        
        if not directory_path:
            flash('Please provide a valid directory path.', 'error')
            return redirect(url_for('dashboard'))
        
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            flash('Directory path does not exist or is not accessible.', 'error')
            return redirect(url_for('dashboard'))
        
        try:
            analysis_result = directory_analyzer.analyze_directory(directory_path)
            content_analysis = file_parser.analyze_directory_content(directory_path)
            ai_insights = ai_summarizer.generate_directory_insights(analysis_result, content_analysis)
            
            analysis_data = {
                'directory_path': directory_path,
                'total_files': analysis_result.get('total_files', 0),
                'total_size': analysis_result.get('total_size', 0),
                'file_type_categories': analysis_result.get('file_type_categories', {}),
                'ai_insights': ai_insights,
                'content_analysis': content_analysis
            }
            
            analysis_id = save_directory_analysis(connection, user_id, directory_path, analysis_data)
            
            session['current_analysis'] = {
                'id': analysis_id,
                'directory_path': directory_path,
                'total_files': analysis_data['total_files'],
                'total_size': analysis_data['total_size']
            }
            
            flash(f'Successfully analyzed directory: {directory_path}', 'success')
            return redirect(url_for('view_analysis'))
            
        except Exception as e:
            flash(f'Error analyzing directory: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/view_analysis')
    @login_required
    def view_analysis():
        """Display detailed analysis results"""
        if 'current_analysis' not in session:
            flash('No analysis data available. Please analyze a directory first.', 'error')
            return redirect(url_for('dashboard'))
        
        analysis_id = session['current_analysis']['id']
        user_id = session['user_id']
        
        try:
            analysis_data = get_analysis_with_matches(connection, analysis_id, user_id)
            
            if not analysis_data:
                flash('Analysis data not found.', 'error')
                return redirect(url_for('dashboard'))
            
            template_matches = session.get('template_matches', [])
            
            return render_template('results.html', 
                                 analysis=analysis_data,
                                 template_matches=template_matches)
                                 
        except Exception as e:
            flash(f'Error loading analysis: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/templates')
    @login_required
    def templates():
        """Template management page"""
        user_id = session['user_id']
        user_templates = get_user_templates(connection, user_id)
        current_analysis = session.get('current_analysis')
        
        return render_template('templates.html',
                             user_templates=user_templates,
                             current_analysis=current_analysis)

    @app.route('/upload_templates', methods=['POST'])
    @login_required
    def upload_templates():
        """Handle template file uploads"""
        uploaded_files = request.files.getlist('template_files')
        template_category = request.form.get('category', 'General')
        user_id = session['user_id']
        
        if not uploaded_files or all(f.filename == '' for f in uploaded_files):
            flash('Please select at least one template file.', 'error')
            return redirect(url_for('templates'))
        
        try:
            upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'user_templates', str(user_id))
            os.makedirs(upload_folder, exist_ok=True)
            
            uploaded_count = 0
            for file in uploaded_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    
                    with open(filepath, 'rb') as f:
                        file_content = f.read()
                    
                    save_user_template(connection, user_id, template_category, filename, file_content)
                    uploaded_count += 1
            
            flash(f'Successfully uploaded {uploaded_count} template files in category "{template_category}".', 'success')
            
        except Exception as e:
            flash(f'Error uploading templates: {str(e)}', 'error')
        
        return redirect(url_for('templates'))

    @app.route('/delete_template/<int:template_id>', methods=['POST'])
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
        
        return redirect(url_for('templates'))

    @app.route('/export_analysis/<format>')
    @login_required
    def export_analysis(format):
        """Export analysis results"""
        if 'current_analysis' not in session:
            flash('No analysis data to export.', 'error')
            return redirect(url_for('dashboard'))
        
        try:
            analysis_id = session['current_analysis']['id']
            user_id = session['user_id']
            analysis_data = get_analysis_with_matches(connection, analysis_id, user_id)
            
            if format == 'json':
                response = make_response(json.dumps(analysis_data, indent=2))
                response.headers['Content-Type'] = 'application/json'
                response.headers['Content-Disposition'] = f'attachment; filename=directory_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                return response
                
            else:
                flash('Unsupported export format.', 'error')
                return redirect(url_for('view_analysis'))
                
        except Exception as e:
            flash(f'Error exporting analysis: {str(e)}', 'error')
            return redirect(url_for('view_analysis'))