from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
from .forms import JobAdForm, RoleTypeForm, QualificationsForm, ExperienceForm, SkillsForm, OutputForm, UserForm
from .models import create_connection, create_tables, save_job_ad, get_job_ad, get_user_job_ads, find_user_by_email
from .models import add_user, add_template, get_templates
from .utils import generate_job_ad, refine_job_ad, extract_text_from_pdf, format_for_pdf, model

app = Blueprint('app', __name__)

# Database connection
db_path = os.path.join(os.path.dirname(__file__), 'static', 'database.db')
connection = create_connection(db_path)
create_tables(connection)

@app.route('/')
def index():
    return render_template('index.html')

job_details = {}

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UserForm()
    if form.validate_on_submit():
        # Save user profile data
        user = find_user_by_email(connection, form.email.data)
        if user:
            flash('Email already exists. Signing you in.', 'success')
            session['user_id'] = user[0]  # Assuming the first column is the user ID
            return redirect(url_for('app.role_type'))
        else:
            user_id = add_user(connection, form.name.data, form.email.data, form.company_name.data)
            if not user_id:
                flash('Error creating user profile', 'error')
                return redirect(url_for('app.index'))
            session['user_id'] = user_id
            flash('Profile saved successfully!', 'success')
            return redirect(url_for('app.role_type'))
    
    return render_template('profile.html', form=form)

@app.route('/role_type', methods=['GET', 'POST'])
def role_type():
    if 'user_id' not in session:
        flash('Please create a profile first', 'warning')
        return redirect(url_for('app.profile'))
    
    form = RoleTypeForm()
    
    # Get saved templates for this user
    templates = get_templates(connection, session['user_id'])
    
    if form.validate_on_submit():
        # Process the role type form
        job_details['role_title'] = form.role_title.data
        job_details['role_type'] = form.role_type.data
        job_details['department'] = form.department.data
        job_details['location'] = form.location.data
        job_details['remote_option'] = form.remote_option.data
        job_details['salary_range'] = form.salary_range.data
        job_details['template_name'] = form.template_name.data
        
        # Check if it's a template load request
        if form.load_template.data and form.template_id.data:
            template_id = int(form.template_id.data)
            for template in templates:
                if template[0] == template_id:  # Assuming first column is ID
                    # Load template data into session
                    job_ad_data = get_job_ad(connection, template_id)
                    if job_ad_data:
                        # Parse stored JSON data
                        import json
                        try:
                            stored_details = json.loads(job_ad_data[5])  # Assuming 6th column is JSON data
                            job_details.update(stored_details)
                            flash('Template loaded successfully', 'success')
                            return redirect(url_for('app.qualifications'))
                        except:
                            flash('Error loading template data', 'error')
            
            flash('Selected template not found', 'error')
            return redirect(url_for('app.role_type'))
        
        return redirect(url_for('app.qualifications'))
    
    return render_template('role_type.html', form=form, templates=templates)

@app.route('/qualifications', methods=['GET', 'POST'])
def qualifications():
    if 'user_id' not in session or 'role_title' not in job_details:
        flash('Please complete all previous steps first', 'warning')
        return redirect(url_for('app.role_type'))
    
    form = QualificationsForm()
    
    if form.validate_on_submit():
        # Process the qualifications form
        job_details['education_required'] = form.education_required.data
        job_details['certifications'] = []
        
        # Process certifications from dynamically added fields
        for key, value in request.form.items():
            if key.startswith('certifications-') and key.endswith('-name'):
                index = key.split('-')[1]
                name = value
                required = request.form.get(f'certifications-{index}-required', 'off') == 'on'
                
                if name.strip():  # Only add non-empty certifications
                    job_details['certifications'].append({
                        'name': name,
                        'required': required
                    })
        
        return redirect(url_for('app.experience'))
    
    return render_template('qualifications.html', form=form, job_details=job_details)

@app.route('/experience', methods=['GET', 'POST'])
def experience():
    if 'user_id' not in session or 'education_required' not in job_details:
        flash('Please complete all previous steps first', 'warning')
        return redirect(url_for('app.qualifications'))
    
    form = ExperienceForm()
    
    if form.validate_on_submit():
        # Process the experience form
        job_details['years_experience'] = form.years_experience.data
        job_details['specific_experience'] = form.specific_experience.data
        job_details['responsibilities'] = []
        
        # Process responsibilities from dynamically added fields
        for key, value in request.form.items():
            if key.startswith('responsibilities-') and key.endswith('-description'):
                index = key.split('-')[1]
                description = value
                
                if description.strip():  # Only add non-empty responsibilities
                    job_details['responsibilities'].append({
                        'description': description
                    })
        
        return redirect(url_for('app.skills'))
    
    return render_template('experience.html', form=form, job_details=job_details)

