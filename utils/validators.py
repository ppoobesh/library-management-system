import re
def validate_name(name):
    pattern = r'^[A-Za-z]{3,50}$'
    return bool(re.fullmatch(pattern,name.strip()))

def validate_email(email):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z]+\.[A-Za-z]{2,}$'
    return bool(re.fullmatch(pattern,email.strip()))

def validate_phone(phone):
    pattern = r'^[6-9][0-9]{9}$'
    return bool(re.fullmatch(pattern,phone.strip()))

def validate_register_number(register_number):
    register_number=register_number.strip()
    return 3<= len(register_number)<=20

def validate_borrow_limit(limit):
    try:
        limit=int(limit)
        return limit>0
    except (ValueError,TypeError):
        return False

def validate_bookcode(bookcode):
    pattern = r'^[A-Za-z0-9_-]{3,30}$'
    return bool(re.fullmatch(pattern, bookcode.strip()))


def validate_title(title):
    if not isinstance(title, str):
        return False

    title = title.strip()

    return 2 <= len(title) <= 100


def validate_author(author):
    pattern = r"^[A-Za-z.' _]{2,100}$"
    return bool(re.fullmatch(pattern, author.strip()))


def validate_category(category):
    category = category.strip()
    return 2 <= len(category) <= 50


def validate_copies(copies):
    try:
        copies = int(copies)
        return copies > 0
    except (ValueError, TypeError):
        return False


def validate_available(available, copies):
    try:
        available = int(available)
        copies = int(copies)
        return 0 <= available <= copies
    except (ValueError, TypeError):
        return False


def validate_shelf(shelf):
    shelf = shelf.strip()
    return 1 <= len(shelf) <= 30


def validate_price(price):
    try:
        price = float(price)
        return price >= 0
    except (ValueError, TypeError):
        return False
