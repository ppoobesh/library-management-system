# 📚 Student Library Management System

A full-stack **Student Library Management System** developed using **Python, Flask, SQLite, HTML, CSS, and Jinja2**.

The system provides separate **Admin** and **Student** portals to manage students, books, physical book copies, borrowing and returns, reservations, lost books, fines, reports, and email notifications.

The application also supports **QR-code-based book return verification**, automated due-date and overdue email reminders, reservation notifications, and CSV report generation using Pandas.

---

## ✨ Key Features

### 👨‍💼 Admin Module

The Admin portal provides complete control over library operations.

- Secure Admin login
- Admin dashboard
- Add new students
- Edit student information
- Search students
- Delete students
- Activate or deactivate student accounts
- Configure student borrowing limits
- Add new books
- Edit book details
- Search books
- Delete books
- Manage multiple physical copies of a book
- Track available copies
- Issue books to students
- View currently borrowed books
- View returned-book history
- Verify book returns using QR codes
- Mark borrowed books as lost
- Calculate lost-book charges
- Manage student reservations
- View library reports
- Export transaction reports as CSV
- Export reservation reports as CSV

---

### 🎓 Student Module

Students have a separate portal for accessing their library account.

- Secure Student login
- Student dashboard
- View student information
- View complete profile
- Change account password
- Browse library books
- Check book availability
- View currently borrowed books
- View returned-book history
- View lost-book records
- Reserve unavailable books
- View reservation status
- Cancel active reservations
- Receive library email notifications

---

## 📖 Book & Physical Copy Management

The system tracks both the main book record and individual physical copies.

For example:

```text
Book Code: BOOK1003
Title: SQL
Total Copies: 2

Physical Copies:
BOOK1003-C01
BOOK1003-C02
```

Each physical copy can have its own status, such as:

```text
Available
Borrowed
Lost
```

This allows the system to identify exactly which physical copy has been issued, returned, or reported lost.

---

## 🔄 Book Issue and Return System

### Book Issue

When an Admin issues a book:

1. The student is selected.
2. An available book is selected.
3. An available physical copy is assigned.
4. A borrowing transaction is created.
5. The physical copy status changes to `Borrowed`.
6. Book availability is updated.
7. The issue date and due date are recorded.
8. A book issue confirmation email is sent to the student.

### Book Return

Book returns use QR-code verification.

1. Admin selects the active borrowing transaction.
2. The QR image of the physical book copy is scanned/uploaded.
3. The system reads the copy code.
4. The copy code is verified against the issued physical copy.
5. The transaction is marked as `Returned`.
6. The physical copy becomes `Available`.
7. Fine is calculated when applicable.
8. Book availability is synchronized.
9. Waiting reservations are checked.

---

## 📱 QR Code Verification

Every physical book copy can be associated with a unique copy code.

Example:

```text
BOOK1003-C01
```

The return process verifies the physical copy using its QR code before completing the return transaction.

This prevents the wrong physical copy from being returned against another borrowing transaction.

---

## 📌 Reservation Management

Students can reserve books when no copies are currently available.

Reservation statuses include:

```text
Waiting
Ready
Completed
Cancelled
Expired
```

When a returned book becomes available, the reservation system can process waiting reservations and update their status.

Students can:

- Reserve unavailable books
- View reservation status
- Cancel reservations
- Receive availability notifications
- View completed or expired reservations

Admins can view and manage reservation records.

---

## ❌ Lost Book Management

An Admin can mark an actively borrowed physical copy as lost.

When a book is marked as lost:

- The transaction status changes to `Lost`
- The exact physical copy is marked as `Lost`
- The lost date is recorded
- The book price can be applied as the lost-book charge
- Availability is synchronized with the remaining physical copies
- The lost transaction appears in lost-book records and reports

---

## 💰 Fine Management

The application supports fine tracking for borrowing transactions.

Fine information is stored with transaction records and displayed in:

- Borrowed/returned book records
- Student borrowing history
- Lost-book records
- Transaction reports
- Report summaries

---

## 📧 Email Notification System

The application includes an email notification service.

Notifications include:

- Book issue confirmation
- Due-date reminders
- Overdue reminders
- Reservation availability notifications

