import pandas as pd
from database import get_connection, close_connection

def get_report_summary():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        summary = {}
        cursor.execute("SELECT COUNT(*)FROM students")
        summary["total_students"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM books")
        summary["total_books"] = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(copies), 0) FROM books")
        summary["total_copies"] = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(available), 0)FROM books")
        summary["available_copies"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'Borrowed'")
        summary["borrowed_books"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'Returned'")
        summary["returned_books"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'Lost'")
        summary["lost_books"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reservations WHERE status IN ('Waiting', 'Ready')")
        summary["active_reservations"] = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(fine), 0) FROM transactions")
        summary["total_fine"] = cursor.fetchone()[0]
        return summary
    finally:
        close_connection(connection)


def get_transaction_report():
    connection = get_connection()
    try:
        query = """
            SELECT
            transactions.id AS transaction_id,
            students.roll_no,
            students.name,
            books.bookcode,
            books.title,
            book_copies.copy_code,
            transactions.issue_date,
            transactions.due_date,
            transactions.return_date,
            transactions.fine,
            transactions.status
            FROM transactions JOIN students ON transactions.student_id = students.id
            JOIN books ON transactions.book_id = books.id
            JOIN book_copies ON transactions.copy_id = book_copies.id ORDER BY transactions.id DESC"""
        return pd.read_sql_query(query, connection)
    finally:
        close_connection(connection)


def get_reservation_report():
    connection = get_connection()
    try:
        query = """SELECT
        reservations.id AS reservation_id,
        students.roll_no,
        students.name,
        books.bookcode,
        books.title,
        reservations.reservation_date,
        reservations.ready_date,
        reservations.status,
        reservations.notification_sent
        FROM reservations JOIN students ON reservations.student_id = students.id
        JOIN books ON reservations.book_id = books.id
        ORDER BY reservations.id DESC"""
        return pd.read_sql_query(query, connection)
    finally:
        close_connection(connection)