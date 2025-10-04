from google import genai
from google.genai.types import GenerateContentConfig
from google.genai import Client
import google.auth
import json
import os

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
        self.client = client
        self.model_name = "gemini-2.0-flash"
        self.ai_available = AI_AVAILABLE
    
    def generate_directory_insights(self, analysis_result, content_analysis):
        """Generate AI-powered insights about the directory"""
        if not self.ai_available:
            return self._generate_fallback_insights(analysis_result, content_analysis)
        
        prompt = f"""
        Analyze this directory structure and content data to provide comprehensive insights:
        
        Directory Analysis:
        - Total Files: {analysis_result.get('total_files', 0)}
        - Total Size: {self._format_size(analysis_result.get('total_size', 0))}
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating AI insights: {e}")
            return self._generate_fallback_insights(analysis_result, content_analysis)
    
    def generate_template_matching_summary(self, matching_results):
        """Generate summary of template matching results"""
        if not self.ai_available:
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating template matching summary: {e}")
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
        total_files = analysis_result.get('total_files', 0)
        total_size = analysis_result.get('total_size', 0)
        file_types = analysis_result.get('file_type_categories', {})
        average_file_size = analysis_result.get('average_file_size', 0)
        
        # Basic text-based insights
        insights = [
            f"Total number of files: {total_files}",
            f"Total size of directory: {self._format_size(total_size)}",
            f"Average file size: {self._format_size(average_file_size)}",
            "File types and counts:",
        ]
        
        for file_type, count in file_types.items():
            insights.append(f"- {file_type}: {count} files")
        
        return "\n".join(insights)
    
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