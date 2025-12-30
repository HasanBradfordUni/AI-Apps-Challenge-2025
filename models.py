import sqlite3
import json
import os
from datetime import datetime

def create_connection(db_file='ai_chatbot.db'):
    """Create database connection"""
    if not os.path.isabs(db_file):
        # If not absolute path, create in static directory
        this_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(this_dir, "static")
        os.makedirs(static_dir, exist_ok=True)
        db_file = os.path.join(static_dir, db_file)
    
    try:
        connection = sqlite3.connect(db_file, check_same_thread=False)
        connection.row_factory = sqlite3.Row  # Enable column access by name
        return connection
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def create_tables(connection):
    """Create all necessary tables for chatbot hub"""
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                default_prompt_mode TEXT DEFAULT 'general',
                theme TEXT DEFAULT 'dark',
                auto_suggest_apps BOOLEAN DEFAULT 1,
                save_chat_history BOOLEAN DEFAULT 1,
                preferences_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_name TEXT,
                prompt_mode TEXT DEFAULT 'general',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                user_id INTEGER,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                prompt_mode TEXT,
                app_referenced TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # App usage logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id INTEGER,
                app_name TEXT NOT NULL,
                action TEXT,
                input_data_json TEXT,
                output_data_json TEXT,
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        # Prompt mode history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_mode_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id INTEGER,
                mode TEXT NOT NULL,
                query TEXT,
                response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        connection.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        return False

def create_or_get_user(connection, username, email):
    """Create user or get existing user"""
    if not connection:
        raise Exception("No database connection")
        
    cursor = connection.cursor()
    
    try:
        # Check if user exists by email
        cursor.execute('SELECT id, username, email FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                         (datetime.now(), user[0]))
            connection.commit()
            return {'id': user[0], 'username': user[1], 'email': user[2]}
        
        # Create new user
        cursor.execute('INSERT INTO users (username, email, last_login) VALUES (?, ?, ?)', 
                      (username, email, datetime.now()))
        connection.commit()
        user_id = cursor.lastrowid
        
        # Create default preferences
        cursor.execute('INSERT INTO user_preferences (user_id) VALUES (?)', (user_id,))
        connection.commit()
        
        return {'id': user_id, 'username': username, 'email': email}
        
    except sqlite3.Error as e:
        raise Exception(f"Database error creating/getting user: {e}")

def get_user_preferences(connection, user_id):
    """Get user preferences"""
    if not connection:
        return None
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT default_prompt_mode, theme, auto_suggest_apps, 
                   save_chat_history, preferences_json
            FROM user_preferences 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'default_prompt_mode': result[0],
                'theme': result[1],
                'auto_suggest_apps': bool(result[2]),
                'save_chat_history': bool(result[3]),
                'custom_preferences': json.loads(result[4]) if result[4] else {}
            }
        return None
        
    except sqlite3.Error as e:
        print(f"Database error getting preferences: {e}")
        return None

