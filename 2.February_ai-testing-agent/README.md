# AI Testing Agent

## Project Overview
The AI Testing Agent is an AI powered web application designed to assist users in evaluating the performance of their software applications by comparing expected results with actual outcomes. Users can upload a PDF containing expected results, a screenshot of the actual results, and a text prompt of the question they want to test. The application generates a detailed comparison and evaluation, along with a concise summary.

## Features
- **File Upload**: Users can upload PDFs (expected results), screenshots (actual results), and text prompts.
- **Project Details Input**: Users can input their project name and additional details.
- **Context Box**: An extra context box for specific commands or additional information about the test.
- **AI-Based Evaluation**: The application generates a comparison between expected and actual results and provides a comprehensive evaluation.
- **Copy Functionality**: Users can copy the full AI evaluation and a shorter summary with separate copy buttons.

## Technical Specifications
- **Programming Language**: Python
- **Framework**: Flask
- **Libraries**: OpenCV or PIL for image processing, Py2PDF or PDFPlumber for PDF handling, NLTK or SpaCy for text analysis.
- **Database**: SQLite for storing user inputs and test results.
- **Deployment**: Docker for containerization and deployment on cloud services like AWS or Azure.
- **Version Control**: Git for source code management.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd 2.February_ai-testing-agent
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application
To run the application, execute the following command:
```
python run.py
```
The application will start on `localhost` at port `6922`.

## Usage
- Navigate to the main page to upload files and input project details.
- After submission, the application will process the inputs and display the evaluation results.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.