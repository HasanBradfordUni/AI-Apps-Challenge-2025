import sqlite3
import json
import os
from datetime import datetime
from sqlite3 import Error

def create_connection(db_file='directory_summaries.db'):
    """Create a database connection to the SQLite database"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(this_dir, "static")
    os.makedirs(static_dir, exist_ok=True)
    db_file = os.path.join(static_dir, db_file)
    
    connection = None
    try:
        connection = sqlite3.connect(db_file, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def create_summary_tables(connection):
    """Create directory summary tables"""
    cursor = connection.cursor()
    
    # Directory summaries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS directory_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            directory_path TEXT NOT NULL,
            total_files INTEGER DEFAULT 0,
            total_size INTEGER DEFAULT 0,
            file_types_json TEXT,
            analysis_data_json TEXT,
            ai_insights TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Template matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS template_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER,
            template_category TEXT,
            template_file TEXT,
            matched_files_json TEXT,
            similarity_scores_json TEXT,
            match_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (summary_id) REFERENCES directory_summaries (id)
        )
    ''')
    
    # File analysis cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_analysis_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE,
            file_size INTEGER,
            file_type TEXT,
            word_count INTEGER,
            character_count INTEGER,
            content_hash TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    connection.commit()

def save_directory_summary(connection, summary_data):
    """Save directory analysis summary to database"""
    cursor = connection.cursor()
    
    analysis_result = summary_data.get('analysis_result', {})
    content_analysis = summary_data.get('content_analysis', {})
    
    cursor.execute('''
        INSERT INTO directory_summaries 
        (directory_path, total_files, total_size, file_types_json, analysis_data_json, ai_insights)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        summary_data['directory_path'],
        analysis_result.get('total_files', 0),
        analysis_result.get('total_size', 0),
        json.dumps(analysis_result.get('file_types', {})),
        json.dumps({
            'analysis': analysis_result,
            'content': content_analysis
        }),
        summary_data.get('ai_insights', '')
    ))
    
    connection.commit()
    return cursor.lastrowid

def get_recent_summaries(connection, limit=10):
    """Get recent directory summaries"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, directory_path, total_files, total_size, created_at
        FROM directory_summaries 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    return [{
        'id': row[0],
        'directory_path': row[1],
        'total_files': row[2],
        'total_size': row[3],
        'created_at': row[4]
    } for row in results]

def save_template_match(connection, match_data):
    """Save template matching results"""
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO template_matches 
        (summary_id, template_category, template_file, matched_files_json, 
         similarity_scores_json, match_count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        match_data['summary_id'],
        match_data['template_category'],
        match_data['template_file'],
        json.dumps(match_data['matched_files']),
        json.dumps(match_data['similarity_scores']),
        match_data['match_count']
    ))
    
    connection.commit()
    return cursor.lastrowid

def get_template_matches(connection, summary_id):
    """Get template matches for a summary"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT template_category, template_file, matched_files_json, 
               similarity_scores_json, match_count
        FROM template_matches 
        WHERE summary_id = ?
        ORDER BY match_count DESC
    ''', (summary_id,))
    
    results = cursor.fetchall()
    return [{
        'category': row[0],
        'template_file': row[1],
        'matched_files': json.loads(row[2]),
        'similarity_scores': json.loads(row[3]),
        'match_count': row[4]
    } for row in results]

def cache_file_analysis(connection, file_path, analysis_data):
    """Cache file analysis results"""
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO file_analysis_cache 
        (file_path, file_size, file_type, word_count, character_count, content_hash)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        file_path,
        analysis_data.get('file_size', 0),
        analysis_data.get('file_type', ''),
        analysis_data.get('word_count', 0),
        analysis_data.get('character_count', 0),
        analysis_data.get('content_hash', '')
    ))
    
    connection.commit()

def get_cached_file_analysis(connection, file_path):
    """Get cached file analysis if available"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT file_size, file_type, word_count, character_count, content_hash, analyzed_at
        FROM file_analysis_cache 
        WHERE file_path = ?
    ''', (file_path,))
    
    result = cursor.fetchone()
    if result:
        return {
            'file_size': result[0],
            'file_type': result[1],
            'word_count': result[2],
            'character_count': result[3],
            'content_hash': result[4],
            'analyzed_at': result[5]
        }
    return None

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_file_type_statistics(connection, summary_id):
    """Get detailed file type statistics for a summary"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT file_types_json FROM directory_summaries WHERE id = ?
    ''', (summary_id,))
    
    result = cursor.fetchone()
    if result and result[0]:
        file_types = json.loads(result[0])
        
        # Calculate percentages and format
        total_files = sum(file_types.values())
        formatted_stats = []
        
        for file_type, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            formatted_stats.append({
                'type': file_type,
                'count': count,
                'percentage': round(percentage, 1)
            })
        
        return formatted_stats
    
    return []

def create_or_get_user(connection, username, email):
    """Create user or get existing user"""
    cursor = connection.cursor()
    
    # Check if user exists
    cursor.execute('SELECT id, username, email FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if user:
        return {'id': user[0], 'username': user[1], 'email': user[2]}
    
    # Create new user
    cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
    connection.commit()
    user_id = cursor.lastrowid
    
    return {'id': user_id, 'username': username, 'email': email}

def save_user_template(connection, user_id, category, filename, file_content):
    """Save user template"""
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO user_templates (user_id, category, filename, file_content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, category, filename, file_content))
    connection.commit()
    return cursor.lastrowid

def get_user_templates(connection, user_id):
    """Get all templates for a user"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, category, filename, created_at 
        FROM user_templates 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    return cursor.fetchall()

def save_directory_analysis(connection, user_id, directory_path, analysis_data):
    """Save directory analysis for user"""
    cursor = connection.cursor()
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

def get_user_recent_analyses(connection, user_id, limit=5):
    """Get recent analyses for user"""
    cursor = connection.cursor()
    cursor.execute('''
        SELECT directory_path, total_files, total_size, created_at
        FROM directory_analyses 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    return cursor.fetchall()

def delete_user_template(connection, template_id, user_id):
    """Delete user template"""
    cursor = connection.cursor()
    cursor.execute('DELETE FROM user_templates WHERE id = ? AND user_id = ?', (template_id, user_id))
    connection.commit()
    return cursor.rowcount > 0