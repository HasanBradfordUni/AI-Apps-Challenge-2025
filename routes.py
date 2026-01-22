from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response
import os
import sys
from datetime import datetime
import sqlite3

# Add project directories to Python path - FIX FOR IMPORTS
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add January project src to path
january_src = os.path.join(current_dir, 'a_january_ai_document_search', 'src')
if january_src not in sys.path:
    sys.path.insert(0, january_src)

# Also add the app directory for January if it has one
january_app = os.path.join(current_dir, 'a_january_ai_document_search')
if january_app not in sys.path:
    sys.path.insert(0, january_app)

# Add March project src to path
march_src = os.path.join(current_dir, 'c_march_ai_work_hours_calculator', 'src')
if march_src not in sys.path:
    sys.path.insert(0, march_src)

# Import functions from previous projects with proper error handling
try:
    # January - General AI Doc Search - FIXED IMPORT
    import importlib.util
    
    # Check what's in the utils folder
    utils_path = os.path.join(january_src, 'utils')
    if os.path.exists(utils_path):
        utils_contents = os.listdir(utils_path)
        print(f"Utils folder contents: {utils_contents}")
    
    # Try multiple import strategies
    try:
        # Strategy 1: Direct import
        from utils.document_processing import handle_documents as january_handle_documents
        from utils.search_algorithm import search_documents as january_search_documents
        from ai.geminiPrompt import generate_ai_summary as january_generate_summary
    except ImportError:
        try:
            # Strategy 2: Import specific files
            doc_proc_path = os.path.join(january_src, 'utils', 'document_processing.py')
            search_alg_path = os.path.join(january_src, 'utils', 'search_algorithm.py')
            ai_prompt_path = os.path.join(january_src, 'ai', 'geminiPrompt.py')
            
            # Load modules directly
            spec1 = importlib.util.spec_from_file_location("january_doc_proc", doc_proc_path)
            doc_proc_module = importlib.util.module_from_spec(spec1)
            spec1.loader.exec_module(doc_proc_module)
            
            spec2 = importlib.util.spec_from_file_location("january_search", search_alg_path)
            search_module = importlib.util.module_from_spec(spec2)
            spec2.loader.exec_module(search_module)
            
            spec3 = importlib.util.spec_from_file_location("january_ai", ai_prompt_path)
            ai_module = importlib.util.module_from_spec(spec3)
            spec3.loader.exec_module(ai_module)
            
            january_handle_documents = getattr(doc_proc_module, 'handle_documents', None)
            january_search_documents = getattr(search_module, 'search_documents', None)
            january_generate_summary = getattr(ai_module, 'generate_ai_summary', None)
        except Exception as e2:
            print(f"Strategy 2 failed: {e2}")
            raise
    
    print("✓ January AI Doc Search imported")
