from datetime import datetime
import sqlite3
import os

DB_PATH = "backend/maintenance.db"

def check_thresholds():
    """
    Checks vehicle mileage/hours against maintenance schedules in the DB
    and sends alerts if thresholds are crossed.
    """
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query all schedules with their current vehicle telemetry
    cursor.execute("""
        SELECT v.name, v.current_mileage, v.current_hours, 
               s.task_name, s.tracking_type, s.interval_value, 
               s.alert_thresholds, s.last_performed_value
        FROM maintenance_schedules s
        JOIN vehicles v ON s.vehicle_id = v.id
        WHERE s.is_active = 1
    """)
    schedules = cursor.fetchall()
    
    print(f"[{datetime.now()}] Checking {len(schedules)} active schedules in database...")
    
    for row in schedules:
        v_name, v_miles, v_hours, s_task, s_type, s_interval, s_thresholds, s_last_val = row
        
        current = v_miles if s_type == "miles" else v_hours
        remaining = (s_last_val + s_interval) - current
        
        print(f"  - {v_name} ({s_task}): {remaining:.1f} {s_type} remaining")
        
        # Parse thresholds (e.g., "500,250,100")
        try:
            threshold_list = [float(t.strip()) for t in s_thresholds.split(",")]
            for t in sorted(threshold_list, reverse=True):
                if remaining <= t:
                    send_alert(v_name, s_task, remaining, s_type)
                    break
        except Exception as e:
            print(f"  Error parsing thresholds for {s_task}: {e}")
            
    conn.close()

def send_alert(vehicle_name, task, remaining, unit):
    """Mocks sending an email alert using configured settings"""
    # In a real app, we would query the 'settings' table for SMTP info
    print(f"!!! ALERT !!! {vehicle_name} is within {remaining:.1f} {unit} of {task} service.")

if __name__ == "__main__":
    check_thresholds()
