# AI Apps Challenge Chatbot  

### © Hasan Akhtar 2025, All Rights Reserved  

<br>  
<hr>  

## General Integrated AI Chatbot – December Project  

### Project Overview  
The **General Integrated AI Chatbot** is the twelfth and final project of the challenge, acting as a **central hub** for all previous apps. It provides a **chat interface** where users can ask general questions or request tasks that map to the earlier projects, such as document summarisation, cover letter generation, or calendar scheduling.  

This chatbot also supports **prompt modes** (code, writing, Q&A, etc.), making it versatile for both general use and specialised workflows.  

### Features  
- **Chatbot Interface:** Conversational UI for queries and tasks.  
- **Prompt Modes:** Switch between *code*, *writing*, *Q&A*, and more.  
- **Integration with 11 Apps:** Calls functions from all previous projects.  
- **Unified Workflow:** Access any app’s functionality from one place.  
- **Directory Structure:** Root app + `l_december_ai_chatbot` folder for helper functions.  
- **Extensible Design:** Easy to add new apps or modes.  

### Technical Specifications  
1. **Programming Language:** Python  
2. **Frameworks and Libraries:**  
   - Flask: Web application framework.
   - PyPDF2 + python-docx: For PDF/Word Doc handling and text extraction.
   - Gemini: For general query handling and prompt modes.
3. **Database:** SQLite for storing users, chatbot sessions and preferences  
4. **Deployment:** Docker containerization and cloud hosting (AWS/Azure)  
5. **Version Control:** Git for source code management  

### Installation  
1. Clone the repository:  
   ```bash  
   git clone <repository-url>  
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd l_december_ai_chatbot  
   ```  
3. Install the required dependencies:  
   ```bash  
   pip install -r requirements.txt  
   ```  

### Running the Application  
To start the chatbot, run:  
```bash  
python run.py  
```  
The application will start on `localhost` at port `6922`.  

### Usage  
- Open the chatbot interface in your browser.  
- Select a **prompt mode** (code, writing, Q&A, etc.).  
- Ask general queries or request tasks from the previous 11 apps.  
- View results directly in the chat window.  

### Contributing  
Contributions are welcome! Please submit a pull request or open an issue for feature suggestions or improvements.  

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.  