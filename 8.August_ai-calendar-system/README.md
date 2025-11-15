# AI Apps Challenge 2025  

### © Hasan Akhtar 2025, All Rights Reserved  

<br>  
<hr>  

## AI Calendar & Scheduling System – August Project  

### Project Overview  
The **AI Calendar & Scheduling System** is an intelligent productivity assistant built for **secretaries, personal assistants (PAs), and executive support staff**. This application connects seamlessly to **email platforms and external calendar services** to automatically parse scheduling requests, resolve conflicts, and recommend optimal meeting times.  

The system provides a unified dashboard to manage multiple calendars, understand natural language commands, and generate AI-powered summaries, briefings, and scheduling follow-ups—giving professional users more control and insight with less manual effort.  

### Features  
- **Email Integration:** Parses scheduling instructions from emails using natural language understanding.  
- **Calendar Syncing:** Connects with Outlook, Google Calendar, and other platforms for real-time updates.  
- **Smart Conflict Resolution:** Detects overlaps and proposes alternate time slots automatically.  
- **Intelligent Suggestions:** Offers recommended meeting times based on context, availability, and user preferences.  
- **Text & Voice Command Input:** Users can issue scheduling commands conversationally.  
- **Multi-User Support:** Manage calendars for multiple team members with role-specific access.  
- **Daily & Weekly Summaries:** Sends briefings via email or dashboard with agendas, tasks, and reminders.  
- **Custom Scheduling Rules:** Define preferred hours, buffer durations, and meeting types for personalised automation.  

### Technical Specifications  
1. **Programming Language:** Python  
2. **Frameworks and Libraries:**  
   - Flask/Django: Web application framework  
   - Gemini API: For NLP and command parsing  
   - Google Calendar API, Microsoft Graph API: For calendar syncing  
   - IMAP/Gmail API: For email parsing  
   - SpeechRecognition or Vosk: For voice command input  
3. **Database:** SQLite for user calendars, configurations, and logs  
4. **Deployment:** Docker containerisation and cloud service deployment (e.g., AWS or Azure)  
5. **Version Control:** Git for source code management  

### Installation  
1. Clone the repository:  
   ```bash  
   git clone <repository-url>  
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd 8.August_ai-calendar-system  
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
- Open the dashboard in your browser to view calendar events.  
- Connect your email and calendar accounts.  
- Use **text or voice commands** to create, move, cancel, or summarise events.  
- View personalised meeting suggestions, scheduling alerts, and daily agenda summaries.  

### Contributing  
Contributions are welcome! Please submit a pull request or open an issue for feature suggestions or improvements.  

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.  
