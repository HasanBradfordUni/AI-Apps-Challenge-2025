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