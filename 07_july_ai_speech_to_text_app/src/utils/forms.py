from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Optional

class SpeechToTextForm(FlaskForm):
    # Audio file upload
    audio_file = FileField(
        "Upload Audio File (MP3, WAV, M4A, MP4)", 
        validators=[
            Optional(),
            FileAllowed(['mp3', 'wav', 'm4a', 'mp4', 'ogg', 'flac'], 'Audio files only!')
        ]
    )
    
    # Summary type selection
    summary_type = SelectField(
        "Summary Type", 
        choices=[
            ("meeting", "Meeting Summary"),
            ("lecture", "Lecture Summary"),
            ("interview", "Interview Summary"),
            ("conversation", "General Conversation"),
            ("quick", "Quick Summary")
        ], 
        validators=[DataRequired()],
        default="meeting"
    )
    
    # Voice training text
    training_text = TextAreaField(
        "Voice Training Text (Read this text aloud for voice training)",
        render_kw={"placeholder": "The quick brown fox jumps over the lazy dog. This sentence contains all letters of the alphabet and is perfect for voice training."}
    )
    
    # User name for voice profile
    user_name = StringField(
        "User Name (for voice profile)",
        validators=[Optional()],
        render_kw={"placeholder": "Enter your name"}
    )
    
    # Voice command input
    voice_command = StringField(
        "Voice Command",
        validators=[Optional()],
        render_kw={"placeholder": "Say: 'Start recording', 'Stop recording', 'Summarize transcript'"}
    )
    
    # Submit buttons
    submit_file = SubmitField("Upload & Transcribe")
    submit_training = SubmitField("Start Voice Training")
    submit_command = SubmitField("Process Voice Command")

class WorkHoursForm(FlaskForm):
    expected_hours = IntegerField("Contracted Hours", validators=[DataRequired()])
    time_frame = SelectField("Time Frame", choices=[("day", "Per Day"), ("week", "Per Week")], validators=[DataRequired()])
    work_hours_description = TextAreaField("Work Hours Description", validators=[DataRequired()])
    submit = SubmitField("Submit")