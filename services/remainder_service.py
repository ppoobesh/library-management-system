from datetime import date

from database import get_connection, close_connection
from config import (DUE_REMINDER_DAYS,OVERDUE_REMINDER_DAYS)
from services.mail_service import send_email
from utils.fine import calculate_fine

def send_due_reminders():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT
        transactions.id,
        transactions.due_date,
        students.name,
        students.email,
        books.bookcode,
        books.title,
        book_copies.copy_codeFROM transactions JOIN students ON transactions.student_id = students.id
        JOIN books ON transactions.book_id = books.id
        JOIN book_copies ON transactions.copy_id = book_copies.id
         WHERE transactions.status = 'Borrowed' """)
        transactions = cursor.fetchall()
        today = date.today()
        sent_count = 0
        for transaction in transactions:
            due_date = date.fromisoformat(transaction["due_date"])
            days_remaining = (due_date - today).days

            if 0 <= days_remaining <= DUE_REMINDER_DAYS:
                subject = "Library Book Due Reminder"
                body = f"""
Hello {transaction['name']},

This is a reminder about your borrowed book.

Book Details
-------------------------
Book Code : {transaction['bookcode']}
Book Title: {transaction['title']}
Copy Code : {transaction['copy_code']}

Due Date       : {transaction['due_date']}
Days Remaining : {days_remaining}

Please return the book on or before the due date
to avoid overdue fines.

Thank you,
Library Management System
"""
                success, message = send_email(transaction["email"],subject,body)
                if success:
                    sent_count += 1
                else:
                    print("Due Reminder Email Failed:",message)
        return True, sent_count
    except Exception as e:
        print("Due Reminder Error:",e)
        return False, 0
    finally:
        close_connection(connection)

def send_overdue_reminders():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT
        transactions.id,
        transactions.due_date,
        students.name,
        students.email,
        books.bookcode,
        books.title,
        book_copies.copy_code FROM transactions
        JOIN students ON transactions.student_id = students.id
        JOIN books ON transactions.book_id = books.id
        JOIN book_copies ON transactions.copy_id = book_copies.id
        WHERE transactions.status = 'Borrowed'""")
        transactions = cursor.fetchall()
        today = date.today()
        sent_count = 0
        for transaction in transactions:
            due_date = date.fromisoformat(transaction["due_date"])
            overdue_days = (today - due_date).days
            if overdue_days <= 0:
                continue
            # 3, 6, 9, 12, ...
            if (overdue_days % OVERDUE_REMINDER_DAYS!= 0):
                continue
            fine = calculate_fine(transaction["due_date"])
            subject = "Library Book Overdue Reminder"
            body = f"""
Hello {transaction['name']},

Your borrowed book is overdue.

Book Details
-------------------------
Book Code : {transaction['bookcode']}
Book Title: {transaction['title']}
Copy Code : {transaction['copy_code']}

Due Date     : {transaction['due_date']}
Overdue Days : {overdue_days}
Current Fine : ₹{fine:.2f}

Please return the book as soon as possible.

The fine may continue to increase until
the book is returned.

Thank you,
Library Management System
"""
            success, message = send_email(transaction["email"],subject,body)
            if success:
                sent_count += 1
            else:
                print("Overdue Email Failed:",message)
        return True, sent_count
    except Exception as e:
        print("Overdue Reminder Error:",e)
        return False, 0
    finally:
        close_connection(connection)