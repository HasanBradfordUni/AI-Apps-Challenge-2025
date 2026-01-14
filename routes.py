from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response
import os
import sys
import json
from datetime import datetime
import sqlite3

# Import functions from previous projects with proper error handling
try:
    # January - General AI Doc Search
    from a_january_ai_document_search.src.utils.document_processing import handle_documents as january_handle_documents
    from a_january_ai_document_search.src.utils.search_algorithm import search_documents as january_search_documents
    from a_january_ai_document_search.src.ai.geminiPrompt import generate_ai_summary as january_generate_summary
    print("✓ January AI Doc Search imported")
except ImportError as e:
    print(f"✗ January import failed: {e}")
    january_handle_documents = None
    january_search_documents = None
    january_generate_summary = None

try:
    # February - AI Testing Agent  
    from b_february_ai_testing_agent.app.utils import process_files as february_process_files
    from b_february_ai_testing_agent.app.utils import generate_ai_comparison as february_generate_comparison
    from b_february_ai_testing_agent.app.utils import generate_summary as february_generate_summary
    print("✓ February AI Testing Agent imported")
except ImportError as e:
    print(f"✗ February import failed: {e}")
    february_process_files = None
    february_generate_comparison = None
    february_generate_summary = None

try:
    # March - AI Work Hours Calculator
    from c_march_ai_work_hours_calculator.src.app import calculate_work_hours as march_calculate_hours
    from c_march_ai_work_hours_calculator.src.ai.geminiPrompt import generate_work_hours_summary as march_generate_summary
    print("✓ March AI Work Hours Calculator imported")
except ImportError as e:
    print(f"✗ March import failed: {e}")
    march_calculate_hours = None
    march_generate_summary = None

try:
    # April - AI Document Extractor & Converter
    from d_april_ai_document_extractor.src.utils.document_processing import (
        get_uploaded_documents as april_get_documents,
        handle_document_upload as april_handle_upload,
        process_uploaded_file as april_process_file,
        get_uploads_folder as april_get_uploads_folder,
        convert_file_format_from_file_path as april_convert_file_format
    )
    from d_april_ai_document_extractor.src.ai.geminiPrompt import generate_conversion_insights as april_generate_insights
    print("✓ April AI Document Extractor imported")
except ImportError as e:
    print(f"✗ April import failed: {e}")
    april_get_documents = None
    april_handle_upload = None
    april_process_file = None
    april_get_uploads_folder = None
    april_convert_file_format = None
    april_generate_insights = None

try:
    # May - AI Cover Letter Writer
    from e_may_ai_cover_letter_writer.app.utils import (
        extract_text_from_pdf as may_extract_text,
        generate_cover_letter as may_generate_letter,
        refine_cover_letter as may_refine_letter,
        extract_cv_structure as may_extract_cv_structure
    )
    print("✓ May AI Cover Letter Writer imported")
except ImportError as e:
    print(f"✗ May import failed: {e}")
    may_extract_text = None
    may_generate_letter = None
    may_refine_letter = None
    may_extract_cv_structure = None

try:
    # June - AI Job Ad Generator
    from f_june_ai_job_ad_generator.app.utils import (
        generate_job_ad as june_generate_ad,
        refine_job_ad as june_refine_ad,
        extract_text_from_pdf as june_extract_text,
        format_for_pdf as june_format_for_pdf
    )
    print("✓ June AI Job Ad Generator imported")
except ImportError as e:
    print(f"✗ June import failed: {e}")
    june_generate_ad = None
    june_refine_ad = None
    june_extract_text = None
    june_format_for_pdf = None

try:
    # July - AI Speech-to-Text App
    from g_july_ai_speech_to_text_app.src.utils.voice_methods import VoiceMethods as july_voice_methods
    from g_july_ai_speech_to_text_app.src.ai.geminiPrompt import (
        generate_transcript_summary as july_generate_transcript,
        generate_voice_command_response as july_generate_voice_response
    )
    print("✓ July AI Speech-to-Text imported")
except ImportError as e:
    print(f"✗ July import failed: {e}")
    july_voice_methods = None
    july_generate_transcript = None
    july_generate_voice_response = None

try:
    # August - AI Calendar & Scheduling System
    from h_august_ai_calendar_system.app.services.ai_parser import AICommandParser as august_ai_parser
    from h_august_ai_calendar_system.app.services.voice_recognition import VoiceRecognitionService as august_voice_recognition
    from h_august_ai_calendar_system.app.services.calendar_sync import (
        GoogleCalendarService as august_google_calendar,
        OutlookCalendarService as august_outlook_calendar
    )
    print("✓ August AI Calendar System imported")
