from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os, json
from datetime import datetime, timedelta
from .models import (create_connection, create_calendar_tables, parse_duration_to_minutes, 
                    minutes_to_duration_string, create_user, create_calendar_event, 
                    get_event_by_id, update_event, get_user_events, find_user_by_email, 
                    log_voice_command, delete_event_by_id)
from .services.ai_parser import AICommandParser
from .services.voice_recognition import VoiceRecognitionService
from .services.calendar_sync import GoogleCalendarService, OutlookCalendarService

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
    tomorrow = today + timedelta(days=1)
    events = get_user_events(connection, session['user_id'], today, tomorrow)  # Add connection parameter
    
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

def execute_voice_command(parsed_command):
    """Execute parsed voice command"""
    action = parsed_command.get('action')
    confidence = parsed_command.get('confidence', 0)
    
    if confidence < 0.5:
        return "Low confidence in command, please try again."
    
    if action == 'create_event':
        event_data = {
            'title': parsed_command.get('event_title', 'New Event'),
            'description': parsed_command.get('description', ''),
            'start_time': f"{parsed_command.get('date')} {parsed_command.get('start_time', '09:00')}",
            'end_time': f"{parsed_command.get('date')} {parsed_command.get('end_time', '10:00')}",
            'location': parsed_command.get('location', ''),
            'attendees': parsed_command.get('attendees', [])
        }
        event_id = create_calendar_event(connection, session['user_id'], event_data)
        return f'Event "{event_data["title"]}" created with ID {event_id}.'
    
    elif action == 'delete_event':
        event_id = parsed_command.get('event_id')
        if event_id:
            # Use the delete_event_by_id function instead
            success = delete_event_by_id(connection, event_id, session['user_id'])
            if success:
                return f'Event ID {event_id} deleted.'
            else:
                return f'Event ID {event_id} not found or permission denied.'
        else:
            return 'No event ID provided for deletion.'
    
    elif action == 'list_events':
        date = parsed_command.get('date', str(datetime.now().date()))
        events = get_user_events(connection, session['user_id'], date, date)  # Add connection parameter
        if events:
            event_list = ', '.join([f"{e[2]} at {e[4]}" for e in events])
            return f'Events on {date}: {event_list}.'
        else:
            return f'No events found on {date}.'
    
    else:
        return 'Unknown command action.'

@calendar_bp.route('/email_sync', methods=['POST'])
def sync_emails():
    """Sync and parse scheduling emails"""
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Not logged in'}), 401
        return redirect(url_for('calendar.login'))
    
    email_subject = request.form.get('subject')
    email_body = request.form.get('body')
    
    if email_subject and email_body:
        try:
            parsed_request = ai_parser.parse_email_scheduling_request(email_subject, email_body)
            
            confidence = parsed_request.get('confidence', 0)
            action = parsed_request.get('action', 'unknown')
            
            if confidence > 0.7 and action == 'create':
                # High confidence - create event
                event_data = {
                    'title': parsed_request.get('event_title', email_subject),
                    'description': f"Created from email: {email_subject}\n\n{email_body[:200]}...",
                    'start_time': f"{parsed_request.get('date')} {parsed_request.get('start_time', '09:00')}",
                    'end_time': f"{parsed_request.get('date')} {parsed_request.get('end_time', '10:00')}",
                    'location': parsed_request.get('location', ''),
                    'attendees': parsed_request.get('attendees', [])
                }
                
                event_id = create_calendar_event(connection, session['user_id'], event_data)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': f'Event "{event_data["title"]}" created from email!',
                        'event_id': event_id,
                        'confidence': confidence
                    })
                
                flash('Event created from email!', 'success')
                
            elif confidence > 0.5:
                # Medium confidence - inform user
                message = f'Email parsed with {confidence:.0%} confidence. Action: {action}. Please review and create manually if needed.'
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': message,
                        'parsed_data': parsed_request
                    })
                
                flash(message, 'warning')
                
            else:
                # Low confidence
                message = 'Could not understand email scheduling request. Please create event manually.'
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': message,
                        'confidence': confidence
                    })
                
                flash(message, 'error')
                
        except Exception as e:
            error_msg = f'Error parsing email: {str(e)}'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': error_msg}), 500
            
            flash(error_msg, 'error')
    else:
        error_msg = 'Please provide both email subject and body.'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': error_msg}), 400
        
        flash(error_msg, 'error')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'message': 'No action taken'})
    
    return redirect(url_for('calendar.dashboard'))

