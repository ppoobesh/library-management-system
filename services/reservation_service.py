from datetime import date,timedelta
from database import get_connection, close_connection
from config import RESERVATION_HOLD_DAYS
from services.mail_service import (send_reservation_ready_email)

def create_reservation(student_id, book_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        if not student:
            return False, "Student not found."
        if student["status"] != "Active":
            return False, "Student account is inactive."
        
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            return False, "Book not found."
        if book["available"] > 0:
            return False, (
                "This book is currently available. "
                "You can borrow it directly."
            )

        cursor.execute("SELECT id FROM reservations WHERE student_id = ? AND book_id = ? AND status IN ('Waiting', 'Ready')", (student_id,book_id))
        existing = cursor.fetchone()
        if existing:
            return False, "You have already reserved this book."
        
        reservation_date = date.today().isoformat()
        cursor.execute("""INSERT INTO reservations(
            student_id,
            book_id,
            reservation_date,
            status,
            notification_sent) VALUES (?, ?, ?, ?, ?)""", (
            student_id,
            book_id,
            reservation_date,
            "Waiting",
            0
        ))
        connection.commit()
        return True, (f"Book '{book['title']}' reserved successfully.")
    except Exception as e:
        connection.rollback()
        print("Reservation Error:", e)
        return False, "An error occurred while reserving the book."
    finally:
        close_connection(connection)

def get_student_reservations(student_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT
            reservations.id,
            reservations.student_id,
            reservations.book_id,
            reservations.reservation_date,
            reservations.status,
            reservations.notification_sent,
            books.bookcode,
            books.title,
            books.author
            FROM reservations
            JOIN books ON reservations.book_id = books.id
            WHERE reservations.student_id = ?
            ORDER BY reservations.reservation_date DESC""", (student_id,))
        return cursor.fetchall()
    finally:
        close_connection(connection)

def update_reservations_for_book(book_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        #chk book availablty
        cursor.execute("SELECT available, title, bookcode FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            return False, "Book not found."
        available = book["available"]
        if available <= 0:
            return True, "No available copies."
        # Get waiting reservations
        # Oldest reservation gets priority
        cursor.execute("""SELECT
            reservations.id,
            reservations.student_id,
            students.name,
            students.email
            FROM reservations
            JOIN students ON reservations.student_id = students.id
            WHERE reservations.book_id = ? AND reservations.status = 'Waiting'
            ORDER BY reservations.reservation_date ASC,reservations.id ASC""", (book_id,))

        reservations = cursor.fetchall()
        if not reservations:
            return True, "No waiting reservations."

        ready_count = min(available,len(reservations))
        ready_date = date.today().isoformat()
        ready_reservations = reservations[:ready_count]

        for reservation in ready_reservations:

            cursor.execute("""UPDATE reservations SET
                status = 'Ready',
                notification_sent = 0,
                ready_date = ?
                WHERE id = ?""", 
                (ready_date,reservation["id"]))

        connection.commit()
        email_count = 0
        for reservation in ready_reservations:
            email_success, email_message = (
                send_reservation_ready_email(
                    student_name=reservation["name"],
                    student_email=reservation["email"],
                    book_title=book["title"],
                    book_code=book["bookcode"]
                )
            )
            if email_success:
                cursor.execute("UPDATE reservations SET notification_sent = 1 WHERE id = ?", (reservation["id"],))
                connection.commit()
                email_count += 1
            else:
                print("Reservation Email Failed:",email_message)

        return True, (
            f"{ready_count} reservation(s) "
            f"marked as Ready. "
            f"{email_count} notification email(s) sent."
        )
    except Exception as e:
        connection.rollback()
        print("Reservation Update Error:",e)
        return False, (
            "An error occurred while "
            "updating reservations."
        )
    finally:
        close_connection(connection)

def get_all_reservations():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT
            reservations.id,
            reservations.student_id,
            reservations.book_id,
            reservations.reservation_date,
            reservations.status,
            reservations.notification_sent,
            students.name,
            students.roll_no,
            books.bookcode,
            books.title FROM reservations
            JOIN students ON reservations.student_id = students.id
            JOIN books ON reservations.book_id = books.id
            ORDER BY CASE WHEN reservations.status = 'Waiting' THEN 0
            WHEN reservations.status = 'Ready' THEN 1 ELSE 2 END,
            reservations.reservation_date ASC""")
        return cursor.fetchall()
    finally:
        close_connection(connection)

def expire_old_reservations():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        expiry_cutoff = (date.today() - timedelta(days=RESERVATION_HOLD_DAYS)).isoformat()
        cursor.execute("UPDATE reservations SET status = 'Expired' WHERE status = 'Ready' AND ready_date IS NOT NULL AND ready_date < ?", (expiry_cutoff,))
        expired_count = cursor.rowcount
        connection.commit()
        return True, expired_count
    except Exception as e:
        connection.rollback()
        print("Reservation Expiry Error:", e)
        return False, 0
    finally:
        close_connection(connection)

def cancel_reservation(reservation_id, student_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = ? AND student_id = ? AND status IN ('Waiting', 'Ready')", (reservation_id,student_id))
        reservation = cursor.fetchone()
        if not reservation:
            return False, "Active reservation not found."
        cursor.execute("UPDATE reservations SET status = 'Cancelled' WHERE id = ?", (reservation_id,))
        connection.commit()
        return True, "Reservation cancelled successfully."

    except Exception as e:
        connection.rollback()
        print("Cancel Reservation Error:", e)
        return False, (
            "An error occurred while cancelling "
            "the reservation."
        )
    finally:
        close_connection(connection)
