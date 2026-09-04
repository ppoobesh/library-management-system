from datetime import date
from database import get_connection, close_connection

def get_lost_book_candidates():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
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
        book_copies.copy_code FROM transactions JOIN students ON transactions.student_id = students.id
        JOIN books ON transactions.book_id = books.id 
        JOIN book_copies ON transactions.copy_id = book_copies.id WHERE transactions.status = 'Lost' ORDER BY transactions.return_date DESC""")
        return cursor.fetchall()
    finally:
        close_connection(connection)

def mark_book_as_lost(transaction_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT
        transactions.id,
        transactions.book_id,
        transactions.copy_id,
        transactions.status,
        books.price,
        book_copies.copy_code FROM transactions JOIN books ON transactions.book_id = books.id
        JOIN book_copies ON transactions.copy_id = book_copies.id 
        WHERE transactions.id = ? AND transactions.status = 'Borrowed'""", (transaction_id,))
        transaction = cursor.fetchone()
        if not transaction:
            return False, ("Active borrowing transaction not found.")
        # Lost book fine
        lost_charge = transaction["price"] or 0
        today = date.today().isoformat()
        cursor.execute("UPDATE transactions SET return_date = ?, fine = ?, status = 'Lost' WHERE id = ?", (today,lost_charge,transaction_id))
        # Mark exact physical copy Lost
        cursor.execute("UPDATE book_copies SET status = 'Lost' WHERE id = ?", (transaction["copy_id"],))
        # Sync avail copies
        cursor.execute("SELECT COUNT(*) FROM book_copies WHERE book_id = ? AND status = 'Available'", (transaction["book_id"],))
        available_count = cursor.fetchone()[0]
        cursor.execute(" UPDATE books SET available = ? WHERE id = ?", (available_count,transaction["book_id"]))

        connection.commit()
        return True, (
            f"Book copy {transaction['copy_code']} marked as lost. "
            f"Charge: ₹{lost_charge:.2f}"
        )
    except Exception as e:
        connection.rollback()
        print("MARK BOOK LOST ERROR:",repr(e))
        return False, (
            "An error occurred while marking "
            "the book as lost."
        )
    finally:
        close_connection(connection)