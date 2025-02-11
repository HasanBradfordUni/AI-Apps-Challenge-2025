from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import UploadForm
from .models import ProjectDetails, EvaluationResults
from .utils import process_files, generate_evaluation

app = Blueprint('app', __name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        project_name = form.project_name.data
        expected_results = form.expected_results.data
        actual_results = form.actual_results.data
        context = form.context.data

        # Process the uploaded files and generate evaluation
        evaluation = process_files(expected_results, actual_results, context)
        
        # Save project details and evaluation results
        project_details = ProjectDetails(name=project_name, context=context)
        evaluation_results = EvaluationResults(evaluation=evaluation)

        # Redirect to results page
        return redirect(url_for('app.results', project_id=project_details.id))

    return render_template('upload.html', form=form)

@app.route('/results/<int:project_id>')
def results(project_id):
    # Fetch the evaluation results based on project_id
    evaluation_results = EvaluationResults.query.get(project_id)
    return render_template('results.html', evaluation=evaluation_results)