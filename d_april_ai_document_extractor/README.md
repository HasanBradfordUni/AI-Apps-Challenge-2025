# AI Apps Challenge 2025  

### © Hasan Akhtar 2025, All Rights Reserved

<br>
<hr>

## AI Document Extractor & Converter - April Project

### Project Overview  
The **AI Document Extractor & Converter** is a dynamic and modular application designed to simplify the process of extracting, processing, and converting data from various document formats. With support for Word, PDF, and plain text files, the tool leverages AI-powered data extraction techniques to provide users with a seamless experience. Through its intuitive web-based interface, users can upload documents, customize configurations, and generate outputs in desired formats, all with real-time feedback and logging.

### Features  
- **Document Upload:** Easily upload files in formats such as `.docx`, `.pdf`, or `.txt`.  
- **Data Extraction:** Automatically identify and extract structured or semi-structured data using regex and NLP techniques.  
- **Data Mapping:** Map extracted fields to predefined or user-defined schemas for structured processing.  
- **File Conversion:** Convert input documents into various output formats, including `.csv`, `.pdf`, and `.docx`.  
- **Modular Design:** Reusable components for integration into other workflows or applications.  
- **Error Handling and Logging:** Comprehensive logs for tracking progress and debugging.  
- **Web Interface:** User-friendly UI for uploads, progress tracking, and output generation.  
- **Custom Configurations:** Support for default or user-specified extraction rules and mapping settings.  

### How It Works  
1. **Input:** Users upload a document via the web interface.  
2. **Processing:** The application extracts relevant data using AI-powered algorithms and maps it to structured schemas.  
3. **File Conversion:** Users can select the desired output format for processed data.  
4. **Output:** A new document is generated based on the extracted and mapped data.  
5. **Logging:** Detailed logs are created for each step of the workflow for transparency and error tracking.

### Technical Specifications  
- **Programming Language:** Python  
- **Frameworks and Libraries:**  
  - Flask/Django for the web application.  
  - PyPDF2/Fitz for PDF handling and text extraction.  
  - python-docx for processing Word documents.  
  - SpaCy/NLTK for natural language processing.  
  - Regex for pattern-based data extraction.  
- **Database:** SQLlite for storing configurations and logs.  
- **Deployment:** Docker containerization for streamlined deployment on cloud services like AWS or Azure.  
- **Version Control:** Git for managing source code and collaborative development.  

### Use Cases  
- Automating data extraction from standardized forms or legacy documents.  
- Converting scanned files or handwritten content into structured digital formats.  
- Streamlining workflows requiring repeated data processing, mapping, and file conversion.  
- Adapting modular components for integration into other applications.  

### Installation  
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd d_april_ai_document_extractor
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application
To start the application, run the following command:  
```bash  
python src/app.py  
```  
The application will start on `localhost` at port `6922`.   

### Contributing  
We welcome contributions! Feel free to fork the repository, submit pull requests, or raise issues for feature requests and improvements.

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.