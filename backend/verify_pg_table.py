from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
print(f"Checking Database: {DB_URL}")

try:
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n--- Current Tables ---")
    for table in tables:
        print(f" - {table}")
    
    if "login_logs" in tables:
        print("\nSUCCESS: 'login_logs' table FOUND.")
    else:
        print("\nFAILURE: 'login_logs' table NOT found.")
        
except Exception as e:
    print(f"\nError: {e}")
