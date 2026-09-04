import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR,'database','library.db')
SECRET_KEY =  'your_secret_key'


BORROW_DAYS = 14
FINE_PER_DAY = 5
OVERDUE_REMINDER_DAYS = 3

DUE_REMINDER_DAYS = 3

QR_FOLDER = os.path.join(BASE_DIR,'static','qrcodes')
UPLOAD_FOLDER = os.path.join(BASE_DIR,'uploads','qr_uploads')
REPORT_FOLDER = os.path.join(BASE_DIR,'reports','csv')
SCHEMA_PATH = os.path.join(BASE_DIR,'database','schema.sql')

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587

MAIL_USERNAME = "example@gmail.com"
MAIL_PASSWORD = "password"
MAIL_FROM = MAIL_USERNAME

RESERVATION_HOLD_DAYS = 2
