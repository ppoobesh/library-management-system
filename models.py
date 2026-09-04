class User:
    def __init__(self,username,password,role,user_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role
    def __str__(self):
        return f"User({self.username},{self.role})"

class Student:
    def __init__(self,name,roll_no,department,year,email,phone,borrow_limit=3,status="Active",student_id=None):
        self.student_id = student_id
        self.roll_no = roll_no
        self.name = name
        self.department = department
        self.year = year
        self.email = email
        self.phone = phone
        self.borrow_limit = borrow_limit
        self.status = status
        
    def __str__(self):
        return f"Student({self.roll_no} - {self.name})"

class Book():
    def __init__(self,bookcode,title,author,category,copies,available,shelf,price,qr_path="",book_id=None):
        self.book_id = book_id
        self.bookcode = bookcode
        self.title = title
        self.author = author
        self.category = category
        self.copies = copies
        self.available = available
        self.shelf = shelf
        self.price = price
        self.qr_path = qr_path
    def __str__(self):
        return f"Book({self.bookcode} - {self.title})"
        

class Transaction:
    def __init__(self,student_id,book_id,issue_date,due_date,return_date,fine,status="Borrowed",transaction_id=None):
        self.transaction_id = transaction_id
        self.book_id = book_id
        self.student_id =student_id
        self.issue_date = issue_date
        self.due_date = due_date
        self.return_date = return_date
        self.fine = fine
        self.status = status
    def __str__(self):
        return(
            f"Transaction (Student = {self.student_id,},"
            f"Book= {self.book_id}, Status={self.status})")
    
class Reservation:

    def __init__(
        self,
        student_id,
        book_id,
        reservation_date,
        status="Waiting",
        notification_sent=False,
        ready_date=None,
        reservation_id=None
    ):

        self.reservation_id = reservation_id
        self.student_id = student_id
        self.book_id = book_id
        self.reservation_date = reservation_date
        self.status = status
        self.notification_sent = notification_sent
        self.ready_date = ready_date

    def __str__(self):

        return (
            f"Reservation("
            f"Student={self.student_id}, "
            f"Book={self.book_id}, "
            f"Status={self.status})"
        )

class BookCopy:

    def __init__(
        self,
        book_id,
        copy_code,
        status="Available",
        qr_path="",
        copy_id=None
    ):

        self.copy_id = copy_id
        self.book_id = book_id
        self.copy_code = copy_code
        self.status = status
        self.qr_path = qr_path

    def __str__(self):

        return f"BookCopy({self.copy_code} - {self.status})"