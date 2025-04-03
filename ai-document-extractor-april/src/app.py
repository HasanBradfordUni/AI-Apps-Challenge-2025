from flask import Flask, request, render_template, jsonify
#from utils.document_processing import process_uploaded_file, convert_file_format
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomString'

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the main page with a form for uploading and processing documents."""
    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded.")

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected.")

        # Process the uploaded file
        try:
            extracted_text = process_uploaded_file(file)
            return render_template('index.html', extracted_text=extracted_text)
        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            return render_template('index.html', error=error_message)

    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    """Convert an uploaded document to a specified format."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    target_format = request.form.get('format')
    if not target_format:
        return jsonify({'error': 'No target format specified'}), 400

    try:
        # Convert the file to the specified format
        converted_file_path = convert_file_format(file, target_format)
        return jsonify({'message': 'File converted successfully', 'file_path': converted_file_path})
    except Exception as e:
        return jsonify({'error': f"Error converting file: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=6922)