import database as db_mod
from database import SessionLocal

def migrate_schedules():
    db = SessionLocal()
    try:
        vehicles = db.query(db_mod.Vehicle).all()
        print(f"Checking {len(vehicles)} vehicles for schedules...")
        
        count = 0
        for v in vehicles:
            existing = db.query(db_mod.MaintenanceSchedule).filter(
                db_mod.MaintenanceSchedule.vehicle_id == v.id
            ).first()
            
            if not existing:
                print(f"Creating default schedule for {v.name}...")
                default_schedule = db_mod.MaintenanceSchedule(
                    vehicle_id=v.id,
                    task_name="Oil Change",
                    tracking_type="miles",
                    interval_value=5000.0,
                    alert_thresholds="4500,4800"
                )
                db.add(default_schedule)
                count += 1
                
        db.commit()
        print(f"Backfilled {count} vehicles.")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_schedules()
