import sqlite3
from config2 import DB_PATH, SCHEMA_PATH
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = get_connection()
    print("DATABASE PATH:", DB_PATH)
    try:
        with open (SCHEMA_PATH,'r',encoding= 'utf-8') as file:
            sql_script = file.read()
        connection.executescript(sql_script)
        connection.commit()
        print('Database initialize successfully')
    except sqlite3.Error as e:
        print(f'Database Error: {e}')
    finally:
        connection.close()

def close_connection(connection):
    if connection:
        connection.close()
