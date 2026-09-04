import os
from flask import(
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)
from config import REPORT_FOLDER
from database import init_db
from services.auth_service import create_default_admin
from config import SECRET_KEY
from services.auth_service import (authenticate_user,change_password)
from models import (Student,Book)
from services.student_services import(
    add_student,
    get_all_students,
    get_student_by_id,
    update_student,
    delete_student,
    search_students,
    get_active_students,
    get_student_by_roll_no
)
from services.book_service import (
    add_book,
    get_all_books,
    get_book,
    update_book,
    delete_book,
    search_books,
    get_available_books,
    get_student_books
)
from services.transaction_service import (
    borrow_book,
    get_borrowed_books,
    return_book_by_copy_code
)
from services.lost_book_service import (
    get_lost_book_candidates,
    mark_book_as_lost
)

from services.reservation_service import (
    create_reservation,
    get_student_reservations,
    update_reservations_for_book,
    get_all_reservations,
    cancel_reservation,
    expire_old_reservations
)
from services.report_service import (
    get_report_summary,
    get_transaction_report,
    get_reservation_report
)

app = Flask(__name__)
app.secret_key= SECRET_KEY
init_db()
create_default_admin()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        login_type = request.form.get(
            "login_type"
        )
        user = authenticate_user(
            username,
            password
        )
        if not user:
            flash(
                "Invalid username or password."
            )
            return render_template(
                "login.html"
            )
        if user.role != login_type:
            if login_type == "Admin":
                flash(
                    "This account is not an "
                    "administrator account."
                )
            else:
                flash(
                    "This account is not a "
                    "student account."
                )
            return render_template(
                "login.html"
            )

        session.clear()

        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role"] = user.role

        if user.role == "Admin":
            return redirect(
                url_for("admin_dashboard")
            )

        return redirect(
            url_for("student_dashboard")
        )

    return render_template("login.html")

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['role']!='Admin':
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html')

