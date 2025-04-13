# General AI Document Search

## Project Overview
The General AI Document Search application leverages AI and natural language processing to enable users to efficiently search and retrieve relevant documents from a vast collection of files. It provides an intelligent search interface that understands user queries in natural language and returns the most pertinent results.

## Objectives
1. Develop an AI-powered search engine capable of processing natural language queries.
2. Implement a user-friendly interface for uploading, indexing, and searching documents.
3. Ensure the system can handle various document formats (e.g., PDFs, Word documents, text files).
4. Provide accurate and relevant search results with minimal response time.
5. Provide an AI Summary on the top using APIs such as Gemini, ChatGPT, etc.
6. Integrate the application with common document storage solutions (optional).

## Key Features
- Natural Language Processing for understanding user queries.
- Document Indexing for quick retrieval.
- Robust Search Algorithm for ranking documents based on relevance.
- Simple and intuitive User Interface for document uploads and search queries.
- Multi-format Support for various document types.
- AI Summary generation based on user queries and relevant documents.
- Scalability to handle large volumes of documents and multiple simultaneous queries.
- Optional integration with popular document storage platforms.

## Technical Specifications
- **Programming Language:** Python
- **Frameworks and Libraries:** Flask for web interface, PyPDF2 and Python Docx to process PDF and Word Documents, Elasticsearch for searching through indexed files, Sci-kit learn for machine learning, Google APIs to link to Gemini AI for search summarisation
- **Database:** SQLite for storing metadata and document indices
- **Deployment:** Docker for containerization and deployment on cloud services
- **Version Control:** Git for source code management

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd 1.January_ai-document-search
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python src/app.py
   ```

## Usage
- Access the application through your web browser at `http://localhost:6922`.
- Upload documents and enter search queries to retrieve relevant results.

## Expected Outcomes
- A fully functional AI-powered document search application.
- Increased efficiency in document retrieval and access.
- Improved user experience through an intuitive search interface.
- Clear search results via the AI Summary at the top.

## Risks and Mitigations
- **Data Privacy:** Implement encryption and access control measures.
- **Performance:** Optimize the search algorithm and indexing process.
- **AI Summary Accuracy:** Ensure the AI Summary is accurate and helpful.
- **Integration Challenges:** Test integration with different document storage platforms.