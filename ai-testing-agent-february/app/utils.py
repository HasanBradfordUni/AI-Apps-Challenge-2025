import PyPDF2
from PIL import Image
import pytesseract

# Configure pytesseract to use the installed Tesseract executable
pytesseract.pytesseract.tesseract_cmd = './bin/tesseract'

def process_files(expected_results, actual_results, context):
    # Process the uploaded files and generate evaluation
    expected_results_text = PyPDF2.PdfReader.read(expected_results)
    actual_results_image = Image.open(actual_results)
    image_text = pytesseract.image_to_string(actual_results_image)
    return expected_results_text, image_text
