import PyPDF2
from PIL import Image
import pytesseract
import os

from google import genai
import google.auth

credentials, project_id = google.auth.default()

# Initialize the new client
client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")

# Configure pytesseract to use the installed Tesseract executable
pytesseract.pytesseract.tesseract_cmd = f"{os.path.dirname(__file__)}\\bin\\tesseract"

def process_files(expected_results, actual_results):
    # Process the uploaded files and generate evaluation
    reader = PyPDF2.PdfReader(expected_results)
    file_path = f"{os.path.dirname(__file__)}\\uploads\\{expected_results.filename}"
    # save the pdf file to the file path using PyPDF2
    with open(file_path, 'wb') as f:
        writer = PyPDF2.PdfWriter()
        for page_num in range(len(reader.pages)):
            writer.add_page(reader.pages[page_num])
        writer.write(f)
        writer.close()
    # Read text from the expected results PDF
    expected_results_text = ""
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            expected_results_text += page.extract_text()
    
    # Read text from the actual results image
    actual_results_image = Image.open(actual_results)
    image_text = pytesseract.image_to_string(actual_results_image)
    
    return expected_results_text, image_text

def generate_ai_comparison(project_name, query, expected_results, actual_results, project_description="", context=""):
    # Function to generate an AI comparison based on the user query, expected results, and actual results
    base_prompt = f"""
    # Software Test Analysis for {project_name}

    **Test Query:** {query}
    {f'**Project Description:** {project_description}' if project_description else ''}
    {f'**Additional Context:** {context}' if context else ''}

    ## Expected Results:
    {expected_results}

    ## Actual Results:
    {actual_results}

    Please provide a detailed comparison analysis using the following structure:
    1. **Key Differences** - Highlight main discrepancies
    2. **Match Analysis** - What aligns correctly
    3. **Critical Issues** - Any major problems identified
    4. **Recommendations** - Suggested improvements or next steps
    """
    
    try:
        response = client.models.generate_content(
            model="publishers/google/models/gemini-2.5-pro",
            contents=[base_prompt]
        )
        return response.text
    except Exception as e:
        print(f"Error generating AI comparison: {str(e)}")
        return f"Unable to generate comparison. Error: {str(e)}"

def generate_summary(evaluation_results, project_name, query, project_description="", context=""):
    # Function to generate a summary based on the evaluation results
    base_prompt = f"""
    Based on the following test analysis for {project_name}, provide a comprehensive evaluation report:

    **Test Query:** {query}
    {f'**Project Description:** {project_description}' if project_description else ''}
    {f'**Additional Context:** {context}' if context else ''}

    **Detailed Analysis:**
    {evaluation_results}

    Please structure your response as follows:

    ## Test Evaluation Report

    ### Detailed Analysis
    [Provide comprehensive analysis of the test results, covering accuracy, completeness, and functionality]

    ### Issues Identified
    [List any problems, bugs, or discrepancies found]

    ### Recommendations
    [Suggest specific improvements or fixes needed]

    ## Summary
    [Provide a concise summary suitable for a testing report, maximum 150 characters, focusing on overall test outcome - PASS/FAIL with key reason]

    Ensure the Summary section is exactly what would go in a formal testing report.
    """
    
    try:
        response = client.models.generate_content(
            model="publishers/google/models/gemini-2.5-pro",
            contents=[base_prompt]
        )
        return response.text
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return f"Unable to generate summary. Error: {str(e)}"
