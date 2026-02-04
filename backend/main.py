import os
import traceback
import sys
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

# FIX: Add current directory to sys.path so local modules like 'database' can be imported on Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Third-party imports
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_to_a_secure_random_string")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- SAFE IMPORT & LIFESPAN ---
SAFE_MODE_ERROR = None

# Global placeholders
jwt = None
CryptContext = None
Session = None
db_mod = None
engine = None
pwd_context = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global SAFE_MODE_ERROR
    global jwt, CryptContext, Session, db_mod, engine, pwd_context
    
    print("BACKEND STARTING UP...")
    try:
        # 1. Critical Imports
        from jose import JWTError
        import jose.jwt as jwt_lib
        jwt = jwt_lib
        
        from passlib.context import CryptContext as CC
        CryptContext = CC
        
        from sqlalchemy.orm import Session as Sess
        Session = Sess
        
        import database as db_module
        db_mod = db_module
        from database import engine as db_engine
        engine = db_engine

        # Initialize Security Context
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

        # 2. Database Checks
        print(f"Database URL configured (Is None? {os.getenv('DATABASE_URL') is None})")
        
        # 3. Seed Admin User
        try:
            # We must use the imported module
            db = db_mod.SessionLocal()
            try:
                admin_email = "admin@geotrack.pro"
                existing = db.query(db_mod.User).filter(db_mod.User.email == admin_email).first()
                if not existing:
                    print(f"Seeding admin user: {admin_email}")
                    hashed_pw = pwd_context.hash("password123")
                    
                    admin_user = db_mod.User(
                        email=admin_email, 
                        hashed_password=hashed_pw, 
                        full_name="Fleet Manager"
                    )
                    db.add(admin_user)
                    db.commit()
            except Exception as seed_err:
                print(f"Startup seed warning: {seed_err}")
            finally:
                db.close()
        except Exception as db_err:
            print(f"Database connection warning: {db_err}")
            
    except Exception as e:
        # If critical imports fail, we capture the error
        SAFE_MODE_ERROR = {
            "status": "CRITICAL_BOOT_FAILURE",
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
        print(f"CRITICAL IMPORT ERROR: {e}")
        print("STARTING IN SAFE MODE")
    
    yield
    print("BACKEND SHUTTING DOWN...")

# --- APP INITIALIZATION ---
app = FastAPI(
    title="Vehicle Maintenance API Pro", 
    root_path="/api",
    lifespan=lifespan
)

# 1. Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    print(f"GLOBAL ERROR: {error_msg}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "traceback": error_msg},
    )

# 2. Safe Mode Middleware
@app.middleware("http")
async def check_safe_mode(request: Request, call_next):
    if SAFE_MODE_ERROR:
        return JSONResponse(status_code=500, content=SAFE_MODE_ERROR)
    return await call_next(request)

# 3. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SECURITY HELPERS ---
def get_password_hash(password):
    if pwd_context:
        return pwd_context.hash(password)
    raise RuntimeError("Security context not initialized")

def verify_password(plain_password, hashed_password):
    if pwd_context:
        return pwd_context.verify(plain_password, hashed_password)
    raise RuntimeError("Security context not initialized")

def create_access_token(data: dict):
    if not jwt:
         raise RuntimeError("JWT library not initialized")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- PYDANTIC SCHEMAS ---
class VehicleBase(BaseModel):
    geotab_id: str
    name: str
    vin: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    current_mileage: float
    current_hours: float
    last_sync: datetime
    class Config:
        from_attributes = True

class ScheduleCreate(BaseModel):
    vehicle_id: int
    task_name: str
    tracking_type: str
    interval_value: float
    alert_thresholds: str

class LogCreate(BaseModel):
    vehicle_id: int
    task_name: str
    performed_at_mileage: float
    performed_at_hours: float
    cost: float
    notes: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str


# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Helper for dependency injection
def get_db_session():
    if not db_mod:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_mod.get_db()

@app.get("/vehicles", response_model=List[Vehicle])
def read_vehicles(db: Session = Depends(lambda: next(get_db_session()))): 
    # Use explicit lambda deferral and handling for Session type hint
    return db.query(db_mod.Vehicle).all()

@app.post("/vehicles", response_model=Vehicle)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(lambda: next(get_db_session()))):
    # Support both Pydantic v1 and v2
    data = vehicle.model_dump() if hasattr(vehicle, "model_dump") else vehicle.dict()
    db_vehicle = db_mod.Vehicle(**data)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@app.post("/schedules")
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(lambda: next(get_db_session()))):
    data = schedule.model_dump() if hasattr(schedule, "model_dump") else schedule.dict()
    db_schedule = db_mod.MaintenanceSchedule(**data)
    db.add(db_schedule)
    db.commit()
    return {"status": "success"}

@app.get("/schedules/{vehicle_id}")
def get_schedules(vehicle_id: int, db: Session = Depends(lambda: next(get_db_session()))):
    return db.query(db_mod.MaintenanceSchedule).filter(db_mod.MaintenanceSchedule.vehicle_id == vehicle_id).all()

@app.post("/logs")
def create_log(log: LogCreate, db: Session = Depends(lambda: next(get_db_session()))):
    data = log.model_dump() if hasattr(log, "model_dump") else log.dict()
    db_log = db_mod.MaintenanceLog(**data)
    db.add(db_log)
    
    schedule = db.query(db_mod.MaintenanceSchedule).filter(
        db_mod.MaintenanceSchedule.vehicle_id == log.vehicle_id,
        db_mod.MaintenanceSchedule.task_name == log.task_name
    ).first()
    
    if schedule:
        if schedule.tracking_type == "miles":
            schedule.last_performed_value = log.performed_at_mileage
        else:
            schedule.last_performed_value = log.performed_at_hours
            
        schedule.last_performed_date = datetime.utcnow()
    
    db.commit()
    return {"status": "success"}

@app.get("/logs/{vehicle_id}")
def get_vehicle_logs(vehicle_id: int, db: Session = Depends(lambda: next(get_db_session()))):
    return db.query(db_mod.MaintenanceLog).filter(db_mod.MaintenanceLog.vehicle_id == vehicle_id).order_by(db_mod.MaintenanceLog.performed_date.desc()).all()

@app.get("/analytics/cost")
def get_cost_analytics(db: Session = Depends(lambda: next(get_db_session()))):
    logs = db.query(db_mod.MaintenanceLog).all()
    total = sum(log.cost for log in logs)
    return {"total_maintenance_cost": total, "count": len(logs)}

@app.get("/settings/all")
def get_all_settings(db: Session = Depends(lambda: next(get_db_session()))):
    settings_list = db.query(db_mod.Setting).all()
    return {s.key: s.value for s in settings_list}

@app.post("/settings")
def update_settings(settings: dict, db: Session = Depends(lambda: next(get_db_session()))):
    for key, value in settings.items():
        db_setting = db_mod.Setting(key=key, value=str(value))
        db.merge(db_setting)
    db.commit()
    return {"status": "success"}

@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(lambda: next(get_db_session()))):
    db_user = db.query(db_mod.User).filter(db_mod.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pass = get_password_hash(user.password)
    new_user = db_mod.User(email=user.email, hashed_password=hashed_pass, full_name=user.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(lambda: next(get_db_session()))):
    db_user = db.query(db_mod.User).filter(db_mod.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
