import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

class CodeProcessor:
    """Handles code processing, analysis, and export functionality"""
    
    def __init__(self):
        self.supported_languages = {
            'python': {'extension': '.py', 'comment': '#'},
            'javascript': {'extension': '.js', 'comment': '//'},
            'typescript': {'extension': '.ts', 'comment': '//'},
            'java': {'extension': '.java', 'comment': '//'},
            'cpp': {'extension': '.cpp', 'comment': '//'},
            'c': {'extension': '.c', 'comment': '//'},
            'csharp': {'extension': '.cs', 'comment': '//'},
            'php': {'extension': '.php', 'comment': '//'},
            'ruby': {'extension': '.rb', 'comment': '#'},
            'go': {'extension': '.go', 'comment': '//'},
            'rust': {'extension': '.rs', 'comment': '//'},
            'swift': {'extension': '.swift', 'comment': '//'},
            'kotlin': {'extension': '.kt', 'comment': '//'},
            'scala': {'extension': '.scala', 'comment': '//'},
            'html': {'extension': '.html', 'comment': '<!--'},
            'css': {'extension': '.css', 'comment': '/*'},
            'scss': {'extension': '.scss', 'comment': '//'},
            'sass': {'extension': '.sass', 'comment': '//'},
            'less': {'extension': '.less', 'comment': '//'},
            'xml': {'extension': '.xml', 'comment': '<!--'},
            'json': {'extension': '.json', 'comment': '//'},
            'yaml': {'extension': '.yaml', 'comment': '#'},
            'yml': {'extension': '.yml', 'comment': '#'},
            'sql': {'extension': '.sql', 'comment': '--'},
            'bash': {'extension': '.sh', 'comment': '#'},
            'powershell': {'extension': '.ps1', 'comment': '#'},
            'batch': {'extension': '.bat', 'comment': 'REM'},
            'perl': {'extension': '.pl', 'comment': '#'},
            'r': {'extension': '.r', 'comment': '#'},
            'matlab': {'extension': '.m', 'comment': '%'},
            'lua': {'extension': '.lua', 'comment': '--'},
            'dart': {'extension': '.dart', 'comment': '//'},
            'haskell': {'extension': '.hs', 'comment': '--'},
            'erlang': {'extension': '.erl', 'comment': '%'},
            'elixir': {'extension': '.ex', 'comment': '#'},
            'clojure': {'extension': '.clj', 'comment': ';;'},
            'scheme': {'extension': '.scm', 'comment': ';;'},
            'lisp': {'extension': '.lisp', 'comment': ';;'},
            'fortran': {'extension': '.f90', 'comment': '!'},
            'cobol': {'extension': '.cob', 'comment': '*'},
            'assembly': {'extension': '.asm', 'comment': ';'},
            'vhdl': {'extension': '.vhd', 'comment': '--'},
            'verilog': {'extension': '.v', 'comment': '//'},
            'other': {'extension': '.txt', 'comment': '#'}
        }
        
        self.export_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports')
        os.makedirs(self.export_folder, exist_ok=True)
    
    def get_supported_file_types(self):
        """Get list of all supported file types for dropdown"""
        file_types = []
        for language, info in self.supported_languages.items():
            if language != 'other':
                file_types.append({
                    'value': language,
                    'label': f"{language.title()} ({info['extension']})",
                    'extension': info['extension']
                })
        return sorted(file_types, key=lambda x: x['label'])
    
    def export_code_only(self, code_content: str, language: str, session_id: str) -> str:
        """Export only the code content as the specified file type"""
        
        # Get file extension for the language
        lang_info = self.supported_languages.get(language, self.supported_languages['other'])
        extension = lang_info['extension']
        
        filename = f"{session_id}_code{extension}"
        file_path = os.path.join(self.export_folder, filename)
        
        # Write only the code content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        return file_path
    
    def download_session_summary(self, code_content: str, ai_suggestion: str, language: str, 
                                session_id: str, export_format: str, settings: Dict = None) -> str:
        """Download session summary as plaintext or markdown without comment symbols"""
        
        if export_format == 'markdown' or export_format == 'md':
            filename = f"{session_id}_session_summary.md"
            file_path = os.path.join(self.export_folder, filename)
            
            # Create markdown content
            markdown_content = f"""# AI Programming Assistant Session Summary

**Session ID:** {session_id}  
**Language:** {language.title()}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📝 Original Code

```{language}
{code_content}
```

---

## 🤖 AI Assistance

{ai_suggestion}

---

## ⚙️ Session Settings

"""
            
            if settings:
                markdown_content += f"- **Assistance Type:** {settings.get('type', 'N/A').title()}\n"
                if settings.get('context'):
                    markdown_content += f"- **Context:** {settings.get('context')}\n"
                if settings.get('error_message'):
                    markdown_content += f"- **Error Message:** {settings.get('error_message')}\n"
                if settings.get('doc_type'):
                    markdown_content += f"- **Documentation Type:** {settings.get('doc_type')}\n"
            else:
                markdown_content += "- No specific settings recorded\n"
            
            markdown_content += f"\n---\n\n*Generated by Has AI - AI Programming Assistant*"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        else:  # Default to txt format
            filename = f"{session_id}_session_summary.txt"
            file_path = os.path.join(self.export_folder, filename)
            
            # Create plain text content
            text_content = f"""AI Programming Assistant Session Summary

Session ID: {session_id}
Language: {language.title()}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*60}
ORIGINAL CODE
{'='*60}

{code_content}

{'='*60}
AI ASSISTANCE
{'='*60}

{ai_suggestion}

{'='*60}
SESSION SETTINGS
{'='*60}

"""
            
            if settings:
                text_content += f"Assistance Type: {settings.get('type', 'N/A').title()}\n"
                if settings.get('context'):
                    text_content += f"Context: {settings.get('context')}\n"
                if settings.get('error_message'):
                    text_content += f"Error Message: {settings.get('error_message')}\n"
                if settings.get('doc_type'):
                    text_content += f"Documentation Type: {settings.get('doc_type')}\n"
            else:
                text_content += "No specific settings recorded\n"
            
            text_content += f"\n{'='*60}\n\nGenerated by Has AI - AI Programming Assistant"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
        
        return file_path
    
    # Keep the original export_code method for backward compatibility
    def export_code(self, code_content: str, ai_suggestion: str, language: str, 
                   export_format: str, session_id: str, settings: Dict = None) -> str:
        """Legacy export method - redirects to new methods"""
        
        if export_format in ['txt', 'markdown', 'md']:
            return self.download_session_summary(code_content, ai_suggestion, language, 
                                               session_id, export_format, settings)
        else:
            return self.export_code_only(code_content, language, session_id)