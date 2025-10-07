import sqlite3
import json
import os
from datetime import datetime

def create_connection(db_file='directory_summariser.db'):
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
    """Create all necessary tables"""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_content BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Directory analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS directory_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                directory_path TEXT NOT NULL,
                total_files INTEGER,
                total_size INTEGER,
                file_types_json TEXT,
                ai_insights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Template matches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                template_id INTEGER,
                category TEXT,
                match_count INTEGER,
                matched_files_json TEXT,
                FOREIGN KEY (analysis_id) REFERENCES directory_analyses (id),
                FOREIGN KEY (template_id) REFERENCES user_templates (id)
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
            return {'id': user[0], 'username': user[1], 'email': user[2]}
        
        # Create new user
        cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
        connection.commit()
        user_id = cursor.lastrowid
        
        return {'id': user_id, 'username': username, 'email': email}
        
    except sqlite3.Error as e:
        raise Exception(f"Database error creating/getting user: {e}")

def save_user_template(connection, user_id, category, filename, file_content):
    """Save user template"""
    if not connection:
        raise Exception("No database connection")
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO user_templates (user_id, category, filename, file_content)
            VALUES (?, ?, ?, ?)
        ''', (user_id, category, filename, file_content))
        connection.commit()
        return cursor.lastrowid
        
    except sqlite3.Error as e:
        raise Exception(f"Database error saving template: {e}")

def get_user_templates(connection, user_id):
    """Get all templates for a user"""
    if not connection:
        return []
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT id, category, filename, created_at 
            FROM user_templates 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Database error getting templates: {e}")
        return []

def save_directory_analysis(connection, user_id, directory_path, analysis_data):
    """Save directory analysis for user"""
    if not connection:
        raise Exception("No database connection")
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO directory_analyses 
            (user_id, directory_path, total_files, total_size, file_types_json, ai_insights)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            directory_path,
            analysis_data.get('total_files', 0),
            analysis_data.get('total_size', 0),
            json.dumps(analysis_data.get('file_type_categories', {})),
            analysis_data.get('ai_insights', '')
        ))
        connection.commit()
        return cursor.lastrowid
        
    except sqlite3.Error as e:
        raise Exception(f"Database error saving analysis: {e}")

def get_user_recent_analyses(connection, user_id, limit=5):
    """Get recent analyses for user"""
    if not connection:
        return []
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT directory_path, total_files, total_size, created_at
            FROM directory_analyses 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Database error getting recent analyses: {e}")
        return []

def delete_user_template(connection, template_id, user_id):
    """Delete user template"""
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('DELETE FROM user_templates WHERE id = ? AND user_id = ?', (template_id, user_id))
        connection.commit()
        return cursor.rowcount > 0
        
    except sqlite3.Error as e:
        print(f"Database error deleting template: {e}")
        return False

def get_template_content(connection, template_id, user_id):
    """Get template file content"""
    if not connection:
        return None
        
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            SELECT file_content, filename, category 
            FROM user_templates 
            WHERE id = ? AND user_id = ?
        ''', (template_id, user_id))
        result = cursor.fetchone()
        
        if result:
            return {
                'content': result[0],
                'filename': result[1],
                'category': result[2]
            }
        return None
        
    except sqlite3.Error as e:
        print(f"Database error getting template content: {e}")
        return None

def save_template_matches(connection, analysis_id, template_matches):
    """Save template matching results"""
    if not connection:
        return False
        
    cursor = connection.cursor()
    
    try:
        for match in template_matches:
            cursor.execute('''
                INSERT INTO template_matches 
                (analysis_id, template_id, category, match_count, matched_files_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                analysis_id,
                match.get('template_id'),
                match.get('category'),
                match.get('match_count', 0),
                json.dumps(match.get('matched_files', []))
            ))
        
        connection.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error saving template matches: {e}")
        return False

def get_analysis_with_matches(connection, analysis_id, user_id):
    """Get analysis with template matches"""
    if not connection:
        return None
        
    cursor = connection.cursor()
    
    try:
        # Get analysis data
        cursor.execute('''
            SELECT directory_path, total_files, total_size, file_types_json, ai_insights, created_at
            FROM directory_analyses 
            WHERE id = ? AND user_id = ?
        ''', (analysis_id, user_id))
        
        analysis = cursor.fetchone()
        if not analysis:
            return None
        
        # Get template matches
        cursor.execute('''
            SELECT category, match_count, matched_files_json
            FROM template_matches 
            WHERE analysis_id = ?
        ''', (analysis_id,))
        
        matches = cursor.fetchall()
        
        return {
            'directory_path': analysis[0],
            'total_files': analysis[1],
            'total_size': analysis[2],
            'file_type_categories': json.loads(analysis[3]) if analysis[3] else {},
            'ai_insights': analysis[4],
            'created_at': analysis[5],
            'template_matches': [
                {
                    'category': match[0],
                    'match_count': match[1],
                    'matched_files': json.loads(match[2]) if match[2] else []
                }
                for match in matches
            ]
        }
        
    except sqlite3.Error as e:
        print(f"Database error getting analysis with matches: {e}")
        return None

def get_user_stats(connection, user_id):
    """Get user statistics"""
    if not connection:
        return {}
        
    cursor = connection.cursor()
    
    try:
        # Get template count
        cursor.execute('SELECT COUNT(*) FROM user_templates WHERE user_id = ?', (user_id,))
        template_count = cursor.fetchone()[0]
        
        # Get analysis count
        cursor.execute('SELECT COUNT(*) FROM directory_analyses WHERE user_id = ?', (user_id,))
        analysis_count = cursor.fetchone()[0]
        
        # Get total files analyzed
        cursor.execute('SELECT SUM(total_files) FROM directory_analyses WHERE user_id = ?', (user_id,))
        total_files = cursor.fetchone()[0] or 0
        
        # Get total size analyzed
        cursor.execute('SELECT SUM(total_size) FROM directory_analyses WHERE user_id = ?', (user_id,))
        total_size = cursor.fetchone()[0] or 0
        
        return {
            'template_count': template_count,
            'analysis_count': analysis_count,
            'total_files_analyzed': total_files,
            'total_size_analyzed': total_size
        }
        
    except sqlite3.Error as e:
        print(f"Database error getting user stats: {e}")
        return {}