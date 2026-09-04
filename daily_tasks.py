from services.remainder_service import (send_due_reminders,send_overdue_reminders)
from services.reservation_service import (expire_old_reservations)
def run_daily_tasks():
    print("Running daily library tasks...")
    success, due_count = send_due_reminders()
    print("Due reminder emails sent:",due_count)
    success, overdue_count = (send_overdue_reminders())
    print("Overdue reminder emails sent:",overdue_count)
    success, expired_count = (expire_old_reservations())
    print("Expired reservations:",expired_count)
    print("Daily tasks completed.")
if __name__ == "__main__":
    run_daily_tasks()