import database as db_mod
import sync_service
from datetime import datetime

def simulate():
    db = db_mod.SessionLocal()
    print("🧪 setting up simulation data...")
    
    # 1. Create Test Vehicle
    v = db.query(db_mod.Vehicle).filter(db_mod.Vehicle.geotab_id == "TEST_ALERT_01").first()
    if not v:
        v = db_mod.Vehicle(
            geotab_id="TEST_ALERT_01",
            name="Simulated Truck",
            current_mileage=15000,
            last_sync=datetime.utcnow()
        )
        db.add(v)
        db.commit()
    
    # 2. Create Overdue Schedule (Due at 10,000 miles, current is 15,000)
    s = db.query(db_mod.MaintenanceSchedule).filter(
        db_mod.MaintenanceSchedule.vehicle_id == v.id,
        db_mod.MaintenanceSchedule.task_name == "Oil Change"
    ).first()
    
    if not s:
        s = db_mod.MaintenanceSchedule(
            vehicle_id=v.id,
            task_name="Oil Change",
            tracking_type="miles",
            interval_value=5000,
            last_performed_value=5000, # Due at 10k
            is_active=True
        )
        db.add(s)
    else:
        # Reset alert timer to force trigger
        s.last_alerted_at = None
        
    db.commit()
    
    print("🧪 Running alert check...")
    sync_service.check_maintenance_alerts(db)
    print("✅ Done.")

if __name__ == "__main__":
    simulate()