def update_user_preferences(connection, user_id, preferences):
    """Update user preferences"""
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            UPDATE user_preferences 
            SET default_prompt_mode = ?, theme = ?, auto_suggest_apps = ?, 
                save_chat_history = ?, preferences_json = ?, updated_at = ?
            WHERE user_id = ?
        ''', (
            preferences.get('default_prompt_mode', 'general'),
            preferences.get('theme', 'dark'),
            preferences.get('auto_suggest_apps', True),
            preferences.get('save_chat_history', True),
            json.dumps(preferences.get('custom_preferences', {})),
            datetime.now(),
            user_id
        ))
        connection.commit()
        return cursor.rowcount > 0
        
    except sqlite3.Error as e:
        print(f"Database error updating preferences: {e}")
        return False

def create_chat_session(connection, user_id, session_name=None, prompt_mode='general'):
    """Create new chat session"""
    if not connection:
        raise Exception("No database connection")
        
    cursor = connection.cursor()
    
    try:
        if not session_name:
            session_name = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        cursor.execute('''
            INSERT INTO chat_sessions (user_id, session_name, prompt_mode)
            VALUES (?, ?, ?)
        ''', (user_id, session_name, prompt_mode))
        connection.commit()
        return cursor.lastrowid
        
    except sqlite3.Error as e:
        raise Exception(f"Database error creating session: {e}")

def get_active_session(connection, user_id):
    """Get or create active chat session"""
    if not connection:
        return None
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT id, session_name, prompt_mode, started_at
            FROM chat_sessions 
            WHERE user_id = ? AND is_active = 1
            ORDER BY last_activity DESC
            LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'session_name': result[1],
                'prompt_mode': result[2],
                'started_at': result[3]
            }
        
        # Create new session if none exists
        session_id = create_chat_session(connection, user_id)
        return {'id': session_id, 'session_name': 'New Chat', 'prompt_mode': 'general'}
        
    except sqlite3.Error as e:
        print(f"Database error getting active session: {e}")
        return None

def save_chat_message(connection, session_id, user_id, message_type, content, 
                     prompt_mode=None, app_referenced=None):
    """Save chat message"""
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO chat_messages 
            (session_id, user_id, message_type, content, prompt_mode, app_referenced)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, message_type, content, prompt_mode, app_referenced))
        
        # Update session last activity
        cursor.execute('''
            UPDATE chat_sessions SET last_activity = ? WHERE id = ?
        ''', (datetime.now(), session_id))
        
        connection.commit()
        return cursor.lastrowid
        
    except sqlite3.Error as e:
        print(f"Database error saving message: {e}")
        return False

def get_session_messages(connection, session_id, limit=50):
    """Get messages for a session"""
    if not connection:
        return []
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT message_type, content, prompt_mode, app_referenced, timestamp
            FROM chat_messages 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (session_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'type': row[0],
                'content': row[1],
                'prompt_mode': row[2],
                'app_referenced': row[3],
                'timestamp': row[4]
            })
        return messages
        
    except sqlite3.Error as e:
        print(f"Database error getting messages: {e}")
        return []

def log_app_usage(connection, user_id, session_id, app_name, action, 
                 input_data=None, output_data=None, success=True, error_message=None):
    """Log app usage"""
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO app_usage_logs 
            (user_id, session_id, app_name, action, input_data_json, 
             output_data_json, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, session_id, app_name, action,
            json.dumps(input_data) if input_data else None,
            json.dumps(output_data) if output_data else None,
            success, error_message
        ))
        connection.commit()
        return cursor.lastrowid
        
    except sqlite3.Error as e:
        print(f"Database error logging app usage: {e}")
        return False

def get_user_app_stats(connection, user_id):
    """Get user app usage statistics"""
    if not connection:
        return {}
        
    cursor = connection.cursor()
    
    try:
        # Most used apps
        cursor.execute('''
            SELECT app_name, COUNT(*) as usage_count
            FROM app_usage_logs 
            WHERE user_id = ? AND success = 1
            GROUP BY app_name
            ORDER BY usage_count DESC
            LIMIT 5
        ''', (user_id,))
        
        most_used = [{'app': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Total sessions
        cursor.execute('SELECT COUNT(*) FROM chat_sessions WHERE user_id = ?', (user_id,))
        total_sessions = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM chat_messages WHERE user_id = ?', (user_id,))
        total_messages = cursor.fetchone()[0]
        
        return {
            'most_used_apps': most_used,
            'total_sessions': total_sessions,
            'total_messages': total_messages
        }
        
    except sqlite3.Error as e:
        print(f"Database error getting app stats: {e}")
        return {}

def get_user_sessions(connection, user_id, limit=10):
    """Get user's recent chat sessions"""
    if not connection:
        return []
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT id, session_name, prompt_mode, started_at, last_activity, is_active
            FROM chat_sessions 
            WHERE user_id = ? 
            ORDER BY last_activity DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'name': row[1],
                'mode': row[2],
                'started_at': row[3],
                'last_activity': row[4],
                'is_active': bool(row[5])
            })
        return sessions
        
    except sqlite3.Error as e:
        print(f"Database error getting sessions: {e}")
        return []

def end_chat_session(connection, session_id):
    """Mark session as inactive"""
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('UPDATE chat_sessions SET is_active = 0 WHERE id = ?', (session_id,))
        connection.commit()
        return cursor.rowcount > 0
        
    except sqlite3.Error as e:
        print(f"Database error ending session: {e}")
        return False

def save_prompt_mode_query(connection, user_id, session_id, mode, query, response):
    """Save prompt mode query and response"""
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO prompt_mode_history (user_id, session_id, mode, query, response)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_id, mode, query, response))
        connection.commit()
        return cursor.lastrowid
        
    except sqlite3.Error as e:
        print(f"Database error saving prompt mode query: {e}")
        return False

def get_recent_app_calls(connection, user_id, limit=10):
    """Get recent app usage for user"""
    if not connection:
        return []
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT app_name, action, success, timestamp
            FROM app_usage_logs 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        calls = []
        for row in cursor.fetchall():
            calls.append({
                'app': row[0],
                'action': row[1],
                'success': bool(row[2]),
                'timestamp': row[3]
            })
        return calls
        
    except sqlite3.Error as e:
        print(f"Database error getting recent app calls: {e}")
        return []