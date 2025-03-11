# AI Version of Work Hours Calculator

## Overview
The **AI Powered Work Hours Calculator** is a flexible and intuitive application designed to help users calculate their work hours effortlessly. This tool leverages the power of AI to interpret and process work hours input in any format, making it perfect for those who want a detailed breakdown of their hours worked, overtime, and undertime. Additionally, it includes a time-based calculator for performing arithmetic operations on hours, streamlining time-related calculations.

## Features
- **Flexible Input Format:** Users can input work hours in natural language or structured formats.
- **AI-Powered Analysis:** An AI chatbot (likely utilizing the Gemini API, or others) processes inputs and generates:
  - A comprehensive breakdown of total hours worked.
  - Overtime or undertime based on the data provided.
- **Time Calculator:** A dedicated calculator for performing operations on hours, such as finding the difference between two times.
- **User-Friendly Interface:** A clean and intuitive interface for seamless interactions.

## How It Works
1. **Input Work Hours:** Enter work hours in the text box. Examples of supported input formats:
   - *Natural Language*:  
     `"I normally work for 7 hours a day, 5 days a week. Yesterday I started at 9am, had my lunch break from 1pm till 1.30pm and finished at 5pm."`  
   - *Structured Format*:  
     `"Usual work hours per week: 40. Day 1: Started - 8am, Finished - 5pm, Lunch - 12.30-1.15pm; Day 2: Started - 8.30am, Finished - 4.45pm, Lunch - 1-2pm."`
2. **AI Analysis:** The AI chatbot processes the input and provides:
   - A detailed breakdown of hours worked.
   - Overtime/undertime details.
3. **Time Calculator:** Use the calculator to perform time-based operations, e.g.:
   - `"19.50 - 17.55"` → `"1.55 (1 hr 55 mins)"`
4. **Copy Results:** Copy the full evaluation or a concise summary.

## Technical Details
- **Programming Language:** Python  
- **Frameworks and Libraries:**
  - Flask/Django: Web application framework.
  - NLP Libraries: NLTK or SpaCy for natural language processing.
  - Time Parsing: Dateutil for handling date and time information.
  - AI Integration: Gemini API or alternative chatbot APIs.
- **Deployment:** Dockerized application ready for deployment on AWS, Azure, or other cloud platforms.
- **Database:** SQLlite to store user inputs and results.

## Installation and Setup
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/ai-work-hours-calculator.git
   cd ai-work-hours-calculator
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up API Keys:** Configure the `.env` file with API keys for AI chatbot services.
4. **Run the Application:**
   ```bash
   python app.py
   ```
5. **Access the Application:** Open `http://localhost:6922` in your browser.

## Usage
1. Enter your work hours into the text box in your preferred format.
2. View the AI-generated breakdown and evaluation in separate result sections.
3. Use the calculator to perform operations on time.
4. Copy the full evaluation or a concise summary with one click.

## Planned Features
- Integration with productivity tools like Google Calendar or Outlook.
- Export functionality for evaluations in PDF or CSV format.
- Support for multilingual inputs.

## Contributing
We welcome contributions! Please feel free to fork this repository and submit a pull request. For major changes, consider opening an issue to discuss your ideas.

## License
This project is licensed under the MIT License. See the [LICENSE](../LICENSE.txt) file for more details.