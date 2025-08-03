from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
from datetime import datetime, timedelta
import json
from .models import create_calendar_tables, CalendarEvent, User
from .services.ai_parser import AICommandParser
from .services.voice_recognition import VoiceRecognitionService
from .services.calendar_sync import GoogleCalendarService, OutlookCalendarService
from .models import create_connection

calendar_bp = Blueprint('calendar', __name__)

# Database setup
db_path = os.path.join(os.path.dirname(__file__), 'static', 'calendar.db')
connection = create_connection(db_path)
create_calendar_tables(connection)

# Initialize services
ai_parser = AICommandParser()
voice_service = VoiceRecognitionService()

@calendar_bp.route('/')
def dashboard():
    """Main dashboard showing calendar overview"""
    if 'user_id' not in session:
        return redirect(url_for('calendar.login'))
    
    # Get today's events
    today = datetime.now().date()
    events = get_user_events(session['user_id'], today, today + timedelta(days=1))
    
    # Generate daily summary
    daily_summary = ai_parser.generate_daily_summary(events, str(today))
    
    return render_template('index.html', events=events, daily_summary=daily_summary, today=today)

@calendar_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login/registration"""
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        
        # Simple login - find or create user
        user = find_user_by_email(connection, email)
        if not user:
            user_id = create_user(connection, name, email)
            flash('Account created successfully!', 'success')
        else:
            user_id = user[0]
            flash('Welcome back!', 'success')
        
        session['user_id'] = user_id
        return redirect(url_for('calendar.dashboard'))
    
    return render_template('login.html')

@calendar_bp.route('/voice_command', methods=['GET', 'POST'])
def voice_command():
    """Handle voice commands"""
    if 'user_id' not in session:
        return redirect(url_for('calendar.login'))
    
    if request.method == 'POST':
        # Check if it's audio file upload or live recording
        if 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            if audio_file.filename:
                command_text = voice_service.process_audio_file(audio_file)
            else:
                flash('No audio file provided', 'error')
                return redirect(url_for('calendar.voice_command'))
        else:
            # Live recording
            command_text = voice_service.listen_for_command()
        
        if command_text and not command_text.startswith(('Timeout', 'Could not', 'Error')):
            # Parse the voice command
            parsed_command = ai_parser.parse_voice_command(command_text)
            
            # Log the command
            log_voice_command(connection, session['user_id'], command_text, parsed_command)
            
            # Execute the command
            result = execute_voice_command(parsed_command)
            
            flash(f"Command processed: {result}", 'success')
            return redirect(url_for('calendar.dashboard'))
        else:
            flash(f"Voice recognition failed: {command_text}", 'error')
    
    return render_template('voice_command.html')

@calendar_bp.route('/email_sync', methods=['POST'])
def sync_emails():
    """Sync and parse scheduling emails"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    # This would integrate with email APIs
    # For demo purposes, we'll accept manual email input
    email_subject = request.form.get('subject')
    email_body = request.form.get('body')
    
    if email_subject and email_body:
        parsed_request = ai_parser.parse_email_scheduling_request(email_subject, email_body)
        
        if parsed_request.get('confidence', 0) > 0.7:
            # High confidence - create event
            if parsed_request.get('action') == 'create':
                event_data = {
                    'title': parsed_request.get('event_title'),
                    'description': f"Created from email: {email_subject}",
                    'start_time': f"{parsed_request.get('date')} {parsed_request.get('start_time')}",
                    'end_time': f"{parsed_request.get('date')} {parsed_request.get('end_time')}",
                    'location': parsed_request.get('location'),
                    'attendees': parsed_request.get('attendees', [])
                }
                
                create_calendar_event(connection, session['user_id'], event_data)
                flash('Event created from email!', 'success')
            else:
                flash(f'Email parsed - Action: {parsed_request.get("action")}', 'info')
        else:
            flash('Could not understand email scheduling request', 'warning')
    
    return redirect(url_for('calendar.dashboard'))

@calendar_bp.route('/api/suggest_times', methods=['POST'])
def suggest_meeting_times():
    """API endpoint to suggest optimal meeting times"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    duration = request.json.get('duration', 60)
    
    # Get existing events for the next 7 days
    today = datetime.now().date()
    events = get_user_events(session['user_id'], today, today + timedelta(days=7))
    
    suggestions = ai_parser.suggest_meeting_times(events, duration)
    
    return jsonify(suggestions)

@calendar_bp.route('/calendar_view')
def calendar_view():
    """Calendar view page"""
    if 'user_id' not in session:
        return redirect(url_for('calendar.login'))
    
    # Get events for the current month
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    events = get_user_events(session['user_id'], start_of_month, end_of_month)
    
    return render_template('calendar_view.html', events=events, current_month=today)

@calendar_bp.route('/create_event', methods=['GET', 'POST'])
def create_event():
    """Manual event creation"""
    if 'user_id' not in session:
        return redirect(url_for('calendar.login'))
    
    if request.method == 'POST':
        event_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'start_time': request.form.get('start_time'),
            'end_time': request.form.get('end_time'),
            'location': request.form.get('location'),
            'attendees': request.form.get('attendees', '').split(',') if request.form.get('attendees') else []
        }
        
        create_calendar_event(connection, session['user_id'], event_data)
        flash('Event created successfully!', 'success')
        return redirect(url_for('calendar.dashboard'))
    
    return render_template('create_event.html')

# Helper functions
def get_user_events(user_id, start_date, end_date):
    """Get user events between dates"""
    cursor = connection.cursor()
    query = """
    SELECT * FROM calendar_events 
    WHERE user_id = ? AND date(start_time) BETWEEN ? AND ?
    ORDER BY start_time
    """
    cursor.execute(query, (user_id, start_date, end_date))
    return cursor.fetchall()

def create_calendar_event(connection, user_id, event_data):
    """Create a new calendar event"""
    cursor = connection.cursor()
    query = """
    INSERT INTO calendar_events (user_id, title, description, start_time, end_time, location, attendees)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    attendees_json = json.dumps(event_data.get('attendees', []))
    cursor.execute(query, (
        user_id,
        event_data.get('title'),
        event_data.get('description'),
        event_data.get('start_time'),
        event_data.get('end_time'),
        event_data.get('location'),
        attendees_json
    ))
    connection.commit()
    return cursor.lastrowid

def find_user_by_email(connection, email):
    """Find user by email"""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone()

def create_user(connection, name, email):
    """Create new user"""
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    connection.commit()
    return cursor.lastrowid

def log_voice_command(connection, user_id, command_text, parsed_command):
    """Log voice command"""
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO voice_commands (user_id, command_text, parsed_intent, action_taken)
    VALUES (?, ?, ?, ?)
    """, (user_id, command_text, json.dumps(parsed_command), 'processed'))
    connection.commit()

def execute_voice_command(parsed_command):
    """Execute parsed voice command"""
    intent = parsed_command.get('intent')
    
    if intent == 'create_event':
        details = parsed_command.get('action_details', {})
        # Create event logic here
        return f"Created event: {details.get('event_title')}"
    elif intent == 'check_schedule':
        return "Checking your schedule..."
    elif intent == 'cancel_event':
        return "Event cancellation requested"
    else:
        return "Command not recognized"