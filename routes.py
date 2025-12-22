from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response
import os
import sys
import json
from datetime import datetime
import sqlite3

# Import functions from previous projects
try:
    # January - General AI Doc Search
    from a_january_ai_document_search.src.utils.document_processing import handle_documents as january_handle_documents
    from a_january_ai_document_search.src.utils.search_algorithm import search_documents as january_search_documents
    from a_january_ai_document_search.src.ai.geminiPrompt import generate_ai_summary as january_generate_summary
    
    # February - AI Testing Agent  
    from b_february_ai_testing_agent.app.utils import process_files as february_process_files
    from b_february_ai_testing_agent.app.utils import generate_ai_comparison as february_generate_comparison
    from b_february_ai_testing_agent.app.utils import generate_summary as february_generate_summary
    
    # March - AI Work Hours Calculator
    from c_march_ai_work_hours_calculator.src.app import calculate_hours as march_calculate_hours
    from c_march_ai_work_hours_calculator.src.ai.geminiPrompt import generate_work_hours_summary as march_generate_summary
    
    # April - AI Document Extractor & Converter
    from d_april_ai_document_extractor.src.utils.document_processing import get_uploaded_documents as april_get_documents, handle_document_upload as april_handle_upload, process_uploaded_file as april_process_file, get_uploads_folder as april_get_uploads_folder, convert_file_format_from_file_path as april_convert_file_format
    from d_april_ai_document_extractor.src.ai.geminiPrompt import generate_conversion_insights as april_generate_insights
    
    # May - AI Cover Letter Writer
    from e_may_ai_cover_letter_writer.app.utils import extract_text_from_pdf as may_extract_text, generate_cover_letter as may_generate_letter, refine_cover_letter as may_refine_letter, extract_cv_structure as may_extract_cv_structure
    
    # June - AI Job Ad Generator
    from f_june_ai_job_ad_generator.app.utils import generate_job_ad as june_generate_ad, refine_job_ad as june_refine_ad, extract_text_from_pdf as june_extract_text, format_for_pdf as june_format_for_pdf
    
    # July - AI Speech-to-Text App
    from g_july_ai_speech_to_text_app.src.utils.voice_methods import VoiceMethods as july_voice_methods
    from g_july_ai_speech_to_text_app.src.ai.geminiPrompt import generate_transcript_summary as july_generate_transcript, generate_voice_command_response as july_generate_voice_response
    
    # August - AI Calendar & Scheduling System
    from h_august_ai_calendar_system.app.services.ai_parser import AICommandParser as august_ai_parser
    from h_august_ai_calendar_system.app.services.voice_recognition import VoiceRecognitionService as august_voice_recognition
    from h_august_ai_calendar_system.app.services.calendar_sync import GoogleCalendarService as august_google_calendar, OutlookCalendarService as august_outlook_calendar
    
    # September - General Document Summarization AI
    from i_september_ai_doc_summariser.src.utils.document_processor import DocumentProcessor as september_document_processor
    from i_september_ai_doc_summariser.src.utils.forms import DocumentSummaryForm as september_document_summary_form
    from i_september_ai_doc_summariser.src.ai.geminiPrompt import generate_document_summary as september_generate_summmary, analyze_document_content as september_analyze_content
    
    # October - Docs Directory AI Summarizer
    from j_october_ai_directory_summariser.app.services.directory_analyzer import DirectoryAnalyzer as october_directory_analyzer
    from j_october_ai_directory_summariser.app.services.file_parser import FileParser as october_file_parser
    from j_october_ai_directory_summariser.app.services.template_matcher import TemplateMatcher as october_template_matcher
    from j_october_ai_directory_summariser.app.services.ai_parser import AISummarizer as october_ai_summarizer
    
    # November - AI Programming Assistant
    from k_november_ai_coding_assistant.src.utils.code_processor import CodeProcessor as november_code_processor
    from k_november_ai_coding_assistant.src.ai.geminiPrompt import generate_code_suggestion as november_generate_suggestion, explain_error as november_explain_error, generate_documentation as november_generate_documentation, complete_code as november_complete_code, analyze_code_quality as november_analyze_code_quality, generate_test_cases as november_generate_test_cases, generate_code_completions as november_generate_code_completions, generate_hover_info as november_generate_hover_info, explain_code_functionality as november_explain_code_functionality
    
    print("Successfully imported all project functions")
    