except ImportError as e:
    print(f"✗ August import failed: {e}")
    august_ai_parser = None
    august_voice_recognition = None
    august_google_calendar = None
    august_outlook_calendar = None

try:
    # September - General Document Summarization AI
    from i_september_ai_doc_summariser.src.utils.document_processor import DocumentProcessor as september_document_processor
    from i_september_ai_doc_summariser.src.ai.geminiPrompt import (
        generate_document_summary as september_generate_summary,
        analyze_document_content as september_analyze_content
    )
    print("✓ September AI Doc Summariser imported")
except ImportError as e:
    print(f"✗ September import failed: {e}")
    september_document_processor = None
    september_generate_summary = None
    september_analyze_content = None

try:
    # October - Docs Directory AI Summarizer
    from j_october_ai_directory_summariser.app.services.directory_analyzer import DirectoryAnalyzer as october_directory_analyzer
    from j_october_ai_directory_summariser.app.services.file_parser import FileParser as october_file_parser
    from j_october_ai_directory_summariser.app.services.template_matcher import TemplateMatcher as october_template_matcher
    from j_october_ai_directory_summariser.app.services.ai_parser import AISummarizer as october_ai_summarizer
    print("✓ October AI Directory Summariser imported")
except ImportError as e:
    print(f"✗ October import failed: {e}")
    october_directory_analyzer = None
    october_file_parser = None
    october_template_matcher = None
    october_ai_summarizer = None

try:
    # November - AI Programming Assistant
    from k_november_ai_coding_assistant.src.utils.code_processor import CodeProcessor as november_code_processor
    from k_november_ai_coding_assistant.src.ai.geminiPrompt import (
        generate_code_suggestion as november_generate_suggestion,
        explain_error as november_explain_error,
        generate_documentation as november_generate_documentation,
        complete_code as november_complete_code,
        analyze_code_quality as november_analyze_code_quality,
        generate_test_cases as november_generate_test_cases,
        explain_code as november_explain_code  # Changed from november_explain_code_functionality
    )
    print("✓ November AI Coding Assistant imported")
except ImportError as e:
    print(f"✗ November import failed: {e}")
    november_code_processor = None
    november_generate_suggestion = None
    november_explain_error = None
    november_generate_documentation = None
    november_complete_code = None
    november_analyze_code_quality = None
    november_generate_test_cases = None
    november_explain_code = None

