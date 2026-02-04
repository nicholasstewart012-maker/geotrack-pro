import os
from database import SessionLocal, User
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin(email, password, name):
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists.")
            return

        hashed_password = pwd_context.hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=name
        )
        db.add(new_user)
        db.commit()
        print(f"Successfully created admin user: {email}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py [email] [password] [name]")
    else:
        create_admin(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "Admin")
