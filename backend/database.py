import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

load_dotenv()

# Replace with Supabase URL in .env later
# e.g., postgresql://user:pass@host:port/db
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./maintenance.db")

# For PostgreSQL, check if the driver is specified, if not add it
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

engine_args = {}
if is_sqlite:
    engine_args["connect_args"] = {"check_same_thread": False}

# Handle Vercel's read-only filesystem by using in-memory SQLite if no DATABASE_URL is provided
if is_sqlite and "maintenance.db" in SQLALCHEMY_DATABASE_URL and os.environ.get("VERCEL"):
    print("WARNING: Running on Vercel without DATABASE_URL. Switching to in-memory SQLite.")
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    geotab_id = Column(String, unique=True, index=True)
    name = Column(String)
    vin = Column(String, nullable=True)
    current_mileage = Column(Float, default=0.0)
    current_hours = Column(Float, default=0.0)
    last_sync = Column(DateTime, default=datetime.utcnow)
    
    schedules = relationship("MaintenanceSchedule", back_populates="vehicle")

class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    task_name = Column(String)
    tracking_type = Column(String) # "miles", "hours", "time"
    interval_value = Column(Float)
    alert_thresholds = Column(String) # comma-separated
    last_performed_value = Column(Float, default=0.0)
    last_performed_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    vehicle = relationship("Vehicle", back_populates="schedules")

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    task_name = Column(String)
    performed_at_mileage = Column(Float)
    performed_at_hours = Column(Float)
    performed_date = Column(DateTime, default=datetime.utcnow)
    cost = Column(Float, default=0.0)
    notes = Column(String, nullable=True)

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(String)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating database tables: {e}")
    # Fallback to in-memory if we failed (likely read-only FS)
    if "readonly" in str(e).lower() or "attempt to write a readonly database" in str(e).lower() or "permission denied" in str(e).lower() or "unable to open database" in str(e).lower():
         print("Fallback to in-memory SQLite due to read-only filesystem")
         # Re-create engine and session for in-memory
         engine = create_engine("sqlite:///:memory:", **engine_args)
         SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
         Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
