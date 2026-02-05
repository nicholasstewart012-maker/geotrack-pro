import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found in .env")
    exit(1)

print(f"Connecting to: {db_url.split('@')[-1]}")

try:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables found in database:")
    with engine.connect() as connection:
        for table in tables:
            try:
                # Use text() for SQL queries
                result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f" - {table}: {count} rows")
            except Exception as table_err:
                 print(f" - {table}: (Error counting: {table_err})")
except Exception as e:
    print(f"Error: {e}")