# Import from December chatbot modules
try:
    from l_december_ai_chatbot.prompt_modes import PromptModeManager
    from l_december_ai_chatbot.ai_parser import AIIntegrationService

    # Initialize services
    prompt_manager = PromptModeManager()
    ai_service = AIIntegrationService()
    
    # Create a proper chatbot engine that uses AI
    class ChatbotEngine:
        def __init__(self, prompt_manager, ai_service):
            self.prompt_manager = prompt_manager
            self.ai_service = ai_service
            self.conversation_history = {}
        
        def process_message(self, message, mode, user_id):
            """Process user message with AI"""
            try:
                # Get mode configuration
                mode_config = self.prompt_manager.get_mode(mode)
                system_prompt = mode_config.get('system_prompt', 'You are a helpful AI assistant.')
                
                # Get user's conversation history
                if user_id not in self.conversation_history:
                    self.conversation_history[user_id] = []
                
                context = self.conversation_history[user_id]
                
                # Generate AI response
                response_text = self.ai_service.generate_response(
                    message, 
                    system_prompt, 
                    context
                )
                
                # Update conversation history
                self.conversation_history[user_id].append({
                    'user_message': message,
                    'ai_response': response_text,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Keep only last 10 messages
                if len(self.conversation_history[user_id]) > 10:
                    self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
                
                return {
                    'response': response_text,
                    'mode': mode,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
            except Exception as e:
                return {
                    'response': f'I encountered an error: {str(e)}',
                    'mode': mode,
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
    
    chatbot_engine = ChatbotEngine(prompt_manager, ai_service)
    print("✓ December AI Chatbot initialized with AI integration")
    
except ImportError as e:
    print(f"✗ December chatbot import failed: {e}")
    # Create fallback classes
    class FallbackManager:
        def get_modes(self): 
            return {
                'general': {'name': 'General', 'icon': '💬', 'description': 'General conversation', 'system_prompt': 'You are a helpful AI assistant.'}
            }
        def get_mode(self, mode): 
            return {'name': 'General', 'system_prompt': 'You are a helpful AI assistant.'}
    
    class FallbackChatbotEngine:
        def process_message(self, message, mode, user_id):
            return {
                'response': f'Echo (AI not available): {message}',
                'mode': mode,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
    
    prompt_manager = FallbackManager()
    ai_service = None
    chatbot_engine = FallbackChatbotEngine()
    print("⚠ Using fallback chatbot engine (no AI)")

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
            # Get or create user session
            if 'user_id' not in session:
                session['user_id'] = f"user_{datetime.now().timestamp()}"
            
            # Process message through chatbot engine with AI
            response = chatbot_engine.process_message(
                user_message, 
                prompt_mode,
                session.get('user_id')
            )
            
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
            if not january_search_documents:
                return jsonify({'error': 'Document search service not available'}), 503
            
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
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/calculate-hours', methods=['POST'])
    def api_calculate_hours():
        """Direct integration with March project"""
        try:
            if not march_generate_summary:
                return jsonify({'error': 'Work hours calculator not available'}), 503
            
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
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/generate-cover-letter', methods=['POST'])
    def api_generate_cover_letter():
        """Direct integration with May project"""
        try:
            if not may_generate_letter:
                return jsonify({'error': 'Cover letter writer not available'}), 503
            
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
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/summarize-document', methods=['POST'])
    def api_summarize_document():
        """Direct integration with September project"""
        try:
            if not september_generate_summary:
                return jsonify({'error': 'Document summarizer not available'}), 503
            
            # Handle text input
            document_text = request.json.get('document_content', '')
            if not document_text:
                return jsonify({'error': 'No document content provided'}), 400
            
            summary = september_generate_summary(document_text, 'general', 'medium', 'neutral')
            
            return jsonify({
                'summary': summary,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/code-assistance', methods={'POST'})
    def api_code_assistance():
        """Direct integration with November project"""
        try:
            if not november_generate_suggestion:
                return jsonify({'error': 'Coding assistant not available'}), 503
            
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
            elif assistance_type == 'explain':
                result = november_explain_code(code_content, language)
            elif assistance_type == 'documentation':
                result = november_generate_documentation(code_content, language, 'docstring')
            elif assistance_type == 'quality_analysis':
                result = november_analyze_code_quality(code_content, language)
            elif assistance_type == 'test_cases':
                result = november_generate_test_cases(code_content, language)
            else:
                return jsonify({'error': 'Unknown assistance type'}), 400
            
            return jsonify({
                'assistance': result,
                'assistance_type': assistance_type,
                'language': language,
                'success': True
            })
        except Exception as e:
            return jsonify({'error': str(e), 'success': False}), 500

    @app.route('/login')
    def get_login():
        """Login page"""
        return render_template('login.html')
    
    @app.route('/login', methods=['POST'])
    def login():
        """Handle login"""
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (for demonstration purposes)
        if username == 'admin' and password == 'password':
            session['user_id'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('chatbot_home'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('get_login'))

    @app.route('/get_logs')
    def get_logs():
        return render_template('logs.html')

# Helper functions
def get_available_apps():
    """Get list of available apps with availability status"""
    return {
        'document_search': {
            'name': 'General AI Doc Search',
            'description': 'Search through documents using AI',
            'icon': '🔍',
            'available': january_search_documents is not None
        },
        'work_hours_calculator': {
            'name': 'AI Work Hours Calculator',
            'description': 'Calculate work hours and overtime',
            'icon': '⏰',
            'available': march_generate_summary is not None
        },
        'cover_letter_writer': {
            'name': 'AI Cover Letter Writer',
            'description': 'Generate professional cover letters',
            'icon': '💼',
            'available': may_generate_letter is not None
        },
        'doc_summariser': {
            'name': 'General Document Summarization AI',
            'description': 'Summarize documents with AI',
            'icon': '📝',
            'available': september_generate_summary is not None
        },
        'coding_assistant': {
            'name': 'AI Programming Assistant',
            'description': 'Get AI help with coding and programming',
            'icon': '💻',
            'available': november_generate_suggestion is not None
        }
    }

def detect_app_intent(message):
    """Detect which app the user might want to use"""
    message_lower = message.lower()
    
    keywords = {
        'document_search': ['search', 'find', 'document', 'lookup'],
        'work_hours_calculator': ['hours', 'work time', 'calculate', 'overtime'],
        'cover_letter_writer': ['cover letter', 'resume', 'job application', 'cv'],
        'doc_summariser': ['summarize', 'summary', 'brief', 'overview'],
        'coding_assistant': ['code', 'programming', 'debug', 'coding help', 'function']
    }
    
    for app_id, app_keywords in keywords.items():
        for keyword in app_keywords:
            if keyword in message_lower:
                apps = get_available_apps()
                app = apps.get(app_id)
                if app and app['available']:
                    return {
                        'app_id': app_id,
                        'app_name': app['name'],
                        'description': app['description'],
                        'confidence': 0.8
                    }
    
    return None