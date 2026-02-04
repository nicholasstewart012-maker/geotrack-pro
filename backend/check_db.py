import sys
import os

try:
    print("Importing database module...")
    import database
    print("Database module imported successfully.")
    
    print("Creating tables...")
    database.Base.metadata.create_all(bind=database.engine)
    print("Tables created successfully.")
    
    # Try to create a session and query
    db = database.SessionLocal()
    print("Session created.")
    
    user_count = db.query(database.User).count()
    print(f"User count: {user_count}")
    
    db.close()
    print("Test Complete: SUCCESS")
    sys.exit(0)
except Exception as e:
    print(f"Test Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
