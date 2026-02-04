from database import engine
from sqlalchemy import text

def add_column():
    print("Migrating Database: Adding last_alerted_at to maintenance_schedules...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE maintenance_schedules ADD COLUMN last_alerted_at DATETIME"))
            print("✅ Column 'last_alerted_at' added successfully.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ Column 'last_alerted_at' already exists.")
            else:
                print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    add_column()