except ImportError as e:
    print(f"✗ January import failed: {e}")
    print(f"January src path: {january_src}")
    print(f"Path exists: {os.path.exists(january_src)}")
    if os.path.exists(january_src):
        print(f"Contents: {os.listdir(january_src)}")
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
    from app import calculate_hours as march_calculate_hours
    from ai.geminiPrompt import generate_work_hours_summary as march_generate_summary
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
        explain_code_functionality as november_explain_code  # Changed back to explain_code_functionality
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
    from l_december_ai_chatbot.logger_setup import chatbot_logger, api_logger, error_logger

    # Initialize services
    prompt_manager = PromptModeManager()
    ai_service = AIIntegrationService()
    
    # Log initialization
    chatbot_logger.addToLogs("Chatbot engine initialized")
    
    # Create a proper chatbot engine that uses AI
    class ChatbotEngine:
        def __init__(self, prompt_manager, ai_service):
            self.prompt_manager = prompt_manager
            self.ai_service = ai_service
            self.conversation_history = {}
            chatbot_logger.addToLogs("ChatbotEngine instance created")
        
        def process_message(self, message, mode, user_id):
            """Process user message with AI"""
            try:
                chatbot_logger.addToInputLogs(f"User {user_id}", f"Mode: {mode}, Message: {message}")
                
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
                
                chatbot_logger.addToLogs(f"Response generated for user {user_id}: {len(response_text)} characters")
                
                return {
                    'response': response_text,
                    'mode': mode,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
            except Exception as e:
                error_logger.addToErrorLogs(f"Message processing error for user {user_id}: {str(e)}")
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
    
    # Fallback logger
    class DummyLogger:
        def addToLogs(self, msg): print(f"[LOG] {msg}")
        def addToErrorLogs(self, msg): print(f"[ERROR] {msg}")
        def addToInputLogs(self, prompt, msg): print(f"[INPUT] {prompt}: {msg}")
    
    chatbot_logger = DummyLogger()
    api_logger = DummyLogger()
    error_logger = DummyLogger()
    
    prompt_manager = FallbackManager()
    ai_service = None
    chatbot_engine = FallbackChatbotEngine()
    print("⚠ Using fallback chatbot engine (no AI)")

def register_routes(app):
    """Register all chatbot routes"""
    
    @app.errorhandler(404)
    def not_found(error):
        error_logger.addToErrorLogs(f"404 error: {request.url}")
        return jsonify({'error': 'Endpoint not found', 'success': False}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        error_logger.addToErrorLogs(f"500 error: {str(error)}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500
    
    @app.before_request
    def log_request():
        """Log all API requests for debugging"""
        if request.path.startswith('/api/'):
            api_logger.addToLogs(f"API Request: {request.method} {request.path}")
            if request.json:
                api_logger.addToInputLogs(f"{request.method} {request.path}", str(request.json))

    @app.route('/')
    def chatbot_home():
        """Main chatbot interface"""
        chatbot_logger.addToLogs("Home page accessed")
        available_apps = get_available_apps()
        return render_template('index.html', 
                             available_apps=available_apps,
                             prompt_modes=prompt_manager.get_modes())
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """Handle chat messages"""
        user_message = request.json.get('message', '').strip()
        prompt_mode = request.json.get('mode', 'general')
        
        api_logger.addToInputLogs("Chat request", f"Mode: {prompt_mode}, Message length: {len(user_message)}")
        
        if not user_message:
            error_logger.addToErrorLogs("Empty message received in chat request")
            return jsonify({'error': 'No message provided'}), 400
        
        try:
            # Get or create user session
            if 'user_id' not in session:
                session['user_id'] = f"user_{datetime.now().timestamp()}"
                chatbot_logger.addToLogs(f"New user session created: {session['user_id']}")
            
            # Get available apps for context
            available_apps = get_available_apps()
            
            # Modify ChatbotEngine to accept available_apps
            class ChatbotEngineWithApps(ChatbotEngine):
                def process_message(self, message, mode, user_id, available_apps=None):
                    """Process user message with AI and app context"""
                    try:
                        chatbot_logger.addToInputLogs(f"User {user_id}", f"Mode: {mode}, Apps context: {len(available_apps) if available_apps else 0}")
                        
                        mode_config = self.prompt_manager.get_mode(mode)
                        system_prompt = mode_config.get('system_prompt', 'You are a helpful AI assistant.')
                        
                        if user_id not in self.conversation_history:
                            self.conversation_history[user_id] = []
                        
                        context = self.conversation_history[user_id]
                        
                        # Generate AI response with available apps context
                        response_text = self.ai_service.generate_response(
                            message, 
                            system_prompt, 
                            context,
                            available_apps
                        )
                        
                        self.conversation_history[user_id].append({
                            'user_message': message,
                            'ai_response': response_text,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        if len(self.conversation_history[user_id]) > 10:
                            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
                        
                        chatbot_logger.addToLogs(f"Response generated with apps context for user {user_id}")
                        
                        return {
                            'response': response_text,
                            'mode': mode,
                            'timestamp': datetime.now().isoformat(),
                            'success': True
                        }
                    except Exception as e:
                        error_logger.addToErrorLogs(f"Enhanced processing error for user {user_id}: {str(e)}")
                        return {
                            'response': f'I encountered an error: {str(e)}',
                            'mode': mode,
                            'timestamp': datetime.now().isoformat(),
                            'success': False
                        }
            
            # Process message through chatbot engine with AI and available apps
            enhanced_engine = ChatbotEngineWithApps(prompt_manager, ai_service)
            response = enhanced_engine.process_message(
                user_message, 
                prompt_mode,
                session.get('user_id'),
                available_apps
            )
            
            # Check if message should route to specific app
            app_suggestion = detect_app_intent(user_message)
            if app_suggestion:
                response['app_suggestion'] = app_suggestion
                chatbot_logger.addToLogs(f"App suggestion made: {app_suggestion['app_name']}")
            
            return jsonify(response)
            
        except Exception as e:
            error_logger.addToErrorLogs(f"Chat processing failed: {str(e)}")
            return jsonify({'error': f'Chat processing failed: {str(e)}'}), 500

    # Direct app integration routes
    @app.route('/api/search-documents', methods=['POST'])
    def api_search_documents():
        """Direct integration with January project"""
        api_logger.addToLogs("Document search API called")
        try:
            if not january_search_documents:
                error_logger.addToErrorLogs("Document search service unavailable")
                return jsonify({'error': 'Document search service not available'}), 503
            
            query = request.json.get('query', '')
            directory = request.json.get('directory', 'default')
            
            api_logger.addToInputLogs("Document search", f"Query: {query}, Directory: {directory}")
            
            if not query:
                return jsonify({'error': 'No search query provided'}), 400
            
            # Use January project functions
            documents = january_handle_documents(directory)
            results = january_search_documents(query, documents)
            ai_summary = january_generate_summary(query, results, documents)
            
            api_logger.addToLogs(f"Document search completed: {len(results)} results")
            
            return jsonify({
                'results': results, 
                'ai_summary': ai_summary,
                'success': True
            })
        except Exception as e:
            error_logger.addToErrorLogs(f"Document search error: {str(e)}")
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
        """View logs page"""
        try:
            chatbot_logger.addToLogs("Logs page accessed")
            
            # Get log files from December project
            logs_dir = os.path.join(current_dir, 'l_december_ai_chatbot', 'logs')
            
            # Ensure logs directory exists
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)
                chatbot_logger.addToLogs(f"Created logs directory: {logs_dir}")
                
                # Create initial log files
                initial_logs = ['chatbot.txt', 'api_requests.txt', 'errors.txt']
                for log_file in initial_logs:
                    log_path = os.path.join(logs_dir, log_file)
                    with open(log_path, 'w', encoding='utf-8') as f:
                        f.write(f"Logging started...\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            available_logs = []
            
            # Safely list directory contents
            try:
                log_files = os.listdir(logs_dir)
                if log_files is None:
                    log_files = []
            except Exception as list_error:
                error_logger.addToErrorLogs(f"Error listing logs directory: {str(list_error)}")
                log_files = []
            
            # Process log files
            for filename in log_files:
                if filename.endswith('.txt'):
                    try:
                        file_path = os.path.join(logs_dir, filename)
                        
                        # Check if file exists and is accessible
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            file_modified = os.path.getmtime(file_path)
                            
                            available_logs.append({
                                'filename': filename,
                                'path': file_path,
                                'size': file_size,
                                'size_formatted': f"{file_size / 1024:.2f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.2f} MB",
                                'modified': datetime.fromtimestamp(file_modified).strftime('%Y-%m-%d %H:%M:%S')
                            })
                    except Exception as file_error:
                        error_logger.addToErrorLogs(f"Error processing log file {filename}: {str(file_error)}")
                        continue
            
            chatbot_logger.addToLogs(f"Logs page loaded with {len(available_logs)} log files")
            
            return render_template('logs.html', 
                                 available_logs=available_logs,
                                 search_results=None,
                                 search_term='',
                                 log_type='all',
                                 selected_file='',
                                 narrow_search='')
                                 
        except Exception as e:
            error_logger.addToErrorLogs(f"Error loading logs page: {str(e)}")
            import traceback
            error_logger.addToErrorLogs(f"Traceback: {traceback.format_exc()}")
            flash(f'Error loading logs: {str(e)}', 'error')
            return redirect(url_for('chatbot_home'))
    
    @app.route('/search_logs', methods=['POST'])
    def search_logs():
        """Search through logs"""
        try:
            search_term = request.form.get('search_term', '').strip()
            log_type = request.form.get('log_type', 'all')
            log_file = request.form.get('log_file', '')
            narrow_search = request.form.get('narrow_search', '').strip()
            
            chatbot_logger.addToInputLogs("Log search", f"User: {session.get('user_id', 'anonymous')}, Term: '{search_term}', Type: {log_type}, File: {log_file}")
            
            if not search_term:
                flash('Please enter a search term', 'warning')
                return redirect(url_for('get_logs'))
            
            if not log_file:
                flash('Please select a log file', 'warning')
                return redirect(url_for('get_logs'))
            
            logs_dir = os.path.join(current_dir, 'l_december_ai_chatbot', 'logs')
            log_path = os.path.join(logs_dir, log_file)
            
            if not os.path.exists(log_path):
                flash(f'Log file not found: {log_file}', 'error')
                return redirect(url_for('get_logs'))
            
            # Get available logs for dropdown
            available_logs = []
            try:
                log_files = os.listdir(logs_dir)
                if log_files is None:
                    log_files = []
            except Exception as list_error:
                error_logger.addToErrorLogs(f"Error listing logs directory: {str(list_error)}")
                log_files = []
            
            for filename in log_files:
                if filename.endswith('.txt'):
                    try:
                        file_path = os.path.join(logs_dir, filename)
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            available_logs.append({
                                'filename': filename,
                                'path': file_path,
                                'size': file_size,
                                'size_formatted': f"{file_size / 1024:.2f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.2f} MB",
                                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                            })
                    except Exception as file_error:
                        continue
            
            # Search logs using autoLogger method
            try:
                # Create a temporary logger instance for the file we're searching
                from l_december_ai_chatbot.logger_setup import general_logger
                temp_logger = general_logger(log_path)
                
                # Use the appropriate search method based on log type
                results_data = []
                
                if log_type == 'output' or log_type == 'all':
                    if narrow_search:
                        results_data = temp_logger.searchWithNarrow('output', search_term, narrow_search)
                    else:
                        results_data = temp_logger.searchForLogs(search_term)
                elif log_type == 'error':
                    if narrow_search:
                        results_data = temp_logger.searchWithNarrow('error', search_term, narrow_search)
                    else:
                        results_data = temp_logger.searchForErrors(search_term)
                elif log_type == 'input':
                    if narrow_search:
                        results_data = temp_logger.searchWithNarrow('input', search_term, narrow_search)
                    else:
                        results_data = temp_logger.searchForInputs(search_term)
                else:
                    # Search all types
                    results_data = temp_logger.searchForLogs(search_term)
                    if narrow_search:
                        # Filter results further
                        results_data = [r for r in results_data if narrow_search.lower() in r.lower()]
                
                # Ensure results_data is a list
                if results_data is None:
                    results_data = []
                
                # Format results for template
                search_results = []
                for i, result in enumerate(results_data[:100], 1):  # Limit to first 100 results
                    # Determine result type from content
                    result_type = 'output'
                    if 'Error:' in result or 'ERROR' in result:
                        result_type = 'error'
                    elif 'User Input:' in result or 'INPUT' in result:
                        result_type = 'input'
                    
                    search_results.append({
                        'line_number': i,
                        'content': result.strip(),
                        'file': log_file,
                        'type': result_type
                    })
                
                chatbot_logger.addToLogs(f"Log search completed: {len(search_results)} results found for '{search_term}' in {log_file}")
                
                if search_results:
                    flash(f'Found {len(search_results)} results', 'success')
                else:
                    flash('No results found', 'info')
                
                return render_template('logs.html', 
                                     available_logs=available_logs,
                                     search_results=search_results, 
                                     search_term=search_term,
                                     log_type=log_type,
                                     selected_file=log_file,
                                     narrow_search=narrow_search)
                
            except Exception as search_error:
                error_logger.addToErrorLogs(f"Search execution error: {str(search_error)}")
                import traceback
                error_logger.addToErrorLogs(f"Search traceback: {traceback.format_exc()}")
                flash(f'Search error: {str(search_error)}', 'error')
                return redirect(url_for('get_logs'))
                
        except Exception as e:
            error_logger.addToErrorLogs(f"Error searching logs: {str(e)}")
            import traceback
            error_logger.addToErrorLogs(f"Traceback: {traceback.format_exc()}")
            flash(f'Error searching logs: {str(e)}', 'error')
            return redirect(url_for('get_logs'))
    
    @app.route('/export_logs', methods=['POST'])
    def export_logs():
        """Export search results or entire log file"""
        try:
            export_type = request.form.get('export_type', 'results')
            export_format = request.form.get('export_format', 'txt')
            
            chatbot_logger.addToLogs(f"User {session.get('user_id', 'anonymous')} exporting logs: type={export_type}, format={export_format}")
            
            # Get search results from session or form data
            # For now, we'll export the current log file
            log_file = request.form.get('log_file', 'chatbot.txt')
            logs_dir = os.path.join(current_dir, 'l_december_ai_chatbot', 'logs')
            log_path = os.path.join(logs_dir, log_file)
            
            if not os.path.exists(log_path):
                flash('Log file not found', 'error')
                return redirect(url_for('get_logs'))
            
            # Create export filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"log_export_{timestamp}.{export_format}"
            
            if export_format == 'txt':
                # Simple text export
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                response = make_response(content)
                response.headers['Content-Type'] = 'text/plain'
                response.headers['Content-Disposition'] = f'attachment; filename={export_filename}'
                
                chatbot_logger.addToLogs(f"Log export completed: {export_filename}")
                return response
                
            elif export_format == 'json':
                import json
                
                # Read log file and convert to JSON
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                log_data = {
                    'export_date': datetime.now().isoformat(),
                    'source_file': log_file,
                    'total_entries': len(lines),
                    'entries': [{'line': i+1, 'content': line.strip()} for i, line in enumerate(lines)]
                }
                
                response = make_response(json.dumps(log_data, indent=2))
                response.headers['Content-Type'] = 'application/json'
                response.headers['Content-Disposition'] = f'attachment; filename={export_filename}'
                
                chatbot_logger.addToLogs(f"Log export completed: {export_filename}")
                return response
            
            else:
                flash('Unsupported export format', 'error')
                return redirect(url_for('get_logs'))
                
        except Exception as e:
            error_logger.addToErrorLogs(f"Error exporting logs: {str(e)}")
            flash(f'Export error: {str(e)}', 'error')
            return redirect(url_for('get_logs'))
    
    @app.route('/clear_logs', methods=['POST'])
    def clear_logs():
        """Clear a specific log file"""
        try:
            filename = request.form.get('log_file') or request.form.get('filename')
            if not filename:
                flash('No filename specified', 'error')
                return redirect(url_for('get_logs'))
            
            logs_dir = os.path.join(current_dir, 'l_december_ai_chatbot', 'logs')
            log_path = os.path.join(logs_dir, filename)
            
            if not os.path.exists(log_path):
                flash(f'Log file not found: {filename}', 'error')
                return redirect(url_for('get_logs'))
            
            # Create backup before clearing
            backup_dir = os.path.join(logs_dir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f"{filename}.backup_{timestamp}")
            
            # Copy to backup
            import shutil
            shutil.copy2(log_path, backup_path)
            
            # Clear the file using autoLogger method
            from l_december_ai_chatbot.logger_setup import general_logger
            temp_logger = general_logger(log_path)
            temp_logger.cleanLoggerFile()
            
            # Add cleared message
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Output:\nLog cleared on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Backup created: {backup_path}\n\n")
            
            chatbot_logger.addToLogs(f"Log file cleared: {filename} (backup: {backup_path})")
            flash(f'Log file cleared: {filename}. Backup created.', 'success')
            return redirect(url_for('get_logs'))
            
        except Exception as e:
            error_logger.addToErrorLogs(f"Error clearing log: {str(e)}")
            flash(f'Error clearing log: {str(e)}', 'error')
            return redirect(url_for('get_logs'))
    
    @app.route('/api/apps/status')
    def api_apps_status():
        """Get status of all available apps"""
        return jsonify(get_available_apps())
    
    @app.route('/api/conversation/history', methods=['GET'])
    def get_conversation_history():
        """Get user's conversation history"""
        if 'user_id' not in session:
            return jsonify({'error': 'No active session'}), 401
        
        user_id = session['user_id']
        history = chatbot_engine.conversation_history.get(user_id, [])
        
        return jsonify({
            'history': history,
            'user_id': user_id,
            'success': True
        })
    
    @app.route('/api/conversation/clear', methods=['POST'])
    def clear_conversation():
        """Clear conversation history"""
        if 'user_id' not in session:
            return jsonify({'error': 'No active session'}), 401
        
        user_id = session['user_id']
        if user_id in chatbot_engine.conversation_history:
            chatbot_engine.conversation_history[user_id] = []
            chatbot_logger.addToLogs(f"Conversation cleared for user {user_id}")
        
        return jsonify({'success': True, 'message': 'Conversation cleared'})
    
    @app.route('/api/modes')
    def get_prompt_modes():
        """Get available prompt modes"""
        return jsonify(prompt_manager.get_modes())
    
    @app.route('/api/app/<app_id>/launch', methods=['POST'])
    def launch_app(app_id):
        """Launch a specific app with parameters"""
        available_apps = get_available_apps()
        
        if app_id not in available_apps:
            return jsonify({'error': 'App not found'}), 404
        
        if not available_apps[app_id]['available']:
            return jsonify({'error': 'App not available'}), 503
        
        # Route to appropriate app endpoint
        app_routes = {
            'document_search': 'api_search_documents',
            'work_hours_calculator': 'api_calculate_hours',
            'cover_letter_writer': 'api_generate_cover_letter',
            'doc_summariser': 'api_summarize_document',
            'coding_assistant': 'api_code_assistance'
        }
        
        if app_id in app_routes:
            # Forward request to the appropriate API endpoint
            return redirect(url_for(app_routes[app_id]), code=307)
        
        return jsonify({'error': 'App launch not implemented'}), 501

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
        'testing_agent': {
            'name': 'AI Testing Agent',
            'description': 'Compare and test AI models',
            'icon': '🧪',
            'available': february_generate_comparison is not None
        },
        'work_hours_calculator': {
            'name': 'AI Work Hours Calculator',
            'description': 'Calculate work hours and overtime',
            'icon': '⏰',
            'available': march_generate_summary is not None
        },
        'document_extractor': {
            'name': 'AI Document Extractor & Converter',
            'description': 'Extract and convert document formats',
            'icon': '📄',
            'available': april_convert_file_format is not None
        },
        'cover_letter_writer': {
            'name': 'AI Cover Letter Writer',
            'description': 'Generate professional cover letters',
            'icon': '💼',
            'available': may_generate_letter is not None
        },
        'job_ad_generator': {
            'name': 'AI Job Ad Generator',
            'description': 'Create compelling job advertisements',
            'icon': '📋',
            'available': june_generate_ad is not None
        },
        'speech_to_text': {
            'name': 'AI Speech-to-Text App',
            'description': 'Convert speech to text with AI',
            'icon': '🎤',
            'available': july_voice_methods is not None
        },
        'calendar_system': {
            'name': 'AI Calendar & Scheduling System',
            'description': 'Manage calendar and schedule events',
            'icon': '📅',
            'available': august_ai_parser is not None
        },
        'doc_summariser': {
            'name': 'General Document Summarization AI',
            'description': 'Summarize documents with AI',
            'icon': '📝',
            'available': september_generate_summary is not None
        },
        'directory_summariser': {
            'name': 'Docs Directory AI Summarizer',
            'description': 'Summarize entire document directories',
            'icon': '📂',
            'available': october_ai_summarizer is not None
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