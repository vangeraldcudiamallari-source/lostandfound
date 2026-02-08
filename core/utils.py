# your_project/utils.py

from datetime import datetime, timedelta

def format_relative_time(report_date):
    """Calculates time difference and returns a user-friendly string."""
    # ... (paste the full function body here)
    now = datetime.now()
    diff = now - report_date
    # ... (rest of the logic)
    if diff < timedelta(hours=1):
        # ...
    # ...
    else:
        return report_date.strftime("%b %d, %Y")