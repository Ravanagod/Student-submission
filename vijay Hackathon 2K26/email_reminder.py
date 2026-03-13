import smtplib

def send_email(student_email,assignment):

    sender="youremail@gmail.com"
    password="yourpassword"

    message=f"""
Subject: Assignment Reminder

Reminder: {assignment} deadline is approaching.
"""

    server=smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(sender,password)
    server.sendmail(sender,student_email,message)
    server.quit()