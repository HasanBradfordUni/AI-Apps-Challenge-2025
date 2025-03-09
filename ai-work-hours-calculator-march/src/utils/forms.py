from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class WorkHoursForm(FlaskForm):
    expected_hours = IntegerField("Hours Worked", validators=[DataRequired()])
    time_frame = SelectField("Time Frame", choices=[("day", "Per Day"), ("week", "Per Week")], validators=[DataRequired()])
    work_hours_description = TextAreaField("Work Hours Description", validators=[DataRequired()])
    submit = SubmitField("Submit")