@calendar_bp.route('/api/suggest_times', methods=['POST'])
def suggest_meeting_times():
    """API endpoint to suggest optimal meeting times"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    duration = request.json.get('duration', 60)
    
    # Get existing events for the next 7 days
    today = datetime.now().date()
    events = get_user_events(connection, session['user_id'], today, today + timedelta(days=7))  # Add connection parameter
    
    suggestions = ai_parser.suggest_meeting_times(events, duration)
    
    return jsonify(suggestions)

@calendar_bp.route('/calendar_view/<int:year>/<int:month>')
def calendar_view_month(year, month):
    """Calendar view for specific month"""
    if 'user_id' not in session:
        return redirect(url_for('calendar.login'))
    
    try:
        # Create date for the specified month
        current_month = datetime(year, month, 1).date()
        
        # Calculate calendar boundaries
        start_of_month = current_month
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Get the first day of the calendar grid (previous month's days)
        start_weekday = start_of_month.weekday()
        # Adjust for Sunday start (0=Monday in Python, we want 0=Sunday)
        start_weekday = (start_weekday + 1) % 7
        start_of_calendar = start_of_month - timedelta(days=start_weekday)
        
        # Get events for the entire calendar view (6 weeks)
        end_of_calendar = start_of_calendar + timedelta(days=41)
        events = get_user_events(connection, session['user_id'], start_of_calendar, end_of_calendar)  # Add connection parameter
        
        # Generate 42 days for the calendar grid
        calendar_days = []
        for i in range(42):
            day = start_of_calendar + timedelta(days=i)
            calendar_days.append({
                'date': day,
                'date_string': day.strftime('%Y-%m-%d'),
                'day_number': day.day,
                'is_current_month': day.month == current_month.month,
                'is_today': day == datetime.now().date()
            })
        
        return render_template('calendar_view.html', 
                             events=events, 
                             current_month=current_month,
                             calendar_days=calendar_days,
                             timedelta=timedelta)
    
    except ValueError:
        flash('Invalid month/year specified', 'error')
        return redirect(url_for('calendar.calendar_view'))

# Update the existing calendar_view route
@calendar_bp.route('/calendar_view')
def calendar_view():
    """Calendar view page - current month"""
    if 'user_id' not in session:
        return redirect(url_for('calendar.login'))
    
    # Redirect to current month view
    today = datetime.now().date()
    return redirect(url_for('calendar.calendar_view_month', year=today.year, month=today.month))

@calendar_bp.route('/api/get_event/<int:event_id>')
def get_event(event_id):
    """Get event details for editing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        event = get_event_by_id(connection, event_id, session['user_id'])
        if event:
            # Determine platform from location/platform data
            platform, clean_location = parse_platform_and_location(event[6], event[8] if len(event) > 8 else '')
            
            return jsonify({
                'id': event[0],
                'title': event[2],
                'description': event[3],
                'start_time': event[4],
                'end_time': event[5],
                'location': clean_location,
                'attendees': event[7] if len(event) > 7 else '',
                'platform': platform,
                'duration': minutes_to_duration_string(event[9] if len(event) > 9 else 60),
                'duration_minutes': event[9] if len(event) > 9 else 60,
                'is_all_day': bool(event[10]) if len(event) > 10 else False
            })
        else:
            return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        print(f"Error getting event: {e}")
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/edit_event/<int:event_id>', methods=['POST'])
def edit_event(event_id):
    """Edit existing event"""
    if 'user_id' not in session:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Unauthorized'}), 401
        return redirect(url_for('calendar.login'))
    
    try:
        # Handle both form data and JSON data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        title = data.get('title')
        description = data.get('description', '')
        date = data.get('date')
        start_time = data.get('start_time')
        duration = data.get('duration', '1h')
        location = data.get('location', '')
        attendees = data.get('attendees', '')
        platform = data.get('platform', '')
        
        # Parse duration and calculate end time
        duration_minutes = parse_duration_to_minutes(duration)
        start_datetime = f"{date} {start_time}"
        
        if duration == 'All Day' or duration_minutes >= 1440:
            end_datetime = f"{date} 23:59"
            is_all_day = True
        else:
            from datetime import datetime, timedelta
            start = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
            end = start + timedelta(minutes=duration_minutes)
            end_datetime = end.strftime('%Y-%m-%d %H:%M')
            is_all_day = False
        
        # Combine platform and location properly
        final_location, final_platform = combine_platform_location(platform, location)
        
        # Update event in database
        success = update_event(connection, event_id, session['user_id'], title, description, 
                             start_datetime, end_datetime, final_location, attendees, 
                             final_platform, duration_minutes)
        
        if success:
            # Return JSON for AJAX requests
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': 'Event updated successfully!',
                    'event_id': event_id
                })
            
            flash('Event updated successfully!', 'success')
            return redirect(url_for('calendar.calendar_view'))
        else:
            raise Exception("Event not found or permission denied")
        
    except Exception as e:
        print(f"Error updating event: {e}")
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': f'Error updating event: {str(e)}'}), 500
        
        flash(f'Error updating event: {str(e)}', 'error')
        return redirect(url_for('calendar.calendar_view'))

