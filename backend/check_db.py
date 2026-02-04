from sqlalchemy import text
from passlib.context import CryptContext

# Ensure we can import database.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db_mod

# Security Check
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

from dotenv import load_dotenv
load_dotenv()

def check_data():
    print("🔍 Checking Environment...")
    print(f"   CWD: {os.getcwd()}")
    print(f"   Env File Exists? {os.path.exists('.env')}")
    print(f"   RAW DATABASE_URL: {os.getenv('DATABASE_URL')}")

    print("\n🔍 Checking Database Content...")
    try:
        db = db_mod.SessionLocal()
        
        # 1. Connection Check
        db.execute(text("SELECT 1"))
        db_name = db.bind.url.database
        print(f"✅ Database Connected: {db_name}")
        
        if "maintenance.db" in str(db_name) or "sqlite" in str(db.bind.url.drivername):
            print("\n⚠️  WARNING: YOU ARE USING SQLITE (LOCAL FILE) INSTEAD OF POSTGRES!")
            print("    The Cloud cannot see this data.")
            print("    Please check your .env file on this computer.")
            print("    It should say: DATABASE_URL=postgresql://postgres:Password012_@localhost:5432/postgres\n")
        
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
