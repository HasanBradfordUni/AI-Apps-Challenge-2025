# AI Programming Assistant  

### © Hasan Akhtar 2025, All Rights Reserved  

<hr>  

## AI Programming Assistant – November Project  

### Project Overview  
The **AI Programming Assistant** is a browser-based coding companion designed to help developers write, understand, and debug code more efficiently. Inspired by GitHub Copilot, this tool provides **AI-powered code suggestions**, **error explanations**, and **inline documentation** through a clean, multi-language interface.  

It’s built for accessibility—no IDE setup required. Just open the app, choose your language, and start coding with AI support.

### Features  
- **Multi-Language Support:** Python, JavaScript, C++, Java, and more.  
- **AI Code Suggestions:** Smart completions and refactoring ideas.  
- **Error Explanation:** Paste error messages and get debugging help.  
- **Inline Documentation:** Generate docstrings and comments automatically.  
- **Syntax Highlighting:** Clean editor with language-specific formatting.  
- **Session Management:** Save and reload code snippets.  
- **Copy & Export Options:** Download (to txt or specific filetype for chosen programming language) or copy code easily.  
- **Responsive UI:** Lightweight IDE-like experience in the browser.

### Technical Specifications  
1. **Programming Language:** Python  
2. **Frameworks and Libraries:**  
   - Flask: Web application framework  
   - CodeMirror or Monaco Editor: For browser-based code editing  
   - Gemini API: For code generation and explanation  
   - Pygments: For syntax highlighting  
   - JavaScript: For dynamic UI interactions 
3. **Deployment:** Docker containerization and cloud hosting (e.g., AWS or Azure)  
4. **Version Control:** Git for source code management  

### Installation  
1. Clone the repository:  
   ```bash  
   git clone <repository-url>  
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd k_november_ai_coding_assistant  
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
- Open the web interface and select your programming language.  
- Start typing code and receive AI-powered suggestions.  
- Paste error messages for debugging help.  
- Generate inline documentation with a single click.  
- Save or export your code when ready.

### Contributing  
Contributions are welcome! Please submit a pull request or open an issue for feature suggestions or improvements.

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.