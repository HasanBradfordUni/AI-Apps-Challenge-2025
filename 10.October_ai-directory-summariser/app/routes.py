from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
import os, json, shutil
from datetime import datetime
from werkzeug.utils import secure_filename

# Import database functions
from .models import (create_connection, create_tables, create_or_get_user, save_user_template, 
                    get_user_templates, save_directory_analysis, get_user_recent_analyses, 
                    delete_user_template, get_analysis_with_matches)

# Import service classes
from .services.directory_analyzer import DirectoryAnalyzer
from .services.file_parser import FileParser
from .services.template_matcher import TemplateMatcher
from .services.ai_parser import AISummarizer

# Import logger from common setup
try:
    from .utils.logger_setup import general_logger
except ImportError:
    print("Logger import failed, using DummyLogger")
    # Fallback if logger is not available
    class DummyLogger:
        def __init__(self, filename): 
            self.file = open(filename, 'a')
            self.file.write("Logging started...\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\n")
            self.file.close()
        def addToLogs(self, msg): print(f"[LOG] {msg}")
        def addToErrorLogs(self, msg): print(f"[ERROR] {msg}")
        def addToInputLogs(self, prompt, msg): print(f"[INPUT] {prompt}: {msg}")
    general_logger = DummyLogger

def register_routes(app):
    """Register all routes with the Flask app"""
    
    # Initialize logger
    log_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'app_logs.txt')
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logger = general_logger(log_file_path)
    
    logger.addToLogs("Flask application starting - routes registration beginning")
    
    # Database setup
    db_path = os.path.join(os.path.dirname(__file__), 'static', 'directory_summariser.db')
    connection = create_connection(db_path)
    create_tables(connection)
    
    logger.addToLogs(f"Database initialized at: {db_path}")

    # Initialize services
    try:
        directory_analyzer = DirectoryAnalyzer()
        file_parser = FileParser()
        template_matcher = TemplateMatcher()
        ai_summarizer = AISummarizer()
        logger.addToLogs("All services initialized successfully")
    except Exception as e:
        logger.addToErrorLogs(f"Failed to initialize services: {str(e)}")
        raise

    def login_required(f):
        """Decorator to check if user is logged in"""
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                logger.addToLogs(f"Unauthorized access attempt to {f.__name__}")
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function

    @app.route('/')
    def index():
        """Redirect to login or dashboard based on session"""
        if 'user_id' in session:
            logger.addToLogs(f"User {session['user_id']} accessed dashboard via root")
            return redirect(url_for('dashboard'))
        logger.addToLogs("Anonymous user redirected to login")
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login/registration"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            
            logger.addToInputLogs("Login attempt", f"Username: {username}, Email: {email}")
            
            if not username or not email:
                logger.addToErrorLogs("Login failed: Missing credentials")
                flash('Please provide both username and email.', 'error')
                return render_template('login.html')
            
            try:
                user = create_or_get_user(connection, username, email)
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                
                logger.addToLogs(f"Successful login for user {user['id']} - {username}")
                flash(f'Welcome, {username}!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                logger.addToErrorLogs(f"Login error for user {username}: {str(e)}")
                flash(f'Login error: {str(e)}', 'error')
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        """Handle user logout"""
        user_id = session.get('user_id', 'unknown')
        logger.addToLogs(f"User {user_id} logged out")
        session.clear()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard showing directory analysis overview"""
        user_id = session['user_id']
        logger.addToLogs(f"User {user_id} accessed dashboard")
        
        try:
            user_templates = get_user_templates(connection, user_id)
            recent_summaries = get_user_recent_analyses(connection, user_id, limit=5)
            current_analysis = session.get('current_analysis')
            
            logger.addToLogs(f"Dashboard loaded for user {user_id}: {len(user_templates or [])} templates, {len(recent_summaries or [])} recent analyses")
            
            return render_template('index.html', 
                                 user_templates=user_templates or [],
                                 recent_summaries=recent_summaries or [],
                                 current_analysis=current_analysis)
                                 
        except Exception as e:
            logger.addToErrorLogs(f"Dashboard error for user {user_id}: {str(e)}")
            flash(f'Error loading dashboard: {str(e)}', 'error')
            return render_template('index.html', 
                                 user_templates=[],
                                 recent_summaries=[],
                                 current_analysis=None)

    @app.route('/analyze_directory', methods=['POST', 'GET'])
    @login_required
    def analyze_directory():
        """Analyze a directory and generate comprehensive summary"""
        directory_path = request.form.get('directory_path', '').strip()
        user_id = session['user_id']
        
        logger.addToInputLogs("Directory analysis request", f"User: {user_id}, Path: {directory_path}")
        print(f"Received analysis request for path: {directory_path} from user {user_id}")
        
        if not directory_path:
            logger.addToErrorLogs("Analysis failed: No directory path provided")
            print(f"Analysis failed: No directory path provided for user {user_id}")
            flash('Please provide a valid directory path.', 'error')
            return redirect(url_for('dashboard'))
        
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            logger.addToErrorLogs(f"Analysis failed: Invalid path - exists: {os.path.exists(directory_path)}, is_dir: {os.path.isdir(directory_path) if os.path.exists(directory_path) else 'N/A'}")
            print(f"Analysis failed: Invalid path provided - {directory_path} for user {user_id}")
            flash('Directory path does not exist or is not accessible.', 'error')
            return redirect(url_for('dashboard'))
        
        try:
            logger.addToLogs("Starting directory structure analysis")
            print(f"Starting directory structure analysis for user {user_id}")
            
            # Use the services that are already initialized in the outer scope
            # No need to check locals() or reinitialize
            
            # Directory analysis
            try:
                print(f"Calling directory_analyzer.analyze_directory for path: {directory_path}")
                analysis_result = directory_analyzer.analyze_directory(directory_path)
                total_files = analysis_result.get('total_files', 0)
                total_size = analysis_result.get('total_size', 0)
                logger.addToLogs(f"Directory analysis complete - found {total_files} files, {total_size} bytes")
                print(f"Directory analysis successful: {total_files} files, {total_size} bytes")
            except Exception as analysis_error:
                logger.addToErrorLogs(f"Directory analysis failed: {str(analysis_error)}")
                print(f"Directory analysis error: {str(analysis_error)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                flash(f'Analysis error: Failed to analyze directory structure. {str(analysis_error)}', 'error')
                return redirect(url_for('dashboard'))
            
            # Content analysis
            try:
                logger.addToLogs("Starting content analysis")
                print("Starting content analysis")
                content_analysis = file_parser.analyze_directory_content(directory_path)
                supported_files = content_analysis.get('supported_files', 0)
                logger.addToLogs(f"Content analysis complete - {supported_files} supported files")
                print(f"Content analysis successful: {supported_files} supported files")
            except Exception as content_error:
                logger.addToErrorLogs(f"Content analysis failed: {str(content_error)}")
                print(f"Content analysis error: {str(content_error)}")
                flash(f'Content analysis error: {str(content_error)}', 'error')
                # Continue with partial analysis
                content_analysis = {'supported_files': 0, 'error': str(content_error)}
            
            # AI insights
            try:
                logger.addToLogs("Generating AI insights")
                print("Starting AI insights generation")
                ai_insights = ai_summarizer.generate_directory_insights(analysis_result, content_analysis)
                logger.addToLogs(f"AI insights generated: {len(ai_insights)} characters")
                print(f"AI insights successful: {len(ai_insights)} characters")
            except Exception as ai_error:
                logger.addToErrorLogs(f"AI insights generation failed: {str(ai_error)}")
                print(f"AI insights error: {str(ai_error)}")
                ai_insights = f"AI analysis unavailable: {str(ai_error)}"
            
            analysis_data = {
                'directory_path': directory_path,
                'total_files': total_files,
                'total_size': total_size,
                'file_type_categories': analysis_result.get('file_type_categories', {}),
                'ai_insights': ai_insights,
                'content_analysis': content_analysis
            }
            
            # Save to database
            try:
                logger.addToLogs("Saving analysis to database")
                print("Saving to database")
                analysis_id = save_directory_analysis(connection, user_id, directory_path, analysis_data)
                logger.addToLogs(f"Analysis saved with ID: {analysis_id}")
                print(f"Database save successful: ID {analysis_id}")
            except Exception as db_error:
                logger.addToErrorLogs(f"Database save failed: {str(db_error)}")
                print(f"Database save error: {str(db_error)}")
                flash(f'Warning: Analysis completed but failed to save to database. {str(db_error)}', 'warning')
                # Continue without saving
                analysis_id = None
            
            session['current_analysis'] = {
                'id': analysis_id,
                'directory_path': directory_path,
                'total_files': total_files,
                'total_size': total_size,
                'file_type_categories': analysis_data['file_type_categories'],
                'ai_insights': ai_insights
            }
            
            logger.addToLogs(f"Analysis complete for user {user_id}, path: {directory_path}")
            print(f"Analysis complete for user {user_id}")
            flash(f'Successfully analyzed directory: {directory_path}', 'success')
            return redirect(url_for('view_analysis'))
            
        except Exception as e:
            logger.addToErrorLogs(f"Analysis failed for user {user_id}: {str(e)}")
            print(f"General analysis error: {str(e)}")
            import traceback
            logger.addToErrorLogs(f"Full traceback: {traceback.format_exc()}")
            print(f"Full traceback: {traceback.format_exc()}")
            flash(f'Error analyzing directory: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/view_analysis')
    @login_required
    def view_analysis():
        """Display detailed analysis results"""
        user_id = session['user_id']
        
        if 'current_analysis' not in session:
            logger.addToLogs(f"User {user_id} tried to view analysis without data")
            flash('No analysis data available. Please analyze a directory first.', 'error')
            return redirect(url_for('dashboard'))
        
        analysis_id = session['current_analysis']['id']
        
        try:
            analysis_data = get_analysis_with_matches(connection, analysis_id, user_id)
            
            if not analysis_data:
                logger.addToErrorLogs(f"Analysis data not found for user {user_id}, analysis ID: {analysis_id}")
                flash('Analysis data not found.', 'error')
                return redirect(url_for('dashboard'))
            
            template_matches = session.get('template_matches', [])
            logger.addToLogs(f"User {user_id} viewed analysis results for analysis ID: {analysis_id}")
            
            return render_template('results.html', 
                                 analysis=analysis_data,
                                 template_matches=template_matches)
                                 
        except Exception as e:
            logger.addToErrorLogs(f"Error loading analysis view for user {user_id}: {str(e)}")
            flash(f'Error loading analysis: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/templates')
    @login_required
    def templates():
        """Template management page"""
        user_id = session['user_id']
        logger.addToLogs(f"User {user_id} accessed templates page")
        
        try:
            user_templates = get_user_templates(connection, user_id)
            current_analysis = session.get('current_analysis')
            logger.addToLogs(f"Templates page loaded for user {user_id}: {len(user_templates or [])} templates")
            
            return render_template('templates.html',
                                 user_templates=user_templates,
                                 current_analysis=current_analysis)
        except Exception as e:
            logger.addToErrorLogs(f"Error loading templates for user {user_id}: {str(e)}")
            flash(f'Error loading templates: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/upload_templates', methods=['POST'])
    @login_required
    def upload_templates():
        """Handle template file uploads"""
        uploaded_files = request.files.getlist('template_files')
        template_category = request.form.get('category', 'General')
        user_id = session['user_id']
        
        logger.addToInputLogs("Template upload", f"User: {user_id}, Category: {template_category}, Files: {len(uploaded_files)}")
        
        if not uploaded_files or all(f.filename == '' for f in uploaded_files):
            logger.addToErrorLogs(f"Template upload failed for user {user_id}: No files selected")
            flash('Please select at least one template file.', 'error')
            return redirect(url_for('templates'))
        
        try:
            upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'user_templates', str(user_id))
            os.makedirs(upload_folder, exist_ok=True)
            
            uploaded_count = 0
            total_size = 0
            
            for file in uploaded_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    
                    file_size = os.path.getsize(filepath)
                    total_size += file_size
                    
                    with open(filepath, 'rb') as f:
                        file_content = f.read()
                    
                    save_user_template(connection, user_id, template_category, filename, file_content)
                    uploaded_count += 1
                    logger.addToLogs(f"Template uploaded: {filename} ({file_size} bytes)")
            
            logger.addToLogs(f"Template upload successful for user {user_id}: {uploaded_count} files, {total_size} total bytes in category '{template_category}'")
            flash(f'Successfully uploaded {uploaded_count} template files in category "{template_category}".', 'success')
            
        except Exception as e:
            logger.addToErrorLogs(f"Template upload error for user {user_id}: {str(e)}")
            flash(f'Error uploading templates: {str(e)}', 'error')
        
        return redirect(url_for('templates'))

    @app.route('/delete_template/<int:template_id>', methods=['POST'])
    @login_required
    def delete_template(template_id):
        """Delete a user template"""
        user_id = session['user_id']
        logger.addToLogs(f"User {user_id} attempting to delete template {template_id}")
        
        try:
            if delete_user_template(connection, template_id, user_id):
                logger.addToLogs(f"Template {template_id} deleted successfully by user {user_id}")
                flash('Template deleted successfully.', 'success')
            else:
                logger.addToErrorLogs(f"Template deletion failed for user {user_id}: Template {template_id} not found or access denied")
                flash('Template not found or access denied.', 'error')
        except Exception as e:
            logger.addToErrorLogs(f"Template deletion error for user {user_id}, template {template_id}: {str(e)}")
            flash(f'Error deleting template: {str(e)}', 'error')
        
        return redirect(url_for('templates'))

    @app.route('/export_analysis/<format>')
    @login_required
    def export_analysis(format):
        """Export analysis results"""
        user_id = session['user_id']
        
        if 'current_analysis' not in session:
            logger.addToErrorLogs(f"User {user_id} tried to export without analysis data")
            flash('No analysis data to export.', 'error')
            return redirect(url_for('dashboard'))
        
        try:
            analysis_id = session['current_analysis']['id']
            analysis_data = get_analysis_with_matches(connection, analysis_id, user_id)
            
            if format == 'json':
                filename = f'directory_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                response = make_response(json.dumps(analysis_data, indent=2))
                response.headers['Content-Type'] = 'application/json'
                response.headers['Content-Disposition'] = f'attachment; filename={filename}'
                
                logger.addToLogs(f"Analysis exported by user {user_id}: Format {format}, Analysis ID: {analysis_id}, File: {filename}")
                return response
                
            else:
                logger.addToErrorLogs(f"User {user_id} requested unsupported export format: {format}")
                flash('Unsupported export format.', 'error')
                return redirect(url_for('view_analysis'))
                
        except Exception as e:
            logger.addToErrorLogs(f"Export error for user {user_id}: {str(e)}")
            flash(f'Error exporting analysis: {str(e)}', 'error')
            return redirect(url_for('view_analysis'))

    @app.route('/logs')
    @login_required
    def logs_page():
        """Logs search and management page"""
        user_id = session['user_id']
        logger.addToLogs(f"User {user_id} accessed logs page")
        
        # Get available log files
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        available_logs = []
        
        if os.path.exists(logs_dir):
            for file in os.listdir(logs_dir):
                if file.endswith('.txt'):
                    file_path = os.path.join(logs_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    available_logs.append({
                        'filename': file,
                        'filepath': file_path,
                        'size': file_size,
                        'modified': file_modified.strftime('%Y-%m-%d %H:%M:%S'),
                        'size_formatted': f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
                    })
        
        # Sort by modification time (newest first)
        available_logs.sort(key=lambda x: x['modified'], reverse=True)
        
        logger.addToLogs(f"Logs page loaded with {len(available_logs)} log files")
        
        return render_template('logs.html', available_logs=available_logs)

    @app.route('/search_logs', methods=['POST'])
    @login_required
    def search_logs():
        """Search through log files using autoLogger functionality"""
        user_id = session['user_id']
        
        search_term = request.form.get('search_term', '').strip()
        log_type = request.form.get('log_type', 'all')  # all, output, error, input
        log_file = request.form.get('log_file', '')
        narrow_search = request.form.get('narrow_search', '').strip()
        
        logger.addToInputLogs("Log search", f"User: {user_id}, Term: '{search_term}', Type: {log_type}, File: {log_file}")
        
        if not search_term:
            flash('Please enter a search term.', 'error')
            return redirect(url_for('logs_page'))
        
        if not log_file:
            flash('Please select a log file to search.', 'error')
            return redirect(url_for('logs_page'))
        
        try:
            # Initialize logger for the selected file
            log_file_path = os.path.join(os.path.dirname(__file__), 'logs', log_file)
            
            if not os.path.exists(log_file_path):
                flash('Selected log file does not exist.', 'error')
                return redirect(url_for('logs_page'))
            
            search_logger = general_logger(log_file_path)
            results = []
            
            # Perform search based on log type
            if log_type == 'output':
                results = search_logger.searchForLogs(search_term)
            elif log_type == 'error':
                results = search_logger.searchForErrors(search_term)
            elif log_type == 'input':
                results = search_logger.searchForInputs(search_term)
            else:  # all types
                # Search all types and combine results
                output_results = search_logger.searchForLogs(search_term)
                error_results = search_logger.searchForErrors(search_term)
                input_results = search_logger.searchForInputs(search_term)
                
                results = []
                if output_results:
                    results.extend([{'type': 'Output', 'content': r} for r in output_results])
                if error_results:
                    results.extend([{'type': 'Error', 'content': r} for r in error_results])
                if input_results:
                    results.extend([{'type': 'Input', 'content': r} for r in input_results])
            
            # If narrow_search is provided, filter results further
            if narrow_search and results:
                if isinstance(results[0], dict):  # Combined results format
                    filtered_results = []
                    for result in results:
                        if narrow_search.lower() in result['content'].lower():
                            filtered_results.append(result)
                    results = filtered_results
                else:  # Single type results format
                    filtered_results = []
                    for result in results:
                        if narrow_search.lower() in result.lower():
                            filtered_results.append(result)
                    results = filtered_results
            
            # Format results for display
            if results and not isinstance(results[0], dict):
                # Convert to uniform format
                results = [{'type': log_type.title(), 'content': r} for r in results]
            
            logger.addToLogs(f"Log search completed: {len(results)} results found for '{search_term}' in {log_file}")
            
            # Store search results in session for pagination/export
            session['last_search'] = {
                'term': search_term,
                'type': log_type,
                'file': log_file,
                'results': results,
                'narrow_search': narrow_search
            }
            
            return render_template('logs.html', 
                             search_results=results,
                             search_term=search_term,
                             log_type=log_type,
                             selected_file=log_file,
                             narrow_search=narrow_search,
                             available_logs=get_available_logs())
            
        except Exception as e:
            logger.addToErrorLogs(f"Log search error for user {user_id}: {str(e)}")
            flash(f'Error searching logs: {str(e)}', 'error')
            return redirect(url_for('logs_page'))

    @app.route('/export_logs', methods=['POST'])
    @login_required
    def export_logs():
        """Export search results or entire log file"""
        user_id = session['user_id']
        export_type = request.form.get('export_type', 'results')  # results or full
        export_format = request.form.get('export_format', 'txt')  # txt or json
        
        logger.addToLogs(f"User {user_id} exporting logs: type={export_type}, format={export_format}")
        
        try:
            if export_type == 'results' and 'last_search' in session:
                # Export search results
                search_data = session['last_search']
                results = search_data['results']
                
                if export_format == 'json':
                    export_data = {
                        'search_term': search_data['term'],
                        'log_type': search_data['type'],
                        'log_file': search_data['file'],
                        'results_count': len(results),
                        'results': results,
                        'exported_at': datetime.now().isoformat()
                    }
                    
                    response = make_response(json.dumps(export_data, indent=2))
                    response.headers['Content-Type'] = 'application/json'
                    filename = f"log_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    
                else:  # txt format
                    export_content = f"Log Search Results\n"
                    export_content += f"==================\n"
                    export_content += f"Search Term: {search_data['term']}\n"
                    export_content += f"Log Type: {search_data['type']}\n"
                    export_content += f"Log File: {search_data['file']}\n"
                    export_content += f"Results Count: {len(results)}\n"
                    export_content += f"Exported At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    
                    for i, result in enumerate(results, 1):
                        export_content += f"Result {i}:\n"
                        if isinstance(result, dict):
                            export_content += f"Type: {result['type']}\n"
                            export_content += f"Content: {result['content']}\n"
                        else:
                            export_content += f"Content: {result}\n"
                        export_content += "-" * 50 + "\n"
                    
                    response = make_response(export_content)
                    response.headers['Content-Type'] = 'text/plain'
                    filename = f"log_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                response.headers['Content-Disposition'] = f'attachment; filename={filename}'
                logger.addToLogs(f"Log search results exported: {filename}")
                return response
                
            else:
                flash('No search results to export.', 'error')
                return redirect(url_for('logs_page'))
                
        except Exception as e:
            logger.addToErrorLogs(f"Log export error for user {user_id}: {str(e)}")
            flash(f'Error exporting logs: {str(e)}', 'error')
            return redirect(url_for('logs_page'))

    @app.route('/clear_logs', methods=['POST'])
    @login_required
    def clear_logs():
        """Clear selected log file (admin function)"""
        user_id = session['user_id']
        log_file = request.form.get('log_file', '')
        
        logger.addToLogs(f"User {user_id} attempting to clear log file: {log_file}")
        
        # You might want to add admin check here
        # if not is_admin(user_id):
        #     flash('Insufficient permissions.', 'error')
        #     return redirect(url_for('logs_page'))
        
        try:
            log_file_path = os.path.join(os.path.dirname(__file__), 'logs', log_file)
            
            if not os.path.exists(log_file_path):
                flash('Log file does not exist.', 'error')
                return redirect(url_for('logs_page'))
            
            # Create backup before clearing
            backup_path = f"{log_file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(log_file_path, backup_path)
            
            # Clear the log file
            clear_logger = general_logger(log_file_path)
            clear_logger.cleanLoggerFile()
            
            # Add clear log entry
            clear_logger.addToLogs(f"Log file cleared by user {user_id} at {datetime.now().isoformat()}")
            
            logger.addToLogs(f"Log file cleared successfully: {log_file} (backup created: {os.path.basename(backup_path)})")
            flash(f'Log file "{log_file}" cleared successfully. Backup created.', 'success')
            
        except Exception as e:
            logger.addToErrorLogs(f"Log clear error for user {user_id}: {str(e)}")
            flash(f'Error clearing log file: {str(e)}', 'error')
        
        return redirect(url_for('logs_page'))

    def get_available_logs():
        """Helper function to get available log files"""
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        available_logs = []
        
        if os.path.exists(logs_dir):
            for file in os.listdir(logs_dir):
                if file.endswith('.txt'):
                    file_path = os.path.join(logs_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    available_logs.append({
                        'filename': file,
                        'filepath': file_path,
                        'size': file_size,
                        'modified': file_modified.strftime('%Y-%m-%d %H:%M:%S'),
                        'size_formatted': f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"
                    })
        
        available_logs.sort(key=lambda x: x['modified'], reverse=True)
        return available_logs

    logger.addToLogs("Flask route registration completed successfully")