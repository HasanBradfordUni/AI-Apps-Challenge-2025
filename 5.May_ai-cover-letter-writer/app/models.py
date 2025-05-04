import sqlite3
from sqlite3 import Error
import os

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

def create_tables(connection):
    # Users table
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(connection, create_users_table)

    # User skills table
    create_skills_table = """
    CREATE TABLE IF NOT EXISTS user_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        skill_name TEXT,
        proficiency TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    execute_query(connection, create_skills_table)

    # User education table
    create_education_table = """
    CREATE TABLE IF NOT EXISTS user_education (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        institution TEXT,
        degree TEXT,
        field TEXT,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    execute_query(connection, create_education_table)

    # User work experience table
    create_experience_table = """
    CREATE TABLE IF NOT EXISTS user_experience (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        company TEXT,
        position TEXT,
        description TEXT,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    execute_query(connection, create_experience_table)

    # Cover letters table
    create_letters_table = """
    CREATE TABLE IF NOT EXISTS cover_letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        job_title TEXT,
        company_name TEXT,
        job_description TEXT,
        generated_letter TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    execute_query(connection, create_letters_table)

# User data functions
def add_user(connection, name, email):
    query = "INSERT INTO users (name, email) VALUES (?, ?)"
    return execute_query(connection, query, (name, email))

def get_user(connection, user_id):
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()

# CV data functions
def add_skill(connection, user_id, skill_name, proficiency):
    query = "INSERT INTO user_skills (user_id, skill_name, proficiency) VALUES (?, ?, ?)"
    return execute_query(connection, query, (user_id, skill_name, proficiency))

def add_education(connection, user_id, institution, degree, field, start_date, end_date):
    query = """
    INSERT INTO user_education (user_id, institution, degree, field, start_date, end_date) 
    VALUES (?, ?, ?, ?, ?, ?)
    """
    return execute_query(connection, query, (user_id, institution, degree, field, start_date, end_date))

def add_experience(connection, user_id, company, position, description, start_date, end_date):
    query = """
    INSERT INTO user_experience (user_id, company, position, description, start_date, end_date) 
    VALUES (?, ?, ?, ?, ?, ?)
    """
    return execute_query(connection, query, (user_id, company, position, description, start_date, end_date))

# Cover letter functions
def save_cover_letter(connection, user_id, job_title, company_name, job_description, letter_text):
    query = """
    INSERT INTO cover_letters (user_id, job_title, company_name, job_description, generated_letter)
    VALUES (?, ?, ?, ?, ?)
    """
    return execute_query(connection, query, (user_id, job_title, company_name, job_description, letter_text))

def get_cover_letter(connection, letter_id):
    cursor = connection.cursor()
    query = "SELECT * FROM cover_letters WHERE id = ?"
    cursor.execute(query, (letter_id,))
    return cursor.fetchone()

def get_user_cover_letters(connection, user_id):
    cursor = connection.cursor()
    query = "SELECT * FROM cover_letters WHERE user_id = ? ORDER BY created_at DESC"
    cursor.execute(query, (user_id,))
    return cursor.fetchall()
