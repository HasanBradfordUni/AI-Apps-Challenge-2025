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
import markdown

calendar_bp = Blueprint('calendar', __name__)

# Database setup
db_path = os.path.join(os.path.dirname(__file__), 'static', 'calendar.db')
connection = create_connection(db_path)
create_calendar_tables(connection)

# Initialize services
ai_parser = AICommandParser()
voice_service = VoiceRecognitionService()

# Add markdown filter
@calendar_bp.app_template_filter('markdown')
def markdown_filter(text):
    """Convert markdown to HTML"""
    if not text:
        return ""
    return markdown.markdown(text, extensions=['nl2br', 'fenced_code'])

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
    
    # Get first and last day of the month
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Debug: Print date range
    print(f"=== CALENDAR VIEW DEBUG ===")
    print(f"Fetching events for user {session['user_id']}")
    print(f"Date range: {first_day.strftime('%Y-%m-%d')} to {last_day.strftime('%Y-%m-%d')}")
    
    # Get events for the month
    events = get_user_events(connection, session['user_id'], 
                            first_day.strftime('%Y-%m-%d'), 
                            last_day.strftime('%Y-%m-%d'))
    
    print(f"Total events found: {len(events) if events else 0}")
    if events:
        for event in events:
            print(f"Event: ID={event[0]}, Title={event[2]}, Start={event[4]}")
    
    # Create calendar grid - 6 weeks (42 days) starting from Monday
    calendar_days = []
    
    # Find the Monday of the week containing the first day of the month
    # weekday() returns 0=Monday, 6=Sunday
    days_from_monday = first_day.weekday()
    calendar_start = first_day - timedelta(days=days_from_monday)
    
    print(f"First day of month: {first_day.strftime('%Y-%m-%d')} ({first_day.strftime('%A')})")
    print(f"Calendar starts on: {calendar_start.strftime('%Y-%m-%d')} ({calendar_start.strftime('%A')})")
    
    # Generate 6 weeks (42 days)
    current_date = calendar_start
    today = datetime.now().date()
    
    for i in range(42):
        date_str = current_date.strftime('%Y-%m-%d')
        is_current_month = current_date.month == month and current_date.year == year
        is_today = current_date == today
        
        # Find events for this day
        day_events = []
        if events:
            for event in events:
                event_date = event[4][:10] if event[4] else ''
                if event_date == date_str:
                    day_events.append({
                        'id': event[0],
                        'title': event[2],
                        'start_time': event[4],
                        'end_time': event[5],
                        'location': event[6] if len(event) > 6 else '',
                        'description': event[3] if len(event) > 3 else ''
                    })
        
        calendar_days.append({
            'date': current_date,
            'date_string': date_str,
            'day_number': current_date.day,
            'is_current_month': is_current_month,
            'is_today': is_today,
            'events': day_events
        })
        
        current_date += timedelta(days=1)
    
    print(f"Calendar days created: {len(calendar_days)}")
    print(f"Days with events: {sum(1 for day in calendar_days if day['events'])}")
    print(f"=== END DEBUG ===")
    
    current_month = first_day
    
    return render_template('calendar_view.html',
                         events=events,
                         current_month=current_month,
                         calendar_days=calendar_days,
                         timedelta=timedelta,
                         datetime=datetime)

# Update the existing calendar_view route
@calendar_bp.route('/calendar_view')
def calendar_view():
    """Redirect to current month's calendar view"""
    now = datetime.now()
    return redirect(url_for('calendar.calendar_view_month', year=now.year, month=now.month))

