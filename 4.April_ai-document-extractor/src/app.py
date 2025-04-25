from flask import Flask, request, render_template, jsonify
from utils.document_processing import handle_document_upload, process_uploaded_file, convert_file_format
from utils.forms import ConfigOptionsForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomString'
input_file = None
output_name = ""
ai_processed_info = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ConfigOptionsForm()
    """Render the main page with a form for uploading and processing documents."""
    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded.", form=form)

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected.", form=form)
        
        input_file = file
        output_name = request.form.get('output-filename')

        # Process the uploaded file
        try:
            # Check if the file type is supported
            filename = file.filename
            if not any(filename.lower().endswith(ext) for ext in ['.pdf', '.docx', '.txt']):
                return render_template('index.html', error="Unsupported file type. Please upload PDF, DOCX, or TXT files.", form=form)
                
            file_path = handle_document_upload(file)
            if file_path is None:
                return render_template('index.html', error="Failed to process the file. File path was empty.", form=form)
                
            # Extract text from the uploaded file
            extracted_text = process_uploaded_file(file_path)
            return render_template('index.html', extracted_text=extracted_text, form=form)
        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            return render_template('index.html', error=error_message, form=form)

    return render_template('index.html', form=form)

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    """Convert an uploaded document to a specified format."""
    if not output_name or not input_file:
        return jsonify({'error': 'No file specified'}), 400

    form = ConfigOptionsForm()
    config_options = []

    if form.validate_on_submit():
        table_handling = form.table_handling.data
        field_mapping = form.field_mapping.data
        placeholder_text = form.placeholder_text.data
        page_range = form.page_range.data
        output_formatting = form.output_formatting.data
        additional_notes = form.additional_notes.data

        #Append required options to config_options
        config_options.append(f"Table Handling: {table_handling}")
        config_options.append(f"Output Formatting: {output_formatting}")
            
        # Append optional options if provided
        if field_mapping:
            config_options.append(f"Field Mapping: {field_mapping}")
        if placeholder_text:
            config_options.append(f"Placeholder Text: {placeholder_text}")
        if page_range:
            config_options.append(f"Page Range: {page_range}")
        if additional_notes:
            config_options.append(f"Additional Notes: {additional_notes}")

        try:
            # Convert the file to the specified format
            converted_file_path = convert_file_format(input_file, ai_processed_info, output_name, config_options)
            if converted_file_path is None:
                return jsonify({'error': 'Failed to convert file'}), 500
            return jsonify({'message': 'File converted successfully', 'file_path': converted_file_path})
        except Exception as e:
            return jsonify({'error': f"Error converting file: {str(e)}"}), 500
        
    else:
        return jsonify({'error': f"Error submitting form: {str(form.errors)}"}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=6922)