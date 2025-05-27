import os
import PyPDF2
from PIL import Image
import pytesseract

import vertexai
from vertexai.generative_models import GenerativeModel
import google.auth

# Initialize Google Vertex AI
credentials, project_id = google.auth.default()
vertexai.init(project="generalpurposeai", location="us-central1")
model = GenerativeModel(model_name="gemini-2.0-flash")

# Configure pytesseract for text extraction from images
pytesseract.pytesseract.tesseract_cmd = f"{os.path.dirname(__file__)}\\bin\\tesseract"

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file (CV or job description)"""
    try:
        os.makedirs(os.path.dirname(__file__) + "\\uploads", exist_ok=True)
        
        file_path = f"{os.path.dirname(__file__)}\\uploads\\{pdf_file.filename}"
        with open(file_path, 'wb') as f:
            pdf_file.save(f)
        
        text = ""
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # Check if page has text
                    text += page_text + "\n\n"
        
        if not text.strip():
            print("Warning: No text extracted from PDF")
            
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_text_from_image(image_file):
    """Extract text from an image file"""
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

def extract_cv_structure(cv_text):
    """Use Gemini AI to extract structured information from CV text"""
    prompt = f"""
    You are a CV parser. Extract structured information from the following CV and return ONLY valid JSON without any additional text, explanations, or markdown formatting:
    
    {cv_text}
    
    Return the information as JSON with the following structure:
    {{
      "skills": [
        {{"skill_name": "Python", "proficiency": "advanced"}},
        {{"skill_name": "JavaScript", "proficiency": "intermediate"}}
      ],
      "education": [
        {{
          "institution": "University Name",
          "degree": "Degree Title", 
          "field": "Field of Study",
          "start_date": "YYYY-MM-DD",
          "end_date": "YYYY-MM-DD"
        }}
      ],
      "experience": [
        {{
          "company": "Company Name",
          "position": "Job Title",
          "exp_description": "Job description",
          "start_date": "YYYY-MM-DD",
          "end_date": "YYYY-MM-DD"
        }}
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Log the raw response for debugging
        print(f"Raw Gemini response: {response_text[:100]}...")  # Print first 100 chars
        
        # Try to find JSON in the response
        import json
        import re
        
        # First, try direct JSON parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON using regex
            json_match = re.search(r'({[\s\S]*})', response_text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    # If regex extraction failed, try cleaning the response
                    cleaned_text = re.sub(r'```json|```', '', response_text)
                    return json.loads(cleaned_text)
            else:
                print("No JSON found in response")
                return None
    except Exception as e:
        print(f"Error in extract_cv_structure: {str(e)}")
        return None

def generate_cover_letter(cv_text, job_description, tone="professional", focus_areas=None):
    """Generate a cover letter using Gemini AI based on CV and job description"""
    prompt = f"""
    Generate a professional cover letter based on the following:
    
    CV DETAILS:
    {cv_text}
    
    JOB DESCRIPTION:
    {job_description}
    
    Tone: {tone}
    """
    
    if focus_areas:
        prompt += f"\nPlease emphasize the following areas: {', '.join(focus_areas)}"
    
    response = model.generate_content(prompt)
    return response.text

def refine_cover_letter(original_letter, feedback):
    """Refine a cover letter based on user feedback"""
    prompt = f"""
    Please refine this cover letter based on the following feedback:
    
    ORIGINAL LETTER:
    {original_letter}
    
    FEEDBACK:
    {feedback}
    """
    
    response = model.generate_content(prompt)
    return response.text

def process_files(expected_results, actual_results):
    """Process uploaded files and extract text"""
    expected_result_text = extract_text_from_pdf(expected_results)
    actual_result_text = extract_text_from_image(actual_results)
    
    return expected_result_text, actual_result_text
