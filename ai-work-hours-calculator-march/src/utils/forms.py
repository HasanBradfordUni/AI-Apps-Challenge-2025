from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class WorkHoursForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    hours_worked = IntegerField("Hours Worked", validators=[DataRequired()])
    submit = SubmitField("Submit")