@calendar_bp.route('/api/get_event/<int:event_id>')
def get_event(event_id):
    """Get event details for editing"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        event = get_event_by_id(connection, event_id, session['user_id'])
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Parse platform and location correctly
        platform_parsed, location_parsed = parse_platform_and_location(
            event[6] if len(event) > 6 else '',  # location (index 6)
            event[11] if len(event) > 11 else ''  # platform (index 11)
        )
        
        # Parse duration
        duration_minutes = event[9] if len(event) > 9 else 60
        duration_str = minutes_to_duration_string(duration_minutes)
        
        # Parse start_time to separate date and time
        start_datetime = datetime.strptime(event[4], '%Y-%m-%d %H:%M')
        
        event_data = {
            'id': event[0],
            'title': event[2],
            'description': event[3] or '',
            'date': start_datetime.strftime('%Y-%m-%d'),
            'start_time': start_datetime.strftime('%H:%M'),
            'duration': duration_str,
            'platform': platform_parsed,
            'location': location_parsed,
            'attendees': event[7] or ''
        }
        
        return jsonify(event_data)
        
    except Exception as e:
        print(f"Error getting event: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@calendar_bp.route('/edit_event/<int:event_id>', methods=['POST'])
def edit_event(event_id):
    """Edit existing event"""
    if 'user_id' not in session:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Not logged in'}), 401
        return redirect(url_for('calendar.login'))
    
    try:
        # Handle both form data and JSON data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        title = data.get('title')
        description = data.get('description', '')
        location = data.get('location', '')
        attendees = data.get('attendees', '')
        platform = data.get('platform', '')
        
        # Get date and time - handle both date-only and datetime inputs
        date_input = data.get('date')
        start_time_input = data.get('start_time')
        duration = data.get('duration', '1h')
        
        # Extract just the date if it contains time info
        if 'T' in str(date_input):
            date = date_input.split('T')[0]
        else:
            date = date_input
        
        # Extract just the time if it contains date info
        if 'T' in str(start_time_input):
            start_time = start_time_input.split('T')[1][:5]  # Get HH:MM
        elif ' ' in str(start_time_input):
            start_time = start_time_input.split(' ')[1][:5]
        else:
            start_time = str(start_time_input)[:5]  # Ensure it's HH:MM
        
        # Parse duration and calculate end time
        duration_minutes = parse_duration_to_minutes(duration)
        start_datetime = f"{date} {start_time}"
        
        if duration == 'All Day' or duration_minutes >= 1440:
            end_datetime = f"{date} 23:59"
        else:
            start_dt = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            end_datetime = end_dt.strftime('%Y-%m-%d %H:%M')
        
        # Combine platform and location properly
        final_location, final_platform = combine_platform_location(platform, location)
        
        # Update event in database
        success = update_event(connection, event_id, session['user_id'], title, description, 
                             start_datetime, end_datetime, final_location, attendees, 
                             final_platform, duration_minutes)
        
        if success:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Event updated successfully!'})
            flash('Event updated successfully!', 'success')
            return redirect(url_for('calendar.dashboard'))
        else:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Failed to update event'}), 400
            flash('Failed to update event', 'error')
            return redirect(url_for('calendar.calendar_view'))
        
    except Exception as e:
        print(f"Error updating event: {e}")
        import traceback
        traceback.print_exc()
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
            
            # Debug logging
            print(f"=== CREATE EVENT DEBUG ===")
            print(f"Raw data received: {dict(data)}")
            
            # Get the simple fields
            start_time_raw = data.get('start_time')  # Could be HH:MM or YYYY-MM-DD HH:MM
            end_time_raw = data.get('end_time')
            duration = data.get('duration', '1h')
            
            # Parse start_time - check if it contains date
            if start_time_raw and ' ' in start_time_raw:
                # Format is YYYY-MM-DD HH:MM
                date, start_time = start_time_raw.split(' ', 1)
            else:
                # Separate date field
                date = data.get('date')
                start_time = start_time_raw
            
            # Parse duration to minutes
            duration_minutes = parse_duration_to_minutes(duration)
            
            print(f"Date: {date}")
            print(f"Start time: {start_time}")
            print(f"Duration: {duration} = {duration_minutes} minutes")
            
            # Calculate start and end datetime
            start_datetime_str = f"{date} {start_time}"
            
            # Calculate end time based on duration
            if duration == 'All Day' or duration_minutes >= 1440:
                end_datetime_str = f"{date} 23:59"
                is_all_day = True
            else:
                start_dt = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
                end_dt = start_dt + timedelta(minutes=duration_minutes)
                end_datetime_str = end_dt.strftime('%Y-%m-%d %H:%M')
                is_all_day = False
            
            print(f"Start datetime: {start_datetime_str}")
            print(f"End datetime: {end_datetime_str}")
            
            # Get platform and location
            platform = data.get('platform', 'In Person')
            location = data.get('location', '')
            
            final_location, final_platform = combine_platform_location(platform, location)
            
            event_data = {
                'title': data.get('title'),
                'description': data.get('description', ''),
                'start_time': start_datetime_str,
                'end_time': end_datetime_str,
                'location': final_location,
                'platform': final_platform,
                'attendees': data.get('attendees', ''),
                'duration_minutes': duration_minutes,
                'is_all_day': is_all_day
            }
            
            print(f"Event data to be saved: {event_data}")
            print(f"=== END DEBUG ===")
            
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
            import traceback
            traceback.print_exc()
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': f'Error creating event: {str(e)}'}), 500
            
            flash(f'Error creating event: {str(e)}', 'error')
            return redirect(url_for('calendar.dashboard'))
    
    return render_template('create_event.html', datetime=datetime)

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
    
    # Ensure both fields are strings
    location_field = str(location_field) if location_field else ''
    platform_field = str(platform_field) if platform_field else ''
    
    # If platform field exists and is valid, use it
    if platform_field and platform_field != 'None':
        if platform_field in platforms:
            return platform_field, location_field
        elif platform_field == 'In Person':
            return 'In Person', location_field
        else:
            # Platform is "Other" or custom value
            return 'Other', platform_field + (' - ' + location_field if location_field else '')
    
    # Check if location contains platform info (legacy format)
    if location_field:
        for platform in platforms:
            if platform in location_field:
                # Extract just the meeting link/location
                location_clean = location_field.replace(platform + ': ', '').strip()
                return platform, location_clean
        
        # If no platform found in location, assume In Person
        return 'In Person', location_field
    
    return 'In Person', ''

def combine_platform_location(platform, location):
    """Combine platform and location for storage"""
    if platform == 'In Person':
        return location, 'In Person'
    elif platform in ['Microsoft Teams', 'Zoom', 'Google Meet', 'Phone Call']:
        return location, platform
    elif platform == 'Other':
        return location, 'Other'
    else:
        return location, platform