from database import engine
from sqlalchemy import text

def add_column():
    print("Migrating Database: Adding last_alerted_at to maintenance_schedules...")
    # Use engine.begin() to automatically commit the transaction
    with engine.begin() as conn:
        try:
            # TIMESTAMP is compatible with both SQLite and Postgres
            conn.execute(text("ALTER TABLE maintenance_schedules ADD COLUMN last_alerted_at TIMESTAMP"))
            print("✅ Column 'last_alerted_at' added successfully.")
        except Exception as e:
            err_str = str(e).lower()
            if "duplicate column" in err_str or "already exists" in err_str:
                print("ℹ️ Column 'last_alerted_at' already exists.")
            else:
                print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    add_column()
