# AI Apps Challenge 2025  

### © Hasan Akhtar 2025, All Rights Reserved  

<br>  
<hr>  

## General Document Summarisation AI – September Project  

### Project Overview  
The **General Document Summarisation AI** is a flexible and accessible tool designed to help users quickly understand **lengthy documents**. Whether you're reviewing research papers, legal contracts, or technical manuals, this app uses **AI-powered summarisation** to extract the most important information and present it in a clear, digestible format.  

It supports **multiple file types**, offers **customisable summary settings**, and is built for general use—making it ideal for students, professionals, and anyone who wants to save time while reading.

### Features  
- **Multi-Format Uploads:** Supports `.pdf`, `.docx`, and `.txt` files.  
- **AI Summarisation Engine:** Generates concise summaries using advanced language models.  
- **Custom Summary Settings:** Adjust length, tone, and focus of the summary.  
- **Live Preview:** View the summary before exporting.  
- **Copy & Export Options:** Easily copy to clipboard or download as `.txt` or `.pdf`.  
- **Simple UI:** Designed for non-technical users with intuitive controls.  
- **Scalable Backend:** Efficiently processes large documents.  
- **Optional Comparison Mode:** Compare summaries with different settings side-by-side.

### Technical Specifications  
1. **Programming Language:** Python  
2. **Frameworks and Libraries:**  
   - Flask/Django: Web application framework  
   - PyPDF2, python-docx: For document parsing  
   - Gemini API: For summarisation  
   - SpaCy or NLTK: For additional text preprocessing  
3. **Deployment:** Docker containerization and cloud service deployment (e.g., AWS or Azure)  
4. **Version Control:** Git for source code management  

### Installation  
1. Clone the repository:  
   ```bash  
   git clone <repository-url>  
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd i_september_ai_doc_summariser  
   ```  
3. Install the required dependencies:  
   ```bash  
   pip install -r requirements.txt  
   ```  

### Running the Application  
To start the application, run the following command:  
```bash  
python run.py  
```  
The application will start on `localhost` at port `6922`.  

### Usage  
- Upload a document via the web interface.  
- Choose your summary settings (length, tone, focus).  
- View the AI-generated summary and make adjustments if needed.  
- Copy or download the final summary for use in your workflow.

### Contributing  
Contributions are welcome! Please submit a pull request or open an issue for feature suggestions or improvements.

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.