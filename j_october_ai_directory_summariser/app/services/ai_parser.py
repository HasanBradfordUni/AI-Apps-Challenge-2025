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
        """Generate AI-powered insights about the directory with balanced content and structure analysis"""
        self.logger.addToLogs("Starting AI insights generation")
        
        if not self.ai_available:
            self.logger.addToLogs("AI not available, using fallback insights")
            return self._generate_fallback_insights(analysis_result, content_analysis)
        
        total_files = analysis_result.get('total_files', 0)
        total_size = analysis_result.get('total_size', 0)
        
        self.logger.addToLogs(f"Generating insights for {total_files} files, {self._format_size(total_size)}")
        
        # Extract structure information but keep it secondary
        directory_structure = analysis_result.get('directory_structure', {})
        organization_metrics = analysis_result.get('organization_metrics', {})
        
        prompt = f"""
        Analyze this directory comprehensively, focusing primarily on CONTENT and FILES with structure as supporting context:
        
        ## PRIMARY ANALYSIS - FILES & CONTENT
        **File Inventory:**
        - Total Files: {total_files}
        - Total Size: {self._format_size(total_size)}
        - Average File Size: {self._format_size(analysis_result.get('average_file_size', 0))}
        - File Types: {json.dumps(analysis_result.get('file_type_categories', {}), indent=2)}
        - File Extensions: {json.dumps(dict(list(analysis_result.get('file_extensions', {}).items())[:10]), indent=2)}
        
        **Content Analysis:**
        - Total Words: {content_analysis.get('total_word_count', 0):,}
        - Total Characters: {content_analysis.get('total_character_count', 0):,}
        - Supported Files for Analysis: {content_analysis.get('supported_files', 0)}
        - Content by File Type: {json.dumps(content_analysis.get('content_by_type', {}), indent=2)}
        - Largest Content Files: {json.dumps(content_analysis.get('largest_files_by_content', [])[:5], indent=2)}
        
        **Largest Files:** {json.dumps(analysis_result.get('largest_files', [])[:5], indent=2)}
        
        ## SECONDARY CONTEXT - STRUCTURE
        - Directory Count: {directory_structure.get('total_directories', 'N/A')}
        - Structure Depth: {directory_structure.get('max_depth', 'N/A')} levels
        - Organization Score: {organization_metrics.get('organization_score', 'N/A')}/100
        - Empty Directories: {len(directory_structure.get('empty_directories', []))}
        
        **FOCUS YOUR ANALYSIS ON:**
        
        ### 📄 File & Content Overview (PRIMARY FOCUS)
        - What types of files dominate this directory?
        - What can you infer about the purpose/use case from the file types and content?
        - Are there any interesting patterns in file sizes, names, or content?
        - What does the content analysis reveal about the nature of work/documents?
        
        ### 📊 Content Insights & Patterns
        - Analyze the word/character counts and what they suggest
        - Comment on content distribution across different file types
        - Identify any content-heavy vs. lightweight files
        - What does the mix of file types suggest about the directory's purpose?
        
        ### 🎯 Directory Purpose & Usage Assessment
        - Based on files and content, what is this directory likely used for?
        - Is this a work directory, project folder, archive, or something else?
        - What activities or workflows do the files suggest?
        
        ### 📁 Organization & Structure Context (SECONDARY)
        - How does the directory structure support or hinder the content organization?
        - Are files appropriately grouped based on their types and purposes?
        - Any structural improvements that would better serve the content?
        
        ### 🚀 Practical Recommendations
        - File management suggestions based on content types and sizes
        - Content archival or cleanup opportunities
        - Ways to improve content accessibility and organization
        
        Keep the analysis CONTENT-FOCUSED with structure as supporting context. Be practical and actionable.
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
    
    def _format_directory_tree_for_ai(self, tree_data, max_depth=3):
        """Format directory tree for AI analysis (limited depth to avoid token limits)"""
        if not tree_data:
            return "Directory tree not available"
        
        def format_node(node, depth=0, prefix=""):
            if depth > max_depth:
                return "..."
            
            result = f"{prefix}{node.get('name', 'Unknown')}"
            if node.get('type') == 'directory':
                file_count = node.get('file_count', 0)
                dir_count = node.get('directory_count', 0)
                result += f" ({file_count} files, {dir_count} subdirs)"
            
            result += "\n"
            
            children = node.get('children', [])
            for i, child in enumerate(children[:5]):  # Limit to first 5 children
                is_last = i == len(children) - 1
                child_prefix = prefix + ("└── " if is_last else "├── ")
                next_prefix = prefix + ("    " if is_last else "│   ")
                result += format_node(child, depth + 1, child_prefix)
            
            if len(children) > 5:
                result += f"{prefix}{'└── ' if len(children) == 6 else '├── '}... and {len(children) - 5} more\n"
            
            return result
        
        return format_node(tree_data)

    def _generate_enhanced_fallback_insights(self, analysis_result, content_analysis):
        """Enhanced fallback insights including structure analysis"""
        self.logger.addToLogs("Generating enhanced fallback insights")
        
        insights = []
        
        # Basic information
        total_files = analysis_result.get('total_files', 0)
        total_size = analysis_result.get('total_size', 0)
        insights.append(f"# Directory Analysis Report\n")
        insights.append(f"**Total Files:** {total_files:,}")
        insights.append(f"**Total Size:** {self._format_size(total_size)}")
        
        # Directory structure insights
        directory_structure = analysis_result.get('directory_structure', {})
        if directory_structure:
            total_dirs = directory_structure.get('total_directories', 0)
            max_depth = directory_structure.get('max_depth', 0)
            empty_dirs = len(directory_structure.get('empty_directories', []))
            
            insights.append(f"\n## 📁 Directory Structure")
            insights.append(f"- **Total Directories:** {total_dirs}")
            insights.append(f"- **Maximum Depth:** {max_depth} levels")
            insights.append(f"- **Empty Directories:** {empty_dirs}")
            
            if max_depth > 6:
                insights.append(f"- ⚠️ **Note:** Directory structure is quite deep ({max_depth} levels)")
            elif max_depth < 2:
                insights.append(f"- ℹ️ **Note:** Relatively flat directory structure")
        
        # Organization insights
        organization_metrics = analysis_result.get('organization_metrics', {})
        if organization_metrics:
            score = organization_metrics.get('organization_score', 0)
            insights.append(f"\n## 🎯 Organization Quality")
            insights.append(f"- **Organization Score:** {score}/100")
            
            if score >= 80:
                insights.append("- ✅ **Assessment:** Well organized directory structure")
            elif score >= 60:
                insights.append("- 📝 **Assessment:** Moderately organized, some improvements possible")
            else:
                insights.append("- ⚠️ **Assessment:** Directory structure needs significant organization")
            
            issues = organization_metrics.get('potential_issues', [])
            if issues:
                insights.append("- **Issues Found:**")
                for issue in issues:
                    insights.append(f"  - {issue}")
        
        # File type distribution
        file_types = analysis_result.get('file_type_categories', {})
        if file_types:
            insights.append(f"\n## 📊 File Distribution")
            for file_type, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (count / total_files) * 100 if total_files > 0 else 0
                insights.append(f"- **{file_type.upper()}:** {count} files ({percentage:.1f}%)")
        
        # Content insights
        content_files = content_analysis.get('supported_files', 0)
        if content_files > 0:
            total_words = content_analysis.get('total_word_count', 0)
            insights.append(f"\n## 📝 Content Analysis")
            insights.append(f"- **Text Files:** {content_files} files analyzed")
            insights.append(f"- **Total Words:** {total_words:,}")
            insights.append(f"- **Average Words per File:** {total_words // content_files if content_files > 0 else 0}")
        
        result = "\n".join(insights)
        self.logger.addToLogs(f"Enhanced fallback insights generated ({len(result)} characters)")
        return result

    def generate_comprehensive_insights(self, analysis_result, content_analysis, template_analysis, template_statistics):
        """Generate comprehensive AI insights including template analysis"""
        self.logger.addToLogs("Starting comprehensive AI insights generation with template analysis")
        
        if not self.ai_available:
            self.logger.addToLogs("AI not available, using comprehensive fallback insights")
            return self._generate_comprehensive_fallback_insights(analysis_result, content_analysis, template_analysis, template_statistics)
        
        total_files = analysis_result.get('total_files', 0)
        total_size = analysis_result.get('total_size', 0)
        
        # Extract structure information
        directory_structure = analysis_result.get('directory_structure', {})
        organization_metrics = analysis_result.get('organization_metrics', {})
        
        # Prepare template analysis summary for AI
        template_summary = self._prepare_template_summary(template_analysis, template_statistics)
        
        prompt = f"""
        Analyze this directory comprehensively, focusing on CONTENT, FILES, ORGANIZATION, and TEMPLATE USAGE:
        
        ## PRIMARY ANALYSIS - FILES & CONTENT
        **File Inventory:**
        - Total Files: {total_files}
        - Total Size: {self._format_size(total_size)}
        - File Types: {json.dumps(analysis_result.get('file_type_categories', {}), indent=2)}
        
        **Content Analysis:**
        - Total Words: {content_analysis.get('total_word_count', 0):,}
        - Total Characters: {content_analysis.get('total_character_count', 0):,}
        - Supported Files for Analysis: {content_analysis.get('supported_files', 0)}
        - Content by File Type: {json.dumps(content_analysis.get('content_by_type', {}), indent=2)}
        
        ## TEMPLATE ANALYSIS & STANDARDIZATION
        **Template Statistics:**
        {template_summary}
        
        ## ORGANIZATION CONTEXT
        - Directory Count: {directory_structure.get('total_directories', 'N/A')}
        - Structure Depth: {directory_structure.get('max_depth', 'N/A')} levels
        - Organization Score: {organization_metrics.get('organization_score', 'N/A')}/100
        
        **PROVIDE COMPREHENSIVE ANALYSIS ON:**
        
        ### 📄 File & Content Overview (PRIMARY FOCUS)
        - What types of files dominate this directory?
        - What can you infer about the purpose/use case from the file types and content?
        - Are there patterns in file sizes, names, or content distribution?
        - What does the content analysis reveal about the work/document types?
        
        ### 📋 Template Usage & Standardization Assessment
        - How well are templates being utilized in this directory?
        - What does the template matching reveal about consistency and standardization?
        - Are there opportunities to improve template adoption?
        - Which template categories are most/least used and why?
        
        ### 📊 Content & Template Integration Insights
        - How do the identified templates relate to the overall content strategy?
        - Are files following template patterns or are there many custom/unique files?
        - What does template usage suggest about workflow standardization?
        - Any gaps between available templates and actual file types?
        
        ### 🎯 Directory Purpose & Workflow Assessment
        - Based on files, content, and template usage, what is this directory's primary purpose?
        - What workflows and activities do the files and templates suggest?
        - Is this a work directory, project folder, template library, or mixed usage?
        
        ### 📁 Organization & Template Management Context
        - How does the directory structure support template usage and content organization?
        - Are templates and their instances logically grouped?
        - Any structural improvements that would better support template workflows?
        
        ### 🚀 Practical Recommendations
        - Template adoption and standardization suggestions
        - Content organization improvements based on template categories
        - Workflow optimization opportunities
        - Template management and maintenance recommendations
        
        Keep the analysis CONTENT-FOCUSED with template insights as valuable supporting analysis. 
        Emphasize practical, actionable insights for better template utilization and content management.
        """
        
        try:
            self.logger.addToLogs("Sending comprehensive analysis request to Google GenAI")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
            
            insights = response.text.strip()
            self.logger.addToLogs(f"Comprehensive AI insights generated successfully ({len(insights)} characters)")
            return insights
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Error generating comprehensive AI insights: {str(e)}")
            self.logger.addToLogs("Falling back to comprehensive basic insights")
            return self._generate_comprehensive_fallback_insights(analysis_result, content_analysis, template_analysis, template_statistics)

    def _prepare_template_summary(self, template_analysis, template_statistics):
        """Prepare template analysis summary for AI consumption"""
        if not template_statistics:
            return "No template analysis available"
        
        if template_statistics.get('error'):
            return f"Template analysis error: {template_statistics['error']}"
        
        summary_parts = []
        
        # Basic stats
        total_templates = template_statistics.get('total_templates', 0)
        total_matches = template_statistics.get('total_matches', 0)
        template_coverage = template_statistics.get('template_coverage', 0)
        
        summary_parts.append(f"- Total Templates Available: {total_templates}")
        summary_parts.append(f"- Total Template Matches Found: {total_matches}")
        summary_parts.append(f"- Template Coverage: {template_coverage:.1f}% of templates are being used")
        
        # Category breakdown
        category_breakdown = template_statistics.get('category_breakdown', {})
        if category_breakdown:
            summary_parts.append("- Category Breakdown:")
            for category, data in category_breakdown.items():
                summary_parts.append(f"  * {category}: {data['templates']} templates, {data['matches']} matches, {data['avg_similarity']:.3f} avg similarity")
        
        # Top matched templates
        top_templates = template_statistics.get('top_matched_templates', [])
        if top_templates:
            summary_parts.append("- Most Used Templates:")
            for template in top_templates[:5]:
                summary_parts.append(f"  * {template['name']} ({template['category']}): {template['matches']} matches")
        
        # Unused templates
        unused_templates = template_statistics.get('unused_templates', [])
        if unused_templates:
            summary_parts.append(f"- Unused Templates ({len(unused_templates)}): {', '.join(unused_templates[:5])}")
            if len(unused_templates) > 5:
                summary_parts.append(f"  ... and {len(unused_templates) - 5} more")
        
        return "\n".join(summary_parts)

    def _generate_comprehensive_fallback_insights(self, analysis_result, content_analysis, template_analysis, template_statistics):
        """Generate comprehensive fallback insights including template analysis"""
        self.logger.addToLogs("Generating comprehensive fallback insights")
        
        insights = []
        
        # Basic information
        total_files = analysis_result.get('total_files', 0)
        total_size = analysis_result.get('total_size', 0)
        insights.append(f"# Comprehensive Directory Analysis Report\n")
        insights.append(f"**Total Files:** {total_files:,}")
        insights.append(f"**Total Size:** {self._format_size(total_size)}")
        
        # Template analysis section
        if template_statistics and not template_statistics.get('error'):
            insights.append(f"\n## 📋 Template Analysis")
            total_templates = template_statistics.get('total_templates', 0)
            total_matches = template_statistics.get('total_matches', 0)
            template_coverage = template_statistics.get('template_coverage', 0)
            
            insights.append(f"- **Available Templates:** {total_templates}")
            insights.append(f"- **Template Matches Found:** {total_matches}")
            insights.append(f"- **Template Coverage:** {template_coverage:.1f}%")
            
            if template_coverage >= 80:
                insights.append("- ✅ **Assessment:** Excellent template utilization")
            elif template_coverage >= 50:
                insights.append("- 📝 **Assessment:** Good template usage with room for improvement")
            elif template_coverage >= 20:
                insights.append("- ⚠️ **Assessment:** Limited template adoption")
            else:
                insights.append("- 🔴 **Assessment:** Poor template utilization")
            
            # Category breakdown
            category_breakdown = template_statistics.get('category_breakdown', {})
            if category_breakdown:
                insights.append("- **Template Categories:**")
                for category, data in category_breakdown.items():
                    insights.append(f"  - **{category}:** {data['matches']} matches from {data['templates']} templates")
            
            # Unused templates
            unused_templates = template_statistics.get('unused_templates', [])
            if unused_templates:
                insights.append(f"- **Unused Templates:** {len(unused_templates)} templates not found in directory")
        
        # Continue with existing fallback insights structure...
        # Directory structure insights
        directory_structure = analysis_result.get('directory_structure', {})
        if directory_structure:
            total_dirs = directory_structure.get('total_directories', 0)
            max_depth = directory_structure.get('max_depth', 0)
            empty_dirs = len(directory_structure.get('empty_directories', []))
            
            insights.append(f"\n## 📁 Directory Structure")
            insights.append(f"- **Total Directories:** {total_dirs}")
            insights.append(f"- **Maximum Depth:** {max_depth} levels")
            insights.append(f"- **Empty Directories:** {empty_dirs}")
        
        # File type distribution
        file_types = analysis_result.get('file_type_categories', {})
        if file_types:
            insights.append(f"\n## 📊 File Distribution")
            for file_type, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (count / total_files) * 100 if total_files > 0 else 0
                insights.append(f"- **{file_type.upper()}:** {count} files ({percentage:.1f}%)")
        
        # Content insights
        content_files = content_analysis.get('supported_files', 0)
        if content_files > 0:
            total_words = content_analysis.get('total_word_count', 0)
            insights.append(f"\n## 📝 Content Analysis")
            insights.append(f"- **Text Files:** {content_files} files analyzed")
            insights.append(f"- **Total Words:** {total_words:,}")
            insights.append(f"- **Average Words per File:** {total_words // content_files if content_files > 0 else 0}")
        
        result = "\n".join(insights)
        self.logger.addToLogs(f"Comprehensive fallback insights generated ({len(result)} characters)")
        return result

# The AISummarizer class is now equipped with enhanced error handling and fallback mechanisms.
# It provides AI-powered directory insights, template matching summaries, organization suggestions,
# and content theme identification, with graceful degradation to fallback methods when AI services are unavailable.

# Note: The actual AI functionality depends on the availability and accessibility of the Google GenAI services.