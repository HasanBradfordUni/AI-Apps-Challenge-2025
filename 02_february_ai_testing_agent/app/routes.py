from flask import Blueprint, render_template, request, redirect, url_for, flash
from .forms import UploadForm
from .models import *
from .utils import *
import os
import markdown

app = Blueprint('app', __name__)
db_path = os.path.join(os.path.dirname(__file__), 'static', 'database.db')
connection = create_connection(db_path)
create_tables(connection)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/latest-results')
def latest_results():
    # Get the latest project ID from the database
    try:
        latest_id = get_last_row_id(connection)[0]
        return redirect(url_for('app.results', project_id=latest_id))
    except:
        flash('No test results available yet. Please upload a test first.', 'warning')
        return redirect(url_for('app.upload'))
    
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

        if not project_description:
            project_description = ""
        if not context:
            context = ""

        # Process the uploaded files and generate evaluation
        expected_result_text, actual_result_text = process_files(expected_results, actual_results)
        
        # Save project details and evaluation results
        add_user_input(connection, project_name, test_query, additional_details=project_description, context=context)

        user_input_id = get_last_row_id(connection)[0]
        
        expected_results_filename = expected_results.filename
        actual_results_filename = actual_results.filename

        add_uploaded_file(connection, "expected", expected_results_filename, user_input_id)
        add_uploaded_file(connection, "actual", actual_results_filename, user_input_id)

        comparison_result = generate_ai_comparison(project_name, test_query, expected_result_text, actual_result_text, project_description, context)
        evaluation_summary = generate_summary(comparison_result, project_name, test_query, project_description, context)
        
        add_evaluation_result(connection, user_input_id, expected_result_text, actual_result_text, comparison_result, evaluation_summary)

        # Redirect to results page
        return redirect(url_for('app.results', project_id=user_input_id))

    return render_template('upload.html', form=form)

@app.route('/results/<int:project_id>')
def results(project_id):
    # Fetch the evaluation results based on project_id
    evaluation_results = get_evaluation_result(connection, project_id)
    comparison = evaluation_results[4]
    evaluation = evaluation_results[5]
    
    # Convert markdown to HTML for display
    comparison_html = markdown.markdown(comparison)
    evaluation_html = markdown.markdown(evaluation)
    
    # Extract the summary section (for copy functionality)
    summary = ""
    evaluation_lower = evaluation.lower()
    if "## summary" in evaluation_lower:
        summary_section = evaluation.split("## Summary" if "## Summary" in evaluation else "## summary")[-1]
        # Extract just the first paragraph/sentence for the 150 char limit
        summary = summary_section.strip().split('\n')[0][:150]
    elif "**summary**" in evaluation_lower:
        summary_section = evaluation.split("**Summary**" if "**Summary**" in evaluation else "**summary**")[-1]
        summary = summary_section.strip().split('\n')[0][:150]
    
    return render_template('results.html', ai_result1=comparison_html, ai_result2=evaluation_html, ai_result3=summary)