@calendar_bp.route('/create_event', methods=['GET', 'POST'])
def create_event():
    """Manual event creation"""
    if 'user_id' not in session:
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Not logged in'}), 401
        return redirect(url_for('calendar.login'))
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form
            
            # Parse duration
            duration = data.get('duration', '1h')
            duration_minutes = parse_duration_to_minutes(duration)
            
            # Combine platform and location
            platform = data.get('platform', '')
            location = data.get('location', '')
            final_location, final_platform = combine_platform_location(platform, location)
            
            event_data = {
                'title': data.get('title'),
                'description': data.get('description', ''),
                'start_time': data.get('start_time'),
                'end_time': data.get('end_time'),
                'location': final_location,
                'platform': final_platform,
                'attendees': data.get('attendees', ''),
                'duration_minutes': duration_minutes,
                'is_all_day': data.get('is_all_day', 'false').lower() == 'true'
            }
            
            event_id = create_calendar_event(connection, session['user_id'], event_data)
            
            # Return JSON for AJAX requests
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': 'Event created successfully!',
                    'event_id': event_id,
                    'event': event_data
                })
            
            flash('Event created successfully!', 'success')
            return redirect(url_for('calendar.dashboard'))
            
        except Exception as e:
            print(f"Error creating event: {e}")
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': f'Error creating event: {str(e)}'}), 500
            
            flash(f'Error creating event: {str(e)}', 'error')
            return redirect(url_for('calendar.dashboard'))
    
    return render_template('create_event.html')

@calendar_bp.route('/auth/google')
def auth_google():
    """Initialize Google Calendar OAuth"""
    try:
        google_service = GoogleCalendarService()
        authorization_url = google_service.get_authorization_url()
        return redirect(authorization_url)
    except Exception as e:
        flash(f'Error connecting to Google Calendar: {str(e)}', 'error')
        return redirect(url_for('calendar.dashboard'))

@calendar_bp.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            raise Exception('No authorization code received')
        
        google_service = GoogleCalendarService()
        google_service.exchange_code_for_token(code, state)
        
        # Get and import events
        events = google_service.get_events()
        imported_count = 0
        
        for event_data in events:
            try:
                create_calendar_event(connection, session['user_id'], event_data)
                imported_count += 1
            except Exception as e:
                print(f"Error importing event: {e}")
        
        flash(f'Successfully imported {imported_count} events from Google Calendar!', 'success')
        
    except Exception as e:
        flash(f'Error importing Google Calendar: {str(e)}', 'error')
    
    return redirect(url_for('calendar.dashboard'))