Book issue emails can be sent immediately during the borrowing operation.

Scheduled notifications such as due-date and overdue reminders are handled separately through:

```text
daily_tasks.py
```

This allows scheduled tasks to run independently from normal browser requests.

---

## ⏰ Daily Task Automation

`daily_tasks.py` is responsible for scheduled library tasks such as:

- Checking books approaching their due date
- Sending due-date reminder emails
- Detecting overdue books
- Sending overdue notifications
- Processing time-dependent library operations

On Windows, the script can be scheduled using **Windows Task Scheduler**.

Example:

```bash
python daily_tasks.py
```

The Flask application handles the web interface, while the scheduled task script handles recurring background operations.

---

## 📊 Reports

The Admin Reports module provides a summary of library activity.

### Dashboard Statistics

The report dashboard includes:

- Total Students
- Total Books
- Total Physical Copies
- Available Copies
- Currently Borrowed Books
- Returned Books
- Lost Books
- Active Reservations
- Total Fine

### Transaction Report

Contains borrowing information such as:

- Transaction ID
- Register Number
- Student Name
- Book Code
- Book Title
- Copy Code
- Issue Date
- Due Date
- Return Date
- Fine
- Status

### Reservation Report

Contains:

- Reservation ID
- Register Number
- Student Name
- Book Code
- Book Title
- Reservation Date
- Ready Date
- Reservation Status
- Notification Status

Reports can be exported to **CSV using Pandas**.

---

## 🔐 Authentication and Authorization

The system provides separate login options for:

### Admin

Administrators can access:

- Student Management
- Book Management
- Issue / Return
- Reservations
- Lost Books
- Reports

### Student

Students can access:

- Student Dashboard
- Profile
- Browse Books
- Borrowing History
- Reservations
- Change Password

Flask sessions are used to maintain authenticated user sessions and restrict access based on user roles.

---

## 🗄️ Database

The application uses **SQLite** as its relational database.

The database stores information related to:

- Users
- Students
- Books
- Physical Book Copies
- Borrowing Transactions
- Reservations

Relationships between these records allow individual physical copies and their circulation history to be tracked.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application and business logic |
| Flask | Backend web framework and routing |
| SQLite | Relational database |
| HTML5 | Web page structure |
| CSS3 | User interface styling |
| Jinja2 | Dynamic HTML template rendering |
| Pandas | Report processing and CSV export |
| QR Code | Physical book-copy identification |
| SMTP / Email | Automated email notifications |
| Git | Version control |
| GitHub | Source-code hosting |

---

## 📁 Project Structure

```text
Student-Library-Management-System/
│
├── app.py
├── config.py
├── database.py
├── daily_tasks.py
├── models.py
├── requirements.txt
│
├── database/
│   └── library.db
│
├── services/
│   ├── auth_service.py
│   ├── book_service.py
│   ├── lost_book_service.py
│   ├── mail_service.py
│   ├── remainder_service.py
│   ├── report_service.py
│   ├── reservation_service.py
│   ├── student_services.py
│   └── transaction_service.py
│
├── utils/
│   └── qr.py
│
├── Templates/
│   ├── base.html
│   ├── login.html
│   ├── ...
│   └── reports/
│
└── Static/
    └── css/
        └── style.css
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Navigate to the Project

```bash
cd Library-management-system
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install Required Packages

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

Open the local Flask address displayed in the terminal.

---

## 🔒 Important Security Note

Do not commit sensitive information such as:

- Email passwords
- SMTP credentials
- Flask secret keys
- Environment variables
- Production database files

Keep sensitive configuration outside the public GitHub repository and load it securely through environment variables or an appropriate configuration mechanism.

---

## 🔮 Future Enhancements

Possible future improvements include:

- Cloud deployment
- REST API
- Camera-based live QR scanning
- Advanced report filtering
- Analytics and charts
- Fine payment tracking
- Student borrowing analytics
- ISBN-based book information
- Pagination for large datasets
- Enhanced email templates

---

## 👨‍💻 Project Category

**Python Full-Stack Web Development Project**

Built using Flask with database management, role-based authentication, QR-code processing, automated email notifications, scheduled tasks, and reporting.
