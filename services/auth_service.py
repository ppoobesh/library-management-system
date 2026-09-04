from database import get_connection,close_connection
from models import User
from utils.auth import verify_password,hash_password

def authenticate_user(username,password):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        query = 'SELECT * FROM users WHERE username = ?'
        cursor = connection.execute(query,(username,))
        row = cursor.fetchone()
        if row is None:
            return None
        if verify_password(password,row['password']):
            return User(
                username=row['username'],
                password=row['password'],
                role=row['role'],
                user_id=row['id']
            )
        return None
    finally:
        close_connection(connection)

def create_default_admin():
    connection = get_connection()
    try:
        cursor=connection.cursor()
        cursor.execute('SELECT id FROM users WHERE username =?',('admin',))
        admin = cursor.fetchone()
        if admin:
            return
        hashed_password = hash_password('admin123')
        cursor.execute('INSERT INTO users (username,password,role) VALUES (?,?,?)',('admin',hashed_password,"Admin"))
        connection.commit()
        print('Default Admin Created successfully.')
    finally:
        close_connection(connection)

def change_password(username,new_password):
    hashed_password = hash_password(new_password)
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute('UPDATE users SET password =? WHERE username =?',(hashed_password,username))
        connection.commit()
        return True,'Password Updated successfully.'
    finally:
        close_connection(connection)