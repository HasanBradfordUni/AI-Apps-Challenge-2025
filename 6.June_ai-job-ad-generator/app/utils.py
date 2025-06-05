import os
import google.generativeai as genai
import PyPDF2
from io import BytesIO
import tempfile
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# Configure Google Gemini API
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'your-api-key')
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
model = genai.GenerativeModel('gemini-pro')

def extract_text_from_pdf(pdf_file):
    """Extract text content from an uploaded PDF file"""
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def generate_job_ad(job_details):
    """Generate a job ad from the provided details"""
    # Construct a prompt for the AI model
    prompt = f"""
    Generate a professional job advertisement based on the following details:
    
    ROLE INFORMATION:
    - Job Title: {job_details.get('role_title', 'Not specified')}
    - Employment Type: {job_details.get('role_type', 'Not specified')}
    - Department: {job_details.get('department', 'Not specified')}
    - Location: {job_details.get('location', 'Not specified')}
    - Remote Option: {job_details.get('remote_option', 'Not specified')}
    - Salary Range: {job_details.get('salary_range', 'Not specified')}
    
    QUALIFICATIONS:
    - Minimum Education: {job_details.get('education_required', 'Not specified')}
    - Required Certifications: {", ".join([cert['name'] for cert in job_details.get('certifications', []) if cert.get('required', False)])}
    - Preferred Certifications: {", ".join([cert['name'] for cert in job_details.get('certifications', []) if not cert.get('required', False)])}
    
    EXPERIENCE:
    - Years of Experience: {job_details.get('years_experience', 'Not specified')}
    - Specific Experience: {job_details.get('specific_experience', 'Not specified')}
    
    JOB RESPONSIBILITIES:
    {" ".join(['- ' + resp['description'] for resp in job_details.get('responsibilities', [])])}
    
    REQUIRED SKILLS:
    {" ".join(['- ' + skill['name'] for skill in job_details.get('required_skills', [])])}
    
    PREFERRED SKILLS:
    {" ".join(['- ' + skill['name'] for skill in job_details.get('preferred_skills', [])])}
    
    PERSONALITY TRAITS:
    {job_details.get('personality_traits', 'Not specified')}
    
    ABOUT THE COMPANY:
    {job_details.get('about_company', 'Not specified')}
    
    DIVERSITY STATEMENT:
    {job_details.get('diversity_statement', 'Not specified')}
    
    APPLICATION PROCESS:
    {job_details.get('application_process', 'Not specified')}
    
    Create a well-structured, engaging job advertisement with the following sections:
    1. Job title and introduction
    2. About the company
    3. Key responsibilities
    4. Requirements (education, experience, skills)
    5. What we offer
    6. Application process
    7. Diversity & inclusion statement
    
    Make it concise, professional, and appealing to job seekers. Use bullet points for skills and responsibilities. 
    Emphasize the most important qualifications. Make it between 400-600 words.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating job ad: {str(e)}")
        return "Error generating job advertisement. Please try again."

def refine_job_ad(original_ad, feedback):
    """Refine a job ad based on user feedback"""
    prompt = f"""
    Please refine the following job advertisement based on this feedback:
    
    ORIGINAL JOB AD:
    {original_ad}
    
    FEEDBACK TO ADDRESS:
    {feedback}
    
    Please provide the entire refined job ad that addresses the feedback while maintaining the professional tone and structure.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error refining job ad: {str(e)}")
        return original_ad

def format_for_pdf(job_ad_data):
    """Format job ad data into a well-designed PDF file"""
    # Extract relevant data
    role_title = job_ad_data[2]  # Assuming 3rd column is role_title
    department = job_ad_data[3]  # Assuming 4th column is department
    job_ad_text = job_ad_data[4]  # Assuming 5th column is job_ad_text
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    filename = temp_file.name
    temp_file.close()
    
    # Create PDF
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', fontName='Helvetica-Bold', fontSize=16, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle(name='Subtitle', fontName='Helvetica', fontSize=12, alignment=TA_CENTER)
    header_style = ParagraphStyle(name='Heading', fontName='Helvetica-Bold', fontSize=12)
    body_style = ParagraphStyle(name='Body', fontName='Helvetica', fontSize=10, alignment=TA_JUSTIFY, leading=14)
    
    # Create content
    content = []
    
    # Title and department
    content.append(Paragraph(f"{role_title}", title_style))
    content.append(Spacer(1, 0.25 * inch))
    content.append(Paragraph(f"{department} Department", subtitle_style))
    content.append(Spacer(1, 0.25 * inch))
    content.append(Paragraph(f"Generated: {timestamp}", subtitle_style))
    content.append(Spacer(1, 0.5 * inch))
    
    # Process job ad text - split by sections and format accordingly
    sections = job_ad_text.split('\n\n')
    for section in sections:
        if section.strip():
            # Check if this is a section header
            if section.strip().isupper() or section.strip().endswith(':'):
                content.append(Spacer(1, 0.2 * inch))
                content.append(Paragraph(section.strip(), header_style))
                content.append(Spacer(1, 0.1 * inch))
            else:
                # Handle bullet points
                paragraphs = section.split('\n')
                for p in paragraphs:
                    if p.strip().startswith('•') or p.strip().startswith('-'):
                        # This is a bullet point
                        content.append(Paragraph(f"<bullet>&bull;</bullet> {p.strip()[1:].strip()}", body_style))
                    elif p.strip():
                        content.append(Paragraph(p.strip(), body_style))
                
                content.append(Spacer(1, 0.1 * inch))
    
    # Build PDF document
    doc.build(content)
    
    return filename