# AI Apps Challenge 2025

### © Hasan Akhtar 2025, All Rights Reserved

<br>
<hr>

## General AI Document Search - January Project 

### Project Overview  
The **General AI Document Search** application is an AI-powered tool designed to help users **efficiently search and retrieve relevant documents** from a vast collection of files. Utilizing **natural language processing**, the system enables users to perform queries in **everyday language** and receive **accurate, context-aware results**. Additionally, the application **generates AI-powered summaries** of search results using APIs like **Gemini** or **ChatGPT**, enhancing retrieval efficiency.

### Features  
- **User-Friendly Web Interface:** A streamlined UI allowing users to **upload, index, and search documents** with ease.  
- **AI-Powered Search:** Uses **natural language processing** to interpret user queries accurately.  
- **Robust Indexing System:** Efficiently organizes and indexes documents for **quick retrieval**.  
- **AI Summary Generation:** Provides **automated summaries** for search results using AI models.  
- **Multi-Format Support:** Compatible with **PDFs, Word documents, and text files**.  
- **Scalability & Performance:** Handles **large document volumes** and **multiple simultaneous queries** efficiently.  
- **Optional Cloud Integration:** Future development may include integration with platforms like **Google Drive or Dropbox**.  

### Technical Specifications  
- **Programming Language:** Python  
- **Framework:** Flask  
- **Libraries:**  
  - PyPDF2 and python-docx for document processing  
  - Elasticsearch for fast indexing and search retrieval  
  - Sci-kit learn for machine learning enhancements  
  - Google APIs for AI-generated search summaries  
- **Database:** SQLite for storing document metadata and indexes  
- **Deployment:** Docker containerization for cloud hosting on AWS or Azure  
- **Version Control:** Git for managing development and updates  

### Installation  
1. Clone the repository:  
   ```bash  
   git clone <repository-url>  
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd 1.January_ai-document-search  
   ```  
3. Install the required dependencies:  
   ```bash  
   pip install -r requirements.txt  
   ```  

### Running the Application  
To start the application, run the following command:  
```bash  
python src/app.py  
```  
The application will start on `localhost` at port `6922`.  

### Usage  
- Open the web interface and **upload documents** to be indexed.  
- Enter **search queries** in natural language and retrieve relevant results.  
- View **AI-generated summaries** for quick insights into search results.  

### Contributing  
Contributions are welcome! Please submit a pull request or open an issue for **feature suggestions** or **improvements**.  

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.  