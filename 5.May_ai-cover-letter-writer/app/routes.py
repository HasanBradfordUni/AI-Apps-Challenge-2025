from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
from .forms import UploadForm, UserForm, CVForm, JobForm, CoverLetterForm
from .models import create_connection, create_tables, add_user, add_skill, add_education, add_experience
from .models import save_cover_letter, get_cover_letter, get_user_cover_letters, find_user_by_email
from .utils import extract_text_from_pdf, generate_cover_letter, refine_cover_letter, extract_cv_structure, model

app = Blueprint('app', __name__)

# Database connection
db_path = os.path.join(os.path.dirname(__file__), 'static', 'database.db')
connection = create_connection(db_path)
create_tables(connection)

@app.route('/')
def index():
    return render_template('index.html')

cv_text = ""

@app.route('/upload_cv', methods=['GET', 'POST'])
def upload_cv():
    global cv_text
    form = UploadForm()
    if form.validate_on_submit():
        # Process uploaded files
        files = request.files.getlist('files')
        if not files:
            flash('No files uploaded', 'error')
            return redirect(url_for('app.upload_cv'))
        
        # Extract text from each file
        for file in files:
            if file:
                cv_text += extract_text_from_pdf(file)
        
        flash('CV processed successfully!', 'success')
        return redirect(url_for('app.profile'))
    
    return render_template('upload_cv.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UserForm()
    if form.validate_on_submit():
        # Save user profile data
        user = find_user_by_email(connection, form.email.data)
        if user:
            flash('Email already exists. Signing you in.', 'success')
            session['user_id'] = user[0]  # Assuming the first column is the user ID
            return redirect(url_for('app.cv_details'))
        else:
            user_id = add_user(connection, form.name.data, form.email.data)
            if not user_id:
                flash('Error creating user profile', 'error')
                return redirect(url_for('app.index'))
            session['user_id'] = user_id
            flash('Profile saved successfully!', 'success')
            return redirect(url_for('app.cv_details'))
    
    return render_template('profile.html', form=form)

@app.route('/cv', methods=['GET', 'POST'])
def cv_details():
    global cv_text
    if 'user_id' not in session:
        flash('Please create a profile first', 'warning')
        return redirect(url_for('app.profile'))
    
    form = CVForm()
    
    # Handle form submission
    if form.validate_on_submit():
        # Process CV file if uploaded
        if form.cv_file.data:
            cv_text = extract_text_from_pdf(form.cv_file.data)
        
        # Save skills
        for skill in form.skills.data:
            add_skill(connection, session['user_id'], skill['skill_name'], skill['proficiency'])
        
        # Save education
        for edu in form.education.data:
            add_education(
                connection, 
                session['user_id'], 
                edu['institution'], 
                edu['degree'], 
                edu['field'], 
                edu['start_date'], 
                edu['end_date']
            )
        
        # Save experience
        for exp in form.experience.data:
            add_experience(
                connection, 
                session['user_id'], 
                exp['company'], 
                exp['position'], 
                exp['exp_description'], 
                exp['start_date'], 
                exp['end_date']
            )
        
        flash('CV details saved successfully!', 'success')
        return redirect(url_for('app.job_details'))
    
    # Auto-populate form if CV is uploaded via AJAX
    if request.method == 'POST' and 'cv_file' in request.files:
        uploaded_file = request.files['cv_file']
        if uploaded_file.filename != '':
            try:
                # Extract text from CV
                cv_text = extract_text_from_pdf(uploaded_file)
                
                # Extract structured data using Gemini
                cv_data = extract_cv_structure(cv_text)
                
                if cv_data:
                    # Return structured data as JSON for client-side form population
                    return jsonify({
                        'success': True,
                        'data': cv_data
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Could not extract structured data from CV'
                    })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Error processing CV: {str(e)}'
                })
    
    return render_template('cv_details.html', form=form)

@app.route('/job', methods=['GET', 'POST'])
def job_details():
    if 'user_id' not in session:
        flash('Please create a profile first', 'warning')
        return redirect(url_for('app.profile'))
    
    form = JobForm()
    if form.validate_on_submit():
        # Process job description file if uploaded
        job_description = ""
        if form.job_description_file.data:
            job_description = extract_text_from_pdf(form.job_description_file.data)
        else:
            job_description = form.job_description_text.data
        
        session['job_title'] = form.job_title.data
        session['company_name'] = form.company_name.data
        session['job_description'] = job_description
        
        return redirect(url_for('app.generate_letter'))
    
    return render_template('job_details.html', form=form)

