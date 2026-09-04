# Student Library Management System

A complete web-based **Student Library Management System** developed using **Python, Flask, SQLite, HTML, CSS, and JavaScript**.

The system provides separate **Admin** and **Student** interfaces for managing students, books, physical book copies, borrowing, QR-based returns, reservations, lost books, fines, email notifications, and reports.

The project is designed to maintain individual physical copies of books and keep book availability synchronized with borrowing, returning, reservation, and lost-book operations.

---

## Features

### Admin Module

Administrators can:

- Login through the Admin portal
- Manage student records
- Add new students
- Edit student information
- Activate or deactivate student accounts
- Configure individual student borrow limits
- Delete eligible student records
- Search students
- Manage library books
- Add books and physical copies
- Edit book details
- Delete eligible books
- Search books
- Issue books to students
- View currently borrowed books
- Return books using QR-code verification
- Mark borrowed books as lost
- View returned book history
- Manage student reservations
- View lost-book records
- View system reports
- Export transaction reports as CSV
- Export reservation reports as CSV

---

### Student Module

Students can:

- Login using their student account
- View their dashboard
- View personal profile information
- Change their password
- Browse library books
- Check book availability
- Reserve unavailable books
- View reservation status
- Cancel reservations
- View currently borrowed books
- View returned and lost-book history
- View due dates and fines

---

## Book Copy Management

The system manages every physical book copy separately.

For example:

```text
BOOK1003
├── BOOK1003-C01
└── BOOK1003-C02
```

Each physical copy can have a status such as:

```text
Available
Borrowed
Lost
```

Book availability is determined using the number of physical copies whose status is:

```text
Available
```

This prevents incorrect availability when individual copies are borrowed, returned, or reported lost.

---

## Borrowing System

When an administrator issues a book:

1. The student account is validated.
2. The student's current borrow count is checked.
3. The student's configured borrow limit is checked.
4. An available physical copy is selected.
5. A transaction is created.
6. The selected physical copy becomes `Borrowed`.
7. Book availability is updated.
8. Any matching `Ready` reservation is completed.
9. The due date is calculated automatically.
10. A borrow confirmation email can be sent to the student.

The current borrowing period is configured as:

```python
BORROW_DAYS = 14
```

---

## QR-Based Book Return

Each physical book copy has its own QR code.

Example:

```text
BOOK1003-C01
```

During a return:

1. The administrator selects the borrowed transaction.
2. The physical book QR image is uploaded.
3. The QR code is decoded.
4. The decoded copy code is compared with the expected copy.
5. The return is accepted only when the correct physical copy is verified.
6. The transaction status becomes `Returned`.
7. The physical copy becomes `Available`.
8. Any overdue fine is calculated.
9. Book availability is synchronized.
10. Waiting reservations for the book are processed.

This ensures that the administrator returns the exact physical copy that was originally issued.

---

## Reservation System

Students can reserve books when no copies are currently available.

Reservation statuses include:

```text
Waiting
Ready
Completed
Cancelled
Expired
```

### Reservation Flow

```text
Book unavailable
      ↓
Student reserves book
      ↓
Waiting
      ↓
A copy becomes available
      ↓
Ready
      ↓
Student receives notification
      ↓
Book collected
      ↓
Completed
```

If a student no longer requires the book, the reservation can be cancelled.

A ready reservation is held for a configured period:

```python
RESERVATION_HOLD_DAYS = 2
```

If the book is not collected within the hold period, the reservation can expire and the next waiting reservation can be processed.

---

## Lost Book Management

An administrator can mark an actively borrowed physical copy as lost.

When a book is marked as lost:

- Only the selected borrowing transaction is affected.
- The transaction status becomes `Lost`.
- The exact physical copy becomes `Lost`.
- The lost date is recorded.
- The book price can be applied as the lost-book charge.
- Other physical copies of the same title are not affected.

Example:

```text
BOOK1003-C01 → Available
BOOK1003-C02 → Lost

Total Copies     : 2
Available Copies : 1
```

---

## Fine Calculation

Overdue fines are calculated according to the configured fine per day.

Example configuration:

```python
FINE_PER_DAY = 5
```

If a student returns a book after its due date, the system calculates the overdue period and applicable fine.

Lost books can use the book price as the replacement/lost-book charge.

---

## Email Notification System

The project supports email notifications using SMTP.

Notifications can include:

- Borrow confirmation email
- Reservation-ready email
- Due-date reminder email
- Overdue reminder email
- Fine information in overdue notifications

Example mail configuration uses:

```text
SMTP Server : smtp.gmail.com
SMTP Port   : 587
Security    : STARTTLS
```

Sensitive email credentials should **not** be stored directly in the source code or uploaded to GitHub.

Use environment variables for credentials.

Example:

