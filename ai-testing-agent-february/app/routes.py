from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import UploadForm
from .models import EvaluationResult, UserInput, UploadedFile
from .utils import process_files
from app import db

app = Blueprint('app', __name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        project_name = form.project_name.data
        test_query = form.test_query.data
        expected_results = form.expected_results.data
        actual_results = form.actual_results.data
        context = form.context.data

        # Process the uploaded files and generate evaluation
        expected_result_text, actual_result_text = process_files(expected_results, actual_results)
        
        # Save project details and evaluation results
        user_input = UserInput(project_name=project_name, test_query=test_query, context=context)
        db.session.add(user_input)
        db.session.commit()

        expected_results_file = UploadedFile(file_type='expected', file_path=expected_results, user_input_id=user_input.id)
        actual_results_file = UploadedFile(file_type='actual', file_path=actual_results, user_input_id=user_input.id)
        db.session.add(expected_results_file)
        db.session.add(actual_results_file)
        db.session.commit()
        
        evaluation_result = EvaluationResult(user_input_id=user_input.id, expected_results=expected_result_text, actual_results=actual_result_text, comparison="", summary="")
        db.session.add(evaluation_result)
        db.session.commit()

        # Redirect to results page
        return redirect(url_for('app.results', project_id=user_input.id))

    return render_template('upload.html', form=form)

@app.route('/results/<int:project_id>')
def results(project_id):
    # Fetch the evaluation results based on project_id
    evaluation_results = EvaluationResult.query.filter_by(user_input_id=project_id).first()
    return render_template('results.html', evaluation=evaluation_results)