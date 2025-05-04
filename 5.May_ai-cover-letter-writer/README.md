# AI Apps Challenge 2025

### © Hasan Akhtar 2025, All Rights Reserved

<br>
<hr>

## AI Cover Letter Writer - May Project 

### Project Overview  
The **AI Cover Letter Writer** is a web-based application designed to help users create **professional and well-structured cover letters** tailored to specific job applications. Using **Gemini 2.0 Flash**, the AI crafts optimised cover letters based on a user’s **CV and job description**, ensuring natural, high-quality text output. The application features **a Flask-powered front-end**, enabling users to generate, edit, and export cover letters effortlessly.  

### Features  
- **User-Friendly Web Interface:** A clean, interactive UI allowing users to input their **CV details** and **job descriptions** easily.  
- **AI-Powered Generation:** Uses **Gemini 2.0 Flash** to craft well-structured cover letters with **optimised prompts** for a professional tone.  
- **Live Preview & Editing:** Users can **view and refine** the AI-generated cover letter before finalising.  
- **Customisation Tools:** Provides options for modifying structure, tone, and wording to ensure personalisation.  
- **Copy & Export Options:** Includes **copy-to-clipboard functionality** and a **PDF download** feature for easy document sharing.  
- **Potential Email Integration:** Future development may allow **direct job application submission** via email.  

### Technical Specifications  
- **Programming Language:** Python  
- **Framework:** Flask  
- **Libraries:**  
  - Gemini AI models for text generation  
  - Jinja2 for dynamic UI rendering  
  - HTML/CSS/JavaScript for front-end enhancements  
- **Database:** SQLite for User inputs which can be reused when generating the cover letter (e.g. Employability Skills, Past education, Work Experience etc.)  
- **Deployment:** Docker containerisation for cloud hosting on AWS or Azure  
- **Version Control:** Git for managing development and updates  

### Installation  
1. Clone the repository:  
   ```bash  
   git clone <repository-url>  
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd 5.May_ai-cover-letter-writer  
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
- Open the web interface and enter your **CV details** and **job description**.  
- Generate an AI-powered cover letter and review the **live preview**.  
- Edit and refine the content before finalising.  
- Copy or download the completed cover letter in **PDF format**.  

### Contributing  
Contributions are welcome! Please submit a pull request or open an issue for feature suggestions or improvements.  

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.  
