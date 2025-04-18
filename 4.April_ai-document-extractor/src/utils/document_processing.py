import docx
import PyPDF2
import os

search_index = {}

def process_uploaded_file(file_path):
    # Function to process a document based on its file type
    file_type = file_path.split('.')[-1]
    match file_type:
        case 'pdf':
            text = extract_text_from_pdf(file_path)
            return text
        case 'docx':
            text = extract_text_from_docx(file_path)
            return text
        case 'txt':
            text = extract_text_from_txt(file_path)
            return text
        case _:
            print(f"Unsupported file type: {file_type}")

def extract_text_from_pdf(pdf_path):
    # Function to extract text from a PDF file
    reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    # Function to extract text from a DOCX file
    doc = docx.Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text += cell.text
    return text

def extract_text_from_txt(txt_path):
    # Function to extract text from a TXT file
    with open(txt_path, 'r') as f:
        text = f.read()
    return text

def handle_document_upload(file):
    # Copy the file to the docs folder
    fileType = file.name
    # Create the docs folder if it doesn't exist
    path = os.path.join(os.getcwd(), 'docs')
    if not os.path.exists(path):
        os.makedirs(path)
    # Define the file path in the docs folder
    file_path = os.path.join('docs', file.filename)
    # Check if the file already exists in the docs folder
    if os.path.exists(file_path):
        # If it exists, delete the existing file
        os.remove(file_path)
    # Save the uploaded file to the docs folder
    match fileType:
        case 'pdf':
            reader = PyPDF2.PdfReader(file)
            # save the pdf file to the file path using PyPDF2
            with open(file_path, 'wb') as f:
                writer = PyPDF2.PdfWriter()
                for page_num in range(len(reader.pages)):
                    writer.add_page(reader.pages[page_num])
                writer.write(f)
                writer.close()
        case 'docx':
            template = docx.Document()
            this_file = docx.Document(file)
            for para in this_file.paragraphs:
                template.add_paragraph(para.text)
            for table in this_file.tables:
                # Get the number of rows and columns from the table
                rows = len(table.rows)
                cols = len(table.columns)
                # Add a table to the template with the same number of rows and columns
                new_table = template.add_table(rows=rows, cols=cols)
                # Copy the content of each cell
                for i in range(rows):
                    for j in range(cols):
                        new_table.cell(i, j).text = table.cell(i, j).text
            template.save(file_path)
        case 'txt':
            fileContents = file.readlines()
            with open(file_path, 'w') as f:
                for line in fileContents:
                    f.write(line.decode('utf-8'))
        case _:
            print(f"Unsupported file type: {fileType}")

def convert_file_format(file, target_format):
    # Function to convert a file to a specified format
    file_path = os.path.join('docs', file.filename)
    handle_document_upload(file, file_path)

    # Process the uploaded file based on its type
    extracted_text = process_uploaded_file(file_path)

    # Save the extracted text to a new file in the target format
    converted_file_path = os.path.splitext(file_path)[0] + '.' + target_format
    with open(converted_file_path, 'w') as f:
        f.write(extracted_text)

    return converted_file_path