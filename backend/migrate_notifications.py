from database import engine, Base
from sqlalchemy import text

def create_table():
    print("Migrating Database: Creating notifications table...")
    try:
        # Create table using SQLAlchemy metadata
        # create_all checks for existence automatically and safely across all DB types
        Base.metadata.create_all(bind=engine)
        print("✅ Tables verified/created successfully.")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    create_table()
