import PyPDF2
from PIL import Image
import pytesseract
import os

import vertexai
from vertexai.generative_models import GenerativeModel
import google.auth

credentials, project_id = google.auth.default()

vertexai.init(project="generalpurposeai", location="us-central1")

model = GenerativeModel(model_name="gemini-1.5-pro")

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

def generate_ai_comparison(project_name, query, expected_results, actual_results):
    # Function to generate an AI comparison based on the user query, expected results, and actual results
    response = model.generate_content(f"I am conducting a software test for my project {project_name}. Can you compare the expected results: {expected_results} with the actual results: {actual_results} based on the testing query: {query}")
    return response.text

def generate_summary(evaluation_results, project_name, query):
    # Function to generate a summary based on the evaluation results
    summary = model.generate_content(f"I am conducting a software test for my project {project_name}. Based on my expected result and actual result comparison: {evaluation_results} and on the testing query: {query}, can you provide a summary of the evaluation (i.e. how successful my software programme is for this query, based on the test)?")
    return summary.text
