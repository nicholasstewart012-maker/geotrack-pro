import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"Connecting to: {db_url.split('@')[-1]}") # Print host only for security

try:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables found in database:")
    for table in tables:
        print(f" - {table}")
except Exception as e:
    print(f"Error: {e}")
