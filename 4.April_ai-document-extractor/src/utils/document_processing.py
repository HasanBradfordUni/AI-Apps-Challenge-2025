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
    fileType = file.filename.split('.')[-1]
    # Get the path of this file
    file_path = os.path.dirname(__file__)
    print(file_path)
    path = os.path.join(file_path, 'docs', 'uploads')
    print(path)
    # Create the docs/uploads folder if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)
    # Define the file path in the docs folder
    file_path = os.path.join(path, file.filename)
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
    return file_path

def convert_file_format(file, ai_info, output_name, config_options):
    """
    Convert an uploaded document based on user configuration options and AI insights.
    
    Args:
        file: The uploaded file object.
        ai_info: Dictionary containing AI-generated insights.
        output_name: String specifying the output file name.
        config_options: List of configuration options selected by the user.
    
    Returns:
        str: Path to the converted file.
    """
    # Handle the uploaded file and save it to the docs folder first
    file_path = handle_document_upload(file)
    if file_path is None:
        return None

    # Parse configuration options into a dictionary for easier access
    config_dict = {}
    for option in config_options:
        if ":" in option:
            key, value = option.split(":", 1)
            config_dict[key.strip()] = value.strip()
    
    # Construct the new file path for the converted file
    base_folder = os.path.dirname(file_path)
    path = os.path.join(base_folder, '..', 'converted')
    # Create the converted folder if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)
        
    # Determine file extension based on the source file
    file_extension = os.path.splitext(file_path)[1]
    # Define the file path in the converted folder
    converted_file_path = os.path.join(path, output_name + file_extension)
    
    # Convert based on file type
    if file_extension.lower() == '.docx':
        convert_docx_document(file_path, converted_file_path, config_dict, ai_info)
    elif file_extension.lower() == '.pdf':
        convert_pdf_document(file_path, converted_file_path, config_dict, ai_info)
    elif file_extension.lower() == '.txt':
        convert_txt_document(file_path, converted_file_path, config_dict, ai_info)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    return converted_file_path

def convert_docx_document(input_path, output_path, config_dict, ai_info):
    """
    Convert a DOCX document based on configuration options and AI insights.
    
    Args:
        input_path: Path to the input DOCX file.
        output_path: Path where the converted DOCX file will be saved.
        config_dict: Dictionary of configuration options.
        ai_info: Dictionary of AI-generated insights.
    """
    # Load the original document
    doc = docx.Document(input_path)
    
    # Create a new document for the converted output
    new_doc = docx.Document()
    
    # Get table handling preference
    table_handling = config_dict.get('Table Handling', 'keep')
    output_formatting = config_dict.get('Output Formatting', 'original')
    field_mapping_str = config_dict.get('Field Mapping', '')
    placeholder_text = config_dict.get('Placeholder Text', '')
    page_range_str = config_dict.get('Page Range', 'all')
    
    # Parse field mapping if provided
    field_mapping = {}
    if field_mapping_str:
        # Simple parsing of "key:value, key2:value2" format
        mapping_pairs = field_mapping_str.split(',')
        for pair in mapping_pairs:
            if ':' in pair:
                k, v = pair.split(':', 1)
                field_mapping[k.strip()] = v.strip()
    
    # Use AI suggestions for field mappings if available
    if ai_info and 'field_mappings' in ai_info:
        ai_mappings = ai_info['field_mappings']
        if isinstance(ai_mappings, dict):
            field_mapping.update(ai_mappings)
    
    # Use AI suggestions for placeholder text if not provided by user
    if not placeholder_text and ai_info and 'placeholder_text' in ai_info:
        placeholder_text = ai_info['placeholder_text']
    
    # Process paragraphs
    for para in doc.paragraphs:
        # Apply field mappings to paragraph text if any
        text = para.text
        for old_field, new_field in field_mapping.items():
            text = text.replace(old_field, new_field)
            
        # Add processed paragraph to the new document
        new_para = new_doc.add_paragraph(text)
        
        # Handle formatting based on user preference
        if output_formatting == 'original':
            # Copy the original paragraph formatting
            new_para.style = para.style
        elif output_formatting == 'default':
            # Use default formatting (no additional styling needed)
            pass
        # Custom formatting could be added here
    
    # Process tables
    for table in doc.tables:
        rows = len(table.rows)
        cols = len(table.columns)
        
        if table_handling == 'remove':
            # Skip adding this table to the new document
            continue
        
        # Add a new table with the same dimensions
        new_table = new_doc.add_table(rows=rows, cols=cols)
        
        # Copy or modify table content based on table handling preference
        for i in range(rows):
            for j in range(cols):
                cell_text = table.cell(i, j).text
                
                if table_handling == 'empty':
                    # Replace content with placeholder text if applicable
                    if i > 0:  # Assuming the first row is headers
                        cell_text = placeholder_text
                elif table_handling == 'keep':
                    # Apply field mappings to cell text if any
                    for old_field, new_field in field_mapping.items():
                        cell_text = cell_text.replace(old_field, new_field)
                
                new_table.cell(i, j).text = cell_text
    
    # Save the converted document
    new_doc.save(output_path)