@calendar_bp.route('/auth/outlook')
def auth_outlook():
    """Initialize Outlook Calendar OAuth"""
    try:
        outlook_service = OutlookCalendarService()
        authorization_url = outlook_service.get_authorization_url()
        return redirect(authorization_url)
    except Exception as e:
        flash(f'Error connecting to Outlook Calendar: {str(e)}', 'error')
        return redirect(url_for('calendar.dashboard'))

@calendar_bp.route('/auth/outlook/callback')
def outlook_callback():
    """Handle Outlook OAuth callback"""
    try:
        code = request.args.get('code')
        
        if not code:
            raise Exception('No authorization code received')
        
        outlook_service = OutlookCalendarService()
        outlook_service.exchange_code_for_token(code)
        
        # Get and import events
        events = outlook_service.get_events()
        imported_count = 0
        
        for event_data in events:
            try:
                create_calendar_event(connection, session['user_id'], event_data)
                imported_count += 1
            except Exception as e:
                print(f"Error importing event: {e}")
        
        flash(f'Successfully imported {imported_count} events from Outlook Calendar!', 'success')
        
    except Exception as e:
        flash(f'Error importing Outlook Calendar: {str(e)}', 'error')
    
    return redirect(url_for('calendar.dashboard'))

@calendar_bp.route('/delete_event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete event"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get event details before deletion for feedback
        event = get_event_by_id(connection, event_id, session['user_id'])
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        success = delete_event_by_id(connection, event_id, session['user_id'])
        if success:
            return jsonify({
                'success': True, 
                'message': f'Event "{event[2]}" deleted successfully!',
                'event_id': event_id
            })
        else:
            return jsonify({'error': 'Failed to delete event'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/api/today_events')
def get_today_events():
    """Get today's events for dashboard updates"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        events = get_user_events(connection, session['user_id'], today, tomorrow)
        
        # Format events for JSON response
        formatted_events = []
        for event in events:
            formatted_events.append({
                'id': event[0],
                'title': event[2],
                'description': event[3],
                'start_time': event[4],
                'end_time': event[5],
                'location': event[6],
                'time_display': event[4].split(' ')[1][:5] if event[4] and ' ' in event[4] else 'TBD'
            })
        
        return jsonify({'events': formatted_events})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_platform_and_location(location_field, platform_field):
    """Parse platform and location from stored data"""
    platforms = ['Microsoft Teams', 'Zoom', 'Google Meet', 'Phone Call']
    
    # If platform field exists, use it
    if platform_field:
        if platform_field == 'In Person':
            return 'In Person', location_field
        elif platform_field in platforms:
            return platform_field, location_field
        else:
            return 'Other', platform_field + (' - ' + location_field if location_field else '')
    
    # Check if location contains platform info
    if location_field:
        location_lower = location_field.lower()
        if 'teams' in location_lower or 'microsoft teams' in location_lower:
            return 'Microsoft Teams', location_field
        elif 'zoom' in location_lower:
            return 'Zoom', location_field
        elif 'google meet' in location_lower or 'meet.google' in location_lower:
            return 'Google Meet', location_field
        elif any(word in location_lower for word in ['phone', 'call', 'dial']):
            return 'Phone Call', location_field
        elif any(word in location_lower for word in ['http', 'www', '.com', '.org']):
            return 'Other', location_field
        else:
            return 'In Person', location_field
    
    return 'In Person', ''

def combine_platform_location(platform, location):
    """Combine platform and location for storage"""
    if platform == 'In Person':
        return location, platform
    elif platform in ['Microsoft Teams', 'Zoom', 'Google Meet', 'Phone Call']:
        return location, platform
    elif platform == 'Other':
        return location, 'Other'
    else:
        return location, 'In Person'