import random
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text # Import text for raw SQL
from passlib.context import CryptContext

# Ensure we can import database.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db_mod

# Security
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Data Generators
VEHICLE_NAMES = ["Ford F-150 #101", "Chevy Silverado #102", "Ram 1500 #103", "Ford Transit #104", "Isuzu NPR #105"]
TASKS = ["Oil Change", "Tire Rotation", "Brake Inspection", "Air Filter Replace", "Transmission Flush"]

def seed_users(db: Session):
    print("🌱 Seeding Users...")
    users = [
        {"email": "nicksstewart01@yahoo.com", "password": "Sniper012_", "name": "Nick Stewart"},
        {"email": "dan@geotrack.pro", "password": "Password012_", "name": "Dan Geotrack"},
        {"email": "admin@geotrack.pro", "password": "password123", "name": "Admin User"}
    ]

    for user in users:
        existing = db.query(db_mod.User).filter(db_mod.User.email == user["email"]).first()
        if existing:
            print(f"   Skipping {user['email']} (already exists)")
            continue
        
        hashed_pw = pwd_context.hash(user["password"])
        new_user = db_mod.User(
            email=user["email"],
            hashed_password=hashed_pw,
            full_name=user["name"],
            is_active=True
        )
        db.add(new_user)
    db.commit()


def seed_vehicles(db: Session):
    print("🌱 Seeding Vehicles...")
    vehicles = []
    for i, name in enumerate(VEHICLE_NAMES):
        # Check if exists
        existing = db.query(db_mod.Vehicle).filter(db_mod.Vehicle.geotab_id == f"g{i}").first()
        if existing:
            print(f"   Skipping {name} (already exists)")
            vehicles.append(existing)
            continue
            
        v = db_mod.Vehicle(
            geotab_id=f"g{i}",
            name=name,
            vin=f"1FAHP26{random.randint(10000, 99999)}",
            current_mileage=random.randint(20000, 80000),
            current_hours=random.randint(1000, 4000),
            last_sync=datetime.utcnow()
        )
        db.add(v)
        vehicles.append(v)
    db.commit()
    return vehicles

def seed_schedules(db: Session, vehicles):
    print("🌱 Seeding Schedules...")
    for v in vehicles:
        # Check for existing scheduler
        count = db.query(db_mod.MaintenanceSchedule).filter(db_mod.MaintenanceSchedule.vehicle_id == v.id).count()
        if count > 0:
            continue

        # Add Oil Change Schedule
        s1 = db_mod.MaintenanceSchedule(
            vehicle_id=v.id,
            task_name="Oil Change",
            tracking_type="miles",
            interval_value=5000,
            alert_thresholds="500",
            last_performed_value=v.current_mileage - random.randint(100, 4000),
            is_active=True
        )
        db.add(s1)
        
        # Add Tire Rotation
        s2 = db_mod.MaintenanceSchedule(
            vehicle_id=v.id,
            task_name="Tire Rotation",
            tracking_type="miles",
            interval_value=10000,
            alert_thresholds="1000",
            last_performed_value=v.current_mileage - random.randint(500, 9000),
            is_active=True
        )
        db.add(s2)
    db.commit()

def seed_logs(db: Session, vehicles):
    print("🌱 Seeding Logs...")
    for v in vehicles:
        # Check if logs exist
        count = db.query(db_mod.MaintenanceLog).filter(db_mod.MaintenanceLog.vehicle_id == v.id).count()
        if count > 5:
            continue
            
        # Create 3-5 random logs per vehicle
        for _ in range(random.randint(3, 5)):
            past_date = datetime.utcnow() - timedelta(days=random.randint(10, 365))
            task = random.choice(TASKS)
            mileage_at_time = v.current_mileage - random.randint(1000, 15000)
            
            log = db_mod.MaintenanceLog(
                vehicle_id=v.id,
                task_name=task,
                performed_at_mileage=max(0, mileage_at_time),
                performed_at_hours=max(0, v.current_hours - random.randint(50, 500)),
                performed_date=past_date,
                cost=random.randint(50, 800),
                notes="Rutine maintenance performed by vendor."
            )
            db.add(log)
    db.commit()

def main():
    print("🔌 connecting to DB...")
    db = db_mod.SessionLocal()
    try:
        # Test connection
        db.execute(text("SELECT 1"))
        print("✅ Connected!")
        
        seed_users(db) # Seed users first
        vehicles = seed_vehicles(db)
        # Re-query valid vehicles to ensure they are bound
        vehicles = db.query(db_mod.Vehicle).all()
        seed_schedules(db, vehicles)
        seed_logs(db, vehicles)
        print("✅ Seeding Complete!")
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
