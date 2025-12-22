from flask import Flask, request, render_template, jsonify, send_file
from utils.document_processing import handle_document_upload, process_uploaded_file, get_uploaded_documents
from utils.forms import ConfigOptionsForm
from ai.geminiPrompt import generate_conversion_insights
import os
import tempfile
import markdown
from markupsafe import Markup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomString'

# Register the markdown filter
@app.template_filter('markdown')
def markdown_filter(text):
    if text:
        # Convert markdown to HTML
        html = markdown.markdown(text, extensions=['fenced_code', 'tables', 'nl2br'])
        return Markup(html)
    return ''

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the main page with a form for uploading and processing documents."""
    form = ConfigOptionsForm()
    
    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded.", form=form)

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected.", form=form)
        
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
            return render_template('index.html', extracted_text=extracted_text, form=form, success_message="Document uploaded successfully!")
        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            return render_template('index.html', error=error_message, form=form)

    return render_template('index.html', form=form)

@app.route('/get-documents', methods=['GET'])
def get_documents():
    """Get list of uploaded documents for the dropdown."""
    try:
        documents = get_uploaded_documents()
        return jsonify({'documents': documents})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convert', methods=['POST'])
def convert():
    """Convert a selected document to a specified format."""
    form = ConfigOptionsForm()
    
    if form.validate_on_submit():
        # Get the selected document and output filename
        selected_document = request.form.get('selected-document')
        output_name = request.form.get('output-filename')
        output_file_type = form.output_file_type.data
        
        if not selected_document:
            return jsonify({'error': 'No document selected'}), 400
        if not output_name:
            return jsonify({'error': 'Output filename is required'}), 400
        
        # Get form data
        table_handling = form.table_handling.data
        field_mapping = form.field_mapping.data
        placeholder_text = form.placeholder_text.data
        page_range = form.page_range.data
        output_formatting = form.output_formatting.data
        additional_notes = form.additional_notes.data

        # Build config options
        config_options = {
            "Table Handling:": table_handling,
            "Output Formatting:": output_formatting,
            "Output File Type:": output_file_type
        }
        
        # Append optional options if provided
        if field_mapping:
            config_options["Field Mapping:"] = field_mapping
        if placeholder_text:
            config_options["Placeholder Text:"] = placeholder_text
        if page_range:
            config_options["Page Range:"] = page_range
        if additional_notes:
            config_options["Additional Notes:"] = additional_notes
        
        try:
            # Get the file path of the selected document
            document_path = get_document_path(selected_document)
            if not document_path:
                return jsonify({'error': 'Selected document not found'}), 404
            
            # Extract text from the selected document
            extracted_text = process_uploaded_file(document_path)
            
            # Generate AI insights
            ai_processed_info = generate_conversion_insights(extracted_text, config_options)
            if ai_processed_info is None:
                return jsonify({'error': 'Failed to generate AI insights'}), 500

            # Convert the file to the specified format
            converted_file_path = convert_file_format_from_path(document_path, ai_processed_info, output_name, config_options, output_file_type)
            if converted_file_path is None:
                return jsonify({'error': 'Failed to convert file'}), 500
                
            return jsonify({
                'message': 'File converted successfully', 
                'file_path': converted_file_path,
                'ai_summary': ai_processed_info.get('full_summary', 'No AI summary available'),
                'download_url': f'/download/{os.path.basename(converted_file_path)}'
            })
        except Exception as e:
            return jsonify({'error': f"Error converting file: {str(e)}"}), 500
        
    else:
        return jsonify({'error': f"Form validation failed: {str(form.errors)}"}), 400

@app.route('/download/<filename>')
def download_file(filename):
    """Download the converted file."""
    try:
        from utils.document_processing import get_uploads_folder
        uploads_folder = get_uploads_folder()
        converted_folder = os.path.join(os.path.dirname(uploads_folder), 'converted')
        file_path = os.path.join(converted_folder, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f"Error downloading file: {str(e)}"}), 500

def get_document_path(document_name):
    """Get the full path of an uploaded document."""
    from utils.document_processing import get_uploads_folder
    uploads_folder = get_uploads_folder()
    document_path = os.path.join(uploads_folder, document_name)
    if os.path.exists(document_path):
        return document_path
    return None

def convert_file_format_from_path(file_path, ai_info, output_name, config_options, output_file_type):
    """Convert a file from its path instead of file object."""
    from utils.document_processing import convert_file_format_from_file_path
    return convert_file_format_from_file_path(file_path, ai_info, output_name, config_options, output_file_type)

if __name__ == '__main__':
    app.run(host='localhost', port=6922)