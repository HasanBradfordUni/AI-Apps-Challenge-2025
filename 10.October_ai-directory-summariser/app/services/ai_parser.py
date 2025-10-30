from google import genai
from google.genai.types import GenerateContentConfig
from google.genai import Client
import google.auth
import json
import os
import datetime

# Remove the autoLogger import section and replace with:
try:
    from ..utils.logger_setup import general_logger
except ImportError:
    # Fallback if logger is not available
    print("Logger import failed for ai parser, using DummyLogger")
    class DummyLogger:
        def __init__(self, filename): 
            self.file = open(filename, 'a')
            self.file.write("Logging started...\n"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\n")
            self.file.close()
        def addToLogs(self, msg): print(f"[LOG] {msg}")
        def addToErrorLogs(self, msg): print(f"[ERROR] {msg}")
        def addToInputLogs(self, prompt, msg): print(f"[INPUT] {prompt}: {msg}")
    general_logger = DummyLogger

# Initialize Google Auth and Client
try:
    credentials, project_id = google.auth.default()
    client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")
    AI_AVAILABLE = True
except Exception as e:
    print(f"AI services not available: {e}")
    AI_AVAILABLE = False
    client = None

class AISummarizer:
    def __init__(self):
        # Initialize logger
        log_file_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'ai_parser.txt')
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        self.logger = general_logger(log_file_path)
        
        self.client = client
        self.model_name = "gemini-2.0-flash"
        self.ai_available = AI_AVAILABLE
        
        if self.ai_available:
            self.logger.addToLogs("AISummarizer initialized with Google GenAI")
        else:
            self.logger.addToLogs("AISummarizer initialized without AI (fallback mode)")
    
    def generate_directory_insights(self, analysis_result, content_analysis):
        """Generate AI-powered insights about the directory"""
        self.logger.addToLogs("Starting AI insights generation")
        
        if not self.ai_available:
            self.logger.addToLogs("AI not available, using fallback insights")
            return self._generate_fallback_insights(analysis_result, content_analysis)
        
        total_files = analysis_result.get('total_files', 0)
        total_size = analysis_result.get('total_size', 0)
        
        self.logger.addToLogs(f"Generating insights for {total_files} files, {self._format_size(total_size)}")
        
        prompt = f"""
        Analyze this directory structure and content data to provide comprehensive insights:
        
        Directory Analysis:
        - Total Files: {total_files}
        - Total Size: {self._format_size(total_size)}
        - File Types: {json.dumps(analysis_result.get('file_type_categories', {}), indent=2)}
        - Average File Size: {self._format_size(analysis_result.get('average_file_size', 0))}
        
        Content Analysis:
        - Total Words: {content_analysis.get('total_word_count', 0)}
        - Total Characters: {content_analysis.get('total_character_count', 0)}
        - Supported Files: {content_analysis.get('supported_files', 0)}
        - Content by Type: {json.dumps(content_analysis.get('content_by_type', {}), indent=2)}
        
        Please provide:
        1. **Directory Overview**: Summarize what type of directory this appears to be
        2. **Content Insights**: Key observations about the content and file composition
        3. **Organization Assessment**: How well organized the directory appears to be
        4. **Recommendations**: Suggestions for better organization or management
        5. **Notable Patterns**: Any interesting patterns or anomalies detected
        
        Keep the analysis professional, concise, and actionable.
        """
        
        try:
            self.logger.addToLogs("Sending request to Google GenAI")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            
            insights = response.text.strip()
            self.logger.addToLogs(f"AI insights generated successfully ({len(insights)} characters)")
            return insights
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Error generating AI insights: {str(e)}")
            self.logger.addToLogs("Falling back to basic insights")
            return self._generate_fallback_insights(analysis_result, content_analysis)
    
    def generate_template_matching_summary(self, matching_results):
        """Generate summary of template matching results"""
        self.logger.addToLogs(f"Generating template matching summary for {len(matching_results)} results")
        
        if not self.ai_available:
            self.logger.addToLogs("AI not available for template matching summary")
            return self._generate_fallback_template_summary(matching_results)
        
        prompt = f"""
        Analyze these template matching results and provide insights:
        
        Template Matching Results:
        {json.dumps(matching_results, indent=2)}
        
        Please provide:
        1. **Matching Overview**: Summary of what was found
        2. **Pattern Analysis**: What patterns emerge from the matches
        3. **Quality Assessment**: How reliable the matches appear to be
        4. **Recommendations**: Suggestions based on the matching results
        
        Keep it concise and focused on actionable insights.
        """
        
        try:
            self.logger.addToLogs("Generating template matching summary with AI")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            
            summary = response.text.strip()
            self.logger.addToLogs("Template matching summary generated successfully")
            return summary
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Error generating template matching summary: {str(e)}")
            return self._generate_fallback_template_summary(matching_results)
    
    def suggest_directory_organization(self, analysis_result, content_analysis):
        """Suggest directory reorganization strategies"""
        if not self.ai_available:
            return self._generate_fallback_organization_suggestions(analysis_result)
        
        prompt = f"""
        Based on this directory analysis, suggest organization improvements:
        
        Current Structure:
        - {analysis_result.get('total_files', 0)} files across {analysis_result.get('total_directories', 0)} directories
        - File types: {json.dumps(analysis_result.get('file_type_categories', {}), indent=2)}
        - Largest files: {json.dumps(analysis_result.get('largest_files', [])[:5], indent=2)}
        
        Content Overview:
        - Content analysis: {json.dumps(content_analysis.get('content_by_type', {}), indent=2)}
        
        Please suggest:
        1. **Folder Structure**: Recommended folder organization
        2. **File Naming**: Naming convention improvements
        3. **Archive Strategy**: What files might need archiving
        4. **Cleanup Opportunities**: Files that might be redundant or outdated
        
        Provide specific, actionable recommendations.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating organization suggestions: {e}")
            return self._generate_fallback_organization_suggestions(analysis_result)
    
    def identify_content_themes(self, content_analysis):
        """Identify themes and topics in the directory content"""
        if not self.ai_available:
            return "AI-powered content theme analysis is not available."
        
        # Get sample content from largest files
        largest_files = content_analysis.get('largest_files_by_content', [])[:10]
        
        if not largest_files:
            return "No content available for theme analysis."
        
        content_sample = ""
        for file_info in largest_files:
            content_sample += f"File: {file_info['name']} ({file_info['word_count']} words)\n"
        
        prompt = f"""
        Based on these file names and content statistics, identify the main themes and topics:
        
        {content_sample}
        
        Content Distribution:
        {json.dumps(content_analysis.get('content_by_type', {}), indent=2)}
        
        Please identify:
        1. **Main Topics**: What are the primary subjects/themes
        2. **Content Categories**: How the content can be categorized
        3. **Purpose Assessment**: What this directory seems to be used for
        4. **Content Quality**: General assessment of content organization
        
        Be specific but concise.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error identifying content themes: {e}")
            return "Unable to analyze content themes at this time."
    
    def _generate_fallback_insights(self, analysis_result, content_analysis):
        """Generate basic insights without AI"""
        self.logger.addToLogs("Generating fallback insights")
        
        total_files = analysis_result.get('total_files', 0)
        total_size = analysis_result.get('total_size', 0)
        file_types = analysis_result.get('file_type_categories', {})
        average_file_size = analysis_result.get('average_file_size', 0)
        
        insights = [
            f"Directory contains {total_files} files",
            f"Total size: {self._format_size(total_size)}",
            f"Average file size: {self._format_size(average_file_size)}",
        ]
        
        if file_types:
            dominant_type = max(file_types.items(), key=lambda x: x[1])
            insights.append(f"Most common file type: {dominant_type[0]} ({dominant_type[1]} files)")
        
        content_files = content_analysis.get('supported_files', 0)
        if content_files > 0:
            total_words = content_analysis.get('total_word_count', 0)
            insights.append(f"Text content: {total_words:,} words across {content_files} files")
        
        result = "\n".join(insights)
        self.logger.addToLogs(f"Fallback insights generated ({len(result)} characters)")
        return result
    
    def _generate_fallback_template_summary(self, matching_results):
        """Generate fallback summary for template matching"""
        return f"Found {len(matching_results)} matching templates. Review manually for details."
    
    def _generate_fallback_organization_suggestions(self, analysis_result):
        """Generate fallback suggestions for directory organization"""
        return "AI-powered organization suggestions are not available."
    
    def _format_size(self, size_in_bytes):
        """Format file size in a human-readable way"""
        if size_in_bytes is None:
            return "N/A"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024
        
        return f"{size_in_bytes:.1f} PB"

# The AISummarizer class is now equipped with enhanced error handling and fallback mechanisms.
# It provides AI-powered directory insights, template matching summaries, organization suggestions,
# and content theme identification, with graceful degradation to fallback methods when AI services are unavailable.

# Note: The actual AI functionality depends on the availability and accessibility of the Google GenAI services.