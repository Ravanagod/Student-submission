# email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# You should set these as environment variables for security
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "assignmentsubmission344@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "kett ekmq pozz hzxy")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(to_email: str, subject: str, message: str):
    """
    Send an email using Gmail SMTP.
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        server.quit()

        print("Email sent successfully")

    except Exception as e:
        print("Email failed:", e)