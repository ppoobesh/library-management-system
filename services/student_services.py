from database import get_connection, close_connection
from models import Student
from utils.validators import (
    validate_email,
    validate_borrow_limit,
    validate_name,
    validate_phone,
    validate_register_number
)
from utils.auth import hash_password

def add_student(student):
    if not validate_name(student.name):
        return False, "Invalid Student Name."
    if not validate_register_number(student.roll_no):
        return False, "Invalid Register number."
    if not validate_phone(student.phone):
        return False, "Invalid Phone number."
    if not validate_borrow_limit(student.borrow_limit):
        return False, "Invalid Borrow limit."
    if not validate_email(student.email):
        return False, "Invalid Email."

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM students WHERE roll_no = ?', (student.roll_no,))
        if cursor.fetchone():
            return False, "Register number already exists."

        cursor.execute('SELECT id FROM students WHERE email =?',(student.email,))
        if cursor.fetchone():
            return False, 'Email already exists.'
        cursor.execute("SELECT id FROM students WHERE phone = ?", (student.phone,))
        if cursor.fetchone():
            return False, "Phone Number already exists."
        
        cursor.execute('''INSERT INTO students
        (roll_no,name,department,year,email,phone,borrow_limit,status)
        VALUES (?,?,?,?,?,?,?,?)''', (student.roll_no,
                                      student.name,
                                      student.department,
                                      student.year,
                                      student.email,
                                      student.phone,
                                      student.borrow_limit,
                                      student.status
                                      ))
        hashed_password = hash_password(student.roll_no)
        cursor.execute('INSERT INTO users(username,password,role)VALUES (?,?,?)',(student.roll_no,hashed_password, 'Student'))
        connection.commit()
        return True, "Student added successfully"
    finally:
        close_connection(connection)

def get_all_students():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM students ORDER BY name')
        students = []
        rows = cursor.fetchall()
        for row in rows:
            students.append(
                Student(
                    student_id=row['id'],
                    roll_no=row['roll_no'],
                    name=row['name'],
                    department=row['department'],
                    year=row['year'],
                    email=row['email'],
                    phone=row['phone'],
                    borrow_limit=row['borrow_limit'],
                    status=row['status']
                )
            )
        return students
    finally:
        close_connection(connection)

def get_student_by_id(student_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT *FROM students WHERE id =?', (student_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Student(
            student_id=row['id'],
            roll_no =row['roll_no'],
            name=row['name'],
            department=row['department'],
            year=row['year'],
            email=row['email'],
            phone=row['phone'],
            borrow_limit=row['borrow_limit'],
            status=row['status'])
    finally:
        close_connection(connection)

def update_student(student):
    if not validate_name(student.name):
        return False, "Invalid Student Name."

    if not validate_email(student.email):
        return False, "Invalid Email."

    if not validate_phone(student.phone):
        return False, "Invalid Phone Number."

    if not validate_borrow_limit(student.borrow_limit):
        return False, "Invalid Borrow Limit."
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM students WHERE email = ? AND id != ?", (student.email,student.student_id))
        if cursor.fetchone():
            return False, "Email already exists."
        cursor.execute("SELECT id FROM students WHERE phone = ? AND id != ?", (student.phone,student.student_id))
        if cursor.fetchone():
            return False, "Phone Number already exists."
        cursor.execute("""
            UPDATE students
            SET
                name = ?,
                department = ?,
                year = ?,
                email = ?,
                phone = ?,
                borrow_limit = ?,
                status = ?
            WHERE id = ?
        """,
        (
            student.name,
            student.department,
            student.year,
            student.email,
            student.phone,
            student.borrow_limit,
            student.status,
            student.student_id
        ))
        connection.commit()
        return True, "Student updated successfully."
    finally:
        close_connection(connection)

def delete_student(student_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE username=(SELECT roll_no FROM students WHERE id=?)",(student_id,))
        cursor.execute("DELETE FROM students WHERE id=?",(student_id,))
        connection.commit()
        return True
    finally:
        close_connection(connection)

def search_students(keyword):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT *
            FROM students
            WHERE name LIKE ? OR roll_no LIKE ? OR department LIKE ?
            ORDER BY name""",(f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        rows = cursor.fetchall()
        students = []
        for row in rows:
            students.append(
                Student(
                    student_id=row["id"],
                    roll_no=row["roll_no"],
                    name=row["name"],
                    department=row["department"],
                    year=row["year"],
                    email=row["email"],
                    phone=row["phone"],
                    borrow_limit=row["borrow_limit"],
                    status=row["status"]
                )
            )
        return students
    finally:
        close_connection(connection)

def get_active_students():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, roll_no, name FROM students WHERE status = 'Active' ORDER BY name")
        return cursor.fetchall()
    finally:
        close_connection(connection)

def get_student_by_roll_no(roll_no):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Student(
            student_id=row["id"],
            roll_no=row["roll_no"],
            name=row["name"],
            department=row["department"],
            year=row["year"],
            email=row["email"],
            phone=row["phone"],
            borrow_limit=row["borrow_limit"],
            status=row["status"]
        )
    finally:
        close_connection(connection)