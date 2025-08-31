import sqlite3
from sqlite3 import Error
from datetime import datetime
import json, os

class CalendarEvent:
    def __init__(self, id=None, user_id=None, title=None, description=None, 
                 start_time=None, end_time=None, location=None, attendees=None,
                 calendar_source=None, external_id=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.attendees = attendees if attendees else []
        self.calendar_source = calendar_source  # 'google', 'outlook', 'manual'
        self.external_id = external_id
        self.created_at = created_at or datetime.now()

class User:
    def __init__(self, id=None, name=None, email=None, google_calendar_token=None,
                 outlook_token=None, preferences=None, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.google_calendar_token = google_calendar_token
        self.outlook_token = outlook_token
        self.preferences = preferences if preferences else {}
        self.created_at = created_at or datetime.now()

def create_connection(db_file='calendar.db'):
    """Create a database connection to the SQLite database specified by db_file"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    path_to = os.path.join(this_dir, "/static")
    db_file = os.path.join(path_to, db_file)
    connection = None
    try:
        connection = sqlite3.connect(db_file, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def create_calendar_tables(connection):
    """Create calendar tables with proper schema"""
    cursor = connection.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Events table with all required fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            location TEXT,
            attendees TEXT,
            platform TEXT,
            duration_minutes INTEGER DEFAULT 60,
            is_all_day BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if columns exist and add them if they don't
    cursor.execute("PRAGMA table_info(events)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'platform' not in columns:
        cursor.execute('ALTER TABLE events ADD COLUMN platform TEXT')
    if 'duration_minutes' not in columns:
        cursor.execute('ALTER TABLE events ADD COLUMN duration_minutes INTEGER DEFAULT 60')
    if 'is_all_day' not in columns:
        cursor.execute('ALTER TABLE events ADD COLUMN is_all_day BOOLEAN DEFAULT 0')
    if 'updated_at' not in columns:
        cursor.execute('ALTER TABLE events ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    
    connection.commit()

def create_calendar_event(connection, user_id, event_data):
    """Create a new calendar event with all fields"""
    cursor = connection.cursor()
    
    # Parse attendees if it's a string
    attendees = event_data.get('attendees', '')
    if isinstance(attendees, list):
        attendees = ', '.join(attendees)
    
    # Parse duration
    duration_minutes = event_data.get('duration_minutes', 60)
    if isinstance(duration_minutes, str):
        duration_minutes = parse_duration_to_minutes(duration_minutes)
    
    cursor.execute('''
        INSERT INTO events (user_id, title, description, start_time, end_time, 
                          location, attendees, platform, duration_minutes, is_all_day)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        event_data['title'],
        event_data.get('description', ''),
        event_data['start_time'],
        event_data['end_time'],
        event_data.get('location', ''),
        attendees,
        event_data.get('platform', ''),
        duration_minutes,
        event_data.get('is_all_day', False)
    ))
    
    connection.commit()
    return cursor.lastrowid

def update_event(connection, event_id, user_id, title, description, start_time, end_time, location, attendees, platform=None, duration_minutes=60):
    """Update an existing event"""
    cursor = connection.cursor()
    
    # Parse attendees if it's a string
    if isinstance(attendees, list):
        attendees = ', '.join(attendees)
    
    cursor.execute('''
        UPDATE events 
        SET title = ?, description = ?, start_time = ?, end_time = ?, 
            location = ?, attendees = ?, platform = ?, duration_minutes = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (title, description, start_time, end_time, location, attendees, platform or '', duration_minutes, event_id, user_id))
    
    connection.commit()
    return cursor.rowcount > 0

def get_event_by_id(connection, event_id, user_id):
    """Get a specific event by ID"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, user_id, title, description, start_time, end_time, 
               location, attendees, platform, duration_minutes, is_all_day
        FROM events 
        WHERE id = ? AND user_id = ?
    ''', (event_id, user_id))
    return cursor.fetchone()

def parse_duration_to_minutes(duration_str):
    """Parse duration string to minutes"""
    if not duration_str:
        return 60
    
    duration_str = str(duration_str).lower().strip()
    
    if duration_str == 'all day':
        return 1440  # 24 hours
    
    import re
    hour_match = re.search(r'(\d+)h', duration_str)
    minute_match = re.search(r'(\d+)m', duration_str)
    
    total_minutes = 0
    if hour_match or minute_match:
        if hour_match:
            total_minutes += int(hour_match.group(1)) * 60
        if minute_match:
            total_minutes += int(minute_match.group(1))
    else:
        try:
            number = int(duration_str)
            if number < 10:
                total_minutes = number * 60  # Hours
            else:
                total_minutes = number  # Minutes
        except ValueError:
            total_minutes = 60  # Default 1 hour
    
    return total_minutes

def minutes_to_duration_string(minutes):
    """Convert minutes to duration string"""
    if minutes >= 1440:
        return "All Day"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0 and mins > 0:
        return f"{hours}h {mins}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}m"
    
def find_user_by_email(connection, email):
    """Find a user by email"""
    cursor = connection.cursor()
    cursor.execute('SELECT id, name, email FROM users WHERE email = ?', (email,))
    return cursor.fetchone()

def create_user(connection, name, email):
    """Create a new user"""
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
    connection.commit()
    return cursor.lastrowid

def delete_event_by_id(connection, event_id, user_id):
    """Delete a specific event by ID"""
    cursor = connection.cursor()
    cursor.execute('DELETE FROM events WHERE id = ? AND user_id = ?', (event_id, user_id))
    connection.commit()
    return cursor.rowcount > 0

def log_voice_command(connection, user_id, command_text, parsed_command=None):
    """Log a voice command for auditing"""
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            command_text TEXT,
            parsed_command TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    parsed_json = json.dumps(parsed_command) if parsed_command else None
    cursor.execute('INSERT INTO voice_commands (user_id, command_text, parsed_command) VALUES (?, ?, ?)', 
                   (user_id, command_text, parsed_json))
    connection.commit()
    return cursor.lastrowid

def get_user_events(connection, user_id, start_date=None, end_date=None):
    """Get events for a user within an optional date range"""
    cursor = connection.cursor()
    query = 'SELECT id, title, description, start_time, end_time, location, attendees, platform, duration_minutes, is_all_day FROM events WHERE user_id = ?'
    params = [user_id]
    
    if start_date:
        query += ' AND start_time >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND end_time <= ?'
        params.append(end_date)
    
    query += ' ORDER BY start_time ASC'
    
    cursor.execute(query, params)
    return cursor.fetchall()