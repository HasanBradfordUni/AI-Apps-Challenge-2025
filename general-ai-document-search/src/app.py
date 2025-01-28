from flask import Flask, request, render_template
from ai.geminiPrompt import generate_ai_summary
from utils.document_processing import process_documents
from utils.search_algorithm import search_documents

app = Flask(__name__)
documents = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Handle document upload and processing
    files = request.files.getlist('documents')
    documents = process_documents(files)
    page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload Success</title>
        <link rel="stylesheet" href="/static/css/hasAi.css">
    </head>
    <body>
        <header>
        <h1>
            <img
            src="https://i.postimg.cc/PqP5VwNZ/Has-AI-logo.png"
            alt="The Has AI logo"
            width="50"
            height="50"
            class="logo"
            />
            Has AI
            <img
            src="https://i.postimg.cc/PqP5VwNZ/Has-AI-logo.png"
            alt="The Has AI logo"
            width="50"
            height="50"
            class="logo"
            />
        </h1>
        <hr />
        </header>
        <section class="mainBody">
            <h1 class='mainHeading'>Documents uploaded and processed successfully.</h1>
            <button onclick="window.location.href='/'">Go back</button>
        </section>
    </body>
    </html>
    """
    return page

@app.route('/search', methods=['POST'])
def search():
    user_query = request.form['query']
    results = search_documents(user_query, documents)
    ai_summary = generate_ai_summary(results)
    return render_template('index.html', results=results, ai_summary=ai_summary)

if __name__ == '__main__':
    app.run(host='localhost', port=6922)