@app.route('/skills', methods=['GET', 'POST'])
def skills():
    if 'user_id' not in session or 'years_experience' not in job_details:
        flash('Please complete all previous steps first', 'warning')
        return redirect(url_for('app.experience'))
    
    form = SkillsForm()
    
    if form.validate_on_submit():
        # Process the skills form
        job_details['required_skills'] = []
        job_details['preferred_skills'] = []
        
        # Process required skills from dynamically added fields
        for key, value in request.form.items():
            if key.startswith('required_skills-') and key.endswith('-name'):
                index = key.split('-')[1]
                name = value
                
                if name.strip():  # Only add non-empty skills
                    job_details['required_skills'].append({
                        'name': name
                    })
        
        # Process preferred skills from dynamically added fields
        for key, value in request.form.items():
            if key.startswith('preferred_skills-') and key.endswith('-name'):
                index = key.split('-')[1]
                name = value
                
                if name.strip():  # Only add non-empty skills
                    job_details['preferred_skills'].append({
                        'name': name
                    })
        
        job_details['personality_traits'] = form.personality_traits.data
        job_details['about_company'] = form.about_company.data
        job_details['diversity_statement'] = form.diversity_statement.data
        job_details['application_process'] = form.application_process.data
        
        # Generate job ad
        return redirect(url_for('app.generate_ad'))
    
    return render_template('skills.html', form=form, job_details=job_details)

@app.route('/generate_ad', methods=['GET', 'POST'])
def generate_ad():
    """Generate and save job ad page"""
    if 'user_id' not in session:
        flash('Please create a profile first', 'warning')
        return redirect(url_for('app.profile'))
    
    form = OutputForm()
    
    if form.validate_on_submit():
        # Debug form data
        print("Form submitted and validated")
        print(f"Job ad text length: {len(form.job_ad.data)}")
        print(f"Save as template: {form.save_as_template.data}")
        
        # Save the job ad
        user_id = session['user_id']
        role_title = job_details.get('role_title', 'Untitled Position')
        department = job_details.get('department', 'General')
        job_ad_text = form.job_ad.data
        is_template = form.save_as_template.data
        template_name = job_details.get('template_name', role_title)
        
        # Save to database with additional error handling
        try:
            ad_id = save_job_ad(connection, user_id, role_title, department, 
                              job_ad_text, is_template, template_name)
            print(f"Job ad saved with ID: {ad_id}")
            if ad_id:
                flash('Job ad saved successfully!', 'success')
                return redirect(url_for('app.view_ad', ad_id=ad_id))
            else:
                flash('Error saving job ad - database operation failed', 'error')
        except Exception as e:
            print(f"Exception saving job ad: {str(e)}")
            flash(f'Error saving job ad: {str(e)}', 'error')
    
    # First load or validation error
    if request.method == 'GET':
        # Generate the job ad if one doesn't exist
        initial_job_ad = generate_job_ad(job_details)
        form.job_ad.data = initial_job_ad
    
    return render_template('generate_ad.html', form=form, job_details=job_details)

@app.route('/view/<int:ad_id>')
def view_ad(ad_id):
    job_ad_data = get_job_ad(connection, ad_id)
    if not job_ad_data:
        flash('Job ad not found', 'error')
        return redirect(url_for('app.index'))
    
    return render_template('view_ad.html', job_ad=job_ad_data)

@app.route('/ad_history')
def ad_history():
    """Show user's saved job ads"""
    if 'user_id' not in session:
        flash('Please create a profile first', 'warning')
        return redirect(url_for('app.profile'))
    
    # Debug logging
    print(f"Getting job ads for user {session['user_id']}")
    
    # Get user's job ads from the database
    ads = get_user_job_ads(connection, session['user_id'])
    print(f"Found {len(ads) if ads else 0} ads")
    
    return render_template('ad_history.html', ads=ads)

@app.route('/refine_ad_api', methods=['POST'])
def refine_ad_api():
    """API endpoint for refining job ad text"""
    try:
        data = request.get_json()
        original_ad = data.get('original_ad', '')
        feedback = data.get('feedback', '')
        
        # Call the refine_job_ad function from utils.py
        refined_ad = refine_job_ad(original_ad, feedback)
        
        return jsonify({'refined_ad': refined_ad})
    except Exception as e:
        print(f"Error refining job ad: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<int:ad_id>')
def download_ad(ad_id):
    from flask import send_file
    
    job_ad_data = get_job_ad(connection, ad_id)
    if not job_ad_data:
        flash('Job ad not found', 'error')
        return redirect(url_for('app.index'))
    
    # Format and generate PDF
    pdf_path = format_for_pdf(job_ad_data)
    
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"job_ad_{ad_id}.pdf"
    )

@app.route('/process_job_description', methods=['POST'])
def process_job_description():
    """Extract key components from an existing job description"""
    if 'job_description_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['job_description_file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    try:
        # Extract text from job description
        job_description_text = extract_text_from_pdf(file)
        
        # Process with AI to extract structured information
        response = model.generate_content(f"""
        Extract structured information from this job description:
        {job_description_text[:3000]}  # First 3000 chars for analysis
        
        Return ONLY valid JSON with the following structure:
        {{
          "role_title": "extracted title",
          "role_type": "full-time/part-time/etc",
          "department": "department name",
          "education_required": "minimum education requirement",
          "years_experience": "number of years",
          "required_skills": ["skill1", "skill2"],
          "preferred_skills": ["skill1", "skill2"],
          "responsibilities": ["responsibility1", "responsibility2"]
        }}
        """)
        
        # Process the response
        try:
            import json
            import re
            
            # Clean up the response to ensure it's valid JSON
            clean_response = re.search(r'\{.*\}', response.text, re.DOTALL)
            if clean_response:
                extracted_data = json.loads(clean_response.group(0))
                return jsonify({
                    'success': True,
                    'data': extracted_data
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Could not parse structured data from response'
                })
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error processing job description: {str(e)}'
            })
            
    except Exception as e:
        print(f"Exception in process_job_description: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing job description: {str(e)}'
        })

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('app.index'))