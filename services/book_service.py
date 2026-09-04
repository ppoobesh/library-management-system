from database import get_connection, close_connection
from models import Book

from utils.validators import (
    validate_author,
    validate_bookcode,
    validate_category,
    validate_copies,
    validate_shelf,
    validate_price,
    validate_title
)

from utils.qr import generate_book_copy_qr



def add_book(book):

    if not validate_bookcode(book.bookcode):
        return False, "Invalid Book Code."

    if not validate_title(book.title):
        return False, "Invalid Book Title."

    if not validate_author(book.author):
        return False, "Invalid Author Name."

    if not validate_category(book.category):
        return False, "Invalid Category."

    if not validate_copies(book.copies):
        return False, "Invalid Number of Copies."

    if not validate_shelf(book.shelf):
        return False, "Invalid Shelf Location."

    if not validate_price(book.price):
        return False, "Invalid Book Price."

    connection = get_connection()

    try:

        cursor = connection.cursor()
        cursor.execute("SELECT id FROM books WHERE bookcode = ?", (book.bookcode,))
        if cursor.fetchone():
            return False, "Book Code already exists."
        # Insert book
        cursor.execute("""INSERT INTO books(
        bookcode,
        title,
        author,
        category,
        copies,
        available,
        shelf,
        price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            book.bookcode,
            book.title,
            book.author,
            book.category,
            book.copies,
            book.copies,
            book.shelf,
            book.price
        ))
        book_id = cursor.lastrowid
        # Create physical copies
        for number in range(1, book.copies + 1):
            copy_code = f"{book.bookcode}-C{number:02d}"
            qr_path = generate_book_copy_qr(copy_code)
            cursor.execute("""INSERT INTO book_copies
            (book_id,
            copy_code,
            status,
            qrpath)VALUES (?, ?, ?, ?)""",
            (
                book_id,
                copy_code,
                "Available",
                qr_path
            ))
        connection.commit()
        return True, "Book added successfully."
    except Exception as e:
        connection.rollback()
        print("ADD BOOK ERROR:", repr(e))
        return False, "Failed to add book."
    finally:
        close_connection(connection)

def update_book(book):
    if not validate_bookcode(book.bookcode):
        return False, "Invalid Book Code."

    if not validate_title(book.title):
        return False, "Invalid Book Title."

    if not validate_author(book.author):
        return False, "Invalid Author Name."

    if not validate_category(book.category):
        return False, "Invalid Category."

    if not validate_copies(book.copies):
        return False, "Invalid Number of Copies."

    if not validate_shelf(book.shelf):
        return False, "Invalid Shelf Location."

    if not validate_price(book.price):
        return False, "Invalid Book Price."
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM books WHERE bookcode = ? AND id != ?", (book.bookcode,book.book_id))
        if cursor.fetchone():
            return False, "Book Code already exists."
        #Currrent book info
        cursor.execute("SELECT copies, available FROM books WHERE id = ?", (book.book_id,))
        current_book = cursor.fetchone()
        if not current_book:
            return False, "Book not found."
        current_copies = current_book["copies"]
        current_available = current_book["available"]

        borrowed_copies = (current_copies - current_available)

        if book.copies < borrowed_copies:
            return False, (f'Cannot reduce the copies below the number of borrowed copies {borrowed_copies}')

        new_available = (book.copies - borrowed_copies)

        cursor.execute("""UPDATE books SET
        bookcode = ?,
        title = ?,
        author = ?,
        category = ?,
        copies = ?,
        available = ?,
        shelf = ?,
        price = ?
        WHERE id = ?""", (
            book.bookcode,
            book.title,
            book.author,
            book.category,
            book.copies,
            new_available,
            book.shelf,
            book.price,
            book.book_id
        ))

        if book.copies > current_copies:
            for number in range(current_copies + 1,book.copies + 1):
                copy_code = (f"{book.bookcode}-C{number:02d}")
                qr_path = generate_book_copy_qr(copy_code)
                cursor.execute("""INSERT INTO book_copies
                (book_id,
                copy_code,
                status,
                qrpath) VALUES (?, ?, ?, ?)""", (
                    book.book_id,
                    copy_code,
                    "Available",
                    qr_path
                ))

        elif book.copies < current_copies:
            copies_to_remove = (current_copies - book.copies)
            cursor.execute("""SELECT id FROM book_copies WHERE book_id = ? AND status = 'Available' ORDER BY id DESC LIMIT ?""", (
                book.book_id,
                copies_to_remove
            ))
            removable_copies = (
                cursor.fetchall()
            )
            if (len(removable_copies)< copies_to_remove):
                connection.rollback()
                return False, ("Unable to remove required copies. "
                    "Some copies may be borrowed, lost, "
                    "or otherwise unavailable.")
            for copy in removable_copies:
                cursor.execute("DELETE FROM book_copies WHERE id = ? AND status = 'Available'", (copy["id"],))
        connection.commit()

        return True, "Book updated successfully."

    except Exception as e:

        connection.rollback()
        print("Update Book Error:",e)
        return False, "Failed to update book."
    finally:
        close_connection(connection)

def get_all_books():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books ORDER BY title")
        rows = cursor.fetchall()
        books = []
        for row in rows:
            book = Book(
                book_id=row["id"],
                bookcode=row["bookcode"],
                title=row["title"],
                author=row["author"],
                category=row["category"],
                copies=row["copies"],
                available=row["available"],
                shelf=row["shelf"],
                price=row["price"],
                qr_path=row["qrpath"]
            )
            books.append(book)
        return books
    finally:
        close_connection(connection)

def get_book(book_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ? ", (book_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Book(
            book_id=row["id"],
            bookcode=row["bookcode"],
            title=row["title"],
            author=row["author"],
            category=row["category"],
            copies=row["copies"],
            available=row["available"],
            shelf=row["shelf"],
            price=row["price"],
            qr_path=row["qrpath"]
        )
    finally:
        close_connection(connection)

def get_available_books():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, bookcode, title, available FROM books WHERE available > 0 ORDER BY title")
        return cursor.fetchall()
    finally:
        close_connection(connection)

def get_book_copies(book_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, book_id, copy_code, status, qrpath FROM book_copies WHERE book_id = ? ORDER BY copy_code ", (book_id,))
        return cursor.fetchall()
    finally:
        close_connection(connection)

def get_available_copy(book_id):

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT
        id,
        book_id,
        copy_code,
        status,
        qrpath FROM book_copies WHERE book_id = ? AND status = 'Available' ORDER BY copy_code LIMIT 1""", (book_id,))
        return cursor.fetchone()
    finally:
        close_connection(connection)

