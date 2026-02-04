import os
import sys
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Add backend to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
import database as db_mod

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def check_thresholds():
    db = next(db_mod.get_db())
    try:
        # Get SMTP settings
        settings_rows = db.query(db_mod.Setting).all()
        settings = {s.key: s.value for s in settings_rows}
        
        smtp_server = settings.get("SMTP_SERVER") or os.getenv("SMTP_SERVER")
        smtp_port = int(settings.get("SMTP_PORT") or os.getenv("SMTP_PORT", 587))
        smtp_user = settings.get("SMTP_USER") or os.getenv("SMTP_USER")
        smtp_pass = settings.get("SMTP_PASS") or os.getenv("SMTP_PASS")
        alert_email = settings.get("ALERT_EMAIL") or os.getenv("ALERT_EMAIL")

        # Get all active schedules
        schedules = db.query(db_mod.MaintenanceSchedule).filter(db_mod.MaintenanceSchedule.is_active == True).all()
        
        print(f"[{datetime.now()}] Checking {len(schedules)} active schedules in Cloud DB...")
        
        for s in schedules:
            vehicle = s.vehicle
            current = vehicle.current_mileage if s.tracking_type == "miles" else vehicle.current_hours
            target = s.last_performed_value + s.interval_value
            remaining = target - current
            
            print(f"  - {vehicle.name} ({s.task_name}): {remaining:.1f} {s.tracking_type} remaining")
            
            # Parse thresholds (e.g., "500, 250, 100")
            try:
                threshold_list = [float(t.strip()) for t in s.alert_thresholds.split(",")]
                # Simple logic: alert if we just crossed a threshold
                # For real production, we'd track "last_alerted_threshold" to avoid spam
                for t in sorted(threshold_list, reverse=True):
                    if remaining <= t:
                        if smtp_user and smtp_pass and alert_email:
                            send_real_email(
                                smtp_server, smtp_port, smtp_user, smtp_pass,
                                alert_email, vehicle.name, s.task_name, remaining, s.tracking_type
                            )
                        else:
                            print(f"!!! ALERT (MOCK) !!! {vehicle.name} needs {s.task_name} soon ({remaining:.1f} {s.tracking_type} left)")
                        break
            except Exception as e:
                print(f"  Error checking {s.task_name}: {e}")

    except Exception as e:
        print(f"Global alert error: {e}")
    finally:
        db.close()

def send_real_email(host, port, user, password, to_email, vehicle, task, remaining, unit):
    subject = f"⚠️ Maintenance Alert: {vehicle}"
    body = f"The vehicle '{vehicle}' is within {remaining:.1f} {unit} of its scheduled '{task}' service.\n\nPlease schedule service soon."
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to_email

    try:
        print(f"Sending real email alert to {to_email}...")
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    check_thresholds()
