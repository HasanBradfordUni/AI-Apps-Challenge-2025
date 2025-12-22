from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Optional

class DocumentSummaryForm(FlaskForm):
    # Document file upload
    document_file = FileField(
        "Upload Document (PDF, DOCX, TXT)", 
        validators=[
            Optional(),
            FileAllowed(['pdf', 'docx', 'txt'], 'Document files only! Supported: PDF, DOCX, TXT')
        ]
    )
    
    # Summary type selection
    summary_type = SelectField(
        "Summary Type", 
        choices=[
            ("general", "General Summary"),
            ("academic", "Academic Summary"),
            ("business", "Business Summary"),
            ("technical", "Technical Summary"),
            ("legal", "Legal Summary"),
            ("research", "Research Summary"),
            ("executive", "Executive Summary")
        ], 
        validators=[DataRequired()],
        default="general"
    )
    
    # Summary length
    summary_length = SelectField(
        "Summary Length",
        choices=[
            ("brief", "Brief (1-2 paragraphs)"),
            ("medium", "Medium (3-4 paragraphs)"),
            ("long", "Long (5+ paragraphs)"),
            ("bullet", "Bullet Points"),
            ("custom", "Custom Length")
        ],
        validators=[DataRequired()],
        default="medium"
    )
    
    # Summary tone
    summary_tone = SelectField(
        "Summary Tone",
        choices=[
            ("neutral", "Neutral"),
            ("formal", "Formal"),
            ("casual", "Casual"),
            ("technical", "Technical"),
            ("simplified", "Simplified")
        ],
        validators=[DataRequired()],
        default="neutral"
    )
    
    # Custom summary instructions
    custom_instructions = TextAreaField(
        "Custom Instructions (Optional)",
        render_kw={"placeholder": "Enter any specific requirements for your summary..."}
    )
    
    # Focus areas
    focus_areas = StringField(
        "Focus Areas (Optional)",
        validators=[Optional()],
        render_kw={"placeholder": "e.g., key findings, methodology, conclusions"}
    )
    
    # Custom word count for summaries
    custom_word_count = IntegerField(
        "Custom Word Count (Optional)",
        validators=[Optional()],
        render_kw={"placeholder": "Enter desired word count"}
    )
    
    # Submit buttons
    submit_file = SubmitField("Upload & Summarize")
    regenerate_summary = SubmitField("Regenerate Summary")
    compare_summaries = SubmitField("Compare Different Summaries")

class WorkHoursForm(FlaskForm):
    expected_hours = IntegerField("Contracted Hours", validators=[DataRequired()])
    time_frame = SelectField("Time Frame", choices=[("day", "Per Day"), ("week", "Per Week")], validators=[DataRequired()])
    work_hours_description = TextAreaField("Work Hours Description", validators=[DataRequired()])
    submit = SubmitField("Submit")

class CodeAssistantForm(FlaskForm):
    # Code input
    code_input = TextAreaField(
        "Code Input", 
        validators=[DataRequired()],
        render_kw={
            "placeholder": "Enter your code here...",
            "rows": 15,
            "class": "code-editor"
        }
    )
    
    # Programming language selection
    programming_language = SelectField(
        "Programming Language", 
        choices=[
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("java", "Java"),
            ("cpp", "C++"),
            ("csharp", "C#"),
            ("php", "PHP"),
            ("ruby", "Ruby"),
            ("go", "Go"),
            ("rust", "Rust"),
            ("typescript", "TypeScript"),
            ("html", "HTML"),
            ("css", "CSS"),
            ("sql", "SQL"),
            ("bash", "Bash/Shell"),
            ("other", "Other")
        ], 
        validators=[DataRequired()],
        default="python"
    )
    
    # Type of assistance needed
    assistance_type = SelectField(
        "Assistance Type",
        choices=[
            ("suggestion", "Code Suggestions"),
            ("error_explanation", "Error Explanation"),
            ("documentation", "Generate Documentation"),
            ("completion", "Code Completion"),
            ("refactoring", "Code Refactoring"),
            ("optimization", "Performance Optimization")
        ],
        validators=[DataRequired()],
        default="suggestion"
    )
    
    # Context for better AI assistance
    context = TextAreaField(
        "Context/Description (Optional)",
        render_kw={
            "placeholder": "Describe what you're trying to achieve or any specific requirements...",
            "rows": 3
        }
    )
    
    # Error message for debugging
    error_message = TextAreaField(
        "Error Message (For Error Explanation)",
        render_kw={
            "placeholder": "Paste the error message here if you need help debugging...",
            "rows": 4
        }
    )
    
    # Documentation type
    doc_type = SelectField(
        "Documentation Type",
        choices=[
            ("docstring", "Docstrings/Function Documentation"),
            ("comments", "Inline Comments"),
            ("readme", "README Documentation"),
            ("api", "API Documentation"),
            ("general", "General Documentation")
        ],
        default="docstring"
    )
    
    # Code style preference
    code_style = SelectField(
        "Code Style Preference",
        choices=[
            ("standard", "Language Standard"),
            ("google", "Google Style Guide"),
            ("pep8", "PEP 8 (Python)"),
            ("airbnb", "Airbnb Style Guide"),
            ("prettier", "Prettier (JavaScript)"),
            ("custom", "Custom Style")
        ],
        default="standard"
    )
    
    # Complexity level
    complexity_level = SelectField(
        "Code Complexity Level",
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
            ("expert", "Expert")
        ],
        default="intermediate"
    )
    
    # Submit buttons
    submit_code = SubmitField("Get AI Assistance")
    analyze_code = SubmitField("Analyze Code Quality")
    generate_tests = SubmitField("Generate Test Cases")

class FileUploadForm(FlaskForm):
    # Code file upload
    code_file = FileField(
        "Upload Code File", 
        validators=[
            Optional(),
            FileAllowed(['py', 'js', 'java', 'cpp', 'c', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'ts', 'html', 'css', 'sql', 'sh', 'txt'], 
                       'Code files only! Supported formats: .py, .js, .java, .cpp, .c, .h, .cs, .php, .rb, .go, .rs, .ts, .html, .css, .sql, .sh, .txt')
        ]
    )
    
    submit_file = SubmitField("Upload & Analyze")