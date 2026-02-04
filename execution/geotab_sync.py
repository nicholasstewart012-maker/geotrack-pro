import os
import sys
import mygeotab
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Add backend to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
import database as db_mod

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def sync_geotab():
    # Load credentials from settings or env
    # For automation, we'll try settings first, then fall back to env
    db = next(db_mod.get_db())
    try:
        settings_rows = db.query(db_mod.Setting).all()
        settings = {s.key: s.value for s in settings_rows}
        
        username = settings.get("GEOTAB_USER") or os.getenv("GEOTAB_USER")
        password = settings.get("GEOTAB_PASS") or os.getenv("GEOTAB_PASS")
        database_name = settings.get("GEOTAB_DB") or os.getenv("GEOTAB_DB")
        server = settings.get("GEOTAB_SERVER") or os.getenv("GEOTAB_SERVER", "my.geotab.com")

        if not all([username, password, database_name]):
            print("Geotab credentials missing. Skipping sync.")
            return

        print(f"[{datetime.now()}] Connecting to Geotab ({server}/{database_name})...")
        client = mygeotab.API(username=username, password=password, database=database_name, server=server)
        client.authenticate()

        # Get all enrolled vehicles
        vehicles = db.query(db_mod.Vehicle).all()
        if not vehicles:
            print("No vehicles enrolled in database. Skipping.")
            return

        for vehicle in vehicles:
            print(f"Syncing {vehicle.name} ({vehicle.geotab_id})...")
            try:
                # Fetch latest device data
                # Using Device id to get status data (Odometer and Engine Hours)
                # Diagnostics: DiagnosticOdometerId (DiagnosticOdometerId), DiagnosticEngineHoursId (DiagnosticEngineHoursAdjustmentId)
                
                # Odometer
                odo_data = client.call("Get", typeName="StatusData", search={
                    "deviceSearch": {"id": vehicle.geotab_id},
                    "diagnosticSearch": {"id": "DiagnosticOdometerId"},
                    "resultsLimit": 1
                })
                
                # Engine Hours
                hours_data = client.call("Get", typeName="StatusData", search={
                    "deviceSearch": {"id": vehicle.geotab_id},
                    "diagnosticSearch": {"id": "DiagnosticEngineHoursId"},
                    "resultsLimit": 1
                })

                if odo_data:
                    # Geotab returns meters, convert to miles
                    meters = odo_data[0]['data']
                    miles = meters * 0.000621371
                    vehicle.current_mileage = miles
                
                if hours_data:
                    # Geotab returns seconds, convert to hours
                    seconds = hours_data[0]['data']
                    hours = seconds / 3600.0
                    vehicle.current_hours = hours
                
                vehicle.last_sync = datetime.utcnow()
                print(f"  - Updated: {vehicle.current_mileage:.1f} mi, {vehicle.current_hours:.1f} hrs")

            except Exception as e:
                print(f"  Error syncing {vehicle.name}: {e}")

        db.commit()
        print("Sync complete.")

    except Exception as e:
        print(f"Global sync error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sync_geotab()
