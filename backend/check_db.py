import os
import sys
from sqlalchemy import text

# Ensure we can import database.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db_mod

def check_data():
    print("🔍 Checking Database Content...")
    try:
        db = db_mod.SessionLocal()
        
        # 1. Connection Check
        db.execute(text("SELECT 1"))
        print("✅ Database Connected")
        
        # 2. Check Users
        users = db.query(db_mod.User).all()
        print(f"\n👥 Users found: {len(users)}")
        for u in users:
            print(f"   - ID: {u.id} | Email: {u.email} | Name: {u.full_name}")

        # 3. Check Vehicles
        vehicles = db.query(db_mod.Vehicle).all()
        print(f"\n🚛 Vehicles found: {len(vehicles)}")
        for v in vehicles:
            print(f"   - {v.name} (GeoTab ID: {v.geotab_id})")

        db.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        print("   (Make sure .env is setup correctly on this machine)")

if __name__ == "__main__":
    check_data()
