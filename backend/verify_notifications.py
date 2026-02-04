import database as db_mod
from datetime import datetime

def verify():
    print("🧪 Verifying Notifications...")
    db = db_mod.SessionLocal()
    
    # 1. Create a Test Notification
    print("   Creating duplicate/test notification...")
    n = db_mod.Notification(
        title="Test Notification",
        message="This is a verified test alert from the backend.",
        type="info",
        created_at=datetime.utcnow()
    )
    db.add(n)
    db.commit()
    print(f"   Created ID: {n.id}")
    
    # 2. Fetch
    print("   Fetching from DB...")
    fetched = db.query(db_mod.Notification).filter(db_mod.Notification.id == n.id).first()
    if fetched:
        print(f"✅ Success! Found: {fetched.title}")
    else:
        print("❌ Failed to fetch.")
        
    db.close()

if __name__ == "__main__":
    verify()
