from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import UploadForm
from .models import *
from .utils import *
import os

app = Blueprint('app', __name__)
db_path = os.path.join(os.path.dirname(__file__), 'static', 'database.db')
connection = create_connection(db_path)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        project_name = form.project_name.data
        project_description = form.project_description.data
        test_query = form.test_query.data
        expected_results = form.expected_results.data
        actual_results = form.actual_results.data
        context = form.context.data

        # Process the uploaded files and generate evaluation
        expected_result_text, actual_result_text = process_files(expected_results, actual_results)
        
        # Save project details and evaluation results
        add_user_input(connection, project_name, test_query, additional_details=project_description, context=context)

        user_input_id = get_last_row_id(connection)
        
        expected_results_filename = expected_results.filename
        actual_results_filename = actual_results.filename

        add_uploaded_file(connection, "expected_results", expected_results_filename, user_input_id)
        add_uploaded_file(connection, "actual_results", actual_results_filename, user_input_id)

        comparison_result = generate_ai_comparison(project_name, test_query, expected_result_text, actual_result_text)
        evaluation_summary = generate_summary(comparison_result)
        
        add_evaluation_result(connection, user_input_id, expected_result_text, actual_result_text, comparison_result, evaluation_summary)

        # Redirect to results page
        return redirect(url_for('app.results', project_id=user_input_id))

    return render_template('upload.html', form=form)

@app.route('/results/<int:project_id>')
def results(project_id):
    # Fetch the evaluation results based on project_id
    evaluation_results = get_evaluation_result(connection, project_id)
    return render_template('results.html', evaluation=evaluation_results)