from apscheduler.schedulers.background import BackgroundScheduler
import datetime

def send_reminder():
    print("Checking deadlines...")

    # In real version integrate email or WhatsApp API
    now = datetime.datetime.now()
    print("Reminder check at:", now)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminder, "interval", minutes=1)
    scheduler.start()