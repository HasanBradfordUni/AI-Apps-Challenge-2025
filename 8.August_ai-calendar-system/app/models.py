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
    """Create calendar-specific database tables"""
    cursor = connection.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        google_calendar_token TEXT,
        outlook_token TEXT,
        preferences TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Calendar events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        location TEXT,
        attendees TEXT,
        calendar_source TEXT,
        external_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Email commands log
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        email_subject TEXT,
        email_body TEXT,
        parsed_command TEXT,
        action_taken TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Voice commands log
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voice_commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        command_text TEXT NOT NULL,
        parsed_intent TEXT,
        action_taken TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    connection.commit()