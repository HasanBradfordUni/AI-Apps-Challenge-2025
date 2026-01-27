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
    import importlib.machinery
    
    # Load modules using absolute file paths
    january_utils_path = os.path.join(january_src, 'utils')
    january_ai_path = os.path.join(january_src, 'ai')
    
    # Add the utils and ai directories to sys.path temporarily
    if january_utils_path not in sys.path:
        sys.path.insert(0, january_utils_path)
    if january_ai_path not in sys.path:
        sys.path.insert(0, january_ai_path)
    
    doc_proc_path = os.path.join(january_src, 'utils', 'document_processing.py')
    search_alg_path = os.path.join(january_src, 'utils', 'search_algorithm.py')
    ai_prompt_path = os.path.join(january_src, 'ai', 'geminiPrompt.py')
    
    # Check files exist
    print(f"Doc processing exists: {os.path.exists(doc_proc_path)}")
    print(f"Search algorithm exists: {os.path.exists(search_alg_path)}")
    print(f"AI prompt exists: {os.path.exists(ai_prompt_path)}")
    
    # Create a fake 'utils' package so imports work
    import types
    utils_package = types.ModuleType('utils')
    utils_package.__path__ = [january_utils_path]
    sys.modules['utils'] = utils_package
    
    # Load document processing module FIRST (since search_algorithm depends on it)
    spec1 = importlib.util.spec_from_file_location("utils.document_processing", doc_proc_path)
    doc_proc_module = importlib.util.module_from_spec(spec1)
    sys.modules['utils.document_processing'] = doc_proc_module
    spec1.loader.exec_module(doc_proc_module)
    
    # Now load search algorithm module (it can now find utils.document_processing)
    spec2 = importlib.util.spec_from_file_location("utils.search_algorithm", search_alg_path)
    search_module = importlib.util.module_from_spec(spec2)
    sys.modules['utils.search_algorithm'] = search_module
    spec2.loader.exec_module(search_module)
    
    # Load AI module
    spec3 = importlib.util.spec_from_file_location("ai.geminiPrompt", ai_prompt_path)
    ai_module = importlib.util.module_from_spec(spec3)
    sys.modules['ai.geminiPrompt'] = ai_module
    sys.modules['geminiPrompt'] = ai_module  # Also register without prefix
    spec3.loader.exec_module(ai_module)
    
    # Get functions from loaded modules
    january_handle_documents = getattr(doc_proc_module, 'handle_documents', None)
    january_search_documents = getattr(search_module, 'search_documents', None)
    january_generate_summary = getattr(ai_module, 'generate_ai_summary', None)
    
    print("✓ January AI Doc Search imported")
except Exception as e:
    print(f"✗ January import failed: {e}")
    import traceback
    print(traceback.format_exc())
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
    # March - AI Work Hours Calculator - FIXED IMPORT
    import importlib.util
    
    march_src = os.path.join(current_dir, 'c_march_ai_work_hours_calculator', 'src')
    march_ai_path = os.path.join(march_src, 'ai', 'geminiPrompt.py')
    
    # Add March paths to sys.path
    if march_src not in sys.path:
        sys.path.insert(0, march_src)
    
    # Create fake 'ai' package for March
    import types
    ai_package = types.ModuleType('ai')
    ai_package.__path__ = [os.path.join(march_src, 'ai')]
    sys.modules['ai'] = ai_package
    
    # Load March AI module
    spec_march = importlib.util.spec_from_file_location("ai.geminiPrompt", march_ai_path)
    march_ai_module = importlib.util.module_from_spec(spec_march)
    sys.modules['ai.geminiPrompt'] = march_ai_module
    spec_march.loader.exec_module(march_ai_module)
    
    # Get the function
    march_generate_summary = getattr(march_ai_module, 'generate_work_hours_summary', None)
    march_calculate_hours = None  # We'll implement this ourselves
    
    print("✓ March AI Work Hours Calculator imported")
