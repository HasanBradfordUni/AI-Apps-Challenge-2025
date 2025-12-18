import sqlite3
from sqlite3 import Error
import os
from datetime import datetime

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query, params=None):
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

def create_tables(conn):
    """Create necessary database tables if they don't exist"""
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            company_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create job_ads table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_title TEXT NOT NULL,
            department TEXT,
            job_ad_text TEXT NOT NULL,
            template_name TEXT,
            is_template INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Create templates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            template_name TEXT NOT NULL,
            job_ad_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (job_ad_id) REFERENCES job_ads (id)
        )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        conn.rollback()

# User data functions
def add_user(connection, name, email, company_name):
    query = "INSERT INTO users (name, email, company_name) VALUES (?, ?, ?)"
    return execute_query(connection, query, (name, email, company_name))

def get_user(connection, user_id):
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()

def find_user_by_email(connection, email):
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE email = ?"
    cursor.execute(query, (email,))
    return cursor.fetchone()

# Job ad functions
def save_job_ad(connection, user_id, role_title, department, job_ad_text, is_template=False, template_name=None):
    """Save a job ad to the database"""
    try:
        cursor = connection.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        query = '''
        INSERT INTO job_ads (user_id, role_title, department, job_ad_text, is_template, template_name, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (user_id, role_title, department, job_ad_text, 
                              1 if is_template else 0, template_name, timestamp))
        connection.commit()
        
        # Return the ID of the inserted row
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving job ad: {str(e)}")
        connection.rollback()
        return None

def get_job_ad(connection, ad_id):
    cursor = connection.cursor()
    query = "SELECT * FROM job_ads WHERE id = ?"
    cursor.execute(query, (ad_id,))
    return cursor.fetchone()

def get_user_job_ads(connection, user_id):
    """Get all job ads for a specific user"""
    try:
        cursor = connection.cursor()
        query = '''
        SELECT * FROM job_ads 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        '''
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error retrieving user job ads: {str(e)}")
        return []

# Template functions
def add_template(connection, user_id, template_name, job_ad_id):
    query = """
    INSERT INTO templates (user_id, template_name, job_ad_id)
    VALUES (?, ?, ?)
    """
    return execute_query(connection, query, (user_id, template_name, job_ad_id))

def get_templates(connection, user_id):
    cursor = connection.cursor()
    query = """
    SELECT t.id, t.template_name, j.role_title, j.department, t.created_at
    FROM templates t
    JOIN job_ads j ON t.job_ad_id = j.id
    WHERE t.user_id = ?
    ORDER BY t.created_at DESC
    """
    cursor.execute(query, (user_id,))
    return cursor.fetchall()

def get_template(connection, template_id):
    cursor = connection.cursor()
    query = """
    SELECT t.*, j.* 
    FROM templates t
    JOIN job_ads j ON t.job_ad_id = j.id
    WHERE t.id = ?
    """
    cursor.execute(query, (template_id,))
    return cursor.fetchone()

def delete_job_ad(connection, ad_id):
    # First check if it's used as a template
    cursor = connection.cursor()
    check_query = "SELECT id FROM templates WHERE job_ad_id = ?"
    cursor.execute(check_query, (ad_id,))
    if cursor.fetchone():
        # Remove template reference first
        delete_template_query = "DELETE FROM templates WHERE job_ad_id = ?"
        execute_query(connection, delete_template_query, (ad_id,))
    
    # Now delete the job ad
    delete_query = "DELETE FROM job_ads WHERE id = ?"
    return execute_query(connection, delete_query, (ad_id,))