```env
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

---

## Daily Automated Tasks

The project includes:

```text
daily_tasks.py
```

This script is intended to run scheduled library tasks such as:

- Checking upcoming due dates
- Sending due-date reminders
- Checking overdue books
- Sending overdue reminder emails
- Processing time-dependent reservation operations

The Flask web server does not need to be manually opened for every scheduled email task if `daily_tasks.py` is independently scheduled by the operating system.

On Windows, the script can be scheduled using **Windows Task Scheduler**.

---

## Reports Module

The Admin Reports module provides an overview of library activity.

The dashboard includes information such as:

- Total students
- Total books
- Total physical copies
- Available copies
- Currently borrowed books
- Returned books
- Lost books
- Active reservations
- Total fines

The system also provides:

### Transaction Report

Contains information about:

- Transaction ID
- Student
- Register number
- Book
- Physical copy
- Issue date
- Due date
- Return date
- Fine
- Transaction status

### Reservation Report

Contains information about:

- Reservation ID
- Student
- Register number
- Book
- Reservation date
- Ready date
- Reservation status
- Notification status

Reports can be exported as **CSV files**.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Page structure |
| CSS3 | User interface styling |
| JavaScript | Client-side functionality and QR processing |
| Jinja2 | Flask template rendering |
| SMTP | Email notifications |
| QR Code | Physical book-copy identification |
| Pandas | Report generation / CSV processing |

---

## Project Structure

```text
Library-management-system/
│
├── app.py
├── config.py
├── database.py
├── models.py
├── daily_tasks.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   ├── schema.sql
│   └── library.db
│
├── services/
│   ├── student_service.py
│   ├── book_service.py
│   ├── transaction_service.py
│   ├── reservation_service.py
│   ├── report_service.py
│   └── ...
│
├── utils/
│   ├── validators.py
│   ├── qr.py
│   ├── mail.py
│   └── ...
│
├── Templates/
│   ├── base.html
│   ├── login.html
│   ├── admin/
│   ├── student/
│   ├── books/
│   ├── transactions/
│   ├── reservations/
│   └── reports/
│
├── Static/
│   ├── css/
│   │   └── style.css
│   └── qrcodes/
│
├── uploads/
│
└── reports/
    └── csv/
```

> The exact service and utility filenames may vary depending on the final project organization.

---

## Database Tables

The system uses SQLite and includes tables for the main library entities.

### Students

Stores student information such as:

- Register number
- Name
- Department
- Year
- Email
- Phone
- Borrow limit
- Account status

### Books

Stores general book information such as:

- Book code
- Title
- Author
- Category
- Number of copies
- Available copies
- Shelf
- Price

### Book Copies

Stores each physical copy separately.

Important fields include:

```text
book_id
copy_code
status
qrpath
```

### Transactions

Stores borrowing and return history.

Important fields include:

```text
student_id
book_id
copy_id
issue_date
due_date
return_date
fine
status
```

### Reservations

Stores student book reservations and their current status.

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
```

Move into the project directory:

```bash
cd Library-management-system
```

---

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Do not store real passwords directly in `config.py`.

Create a `.env` file or configure operating-system environment variables for sensitive values.

Example:

```env
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
SECRET_KEY=your_secret_key
```

Make sure `.env` is included in `.gitignore`.

---

### 5. Initialize the Database

Ensure the SQLite schema is available in:

```text
database/schema.sql
```

Initialize the database using the initialization method provided by the application.

The application database is stored locally as:

```text
database/library.db
```

For a public GitHub repository, the working database should normally be excluded from version control and recreated from `schema.sql`.

---

### 6. Run the Flask Application

```bash
python app.py
```

The development server normally starts at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser.

---

## Login System

The application provides separate login options for:

### Administrator

Administrators can access management modules including:

```text
Student Management
Book Management
Issue / Return
Reservations
Lost Books
Reports
```

### Student

Students can access:

```text
My Information
My Borrowed Books
Browse Books
My Reservations
My Profile
Change Password
```

Authentication is session-based, and protected routes verify the logged-in user's role before allowing access.

---

## Book Status Workflow

A normal book-copy lifecycle is:

```text
Available
   ↓
Borrowed
   ↓
Returned
   ↓
Available
```

For a lost book:

```text
Available
   ↓
Borrowed
   ↓
Lost
```

The transaction history and physical-copy status are maintained separately.

For example, after returning a book:

```text
Transaction status : Returned
Copy status        : Available
```

This allows the transaction to remain permanently in the student's borrowing history while making the physical copy available for another student.

---

## Reservation and Return Integration

When a physical copy is returned:

```text
Borrowed Copy
      ↓
Return verified
      ↓
Copy becomes Available
      ↓
Availability synchronized
      ↓
Waiting reservations checked
      ↓
Next eligible reservation becomes Ready
      ↓
Student notification sent
```

This connects the transaction, inventory, reservation, and email modules.

---

## Security Notes

Before deploying or publishing this project:

- Never commit email passwords.
- Never commit Gmail App Passwords.
- Keep `.env` files out of Git.
- Use environment variables for secrets.
- Use a strong Flask `SECRET_KEY`.
- Do not publish a production database containing real student information.
- Disable Flask debug mode in production.
- Validate all user input.
- Restrict Admin routes to authenticated Admin accounts.

If a password or API credential was accidentally committed to Git, revoke/rotate it immediately.

---

## Future Enhancements

Possible future improvements include:

- Live camera-based QR scanning
- PDF report generation
- Advanced report filters
- Fine payment tracking
- Student notification dashboard
- Book categories and advanced filtering
- Reservation queue visualization
- Admin analytics charts
- Cloud database support
- Deployment to a production server
- Automated backups
- Responsive mobile UI improvements

---

## Purpose of the Project

This project demonstrates practical implementation of:

- Python web development
- Flask routing
- Role-based authentication
- Session management
- SQLite database operations
- Relational database design
- CRUD operations
- Physical inventory management
- Transaction processing
- QR-code integration
- Reservation queue management
- Email automation
- Fine calculation
- Scheduled background tasks
- Report generation
- Responsive web interface design

---

## Author

Developed as a **Student Library Management System** project using Python and Flask.

---

## License

This project is intended for educational and academic purposes.
