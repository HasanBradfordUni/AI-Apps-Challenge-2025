from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    test_query = db.Column(db.String(250), nullable=False)
    additional_details = db.Column(db.Text, nullable=True)
    context = db.Column(db.Text, nullable=True)

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    user_input_id = db.Column(db.Integer, db.ForeignKey('user_input.id'), nullable=False)

class EvaluationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input_id = db.Column(db.Integer, db.ForeignKey('user_input.id'), nullable=False)
    expected_results = db.Column(db.Text, nullable=False)
    actual_results = db.Column(db.Text, nullable=False)
    comparison = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)