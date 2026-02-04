from sqlalchemy import text
from passlib.context import CryptContext

# Ensure we can import database.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db_mod

# Security Check
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

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

        # 2a. Verify Password
        target_email = "nicksstewart01@yahoo.com"
        target_pass = "Sniper012_"
        u = db.query(db_mod.User).filter(db_mod.User.email == target_email).first()
        if u:
            print(f"\n🔐 Verifying password for {target_email}...")
            is_valid = pwd_context.verify(target_pass, u.hashed_password)
            if is_valid:
                print(f"   ✅ Password '{target_pass}' represents a MATCH!")
            else:
                print(f"   ❌ Password INVALID. Hash mismatch.")
                print(f"   Stored Hash: {u.hashed_password}")

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