@app.route('/generate', methods=['GET', 'POST'])
def generate_letter():
    if 'user_id' not in session or 'job_description' not in session:
        flash('Please complete all previous steps first', 'warning')
        return redirect(url_for('app.index'))
    
    job_description = session.get('job_description', '')
    
    # Generate cover letter
    cover_letter = generate_cover_letter(cv_text, job_description)
    
    form = CoverLetterForm(cover_letter=cover_letter)
    if form.validate_on_submit():
        # Save the final cover letter
        letter_id = save_cover_letter(
            connection,
            session['user_id'],
            session.get('job_title', ''),
            session.get('company_name', ''),
            job_description,
            form.cover_letter.data
        )
        
        return redirect(url_for('app.view_letter', letter_id=letter_id))
    
    return render_template('generate_letter.html', form=form)

@app.route('/view/<int:letter_id>')
def view_letter(letter_id):
    letter_data = get_cover_letter(connection, letter_id)
    if not letter_data:
        flash('Cover letter not found', 'error')
        return redirect(url_for('app.index'))
    
    return render_template('view_letter.html', letter=letter_data)

@app.route('/history')
def letter_history():
    if 'user_id' not in session:
        flash('Please sign in first', 'warning')
        return redirect(url_for('app.profile'))
    
    letters = get_user_cover_letters(connection, session['user_id'])
    return render_template('letter_history.html', letters=letters)

@app.route('/api/refine_letter', methods=['POST'])
def refine_letter_api():
    data = request.json
    original_letter = data.get('original_letter', '')
    feedback = data.get('feedback', '')
    
    refined_letter = refine_cover_letter(original_letter, feedback)
    return jsonify({'refined_letter': refined_letter})

@app.route('/process_cv', methods=['POST', 'GET'])
def process_cv():
    global cv_text
    
    if 'cv_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['cv_file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    try:
        # Extract text from CV
        cv_text = extract_text_from_pdf(file)
        session['cv_text'] = cv_text  # Store in session for later use
        
        print(f"Extracted text (first 100 chars): {cv_text[:100]}...")
        
        # Extract structured data using Gemini
        cv_data = extract_cv_structure(cv_text)
        
        if cv_data:
            # Validate the structure of cv_data
            if (isinstance(cv_data, dict) and 
                'skills' in cv_data and 
                'education' in cv_data and 
                'experience' in cv_data):
                
                return jsonify({
                    'success': True,
                    'data': cv_data
                })
            else:
                print(f"Invalid CV data structure: {cv_data}")
                return jsonify({
                    'success': False,
                    'message': 'Invalid data structure from CV parsing'
                })
        else:
            # Provide a fallback structure
            fallback_data = {
                'skills': [{'skill_name': '', 'proficiency': 'beginner'}],
                'education': [{'institution': '', 'degree': '', 'field': '', 'start_date': None, 'end_date': None}],
                'experience': [{'company': '', 'position': '', 'exp_description': '', 'start_date': None, 'end_date': None}]
            }
            
            return jsonify({
                'success': True,
                'data': fallback_data,
                'message': 'Could not extract data from CV, please fill in manually'
            })
    except Exception as e:
        print(f"Exception in process_cv: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing CV: {str(e)}'
        })

@app.route('/debug_cv_extraction', methods=['GET', 'POST'])
def debug_cv_extraction():
    if request.method == 'POST':
        if 'cv_file' not in request.files:
            return "No file uploaded"
        
        file = request.files['cv_file']
        if file.filename == '':
            return "No file selected"
        
        try:
            # Extract text
            text = extract_text_from_pdf(file)
            
            # Try to get structured data
            response = model.generate_content(f"""
            Extract structured information from this CV:
            {text[:2000]}  # First 2000 chars for brevity
            
            Return ONLY valid JSON without explanations.
            """)
            
            # Return the raw response for inspection
            return f"""
            <h3>Extracted Text (first 500 chars)</h3>
            <pre>{text[:500]}</pre>
            
            <h3>Raw Gemini Response</h3>
            <pre>{response.text}</pre>
            """
        except Exception as e:
            return f"Error: {str(e)}"
            
    return """
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="cv_file">
        <button type="submit">Upload and Test</button>
    </form>
    """