except ImportError as e:
    print(f"Warning: Could not import some project functions: {e}")

# Import from December chatbot modules
try:
    from l_december_ai_chatbot.prompt_modes import PromptModeManager
    from l_december_ai_chatbot.ai_parser import AIIntegrationService

    # Initialize services
    prompt_manager = PromptModeManager()
    ai_service = AIIntegrationService()
except ImportError as e:
    print(f"Warning: December chatbot modules not available: {e}")
    # Create fallback classes
    class FallbackManager:
        def get_modes(self): return {}
        def get_mode(self, mode): return {'name': 'General', 'system_prompt': 'You are a helpful AI assistant.'}
    
    prompt_manager = FallbackManager()
    ai_service = None
    chatbot_engine = None

def register_routes(app):
    """Register all chatbot routes"""
    
    @app.route('/')
    def chatbot_home():
        """Main chatbot interface"""
        available_apps = get_available_apps()
        return render_template('index.html', 
                             available_apps=available_apps,
                             prompt_modes=prompt_manager.get_modes())
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """Handle chat messages"""
        user_message = request.json.get('message', '').strip()
        prompt_mode = request.json.get('mode', 'general')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        try:
            # Process message through chatbot engine
            if chatbot_engine:
                response = chatbot_engine.process_message(
                    user_message, 
                    prompt_mode,
                    session.get('user_id')
                )
            else:
                response = {
                    'response': 'Chatbot engine not available. Please check the setup.',
                    'mode': prompt_mode,
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
            
            # Check if message should route to specific app
            app_suggestion = detect_app_intent(user_message)
            if app_suggestion:
                response['app_suggestion'] = app_suggestion
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({'error': f'Chat processing failed: {str(e)}'}), 500
    
    # Direct app integration routes
    @app.route('/api/search-documents', methods=['POST'])
    def api_search_documents():
        """Direct integration with January project"""
        try:
            query = request.json.get('query', '')
            directory = request.json.get('directory', 'default')
            
            if not query:
                return jsonify({'error': 'No search query provided'}), 400
            
            # Use January project functions
            documents = january_handle_documents(directory)
            results = january_search_documents(query, documents)
            ai_summary = january_generate_summary(query, results, documents)
            
            return jsonify({
                'results': results, 
                'ai_summary': ai_summary,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/run-test', methods=['POST'])
    def api_run_test():
        """Direct integration with February project"""
        try:
            project_name = request.json.get('project_name', 'Test Project')
            test_query = request.json.get('test_query', '')
            expected_results = request.json.get('expected_results', '')
            actual_results = request.json.get('actual_results', '')
            project_description = request.json.get('project_description', '')
            context = request.json.get('context', '')
            
            if not test_query:
                return jsonify({'error': 'No test query provided'}), 400
            
            # Process files and generate comparison
            comparison_result = february_generate_comparison(
                project_name, test_query, expected_results, 
                actual_results, project_description, context
            )
            evaluation_summary = february_generate_summary(
                comparison_result, project_name, test_query, 
                project_description, context
            )
            
            return jsonify({
                'comparison_result': comparison_result,
                'evaluation_summary': evaluation_summary,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/calculate-hours', methods=['POST'])
    def api_calculate_hours():
        """Direct integration with March project"""
        try:
            contracted_hours = request.json.get('contracted_hours', '')
            time_frame = request.json.get('time_frame', 'week')
            work_hours_description = request.json.get('work_hours_description', '')
            
            if contracted_hours:
                contracted_hours_formatted = f"{contracted_hours} hours per {time_frame}"
            else:
                contracted_hours_formatted = "40 hours per week"
            
            # Generate work hours summary
            summary = march_generate_summary(contracted_hours_formatted, work_hours_description)
            
            return jsonify({
                'summary': summary,
                'contracted_hours': contracted_hours_formatted,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/extract-convert', methods=['POST'])
    def api_extract_convert():
        """Direct integration with April project"""
        try:
            # Handle file upload or document selection
            document_name = request.json.get('document_name')
            output_filename = request.json.get('output_filename', 'converted_document')
            output_file_type = request.json.get('output_file_type', 'txt')
            
            if not document_name:
                return jsonify({'error': 'No document specified'}), 400
            
            # Get uploaded documents
            documents = april_get_documents()
            
            if document_name not in documents:
                return jsonify({'error': 'Document not found'}), 404
            
            # Process the document
            document_path = april_get_uploads_folder() + '/' + document_name
            extracted_text = april_process_file(document_path)
            
            # Generate insights and convert
            config_options = {"Output File Type": output_file_type}
            ai_processed_info = april_generate_insights(extracted_text, config_options)
            
            converted_file_path = april_convert_file_format(
                document_path, ai_processed_info, output_filename, config_options, output_file_type
            )
            
            return jsonify({
                'extracted_text': extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                'ai_insights': ai_processed_info,
                'converted_file_path': converted_file_path,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/generate-cover-letter', methods=['POST'])
    def api_generate_cover_letter():
        """Direct integration with May project"""
        try:
            cv_text = request.json.get('cv_text', '')
            job_description = request.json.get('job_description', '')
            tone = request.json.get('tone', 'professional')
            focus_areas = request.json.get('focus_areas', [])
            
            if not cv_text or not job_description:
                return jsonify({'error': 'CV text and job description are required'}), 400
            
            letter = may_generate_letter(cv_text, job_description, tone, focus_areas)
            
            return jsonify({
                'cover_letter': letter,
                'tone': tone,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/generate-job-ad', methods=['POST'])
    def api_generate_job_ad():
        """Direct integration with June project"""
        try:
            job_details = request.json.get('job_details', {})
            
            if not job_details:
                return jsonify({'error': 'No job details provided'}), 400
            
            job_ad = june_generate_ad(job_details)
            
            return jsonify({
                'job_ad': job_ad,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/speech-to-text', methods=['POST'])
    def api_speech_to_text():
        """Direct integration with July project"""
        try:
            # Handle file upload
            if 'audio_file' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            audio_file = request.files['audio_file']
            summary_type = request.form.get('summary_type', 'conversation')
            
            if audio_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Initialize voice methods
            voice_methods = july_voice_methods(
                upload_folder=os.path.join(os.path.dirname(__file__), 'temp'),
                voice_profiles_folder=os.path.join(os.path.dirname(__file__), 'temp')
            )
            
            # Save and process audio file
            filename = ""
            filepath = os.path.join(os.path.dirname(__file__), 'temp', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            audio_file.save(filepath)
            
            # Transcribe audio
            transcript = voice_methods.transcribe_audio_file(filepath)
            
            # Generate summary
            summary = july_generate_transcript(transcript, summary_type)
            
            # Clean up temp file
            os.remove(filepath)
            
            return jsonify({
                'transcript': transcript,
                'summary': summary,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/create-calendar-event', methods=['POST'])
    def api_create_calendar_event():
        """Direct integration with August project"""
        try:
            event_data = request.json
            
            # Initialize AI parser
            ai_parser = august_ai_parser()
            
            # Parse natural language event creation
            if 'natural_language' in event_data:
                parsed_command = ai_parser.parse_voice_command(event_data['natural_language'])
                if parsed_command.get('action') == 'create_event':
                    event_details = {
                        'title': parsed_command.get('event_title', 'New Event'),
                        'description': parsed_command.get('description', ''),
                        'start_time': f"{parsed_command.get('date')} {parsed_command.get('start_time', '09:00')}",
                        'end_time': f"{parsed_command.get('date')} {parsed_command.get('end_time', '10:00')}",
                        'location': parsed_command.get('location', ''),
                        'attendees': parsed_command.get('attendees', [])
                    }
                else:
                    return jsonify({'error': 'Could not parse event creation request'}), 400
            else:
                event_details = event_data
            
            return jsonify({
                'event': event_details,
                'message': 'Event details processed successfully',
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/summarize-document', methods=['POST'])
    def api_summarize_document():
        """Direct integration with September project"""
        try:
            # Handle file upload
            if 'document_file' in request.files:
                document_file = request.files['document_file']
                summary_type = request.form.get('summary_type', 'general')
                summary_length = request.form.get('summary_length', 'medium')
                summary_tone = request.form.get('summary_tone', 'neutral')
                
                if document_file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                # Initialize document processor
                doc_processor = september_document_processor()
                
                # Save and process file
                filename = ""
                filepath = os.path.join(os.path.dirname(__file__), 'temp', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                document_file.save(filepath)
                
                # Extract text and generate summary
                document_text = doc_processor.extract_text_from_file(filepath)
                summary = september_generate_summmary(document_text, summary_type, summary_length, summary_tone)
                analysis = september_analyze_content(document_text)
                
                # Clean up temp file
                os.remove(filepath)
                
                return jsonify({
                    'document_text': document_text[:500] + "..." if len(document_text) > 500 else document_text,
                    'summary': summary,
                    'analysis': analysis,
                    'success': True
                })
            else:
                # Handle text input
                document_text = request.json.get('document_content', '')
                if not document_text:
                    return jsonify({'error': 'No document content provided'}), 400
                
                summary = september_generate_summmary(document_text, 'general', 'medium', 'neutral')
                
                return jsonify({
                    'summary': summary,
                    'success': True
                })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analyze-directory', methods=['POST'])
    def api_analyze_directory():
        """Direct integration with October project"""
        try:
            directory_path = request.json.get('directory_path')
            
            if not directory_path:
                return jsonify({'error': 'No directory path provided'}), 400
            
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return jsonify({'error': 'Invalid directory path'}), 400
            
            # Initialize services
            directory_analyzer = october_directory_analyzer()
            file_parser = october_file_parser()
            template_matcher = october_template_matcher()
            ai_summarizer = october_ai_summarizer()
            
            # Analyze directory
            analysis_result = directory_analyzer.analyze_directory(directory_path)
            content_analysis = file_parser.analyze_directory_content(directory_path)
            
            # Generate AI insights
            ai_insights = ai_summarizer.generate_comprehensive_insights(
                analysis_result, content_analysis, [], {}
            )
            
            return jsonify({
                'directory_path': directory_path,
                'analysis_result': analysis_result,
                'content_analysis': content_analysis,
                'ai_insights': ai_insights,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/code-assistance', methods=['POST'])
    def api_code_assistance():
        """Direct integration with November project"""
        try:
            code_data = request.json
            code_content = code_data.get('code', '')
            language = code_data.get('language', 'python')
            assistance_type = code_data.get('request_type', 'suggestion')
            context = code_data.get('context', '')
            
            if not code_content:
                return jsonify({'error': 'No code provided'}), 400
            
            # Generate assistance based on type
            if assistance_type == 'suggestion':
                result = november_generate_suggestion(code_content, language, context)
            elif assistance_type == 'error_explanation':
                error_message = code_data.get('error_message', '')
                result = november_explain_error(code_content, error_message, language)
            elif assistance_type == 'documentation':
                doc_type = code_data.get('doc_type', 'docstring')
                result = november_generate_documentation(code_content, language, doc_type)
            elif assistance_type == 'completion':
                result = november_complete_code(code_content, language, context)
            elif assistance_type == 'quality_analysis':
                result = november_analyze_code_quality(code_content, language)
            elif assistance_type == 'test_cases':
                result = november_generate_test_cases(code_content, language)
            elif assistance_type == 'explain':
                result = november_explain_code_functionality(code_content, language)
            else:
                return jsonify({'error': 'Unknown assistance type'}), 400
            
            return jsonify({
                'assistance': result,
                'assistance_type': assistance_type,
                'language': language,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_login():
        """Login page"""
        return render_template('login.html')
    
    def get_logs():
        """View logs page"""
        return render_template('logs.html')

# Helper functions
def get_available_apps():
    """Get list of available apps"""
    return {
        'document_search': {
            'name': 'General AI Doc Search',
            'description': 'Search through documents using AI',
            'icon': '🔍',
            'available': True
        },
        'testing_agent': {
            'name': 'AI Testing Agent', 
            'description': 'Automated testing with AI assistance',
            'icon': '🧪',
            'available': True
        },
        'work_hours_calculator': {
            'name': 'AI Work Hours Calculator',
            'description': 'Calculate work hours and overtime',
            'icon': '⏰',
            'available': True
        },
        'document_extractor': {
            'name': 'AI Document Extractor & Converter',
            'description': 'Extract and convert document content',
            'icon': '📄',
            'available': True
        },
        'cover_letter_writer': {
            'name': 'AI Cover Letter Writer',
            'description': 'Generate professional cover letters',
            'icon': '💼',
            'available': True
        },
        'job_ad_generator': {
            'name': 'AI Job Ad Generator',
            'description': 'Create optimized job advertisements',
            'icon': '📋',
            'available': True
        },
        'speech_to_text': {
            'name': 'AI Speech-to-Text App',
            'description': 'Convert speech to text with voice commands',
            'icon': '🎤',
            'available': True
        },
        'calendar_system': {
            'name': 'AI Calendar & Scheduling System',
            'description': 'Manage calendar and schedule events',
            'icon': '📅',
            'available': True
        },
        'doc_summariser': {
            'name': 'General Document Summarization AI',
            'description': 'Summarize documents with AI',
            'icon': '📝',
            'available': True
        },
        'directory_summariser': {
            'name': 'Docs Directory AI Summarizer',
            'description': 'Analyze and summarize directory contents',
            'icon': '📁',
            'available': True
        },
        'coding_assistant': {
            'name': 'AI Programming Assistant',
            'description': 'Get AI help with coding and programming',
            'icon': '💻',
            'available': True
        }
    }

def detect_app_intent(message):
    """Detect which app the user might want to use"""
    message_lower = message.lower()
    
    keywords = {
        'document_search': ['search', 'find', 'document', 'lookup'],
        'testing_agent': ['test', 'testing', 'qa', 'quality assurance'],
        'work_hours_calculator': ['hours', 'work time', 'calculate', 'overtime'],
        'document_extractor': ['extract', 'convert', 'transform', 'format'],
        'cover_letter_writer': ['cover letter', 'resume', 'job application'],
        'job_ad_generator': ['job ad', 'job posting', 'hire', 'recruitment'],
        'speech_to_text': ['speech', 'voice', 'audio', 'transcribe'],
        'calendar_system': ['calendar', 'schedule', 'meeting', 'event', 'appointment'],
        'doc_summariser': ['summarize', 'summary', 'brief', 'overview'],
        'directory_summariser': ['directory', 'folder', 'files', 'analyze'],
        'coding_assistant': ['code', 'programming', 'debug', 'coding help']
    }
    
    for app_id, app_keywords in keywords.items():
        for keyword in app_keywords:
            if keyword in message_lower:
                apps = get_available_apps()
                return {
                    'app_id': app_id,
                    'app_name': apps[app_id]['name'],
                    'description': apps[app_id]['description'],
                    'confidence': 0.8
                }
    
    return None

def execute_quick_action(action, params):
    """Execute quick actions for different apps"""
    try:
        if action == 'search_documents':
            query = params.get('query', '')
            directory = params.get('directory', 'default')
            documents = january_handle_documents(directory)
            results = january_search_documents(query, documents)
            return {'result': results}
            
        elif action == 'run_test':
            test_data = params.get('test_data', '')
            # Simplified test execution
            return {'result': f'Test executed with data: {test_data}'}
            
        elif action == 'generate_cover_letter':
            cv_text = params.get('cv_text', '')
            job_description = params.get('job_description', '')
            letter = may_generate_letter(cv_text, job_description)
            return {'result': letter}
            
        elif action == 'summarize_document':
            content = params.get('content', '')
            summary = september_generate_summmary(content, 'general', 'medium', 'neutral')
            return {'result': summary}
            
        elif action == 'generate_job_ad':
            job_details = params.get('job_details', {})
            job_ad = june_generate_ad(job_details)
            return {'result': job_ad}
            
        elif action == 'code_suggestion':
            code = params.get('code', '')
            language = params.get('language', 'python')
            suggestion = november_generate_suggestion(code, language, '')
            return {'result': suggestion}
            
        else:
            return {'error': f'Unknown action: {action}'}
    except Exception as e:
        return {'error': str(e)}