def delete_book(book_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        # Check borrowed copies
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE book_id = ? AND status = 'Borrowed'", (book_id,))
        borrowed_count = cursor.fetchone()[0]
        if borrowed_count > 0:
            return False, ("Book cannot be deleted while it is borrowed.")
        # Check reservations
        cursor.execute("SELECT COUNT(*) FROM reservations WHERE book_id = ? AND status = 'Waiting'", (book_id,))
        reservation_count = cursor.fetchone()[0]
        if reservation_count > 0:
            return False, ("Book cannot be deleted because it has reservations.")
        # Delete physical copies first
        cursor.execute("DELETE FROM book_copies WHERE book_id = ?", (book_id,))
        # Delete book
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        if cursor.rowcount == 0:
            return False, "Book not found."
        connection.commit()
        return True, "Book deleted successfully."
    finally:
        close_connection(connection)

def search_books(keyword):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        search_value = f"%{keyword}%"
        cursor.execute("""SELECT * FROM books WHERE bookcode LIKE ? OR title LIKE ?
        OR author LIKE ? OR category LIKE ? OR shelf LIKE ? ORDER BY title""",
        (
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ))
        rows = cursor.fetchall()
        books = []
        for row in rows:
            book = Book(
                book_id=row["id"],
                bookcode=row["bookcode"],
                title=row["title"],
                author=row["author"],
                category=row["category"],
                copies=row["copies"],
                available=row["available"],
                shelf=row["shelf"],
                price=row["price"]
            )
            books.append(book)
        return books
    finally:
        close_connection(connection)

def get_student_books():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""SELECT
        id AS book_id,
        bookcode,
        title,
        author,
        category,
        available,
        copies,
        shelf FROM books ORDER BY title""")
        return cursor.fetchall()
    finally:
        close_connection(connection)