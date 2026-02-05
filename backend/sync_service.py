import time
import os
import mygeotab
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import database as db_mod
import email_utils

# Load environment variables
load_dotenv()

# Configuration
GEOTAB_SERVER = os.getenv("GEOTAB_SERVER", "my.geotab.com")
GEOTAB_USER = os.getenv("GEOTAB_USER")
GEOTAB_PASS = os.getenv("GEOTAB_PASSWORD")
GEOTAB_DB = os.getenv("GEOTAB_DATABASE")

SYNC_INTERVAL = 60 # seconds

def get_geotab_api():
    """Authenticate and return Geotab API object"""
    try:
        api = mygeotab.API(username=GEOTAB_USER, password=GEOTAB_PASS, database=GEOTAB_DB)
        api.authenticate()
        print(f"✅ Authenticated with Geotab: {GEOTAB_USER}")
        return api
    except mygeotab.AuthenticationException as e:
        print(f"❌ Geotab Authorization Failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Geotab Connection Error: {e}")
        return None

def sync_vehicles(api, db: Session):
    """Fetch all devices and update local DB"""
    print("🔄 Syncing Vehicles...")
    try:
        devices = api.get("Device", search={"groups": [{"id": "GroupCompanyId"}]})
        print(f"   Found {len(devices)} devices in Geotab.")
        
        count_updated = 0
        count_new = 0

        for device in devices:
            g_id = device['id']
            name = device.get('name', 'Unknown')
            vin = device.get('serialNumber', None)
            
            # Find existing
            existing = db.query(db_mod.Vehicle).filter(db_mod.Vehicle.geotab_id == g_id).first()
            
            if existing:
                if existing.name != name or existing.vin != vin:
                    existing.name = name
                    existing.vin = vin
                    existing.last_sync = datetime.utcnow()
                    count_updated += 1
            else:
                new_v = db_mod.Vehicle(
                    geotab_id=g_id,
                    name=name,
                    vin=vin,
                    last_sync=datetime.utcnow()
                )
                db.add(new_v)
                count_new += 1
        
        db.commit()
        print(f"   Saved: {count_new} new, {count_updated} updated.")

    except Exception as e:
        print(f"❌ Error syncing vehicles: {e}")
        db.rollback()

def check_maintenance_alerts(db: Session):
    """Check if any vehicles are due for maintenance and send alerts"""
    print("🔍 Checking Maintenance Alerts...")
    schedules = db.query(db_mod.MaintenanceSchedule)\
                  .join(db_mod.Vehicle)\
                  .filter(db_mod.MaintenanceSchedule.is_active == True).all()

    for schedule in schedules:
        vehicle = schedule.vehicle
        if not vehicle: continue

        is_due = False
        current_val = 0
        due_val = 0
        
        # 1. Check Logic
        if schedule.tracking_type == "miles":
            current_val = vehicle.current_mileage
            due_val = schedule.last_performed_value + schedule.interval_value
            if current_val >= due_val:
                is_due = True
        
        elif schedule.tracking_type == "hours":
            current_val = vehicle.current_hours
            due_val = schedule.last_performed_value + schedule.interval_value
            if current_val >= due_val:
                is_due = True
                
        # 2. Alert Logic
        if is_due:
            # Check cooldown (don't spam - alert once per 24h for same issue)
            if schedule.last_alerted_at:
                cutoff = datetime.utcnow() - timedelta(hours=24)
                if schedule.last_alerted_at > cutoff:
                    continue # Already alerted recently
            
            # Send Email
            subject = f"Maintenance Alert: {vehicle.name} - {schedule.task_name}"
            body = f"""
            Maintenance Alert
            -----------------
            Vehicle: {vehicle.name}
            Task: {schedule.task_name}
            
            Current Usage: {current_val} {schedule.tracking_type}
            Due At: {due_val} {schedule.tracking_type}
            Overdue By: {round(current_val - due_val, 1)} {schedule.tracking_type}
            
            Please schedule service soon.
            """
            
            print(f"   ⚠️ sending alert for {vehicle.name}...")
            success = email_utils.send_email_notification(subject, body)
            
            if success:
                schedule.last_alerted_at = datetime.utcnow()
                
                # Create In-App Notification
                new_notif = db_mod.Notification(
                    title=f"Maintenance Due: {vehicle.name}",
                    message=f"{schedule.task_name} is overdue. Current: {current_val}, Due: {due_val}",
                    type="warning"
                )
                db.add(new_notif)
                
                db.commit()

def sync_status_data(api, db: Session):
    """Fetch odometer and engine hours"""
    print("🔄 Syncing Telemetry (Odometer/Hours)...")
    try:
        # Get all vehicles from DB to map IDs
        vehicles = db.query(db_mod.Vehicle).all()
        
        for v in vehicles:
            try:
                # Get Odometer
                odom_readings = api.get("StatusData", search={
                    "deviceSearch": {"id": v.geotab_id},
                    "diagnosticSearch": {"id": "DiagnosticOdometerId"},
                    "fromDate": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",
                    "take": 1
                })
                
                if odom_readings:
                    # Convert meters to miles? Assuming meters from Geotab usually
                    # 1 meter = 0.000621371 miles
                    meters = odom_readings[0]['data']
                    miles = meters * 0.000621371
                    v.current_mileage = round(miles, 1)

                # Get AccessEngineHours
                hours_readings = api.get("StatusData", search={
                    "deviceSearch": {"id": v.geotab_id},
                    "diagnosticSearch": {"id": "DiagnosticEngineHoursWrapperId"}, # or similar
                    "fromDate": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",
                    "take": 1
                })
                # Fallback to DiagnosticEngineHoursId if Wrapper not found? 
                # Keep simple for now.
                
                if hours_readings:
                    # Seconds to Hours
                    seconds = hours_readings[0]['data']
                    hours = seconds / 3600.0
                    v.current_hours = round(hours, 1)
                
                v.last_sync = datetime.utcnow()
                
            except Exception as ve:
                print(f"   ⚠️ Failed to sync vehicle {v.name}: {ve}")
                
        db.commit()
        print("   Telemetry updated.")

    except Exception as e:
        print(f"❌ Error syncing status data: {e}")
        db.rollback()

import argparse

def main():
    parser = argparse.ArgumentParser(description="Geotab Sync Service")
    parser.add_argument("--once", action="store_true", help="Run sync once and exit")
    args = parser.parse_args()

    print("🚀 Starting Geotab Sync Service...")
    if args.once:
        print("   Mode: Run Once")
    else:
        print("   Mode: Continuous Loop")
        print("   Press Ctrl+C to stop.")
    
    while True:
        api = get_geotab_api()
        if not api:
            if args.once:
                print("❌ Failed to authenticate. Exiting.")
                return
            print("   Retrying in 60s...")
            time.sleep(60)
            continue
            
        # Connect to DB
        try:
            db = db_mod.SessionLocal()
            sync_vehicles(api, db)
            sync_status_data(api, db)
            check_maintenance_alerts(db)
            db.close()
        except Exception as e:
            print(f"❌ Database Connection Failed: {e}")
        
        if args.once:
            print("✅ Sync complete. Exiting.")
            break
            
        print(f"💤 Sleeping {SYNC_INTERVAL}s...")
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
