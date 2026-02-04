import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional

# Configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email_notification(subject: str, body: str, attachment_path: Optional[str] = None):
    """
    Sends a generic email notification via Gmail SMTP.
    """
    if not EMAIL_USER or not EMAIL_PASS:
        print("WARNING: Email credentials not set. Skipping email.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER # Admin receives all notifications for now
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            
        print(f"SUCCESS: Email sent to {EMAIL_USER}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        return False
