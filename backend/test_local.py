from sqlalchemy import create_engine, text

# Try localhost
URL = "postgresql://postgres:Password012_@localhost:5432/postgres"

def check_local():
    print(f"Testing connection to: {URL}")
    try:
        engine = create_engine(URL)
        with engine.connect() as conn:
            res = conn.execute(text("SELECT 1"))
            print(f"✅ Success! Result: {res.fetchone()}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    check_local()
