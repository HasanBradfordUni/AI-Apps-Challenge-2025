# AI Apps Challenge 2025  

### © Hasan Akhtar 2025, All Rights Reserved  

<br>  
<hr>  

## Docs Directory AI Summariser – October Project  

### Project Overview  
The **Docs Directory AI Summariser** is a powerful utility designed to provide **high-level insights into document folders** without requiring users to manually inspect each file. By inputting a folder path, the app generates a **comprehensive summary** of the directory’s contents—including file counts, word and character statistics, and breakdowns by file type.  

The system also features a **template matching module**, allowing users to upload sample files (e.g. Word, PDF, Excel, PowerPoint, TXT, MD) and detect how many similar files exist in the directory. This makes it ideal for **content managers, researchers, and administrators** who need to audit or analyse document repositories quickly and efficiently.

### Features  
- **Folder Path Input:** Users specify a directory to analyse.  
- **File Count & Type Breakdown:** Displays total files and groups them by extension.  
- **Textual Analysis:** Calculates word and character counts for individual files, plus total and average across the folder.  
- **Template Matching System:** Upload sample files to detect and count similar files in the directory.  
- **Selective Display:** Only shows template categories with at least one match.  
- **File Type Summary:** Aggregates statistics by file type.  
- **Clean Summary Output:** Structured dashboard or report view with sortable metrics.  
- **Scalable Performance:** Efficiently handles large directories with hundreds of files.

### Technical Specifications  
1. **Programming Language:** Python  
2. **Frameworks and Libraries:**  
   - Flask or Streamlit: Web application framework  
   - os, pathlib: For directory traversal  
   - python-docx, PyPDF2, openpyxl, python-pptx: For file parsing  
   - difflib or fuzzywuzzy: For template similarity matching  
   - Pandas: For tabular data aggregation and filtering  
3. **Database:** SQLite for storing template metadata and cached summaries  
4. **Deployment:** Docker containerization and optional cloud deployment (e.g., AWS, Azure)  
5. **Version Control:** Git for source code management  

### Installation  
1. Clone the repository:  
   ```bash  
   git clone <repository-url>  
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd 10.October_ai-directory-summariser  
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
- Enter the path to the folder you want to summarise.  
- View file counts, word/character statistics, and breakdowns by file type.  
- Upload template files to detect and count similar documents.  
- Review the structured summary and export results if needed.

### Contributing  
Contributions are welcome! Please submit a pull request or open an issue for feature suggestions or improvements.

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.  
