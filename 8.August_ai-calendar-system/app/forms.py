from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, SubmitField, HiddenField
from wtforms import FieldList, FormField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    submit = SubmitField('Save Profile')

class RoleTypeForm(FlaskForm):
    role_title = StringField('Job Title', validators=[DataRequired()])
    role_type = SelectField('Employment Type', choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship')
    ], validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    remote_option = SelectField('Remote Work Option', choices=[
        ('office', 'Office-based'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Fully Remote')
    ], validators=[DataRequired()])
    salary_range = StringField('Salary Range', validators=[Optional()])
    template_name = StringField('Template Name (if saving as template)', validators=[Optional()])
    template_id = HiddenField('Template ID')
    load_template = BooleanField('Load Template')
    submit = SubmitField('Continue')

class CertificationForm(FlaskForm):
    name = StringField('Certification Name')
    required = BooleanField('Required')

class QualificationsForm(FlaskForm):
    education_required = SelectField('Minimum Education Required', choices=[
        ('none', 'No formal education required'),
        ('high-school', 'High School Diploma'),
        ('associates', 'Associate\'s Degree'),
        ('bachelors', 'Bachelor\'s Degree'),
        ('masters', 'Master\'s Degree'),
        ('phd', 'Doctorate/PhD')
    ], validators=[DataRequired()])
    certifications = FieldList(FormField(CertificationForm), min_entries=1)
    submit = SubmitField('Continue')

class ResponsibilityForm(FlaskForm):
    description = TextAreaField('Responsibility')

class ExperienceForm(FlaskForm):
    years_experience = IntegerField('Years of Experience Required', validators=[NumberRange(min=0, max=30)])
    specific_experience = TextAreaField('Specific Experience Required', validators=[Optional()])
    responsibilities = FieldList(FormField(ResponsibilityForm), min_entries=3)
    submit = SubmitField('Continue')

class SkillForm(FlaskForm):
    name = StringField('Skill')

class SkillsForm(FlaskForm):
    required_skills = FieldList(FormField(SkillForm), min_entries=1)
    preferred_skills = FieldList(FormField(SkillForm), min_entries=1)
    personality_traits = TextAreaField('Desired Personality Traits', validators=[Optional()])
    about_company = TextAreaField('About Your Company', validators=[Optional()])
    diversity_statement = TextAreaField('Diversity & Inclusion Statement', validators=[Optional()])
    application_process = TextAreaField('Application Process Details', validators=[Optional()])
    submit = SubmitField('Generate Job Ad')

class OutputForm(FlaskForm):
    job_ad = TextAreaField('Generated Job Ad', validators=[DataRequired()])
    save_as_template = BooleanField('Save as Template')
    submit = SubmitField('Save Job Ad')

class JobAdForm(FlaskForm):
    """Main form that combines all sub-forms"""
    role_type = FormField(RoleTypeForm)
    qualifications = FormField(QualificationsForm)
    experience = FormField(ExperienceForm)
    skills = FormField(SkillsForm)
    output = FormField(OutputForm)
    submit = SubmitField('Submit')