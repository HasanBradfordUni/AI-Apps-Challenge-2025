from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FieldList, FormField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email

class UploadForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_description = TextAreaField('Project Description')
    expected_results = FileField('Upload Expected Results (PDF)', validators=[DataRequired()])
    actual_results = FileField('Upload Actual Results (Screenshot)', validators=[DataRequired()])
    test_query = StringField('Test Query', validators=[DataRequired()])
    context = TextAreaField('Additional Context')
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Profile')

class SkillForm(FlaskForm):
    skill_name = StringField('Skill', validators=[DataRequired()])
    proficiency = SelectField('Proficiency', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ])

class EducationForm(FlaskForm):
    institution = StringField('Institution', validators=[DataRequired()])
    degree = StringField('Degree', validators=[DataRequired()])
    field = StringField('Field of Study')
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[], render_kw={"type": "date"})
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[], render_kw={"type": "date"})

class ExperienceForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    exp_description = TextAreaField('Description')
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[], render_kw={"type": "date"})
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[], render_kw={"type": "date"})

class CVForm(FlaskForm):
    cv_file = FileField('Upload your CV (PDF)', validators=[
        FileAllowed(['pdf'], 'PDF files only!')
    ])
    skills = FieldList(FormField(SkillForm), min_entries=1)
    education = FieldList(FormField(EducationForm), min_entries=1)
    experience = FieldList(FormField(ExperienceForm), min_entries=1)
    submit = SubmitField('Save CV Details')

class JobForm(FlaskForm):
    job_title = StringField('Job Title', validators=[DataRequired()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    job_description_file = FileField('Upload Job Description (PDF)', validators=[
        FileAllowed(['pdf'], 'PDF files only!')
    ])
    job_description_text = TextAreaField('Or paste job description here')
    submit = SubmitField('Continue')

class CoverLetterForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter', validators=[DataRequired()])
    tone = SelectField('Letter Tone', choices=[
        ('professional', 'Professional'),
        ('enthusiastic', 'Enthusiastic'),
        ('confident', 'Confident'),
        ('creative', 'Creative')
    ])
    submit = SubmitField('Save Cover Letter')