except Exception as e:
    print(f"✗ March import failed: {e}")
    import traceback
    print(traceback.format_exc())
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

    @app.route('/api/run-test-comparison', methods=['POST'])
    def api_run_test_comparison():
        """Direct integration with February project - AI Testing Agent"""
        try:
            api_logger.addToLogs("Test comparison API called")
            
            if not february_generate_comparison:
                error_logger.addToErrorLogs("Testing agent service unavailable")
                return jsonify({'error': 'Testing agent not available'}), 503
            
            # Get form data - FIXED to handle multipart/form-data
            project_name = request.form.get('project_name', '')
            project_description = request.form.get('project_description', '')
            test_query = request.form.get('test_query', '')
            additional_context = request.form.get('additional_context', '')
            
            api_logger.addToInputLogs("Test comparison", f"Project: {project_name}, Query: {test_query}")
            
            # Get uploaded files
            expected_results = request.files.get('expected_results')
            actual_results = request.files.get('actual_results')
            
            if not project_name or not test_query:
                error_logger.addToErrorLogs("Missing project name or test query")
                return jsonify({'error': 'Project name and test query are required'}), 400
            
            if not expected_results or not actual_results:
                error_logger.addToErrorLogs("Missing expected or actual results files")
                return jsonify({'error': 'Both expected and actual results files are required'}), 400
            
            # Validate file types
            expected_filename = expected_results.filename.lower()
            actual_filename = actual_results.filename.lower()
            
            if not expected_filename.endswith('.pdf'):
                return jsonify({'error': 'Expected results must be a PDF file'}), 400
            
            allowed_image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
            if not any(actual_filename.endswith(ext) for ext in allowed_image_extensions):
                return jsonify({'error': 'Actual results must be an image file'}), 400
            
            api_logger.addToLogs(f"Processing files: {expected_filename}, {actual_filename}")
            
            # Process files using February's methods
            try:
                expected_text, actual_text = february_process_files(expected_results, actual_results)
                api_logger.addToLogs(f"Files processed: Expected={len(expected_text)} chars, Actual={len(actual_text)} chars")
            except Exception as e:
                error_logger.addToErrorLogs(f"File processing error: {str(e)}")
                import traceback
                error_logger.addToErrorLogs(f"Traceback: {traceback.format_exc()}")
                return jsonify({'error': f'File processing failed: {str(e)}'}), 500
            
            # Generate comparison
            try:
                comparison = february_generate_comparison(
                    project_name,
                    test_query,
                    expected_text,
                    actual_text,
                    project_description,
                    additional_context
                )
                api_logger.addToLogs(f"Comparison generated: {len(comparison)} chars")
            except Exception as e:
                error_logger.addToErrorLogs(f"Comparison generation error: {str(e)}")
                return jsonify({'error': f'Comparison generation failed: {str(e)}'}), 500
            
            # Generate summary
            try:
                summary = february_generate_summary(
                    comparison,
                    project_name,
                    test_query,
                    project_description,
                    additional_context
                )
                api_logger.addToLogs(f"Summary generated: {len(summary)} chars")
            except Exception as e:
                error_logger.addToErrorLogs(f"Summary generation error: {str(e)}")
                # Continue without summary if it fails
                summary = "Summary generation failed."
            
            # Convert markdown to HTML
            try:
                import markdown
                comparison_html = markdown.markdown(comparison)
                summary_html = markdown.markdown(summary)
            except Exception as e:
                error_logger.addToErrorLogs(f"Markdown conversion error: {str(e)}")
                # Use plain text if markdown conversion fails
                comparison_html = f"<pre>{comparison}</pre>"
                summary_html = f"<pre>{summary}</pre>"
            
            api_logger.addToLogs(f"Test comparison completed successfully for {project_name}")
            
            return jsonify({
                'comparison': comparison_html,
                'summary': summary_html,
                'project_name': project_name,
                'success': True
            }), 200
            
        except Exception as e:
            error_logger.addToErrorLogs(f"Test comparison error: {str(e)}")
            import traceback
            error_logger.addToErrorLogs(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': str(e), 'success': False}), 500

    @app.route('/api/convert-document', methods=['POST'])
    def api_convert_document():
        """Direct integration with April project - Document Extractor"""
        try:
            if not april_convert_file_format:
                return jsonify({'error': 'Document converter not available'}), 503
            
            # Get uploaded file
            document_file = request.files.get('document_file')
            if not document_file:
                return jsonify({'error': 'No document file provided'}), 400
            
            # Get conversion parameters
            output_format = request.form.get('output_format', 'same')
            table_handling = request.form.get('table_handling', 'keep')
            field_mapping = request.form.get('field_mapping', '{}')
            placeholder_text = request.form.get('placeholder_text', '')
            page_range = request.form.get('page_range', 'all')
            output_formatting = request.form.get('output_formatting', 'original')
            additional_notes = request.form.get('additional_notes', '')
            
            # Save uploaded file temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document_file.filename)[1]) as tmp:
                document_file.save(tmp.name)
                temp_path = tmp.name
            
            try:
                # Parse field mapping JSON
                import json
                try:
                    field_mapping_dict = json.loads(field_mapping) if field_mapping else {}
                except:
                    field_mapping_dict = {}
                
                # Convert document using April's function
                conversion_config = {
                    'output_format': output_format,
                    'table_handling': table_handling,
                    'field_mapping': field_mapping_dict,
                    'placeholder_text': placeholder_text,
                    'page_range': page_range,
                    'output_formatting': output_formatting,
                    'additional_notes': additional_notes
                }
                
                # Process the file
                converted_file_path = april_convert_file_format(
                    temp_path,
                    output_format if output_format != 'same' else os.path.splitext(document_file.filename)[1][1:],
                    conversion_config
                )
                
                # Generate insights if available
                insights = ""
                if april_generate_insights:
                    insights = april_generate_insights(document_file.filename, conversion_config)
                
                # Read converted file
                with open(converted_file_path, 'rb') as f:
                    converted_content = f.read()
                
                # Encode as base64 for JSON response
                import base64
                converted_base64 = base64.b64encode(converted_content).decode('utf-8')
                
                api_logger.addToLogs(f"Document conversion completed: {document_file.filename}")
                
                return jsonify({
                    'converted_file': converted_base64,
                    'filename': os.path.basename(converted_file_path),
                    'insights': insights,
                    'success': True
                })
                
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                if 'converted_file_path' in locals() and os.path.exists(converted_file_path):
                    os.unlink(converted_file_path)
            
        except Exception as e:
            error_logger.addToErrorLogs(f"Document conversion error: {str(e)}")
            import traceback
            error_logger.addToErrorLogs(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': str(e), 'success': False}), 500

    @app.route('/api/generate-job-ad', methods=['POST'])
    def api_generate_job_ad():
        """Direct integration with June project - Job Ad Generator"""
        try:
            if not june_generate_ad:
                return jsonify({'error': 'Job ad generator not available'}), 503
            
            # Collect all job details
            job_data = {
                'job_title': request.form.get('job_title', ''),
                'employment_type': request.form.get('employment_type', 'full-time'),
                'work_mode': request.form.get('work_mode', 'remote'),
                'department': request.form.get('department', ''),
                'location': request.form.get('location', ''),
                'salary_range': request.form.get('salary_range', ''),
                'min_education': request.form.get('min_education', ''),
                'experience_reqs': request.form.get('experience_reqs', ''),
                'job_responsibilities': request.form.get('job_responsibilities', ''),
                'required_skills': request.form.get('required_skills', ''),
                'preferred_skills': request.form.get('preferred_skills', ''),
                'personality_traits': request.form.get('personality_traits', ''),
                'company_name': request.form.get('company_name', ''),
                'about_company': request.form.get('about_company', ''),
                'diversity_statement': request.form.get('diversity_statement', ''),
                'application_process': request.form.get('application_process', '')
            }
            
            if not job_data['job_title']:
                return jsonify({'error': 'Job title is required'}), 400
            
            # Generate job ad
            job_ad = june_generate_ad(job_data)
            
            # Convert to HTML if markdown
            import markdown
            job_ad_html = markdown.markdown(job_ad)
            
            api_logger.addToLogs(f"Job ad generated for {job_data['job_title']}")
            
            return jsonify({
                'job_ad': job_ad_html,
                'job_ad_raw': job_ad,
                'success': True
            })
            
        except Exception as e:
            error_logger.addToErrorLogs(f"Job ad generation error: {str(e)}")
            return jsonify({'error': str(e), 'success': False}), 500

    @app.route('/api/transcribe-audio', methods=['POST'])
    def api_transcribe_audio():
        """Direct integration with July project - Speech to Text"""
        try:
            if not july_voice_methods:
                return jsonify({'error': 'Speech-to-text not available'}), 503
            
            audio_file = request.files.get('audio_file')
            if not audio_file:
                return jsonify({'error': 'No audio file provided'}), 400
            
            # Save audio temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                audio_file.save(tmp.name)
                temp_path = tmp.name
            
            try:
                # Transcribe using July's methods
                voice_service = july_voice_methods()
                transcription = voice_service.transcribe_audio(temp_path)
                
                # Generate summary if available
                summary = ""
                if july_generate_transcript:
                    summary = july_generate_transcript(transcription)
                
                api_logger.addToLogs("Audio transcription completed")
                
                return jsonify({
                    'transcription': transcription,
                    'summary': summary,
                    'success': True
                })
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
        except Exception as e:
            error_logger.addToErrorLogs(f"Audio transcription error: {str(e)}")
            return jsonify({'error': str(e), 'success': False}), 500

    @app.route('/api/create-calendar-event', methods=['POST'])
    def api_create_calendar_event():
        """Direct integration with August project - Calendar System"""
        try:
            if not august_ai_parser:
                return jsonify({'error': 'Calendar system not available'}), 503
            
            event_title = request.json.get('event_title', '')
            event_datetime = request.json.get('event_datetime', '')
            
            if not event_title or not event_datetime:
                return jsonify({'error': 'Event title and datetime are required'}), 400
            
            # Parse event using August's AI parser
            parser = august_ai_parser()
            event_data = parser.parse_event_command(f"Create event '{event_title}' on {event_datetime}")
            
            api_logger.addToLogs(f"Calendar event created: {event_title}")
            
            return jsonify({
                'event': event_data,
                'message': f'Event "{event_title}" created successfully',
                'success': True
            })
            
        except Exception as e:
            error_logger.addToErrorLogs(f"Calendar event error: {str(e)}")
            return jsonify({'error': str(e), 'success': False}), 500

    @app.route('/api/analyze-directory', methods=['POST'])
    def api_analyze_directory():
        """Direct integration with October project - Directory Summarizer"""
        try:
            if not october_directory_analyzer:
                return jsonify({'error': 'Directory analyzer not available'}), 503
            
            directory_path = request.json.get('directory_path', '')
            
            if not directory_path:
                return jsonify({'error': 'Directory path is required'}), 400
            
            if not os.path.exists(directory_path):
                return jsonify({'error': 'Directory does not exist'}), 400
            
            # Analyze directory using October's analyzer
            analyzer = october_directory_analyzer()
            analysis = analyzer.analyze_directory(directory_path)
            
            # Generate AI summary if available
            summary = ""
            if october_ai_summarizer:
                summarizer = october_ai_summarizer()
                summary = summarizer.generate_summary(analysis)
            
            api_logger.addToLogs(f"Directory analyzed: {directory_path}")
            
            return jsonify({
                'analysis': analysis,
                'summary': summary,
                'success': True
            })
            
        except Exception as e:
            error_logger.addToErrorLogs(f"Directory analysis error: {str(e)}")
            return jsonify({'error': str(e), 'success': False}), 500

    @app.route('/get_login')
    def get_login():
        """Get login page"""
        chatbot_logger.addToLogs("Login page accessed")
        return render_template('login.html')

    @app.route('/get_logs')
    def get_logs():
        """Get logs page"""
        chatbot_logger.addToLogs("Logs page accessed")
        return render_template('logs.html')
        
    @app.route('/login', methods=['POST'])
    def login():
        """Handle login"""
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        api_logger.addToInputLogs("Login attempt", f"Username: {username}")
        
        # Simple authentication (replace with your actual auth logic)
        if username and password:
            session['user_id'] = username
            session['authenticated'] = True
            chatbot_logger.addToLogs(f"User logged in: {username}")
            flash('Login successful!', 'success')
            return redirect(url_for('chatbot_home'))
        else:
            error_logger.addToErrorLogs(f"Failed login attempt for username: {username}")
            flash('Invalid credentials', 'error')
            return redirect(url_for('get_login'))
    
    @app.route('/logout')
    def logout():
        """Handle logout"""
        user_id = session.get('user_id', 'Unknown')
        session.clear()
        chatbot_logger.addToLogs(f"User logged out: {user_id}")
        flash('Logged out successfully', 'info')
        return redirect(url_for('get_login'))
    
    # Logger viewing routes
    @app.route('/logs')
    def view_logs():
        """View all logs"""
        if not session.get('authenticated'):
            return redirect(url_for('get_login'))
        
        try:
            # Get logs from logger
            logs = chatbot_logger.getLogs()
            api_logs = api_logger.getLogs()
            error_logs = error_logger.getLogs()
            
            return render_template('logs.html', 
                                    logs=logs, 
                                    api_logs=api_logs, 
                                    error_logs=error_logs)
        except Exception as e:
            error_logger.addToErrorLogs(f"Error viewing logs: {str(e)}")
            flash('Error loading logs', 'error')
            return redirect(url_for('chatbot_home'))
    
    @app.route('/logs/chatbot')
    def view_chatbot_logs():
        """View chatbot logs only"""
        if not session.get('authenticated'):
            return redirect(url_for('get_login'))
        
        try:
            logs = chatbot_logger.getLogs()
            return render_template('chatbot_logs.html', logs=logs)
        except Exception as e:
            error_logger.addToErrorLogs(f"Error viewing chatbot logs: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/logs/api')
    def view_api_logs():
        """View API logs only"""
        if not session.get('authenticated'):
            return redirect(url_for('get_login'))
        
        try:
            logs = api_logger.getLogs()
            return render_template('api_logs.html', logs=logs)
        except Exception as e:
            error_logger.addToErrorLogs(f"Error viewing API logs: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/logs/errors')
    def view_error_logs():
        """View error logs only"""
        if not session.get('authenticated'):
            return redirect(url_for('get_login'))
        
        try:
            logs = error_logger.getLogs()
            return render_template('error_logs.html', logs=logs)
        except Exception as e:
            flash('Error loading error logs', 'error')
            return redirect(url_for('chatbot_home'))
    
    @app.route('/logs/clear', methods=['POST'])
    def clear_logs():
        """Clear all logs"""
        if not session.get('authenticated'):
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            log_type = request.json.get('log_type', 'all')
            
            if log_type == 'all' or log_type == 'chatbot':
                chatbot_logger.clearLogs()
            if log_type == 'all' or log_type == 'api':
                api_logger.clearLogs()
            if log_type == 'all' or log_type == 'error':
                error_logger.clearLogs()
            
            chatbot_logger.addToLogs(f"Logs cleared: {log_type}")
            return jsonify({'success': True, 'message': f'{log_type} logs cleared'})
        except Exception as e:
            error_logger.addToErrorLogs(f"Error clearing logs: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/logs/download/<log_type>')
    def download_logs(log_type):
        """Download logs as text file"""
        if not session.get('authenticated'):
            return redirect(url_for('get_login'))
        
        try:
            if log_type == 'chatbot':
                logs = chatbot_logger.getLogs()
            elif log_type == 'api':
                logs = api_logger.getLogs()
            elif log_type == 'error':
                logs = error_logger.getLogs()
            else:
                return jsonify({'error': 'Invalid log type'}), 400
            
            # Create text file
            log_text = '\n'.join(logs)
            
            response = make_response(log_text)
            response.headers['Content-Type'] = 'text/plain'
            response.headers['Content-Disposition'] = f'attachment; filename={log_type}_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            
            chatbot_logger.addToLogs(f"Logs downloaded: {log_type}")
            return response
        except Exception as e:
            error_logger.addToErrorLogs(f"Error downloading logs: {str(e)}")
            flash('Error downloading logs', 'error')
            return redirect(url_for('view_logs'))
    
    @app.route('/api/logs/recent')
    def get_recent_logs():
        """Get recent logs via API"""
        if not session.get('authenticated'):
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            limit = request.args.get('limit', 50, type=int)
            log_type = request.args.get('type', 'all')
            
            logs_data = {}
            
            if log_type == 'all' or log_type == 'chatbot':
                logs_data['chatbot'] = chatbot_logger.getLogs()[-limit:]
            if log_type == 'all' or log_type == 'api':
                logs_data['api'] = api_logger.getLogs()[-limit:]
            if log_type == 'all' or log_type == 'error':
                logs_data['error'] = error_logger.getLogs()[-limit:]
            
            return jsonify({
                'logs': logs_data,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
        except Exception as e:
            error_logger.addToErrorLogs(f"Error getting recent logs: {str(e)}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    # Statistics and monitoring routes
    @app.route('/stats')
    def view_stats():
        """View system statistics"""
        if not session.get('authenticated'):
            return redirect(url_for('get_login'))
        
        try:
            stats = {
                'total_chatbot_logs': len(chatbot_logger.getLogs()),
                'total_api_logs': len(api_logger.getLogs()),
                'total_error_logs': len(error_logger.getLogs()),
                'available_apps': sum(1 for app in get_available_apps().values() if app['available']),
                'total_apps': len(get_available_apps()),
                'active_sessions': len(chatbot_engine.conversation_history) if hasattr(chatbot_engine, 'conversation_history') else 0
            }
            
            return render_template('stats.html', stats=stats)
        except Exception as e:
            error_logger.addToErrorLogs(f"Error viewing stats: {str(e)}")
            flash('Error loading statistics', 'error')
            return redirect(url_for('chatbot_home'))
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        try:
            available_apps = get_available_apps()
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'apps': {
                    app_id: app['available'] 
                    for app_id, app in available_apps.items()
                },
                'services': {
                    'chatbot': chatbot_engine is not None,
                    'ai_service': ai_service is not None,
                    'prompt_manager': prompt_manager is not None,
                    'logging': all([chatbot_logger, api_logger, error_logger])
                }
            }
            
            return jsonify(health_status)
        except Exception as e:
            error_logger.addToErrorLogs(f"Health check error: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    chatbot_logger.addToLogs("All routes registered successfully")    

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