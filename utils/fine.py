from datetime import date,datetime
from config2 import FINE_PER_DAY
def calculate_fine(due_date):
    if not due_date:
        return 0.0
    if isinstance(due_date,str):
        due_date=datetime.strptime(
            due_date, "%Y-%m-%d"
        ).date()
    today = date.today()
    if today<= due_date:
        return 0.0
    overdue_days =(today-due_date).days
    return overdue_days* FINE_PER_DAY