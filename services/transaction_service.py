from datetime import date, timedelta
from database import get_connection, close_connection
from utils.fine import calculate_fine

from config import BORROW_DAYS

from services.mail_service import (
    send_borrow_confirmation_email
)
from services.reservation_service import (
            update_reservations_for_book
        )

def borrow_book(student_id, book_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        if not student:
            return False, "Student not found."
        if student["status"] != "Active":
            return False, "Student account is inactive."
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE student_id = ? AND status = 'Borrowed'", (student_id,))
        borrowed_count = cursor.fetchone()[0]
        if borrowed_count >= student["borrow_limit"]:
            return False, "Borrow limit reached."

        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            return False, "Book not found."

        cursor.execute("SELECT * FROM book_copies WHERE book_id = ? AND status = 'Available' ORDER BY id LIMIT 1", (book_id,))
        copy = cursor.fetchone()
        if not copy:
            return False, "No available copy of this book."
        copy_id = copy["id"]

        cursor.execute("SELECT id FROM transactions WHERE student_id = ? AND book_id = ? AND status = 'Borrowed'", (student_id, book_id))
        if cursor.fetchone():
            return False, "Student has already borrowed this book."
        
        issue_date = date.today()
        due_date = issue_date + timedelta(days=BORROW_DAYS)

        cursor.execute("""
            INSERT INTO transactions
            (
                student_id,
                book_id,
                copy_id,
                issue_date,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            book_id,
            copy_id,
            issue_date.isoformat(),
            due_date.isoformat(),
            "Borrowed"
        ))
        cursor.execute("UPDATE book_copies SET status = 'Borrowed' WHERE id = ?", (copy_id,))
        cursor.execute("UPDATE books SET available = available - 1 WHERE id = ? AND available > 0", (book_id,))
        cursor.execute("UPDATE reservations SET status = 'Completed' WHERE student_id = ? AND book_id = ? AND status = 'Ready'", (student_id,book_id))
        connection.commit()
        email_success, email_message = (
        send_borrow_confirmation_email(
            student_name=student["name"],
            student_email=student["email"],
            book_title=book["title"],
            book_code=book["bookcode"],
            copy_code=copy["copy_code"],
            issue_date=issue_date.isoformat(),
            due_date=due_date.isoformat()
        )
    )
        if not email_success:
            print('Borrow Confirmation Email Failed.',email_message)
        return True, (
            f"Book borrowed successfully. "
            f"Copy: {copy['copy_code']}. "
            f"Due date: {due_date.isoformat()}"
        )
    except Exception as e:
        connection.rollback()
        print('Borrow Book error:' , e)
        return False, "An error occurred while borrowing the book."
    finally:
        close_connection(connection)

def get_borrowed_books(student_id=None):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        base_query = """
            SELECT
                transactions.id,
                transactions.student_id,
                transactions.book_id,
                transactions.copy_id,
                transactions.issue_date,
                transactions.due_date,
                transactions.return_date,
                transactions.fine,
                transactions.status,
                students.roll_no,
                students.name,
                books.bookcode,
                books.title,
                book_copies.copy_code
            FROM transactions
            JOIN students 
                ON transactions.student_id = students.id
            JOIN books 
                ON transactions.book_id = books.id
            JOIN book_copies 
                ON transactions.copy_id = book_copies.id"""
        if student_id is not None:
            query = base_query + """
            WHERE transactions.student_id = ?
                ORDER BY
                    CASE
                        WHEN transactions.status = 'Borrowed'
                        THEN 0
                        WHEN transactions.status = 'Lost'
                        THEN 1
                        WHEN transactions.status = 'Returned'
                        THEN 2
                        ELSE 3
                    END,
                    transactions.due_date DESC
            """
            cursor.execute(query,(student_id,))
        else:
            query = base_query + """
                ORDER BY
                    CASE
                        WHEN transactions.status = 'Borrowed'
                        THEN 0

                        WHEN transactions.status = 'Lost'
                        THEN 1

                        WHEN transactions.status = 'Returned'
                        THEN 2

                        ELSE 3
                    END,

                    transactions.due_date DESC
            """
            cursor.execute(query)
        transactions = cursor.fetchall()
        return transactions
    finally:
        close_connection(connection)

def return_book(transaction_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ? AND status = 'Borrowed'", (transaction_id,))
        transaction = cursor.fetchone()
        if not transaction:
            return False, ("Active borrowing transaction not found.")

        fine = calculate_fine(transaction["due_date"])

        return_date = date.today().isoformat()

        book_id = transaction["book_id"]
        copy_id = transaction["copy_id"]

        cursor.execute("""UPDATE transactions
            SET
                return_date = ?,
                fine = ?,
                status = 'Returned'
            WHERE id = ?
        """, (
            return_date,
            fine,
            transaction_id
        ))
        # Mark Exact Copy Available
        cursor.execute("""
            UPDATE book_copies
            SET status = 'Available'
            WHERE id = ?
        """, (
            copy_id,
        ))
        # Recalculate Available Copies
        cursor.execute("SELECT COUNT(*) FROM book_copies WHERE book_id = ? AND status = 'Available'", (book_id,))

        available_count = cursor.fetchone()[0]
        # Update Book Availability
        cursor.execute("UPDATE books  SET available = ? WHERE id = ?", (available_count,book_id))
        connection.commit()
        # Process Waiting Reservations
        reservation_success, reservation_message = (
            update_reservations_for_book(book_id)
        )
        print(
            "Reservation after return:",
            reservation_success,
            reservation_message
        )
        # Return Result
        if fine > 0:
            return True, (
                f"Book returned successfully. "
                f"Fine: ₹{fine:.2f}"
            )
        return True, (
            "Book returned successfully."
        )
    except Exception as e:
        connection.rollback()
        print("Return Book Error:",e)
        return False, ("An error occurred while returning the book.")
    finally:
        close_connection(connection)

def return_book_by_copy_code(copy_code):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        # Find physical copy
        cursor.execute("SELECT id, book_id, copy_code, status FROM book_copies WHERE copy_code = ?", (copy_code.strip(),))
        copy = cursor.fetchone()
        if not copy:
            return False, "Book copy not found."

        if copy["status"] == "Available":
            return False, ("This book copy is already available.")

        if copy["status"] == "Lost":
            return False, ("This book copy is marked as lost.")

        # Find active borrowing transaction
        cursor.execute("SELECT id FROM transactions WHERE copy_id = ? AND status = 'Borrowed'", (copy["id"],))
        transaction = cursor.fetchone()
        if not transaction:
            return False, ("No active borrowing transaction found for this book copy.")
        transaction_id = transaction["id"]
    finally:
        close_connection(connection)
    return return_book(
        transaction_id
    )

def mark_book_lost(transaction_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        # Get Active Transaction

        cursor.execute("SELECT * FROM transactions WHERE id = ? AND status = 'Borrowed'", (transaction_id,))
        transaction = cursor.fetchone()
        if not transaction:
            return False, "Active borrowing transaction not found."

        fine = calculate_fine(transaction["due_date"])
        lost_date = date.today().isoformat()

        # Mark Transaction as Lost
        cursor.execute("""UPDATE transactions SET
                return_date = ?,
                fine = ?,
                status = 'Lost'
            WHERE id = ?
        """, (lost_date,fine,transaction_id))

        # Mark Physical Copy as Lost

        cursor.execute("UPDATE book_copies SET status = 'Lost' WHERE id = ?", (transaction["copy_id"],))
        connection.commit()
        return True, (
            f"Book marked as lost successfully. "
            f"Fine: ₹{fine:.2f}"
        )
    except Exception as e:
        connection.rollback()
        print("Lost Book Error:", e)
        return False, (
            "An error occurred while marking "
            "the book as lost."
        )
    finally:
        close_connection(connection)