from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired()])
    expected_results = FileField('Upload Expected Results (PDF)', validators=[DataRequired()])
    actual_results = FileField('Upload Actual Results (Screenshot)', validators=[DataRequired()])
    test_query = StringField('Test Query', validators=[DataRequired()])
    context = TextAreaField('Additional Context')
    submit = SubmitField('Submit')