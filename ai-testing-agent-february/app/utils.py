import PyPDF2
from PIL import Image
import pytesseract
import os

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
