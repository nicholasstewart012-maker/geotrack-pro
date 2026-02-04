from database import engine, Base
from sqlalchemy import text

def create_table():
    print("Migrating Database: Creating notifications table...")
    try:
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'"))
            if result.fetchone():
                print("ℹ️ Table 'notifications' already exists.")
                return

        # Create table using SQLAlchemy metadata
        # (This is safer than raw SQL for full table creation)
        Base.metadata.create_all(bind=engine)
        print("✅ Table 'notifications' created successfully.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    create_table()
