import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM,
    RESERVATION_HOLD_DAYS
)

def send_email(student_email,subject,body):
    message = MIMEMultipart()
    message["From"] = MAIL_FROM
    message["To"] = student_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(MAIL_SERVER,MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME,MAIL_PASSWORD)
            server.sendmail(MAIL_FROM,student_email,message.as_string())
        print(f"Email sent successfully to{student_email}")
        return True, "Email sent successfully."
    except Exception as e:
        print("Email Error:",e)
        return False, "Failed to send email."

def send_reservation_ready_email(student_name,student_email,book_title,book_code):
    subject = "Your Reserved Book is Ready"
    body = f"""
Hello {student_name},

Good news!

The book you reserved is now available.

Book Details
-------------------------

Book Code : {book_code}
Book Title: {book_title}

Please collect the book from the library within
{RESERVATION_HOLD_DAYS} day(s).

If you no longer need this book, you can cancel your
reservation from the Library Management System.

Thank you,
Library Management System
"""

    return send_email(student_email,subject, body)

def send_borrow_confirmation_email(
    student_name,
    student_email,
    book_title,
    book_code,
    copy_code,
    issue_date,
    due_date
):
    subject = "Library Book Issued Successfully"
    body = f"""
Hello {student_name},

The following book has been issued to you successfully.

Book Details
-------------------------

Book Code : {book_code}
Book Title: {book_title}
Copy Code : {copy_code}

Issue Date: {issue_date}
Due Date  : {due_date}

Please return the book on or before the due date
to avoid overdue fines.

Thank you,
Library Management System
"""
    return send_email(student_email,subject,body)