def convert_pdf_document(input_path, output_path, config_dict, ai_info):
    """
    Convert a PDF document based on configuration options and AI insights.
    
    Args:
        input_path: Path to the input PDF file.
        output_path: Path where the converted PDF file will be saved.
        config_dict: Dictionary of configuration options.
        ai_info: Dictionary of AI-generated insights.
    """
    # Parse page range if provided
    page_range_str = config_dict.get('Page Range', 'all')
    
    # Use AI insights to determine optimal page range if available
    if ai_info and 'page_range_recommendation' in ai_info and page_range_str == 'all':
        page_range_str = ai_info.get('page_range_recommendation', 'all')
    
    # Load the original PDF
    reader = PyPDF2.PdfReader(input_path)
    writer = PyPDF2.PdfWriter()
    
    # Determine which pages to include
    if page_range_str.lower() == 'all':
        page_indices = list(range(len(reader.pages)))
    else:
        try:
            page_indices = []
            ranges = page_range_str.split(',')
            for r in ranges:
                if '-' in r:
                    start, end = map(int, r.split('-'))
                    # Convert from 1-based to 0-based indexing
                    page_indices.extend(range(start-1, end))
                else:
                    # Convert from 1-based to 0-based indexing
                    page_indices.append(int(r) - 1)
        except ValueError:
            # Default to all pages if parsing fails
            page_indices = list(range(len(reader.pages)))
    
    # Add selected pages to the output PDF
    for idx in page_indices:
        if 0 <= idx < len(reader.pages):
            page = reader.pages[idx]
            
            # If we have AI insights for text replacement, apply them
            if ai_info and 'field_mappings' in ai_info:
                # For PDFs, we'd need to use a different approach since we can't
                # directly modify text in PDF pages without more complex libraries
                # This is a placeholder for future enhancement
                # One approach would be to extract text, modify it, and create a new PDF
                pass
            
            # Add the page (modified or original) to the output
            writer.add_page(page)
    
    # If AI provides additional insights about PDF structure or metadata
    if ai_info and 'additional_insights' in ai_info:
        # Here we could apply additional PDF-specific modifications
        # based on AI recommendations (e.g., metadata changes)
        pass
    
    # Save the converted PDF
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

def convert_txt_document(input_path, output_path, config_dict, ai_info):
    """
    Convert a text document based on configuration options and AI insights.
    
    Args:
        input_path: Path to the input text file.
        output_path: Path where the converted text file will be saved.
        config_dict: Dictionary of configuration options.
        ai_info: Dictionary of AI-generated insights.
    """
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Apply field mappings if provided
    field_mapping_str = config_dict.get('Field Mapping', '')
    if field_mapping_str:
        mapping_pairs = field_mapping_str.split(',')
        for pair in mapping_pairs:
            if ':' in pair:
                old_field, new_field = pair.split(':', 1)
                content = content.replace(old_field.strip(), new_field.strip())
    
    # Use AI suggestions for field mappings if available
    if ai_info and 'field_mappings' in ai_info:
        ai_mappings = ai_info['field_mappings']
        if isinstance(ai_mappings, dict):
            for old_field, new_field in ai_mappings.items():
                content = content.replace(old_field, new_field)
    
    # Write the converted content to the output file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(content)