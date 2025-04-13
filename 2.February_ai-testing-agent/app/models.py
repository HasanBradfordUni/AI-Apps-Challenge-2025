import sqlite3
from sqlite3 import Error

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def get_last_row_id(connection):
    cursor = connection.cursor()
    select_statement = """
SELECT id FROM user_input
ORDER BY id DESC
LIMIT 1;
"""
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(select_statement)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def create_tables(connection):
    query = """
    CREATE TABLE IF NOT EXISTS user_input (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        test_query TEXT NOT NULL,
        additional_details TEXT,
        context TEXT
    );
    """

    execute_query(connection, query)

    query = """
    CREATE TABLE IF NOT EXISTS uploaded_file (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_type TEXT NOT NULL,
        file_path TEXT NOT NULL,
        user_input_id INTEGER NOT NULL,
        FOREIGN KEY (user_input_id) REFERENCES user_input (id)
    );
    """

    execute_query(connection, query)

    query = """
    CREATE TABLE IF NOT EXISTS evaluation_result (
        evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input_id INTEGER NOT NULL,
        expected_results TEXT NOT NULL,
        actual_results TEXT NOT NULL,
        comparison TEXT NOT NULL,
        summary TEXT NOT NULL,
        FOREIGN KEY (user_input_id) REFERENCES user_input (id)
    );
    """

    execute_query(connection, query)

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return cursor.fetchall()
    except Error as e:
        return f"The error '{e}' occurred"
    
def add_user_input(connection, project_name, test_query, additional_details, context):
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO user_input (project_name, test_query, additional_details, context)
    VALUES (?, ?, ?, ?)
    """, (project_name, test_query, additional_details, context))
    connection.commit()
    return cursor.lastrowid

def add_uploaded_file(connection, file_type, file_path, user_input_id):
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO uploaded_file (file_type, file_path, user_input_id)
    VALUES (?, ?, ?)
    """, (file_type, file_path, user_input_id))
    connection.commit()
    return cursor.lastrowid

def add_evaluation_result(connection, user_input_id, expected_results, actual_results, comparison, summary):
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO evaluation_result (user_input_id, expected_results, actual_results, comparison, summary)
    VALUES (?, ?, ?, ?, ?)
    """, (user_input_id, expected_results, actual_results, comparison, summary))
    connection.commit()
    return cursor.lastrowid

def get_user_input(connection, user_input_id):
    cursor = connection.cursor()
    cursor.execute(f"""
    SELECT * FROM user_input
    WHERE id = {user_input_id}
    """)
    return cursor.fetchone()

def get_uploaded_files(connection, user_input_id):
    cursor = connection.cursor()
    cursor.execute(f"""
    SELECT * FROM uploaded_file
    WHERE user_input_id = {user_input_id}
    """)
    return cursor.fetchone()

def get_evaluation_result(connection, user_input_id):
    cursor = connection.cursor()
    cursor.execute(f"""
    SELECT * FROM evaluation_result
    WHERE user_input_id = {user_input_id}
    """)
    return cursor.fetchone()
