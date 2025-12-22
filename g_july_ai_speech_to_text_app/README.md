# AI Apps Challenge 2025  

### © Hasan Akhtar 2025, All Rights Reserved  

<br>  
<hr>  

## AI Speech-to-Text App (Including Voice Commands) - July Project  

### Project Overview  
The **AI Speech-to-Text App** is a smart voice assistant–style application that enables **real-time transcription, AI summarisation**, and **interactive voice command functionality**. Users can speak naturally to the app, transcribe ongoing meetings, livestreams, or recorded audio (up to 1 hour), and receive a **clear AI-generated summary** of the conversation or media.

Beyond basic transcription, the system supports **custom voice commands** to trigger in-app features such as starting or pausing transcriptions, requesting summaries, and more. To enhance accuracy, the app includes a **voice training feature**, allowing users to record and store vocal samples for improved individual voice recognition.

### Features  
- **Conversational Voice Assistant:** Engage in back-and-forth voice conversations with real-time AI replies.  
- **Audio Transcription:** Transcribes speech from uploaded files, meetings, or live input (up to 60 minutes).  
- **Smart Summarisation:** AI-generated summaries of meetings, conversations, or video content.  
- **Voice Command Detection:** Responds to spoken commands to control app behavior (e.g., "Start transcription").  
- **Voice Training Module:** Users can train the app to better recognise their individual voice tone and pitch.  
- **File & Stream Input Support:** Accepts audio from files, microphone, or live stream inputs.  
- **Export Options:** Transcripts and summaries can be copied to clipboard or exported as `.txt` or `.pdf`.

### Technical Specifications  
1. **Programming Language:** Python  
2. **Frameworks and Libraries:**  
   - **Flask/Django**: Web application framework  
   - **SpeechRecognition**, **PyAudio**, **whisperx** or **Vosk**: For STT (speech-to-text)  
   - **webrtcvad**: For voice activity detection  
   - **SpaCy** or **NLTK**: For natural language understanding and intent recognition  
3. **Database:** SQLite for storing user-defined configurations and logs  
4. **Deployment:** Docker containerization and cloud service deployment (e.g., AWS or Azure)  
5. **Version Control:** Git for source code management  

### Installation  
1. Clone the repository:  
   ```bash  
   git clone <repository-url>  
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd g_july_ai_speech_to_text_app  
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
- Speak directly into your microphone or upload audio/video files.  
- The app will transcribe, summarise, and display the content in real-time.  
- Issue voice commands to control features like **start, pause, summarise**, or **reset**.  
- Use the voice training module to increase recognition accuracy over time.  
- Copy or download transcripts and summaries for future reference.

### Contributing  
Contributions are welcome! Please submit a pull request or open an issue for feature suggestions or improvements.

### License  
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for details.