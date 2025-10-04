from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
import os, json, shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from .models import (create_connection, create_summary_tables, save_directory_summary, 
                    get_recent_summaries, save_template_match, get_template_matches)
from .services.directory_analyzer import DirectoryAnalyzer
from .services.file_parser import FileParser
from .services.template_matcher import TemplateMatcher
from .services.ai_parser import AISummarizer

main_bp = Blueprint('main', __name__)

# Database setup
db_path = os.path.join(os.path.dirname(__file__), 'static', 'directory_summaries.db')
connection = create_connection(db_path)
create_summary_tables(connection)

# Initialize services
directory_analyzer = DirectoryAnalyzer()
file_parser = FileParser()
template_matcher = TemplateMatcher()
ai_summarizer = AISummarizer()

@main_bp.route('/')
def dashboard():
    """Main dashboard showing directory analysis overview"""
    # Get recent summaries
    recent_summaries = get_recent_summaries(connection, limit=5)
    
    return render_template('index.html', recent_summaries=recent_summaries)

@main_bp.route('/analyze_directory', methods=['POST'])
def analyze_directory():
    """Analyze a directory and generate comprehensive summary"""
    directory_path = request.form.get('directory_path', '').strip()
    
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
        
        # Save to database
        summary_id = save_directory_summary(connection, {
            'directory_path': directory_path,
            'analysis_result': analysis_result,
            'content_analysis': content_analysis,
            'ai_insights': ai_insights,
            'analyzed_at': datetime.now()
        })
        
        session['current_analysis'] = {
            'summary_id': summary_id,
            'directory_path': directory_path,
            'analysis_result': analysis_result,
            'content_analysis': content_analysis,
            'ai_insights': ai_insights
        }
        
        flash(f'Successfully analyzed directory: {directory_path}', 'success')
        return redirect(url_for('main.view_analysis'))
        
    except Exception as e:
        flash(f'Error analyzing directory: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/view_analysis')
def view_analysis():
    """Display detailed analysis results"""
    if 'current_analysis' not in session:
        flash('No analysis data available. Please analyze a directory first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    analysis_data = session['current_analysis']
    return render_template('analysis_results.html', analysis=analysis_data)

@main_bp.route('/upload_templates', methods=['GET', 'POST'])
def upload_templates():
    """Handle template file uploads for similarity matching"""
    if request.method == 'POST':
        uploaded_files = request.files.getlist('template_files')
        template_category = request.form.get('template_category', 'General')
        
        if not uploaded_files or all(f.filename == '' for f in uploaded_files):
            flash('Please select at least one template file.', 'error')
            return redirect(url_for('main.upload_templates'))
        
        try:
            template_paths = []
            upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'templates')
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in uploaded_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    template_paths.append(filepath)
            
            # Store template information in session for matching
            if 'templates' not in session:
                session['templates'] = []
            
            session['templates'].extend([{
                'path': path,
                'category': template_category,
                'filename': os.path.basename(path)
            } for path in template_paths])
            
            flash(f'Successfully uploaded {len(template_paths)} template files in category "{template_category}".', 'success')
            
        except Exception as e:
            flash(f'Error uploading templates: {str(e)}', 'error')
    
    return render_template('upload_templates.html')

@main_bp.route('/template_matching', methods=['POST'])
def template_matching():
    """Perform template matching against directory contents"""
    if 'current_analysis' not in session:
        flash('Please analyze a directory first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if 'templates' not in session or not session['templates']:
        flash('Please upload template files first.', 'error')
        return redirect(url_for('main.upload_templates'))
    
    try:
        analysis_data = session['current_analysis']
        directory_path = analysis_data['directory_path']
        templates = session['templates']
        
        # Perform template matching
        matching_results = template_matcher.find_similar_files(directory_path, templates)
        
        # Save template matching results
        for result in matching_results:
            save_template_match(connection, {
                'summary_id': analysis_data['summary_id'],
                'template_category': result['category'],
                'template_file': result['template_file'],
                'matched_files': result['matched_files'],
                'similarity_scores': result['similarity_scores'],
                'match_count': len(result['matched_files'])
            })
        
        # Update session with matching results
        session['current_analysis']['template_matches'] = matching_results
        
        flash(f'Template matching completed. Found matches across {len(matching_results)} categories.', 'success')
        return redirect(url_for('main.view_analysis'))
        
    except Exception as e:
        flash(f'Error performing template matching: {str(e)}', 'error')
        return redirect(url_for('main.upload_templates'))

@main_bp.route('/api/directory_stats/<path:directory_path>')
def get_directory_stats(directory_path):
    """API endpoint to get quick directory statistics"""
    try:
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return jsonify({'error': 'Directory not found'}), 404
        
        stats = directory_analyzer.get_quick_stats(directory_path)
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/export_analysis/<format>')
def export_analysis(format):
    """Export analysis results in different formats"""
    if 'current_analysis' not in session:
        flash('No analysis data to export.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        analysis_data = session['current_analysis']
        
        if format == 'json':
            return jsonify(analysis_data)
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

@main_bp.route('/clear_session')
def clear_session():
    """Clear current analysis session"""
    session.pop('current_analysis', None)
    session.pop('templates', None)
    flash('Session cleared successfully.', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/recent_analysis/<int:summary_id>')
def load_recent_analysis(summary_id):
    """Load a previous analysis from database"""
    try:
        # This would load from database - simplified for now
        flash('Loading previous analysis...', 'info')
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        flash(f'Error loading analysis: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/batch_analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple directories in batch"""
    directory_paths = request.form.get('directory_paths', '').strip()
    
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