@app.route("/student/dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Student":
        return redirect(url_for("login"))

    student = get_student_by_roll_no(session["username"])
    if student is None:
        flash("Student profile not found.")
        return redirect(url_for("logout"))
    return render_template(
        "student/dashboard.html",
        student=student
    )

@app.route("/admin/reports")
def reports_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") != "Admin":
        return redirect(url_for("login"))
    summary = get_report_summary()
    return render_template(
        "reports/reports.html",
        summary=summary)

@app.route("/admin/reports/transactions")
def transaction_report():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") != "Admin":
        return redirect(url_for("login"))
    dataframe = get_transaction_report()
    records = dataframe.to_dict(orient="records")
    return render_template(
        "reports/transaction_report.html",
        transactions=records
    )

@app.route("/admin/reports/transactions/export")
def export_transaction_report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        return redirect(url_for("login"))
    dataframe = get_transaction_report()
    os.makedirs(REPORT_FOLDER,exist_ok=True)
    file_path = os.path.join(REPORT_FOLDER,"transaction_report.csv")
    dataframe.to_csv(file_path,index=False)
    return send_file(file_path,as_attachment=True,download_name="transaction_report.csv")

@app.route("/admin/reports/reservations")
def reservation_report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        return redirect(url_for("login"))
    dataframe = get_reservation_report()
    records = dataframe.to_dict(orient="records")
    return render_template(
        "reports/reservation_report.html",
        reservations=records)

@app.route("/admin/reports/reservations/export")
def export_reservation_report():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    dataframe = get_reservation_report()

    os.makedirs(REPORT_FOLDER,exist_ok=True)

    file_path = os.path.join(REPORT_FOLDER,"reservation_report.csv")
    dataframe.to_csv(file_path,index=False)

    return send_file(file_path,as_attachment=True,download_name="reservation_report.csv")

@app.route("/student/borrowed-books")
def student_borrowed_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Student":
        return redirect(url_for("login"))

    student = get_student_by_roll_no(session["username"])

    if student is None:
        flash("Student profile not found.")
        return redirect(url_for("logout"))

    transactions = get_borrowed_books(student.student_id)

    return render_template(
        "student/borrowed_books.html",
        transactions=transactions,
        student=student
    )

@app.route('/students')
def view_students():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['role']!= 'Admin':
        return redirect(url_for('login'))
    students = get_all_students()
    return render_template(
        'student/view_students.html',
        students=students
    )

@app.route('/students/add', methods =['GET','POST'])
def add_student_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['role'] !='Admin':
        return redirect(url_for('login'))
    if request.method =='POST':
        student = Student(
            student_id=None,
            roll_no = request.form['roll_no'],
            name=request.form['name'],
            department=request.form['department'],
            year=request.form['year'],
            email=request.form['email'],
            phone=request.form['phone'],
        )
        success,message = add_student(student)
        flash(message)
        if success:
            return redirect(url_for('view_students'))
    return render_template('student/add_student.html')
    
@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(url_for("login"))

    student = get_student_by_id(student_id)

    if student is None:
        flash("Student not found.")
        return redirect(url_for("view_students"))

    if request.method == "POST":
        
        student.name = request.form["name"]
        student.department = request.form["department"]
        student.year = request.form["year"]
        student.email = request.form["email"]
        student.phone = request.form["phone"]
        student.borrow_limit = request.form["borrow_limit"]
        student.status = request.form["status"]

        success,message = update_student(student)
        flash(message)
        if success: 
            return redirect(url_for("view_students"))

    return render_template(
        "student/edit_student.html",
        student=student
    )

@app.route("/students/delete/<int:student_id>")
def delete_student_route(student_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(url_for("login"))

    delete_student(student_id)

    flash("Student deleted successfully.")

    return redirect(url_for("view_students"))

@app.route("/students/search")
def search_student_route():

    if "user_id" not in session:
        return redirect(url_for("login"))

    keyword = request.args.get("keyword", "")

    students = search_students(keyword)

    return render_template(
        "student/view_students.html",
        students=students
    )
    
@app.route("/logout")
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for("login"))

@app.route('/change_password', methods=['GET','POST'])
def change_password_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'Student':
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash('Passwords do not match.')
            return render_template('student/change_password.html')
        if len(new_password) < 6:
            flash('Password must contain atleast 6 characters.')
            return render_template('student/change_password.html')

        success,message = change_password(
            session['username'],
            new_password)
        flash(message)
        if success:
            return redirect(url_for('student_dashboard'))
    return render_template('student/change_password.html')

@app.route("/books")
def view_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(url_for("student_dashboard"))

    keyword = request.args.get("search", "").strip()

    if keyword:
        books = search_books(keyword)
    else:
        books = get_all_books()

    return render_template(
        "books/view_books.html",
        books=books,
        keyword=keyword
    )

@app.route("/books/add", methods=["GET", "POST"])
def add_book_route():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":

        book = Book(
            bookcode=request.form["bookcode"].strip(),
            title=request.form["title"].strip(),
            author=request.form["author"].strip(),
            category=request.form["category"].strip(),
            copies=int(request.form["copies"]),
            available=int(request.form["copies"]),
            shelf=request.form["shelf"].strip(),
            price=float(request.form["price"]),
            qr_path=""
        )

        success, message = add_book(book)

        flash(message)

        if success:
            return redirect(url_for("view_books"))

        return render_template(
            "books/add_book.html",
            book=book
        )

    return render_template("books/add_book.html")

@app.route("/books/edit/<int:book_id>",methods=["GET", "POST"])
def edit_book_route(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(url_for("student_dashboard"))

    book = get_book(book_id)

    if not book:
        flash("Book not found.")
        return redirect(url_for("view_books"))

    if request.method == "POST":
        book.title = request.form["title"].strip()
        book.author = request.form["author"].strip()
        book.category = request.form["category"].strip()

        try:

            book.copies = int(request.form["copies"])
            book.price = float(request.form["price"])

        except ValueError:

            flash(
                "Copies must be a number and "
                "price must be a valid number."
            )

            return render_template("books/edit_book.html",book=book)

        book.shelf = request.form["shelf"].strip()

        success, message = update_book(book)

        flash(message)

        if success:
            update_reservations_for_book(book.book_id)
            return redirect(url_for("view_books"))

    return render_template("books/edit_book.html",book=book)

@app.route("/books/delete/<int:book_id>")
def delete_book_route(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(url_for("student_dashboard"))

    success, message = delete_book(book_id)

    flash(message)

    return redirect(url_for("view_books"))

@app.route("/borrow", methods=["GET", "POST"])
def borrow_book_route():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":

        student_id = request.form["student_id"]
        book_id = request.form["book_id"]

        success, message = borrow_book(
            student_id,
            book_id
        )

        flash(message)

        if success:
            return redirect(url_for("borrowed_books"))

    students = get_active_students()
    books = get_available_books()

    return render_template(
        "transactions/borrow_book.html",
        students=students,
        books=books
    )


@app.route("/borrowed-books")
def borrowed_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(
            url_for("student_borrowed_books")
        )

    transactions = get_borrowed_books()

    return render_template(
        "transactions/borrowed_books.html",
        transactions=transactions
    )


@app.route("/admin/scan-return/<int:transaction_id>")
def scan_return(transaction_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    transactions = get_borrowed_books()

    transaction = None

    for item in transactions:

        if item["id"] == transaction_id:
            transaction = item
            break

    if transaction is None:
        flash("Borrowed book not found.")

        return redirect(url_for("borrowed_books"))

    return render_template(
        "transactions/scan_return.html",
        transaction=transaction
    )

@app.route("/admin/return-book/qr", methods=["POST"])
def return_book_qr():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    transaction_id = request.form.get("transaction_id")

    copy_code = request.form.get("copy_code","").strip()

    if not transaction_id or not copy_code:

        flash(
            "Please upload the correct book QR code."
        )

        return redirect(url_for("borrowed_books"))

    success, message = return_book_by_copy_code(
        copy_code
    )
    flash(message)

    return redirect(url_for("borrowed_books"))

@app.route("/admin/issue-return")
def issue_return_module():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        flash("Admin access required.")
        return redirect(url_for("login"))

    return render_template("transactions/issue_return.html")

@app.route("/student/profile")
def student_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Student":
        return redirect(url_for("login"))

    student = get_student_by_roll_no(session["username"])

    if student is None:
        flash("Student profile not found.")
        return redirect(url_for("logout"))

    return render_template("student/profile.html",student=student)

@app.route("/admin/lost-books")
def lost_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "Admin":
        return redirect(url_for("student_dashboard"))

    transactions = get_lost_book_candidates()

    return render_template(
        "lost_books/lost_books.html",
        transactions=transactions
    )


@app.route("/admin/mark-lost/<int:transaction_id>", methods=["POST"])
def mark_book_lost(transaction_id):

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    success, message = mark_book_as_lost(transaction_id)

    flash(message)

    return redirect(url_for("lost_books"))

@app.route("/student/reserve/<int:book_id>", methods=["POST"])
def reserve_book(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Student":
        return redirect(url_for("login"))

    student = get_student_by_roll_no(
        session["username"]
    )

    if student is None:
        flash("Student profile not found.")
        return redirect(url_for("logout"))

    success, message = create_reservation(
        student.student_id,
        book_id
    )

    flash(message)

    return redirect(
        url_for("student_books")
    )

@app.route("/student/books")
def student_books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Student":
        return redirect(url_for("login"))

    books = get_student_books()

    return render_template(
        "student/books.html",
        books=books
    )

@app.route("/student/reservations")
def student_reservations():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Student":
        return redirect(url_for("login"))

    expire_old_reservations()

    student = get_student_by_roll_no(
        session["username"]
    )

    if student is None:
        flash("Student profile not found.")
        return redirect(url_for("logout"))

    reservations = get_student_reservations(
        student.student_id
    )

    return render_template(
        "student/reservations.html",
        reservations=reservations
    )

@app.route("/admin/reservations")
def admin_reservations():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Admin":
        return redirect(url_for("login"))

    expire_old_reservations()

    reservations = get_all_reservations()

    return render_template(
        "reservations/admin_reservations.html",
        reservations=reservations
    )

@app.route(
    "/student/reservation/cancel/<int:reservation_id>",
    methods=["POST"]
)
def cancel_reservation_route(reservation_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Student":
        return redirect(url_for("login"))

    student = get_student_by_roll_no(
        session["username"]
    )

    if student is None:
        flash("Student profile not found.")
        return redirect(url_for("logout"))

    success, message = cancel_reservation(
        reservation_id,
        student.student_id
    )

    flash(message)

    return redirect(
        url_for("student_reservations")
    )



if __name__ == '__main__':
    app.run(debug=True)