import os
import traceback
import sys
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

# FIX: Add current directory to sys.path so local modules like 'database' can be imported on Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Third-party imports
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
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
pwd_context = None
text = None
joinedload = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global SAFE_MODE_ERROR
    global jwt, CryptContext, Session, db_mod, engine, pwd_context, text, joinedload
    
    print("BACKEND STARTING UP...")
    try:
        # 1. Critical Imports
        from jose import JWTError
        import jose.jwt as jwt_lib
        jwt = jwt_lib
        
        from passlib.context import CryptContext as CC
        CryptContext = CC
        
        from sqlalchemy.orm import Session as Sess, sessionmaker, joinedload as joinedload_lib
        Session = Sess
        joinedload = joinedload_lib
        
        import database as db_module
        db_mod = db_module
        from database import engine as db_engine
        engine = db_engine
        
        from sqlalchemy import text as s_text # Import text for raw SQL
        text = s_text

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
    if SAFE_MODE_ERROR and request.url.path != "/api/health" and request.url.path != "/health":
        return JSONResponse(status_code=503, content=SAFE_MODE_ERROR)
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

# --- SECURITY SCHEME ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict):
    if not jwt:
         raise RuntimeError("JWT library not initialized")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(lambda: next(get_db_session()))):
    if not jwt:
        raise HTTPException(status_code=503, detail="Auth not initialized")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception: # JWTError
        raise credentials_exception
        
    user = db.query(db_mod.User).filter(db_mod.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

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
    health_status = {
        "status": "ok", 
        "timestamp": datetime.now().isoformat(),
        "database": "unknown",
        "connection_info": "unknown"
    }

    # Debug: Identify which DB we are using
    if db_mod and engine:
        try:
            url = engine.url
            clean_host = url.host if url.host else "localhost"
            clean_driver = url.drivername
            health_status["connection_info"] = f"{clean_driver}://{clean_host}"
        except:
            health_status["connection_info"] = "parsing_error"
    
    if SAFE_MODE_ERROR:
        return {
            "status": "degraded", 
            "mode": "SAFE_MODE", 
            "error": SAFE_MODE_ERROR
        }
    
    # Try to connect to DB
    try:
        # Use a fresh session for check
        if db_mod and hasattr(db_mod, "SessionLocal"):
            db = db_mod.SessionLocal()
            try:
                # Simple query to verify connection and table existence
                db.execute(text("SELECT 1")) # Use text() wrapper
                health_status["database"] = "connected"
                
                # Check if tables exist
                try:
                    user_count = db.query(db_mod.User).count()
                    health_status["user_count"] = user_count
                    
                    vehicle_count = db.query(db_mod.Vehicle).count()
                    health_status["vehicle_count"] = vehicle_count
                    
                    # Debug first vehicle
                    first_v = db.query(db_mod.Vehicle).first()
                    if first_v:
                        health_status["sample_vehicle"] = {
                            "id": first_v.id,
                            "name": first_v.name,
                            "geotab_id": first_v.geotab_id
                        }
                except Exception as table_err:
                    health_status["table_error"] = str(table_err)
            except Exception as e:
                 health_status["database_error"] = str(e)
                 health_status["status"] = "db_error"
            finally:
                db.close()
    except Exception as e:
        health_status["database_Check_error"] = str(e)

    return health_status

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

@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(lambda: next(get_db_session()))):
    # Check existence
    vehicle = db.query(db_mod.Vehicle).filter(db_mod.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
        
    # Delete related logs first
    db.query(db_mod.MaintenanceLog).filter(db_mod.MaintenanceLog.vehicle_id == vehicle_id).delete()
    
    # Delete related schedules
    db.query(db_mod.MaintenanceSchedule).filter(db_mod.MaintenanceSchedule.vehicle_id == vehicle_id).delete()
    
    # Delete vehicle
    db.delete(vehicle)
    db.commit()
    
    return {"status": "success", "id": vehicle_id}

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

@app.get("/admin/logs/login")
def get_login_logs(db: Session = Depends(lambda: next(get_db_session()))):
    return db.query(db_mod.LoginLog).order_by(db_mod.LoginLog.login_time.desc()).limit(100).all()

@app.get("/analytics/cost")
def get_cost_analytics(db: Session = Depends(lambda: next(get_db_session()))):
    logs = db.query(db_mod.MaintenanceLog).all()
    total = sum(log.cost for log in logs)
    return {"total_maintenance_cost": total, "count": len(logs)}

    return {
        "labels": labels,
        "data": data
    }

@app.get("/analytics/health")
def get_health_index(db: Session = Depends(lambda: next(get_db_session()))):
    # Core Health Index = (Total Vehicles - Vehicles with Maint in last 30d) / Total Vehicles
    total_vehicles = db.query(db_mod.Vehicle).count()
    if total_vehicles == 0:
        return {"health_index": 100, "detail": "No vehicles"}
        
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Count unique vehicles that had maintenance
    # distinct(MaintenanceLog.vehicle_id)
    unique_maint_vehicles = db.query(db_mod.MaintenanceLog.vehicle_id)\
        .filter(db_mod.MaintenanceLog.performed_date >= thirty_days_ago)\
        .distinct().count()
        
    healthy_vehicles = total_vehicles - unique_maint_vehicles
    health_index = int((healthy_vehicles / total_vehicles) * 100)
    
    return {
        "health_index": health_index,
        "total_vehicles": total_vehicles,
        "vehicles_in_shop_last_30d": unique_maint_vehicles
    }

@app.get("/analytics/cost-trend")
def get_cost_trend(period: str = "6M", db: Session = Depends(lambda: next(get_db_session()))):
    from collections import defaultdict
    
    # Periods: 1W, 1M, 3M, 6M, 1Y, ALL
    today = datetime.utcnow()
    start_date = today
    
    if period == "1W":
        start_date = today - timedelta(days=7)
        bucket_format = "%a" # Mon, Tue
        delta_step = timedelta(days=1)
        step_count = 7
    elif period == "1M":
        start_date = today - timedelta(days=30)
        bucket_format = "%d" # 01, 02 (Day of month)
        delta_step = timedelta(days=1)
        step_count = 30
    elif period == "3M":
        start_date = today - timedelta(days=90)
        bucket_format = "W%W" # Week number
        delta_step = timedelta(weeks=1)
        step_count = 12
    elif period == "1Y":
        start_date = today - timedelta(days=365)
        bucket_format = "%b" # Jan, Feb
        delta_step = timedelta(days=30)
        step_count = 12
    else: # 6M or default
        start_date = today - timedelta(days=180)
        bucket_format = "%b"
        delta_step = timedelta(days=30)
        step_count = 6
        
    logs = db.query(db_mod.MaintenanceLog).filter(db_mod.MaintenanceLog.performed_date >= start_date).all()
    
    # bucket
    data_map = defaultdict(float)
    
    # Pre-fill
    # This pre-fill logic is a bit simplistic for variable months but works for charts
    # A better way for pre-fill is iterating from start_date to today
    
    cursor = start_date
    labels = []
    
    # Generate labels strictly
    if period in ["1W", "1M"]:
        # Daily iteration
        curr = start_date
        while curr <= today:
            lbl = curr.strftime(bucket_format)
            data_map[lbl] = 0.0
            if lbl not in labels: labels.append(lbl)
            curr += timedelta(days=1)
    elif period == "3M":
         # Weekly iteration
        curr = start_date
        while curr <= today:
            lbl = curr.strftime(bucket_format)
            data_map[lbl] = 0.0
            if lbl not in labels: labels.append(lbl)
            curr += timedelta(days=7)           
    else:
        # Monthly iteration (approx)
        for i in range(step_count -1, -1, -1):
            d = today - (delta_step * i)
            lbl = d.strftime(bucket_format)
            data_map[lbl] = 0.0
            if lbl not in labels: labels.append(lbl)

    # Aggregate
    for log in logs:
        if log.performed_date:
            key = log.performed_date.strftime(bucket_format)
            data_map[key] += log.cost
            
    # Build result
    result_data = [data_map[lbl] for lbl in labels]
            
    return {
        "labels": labels,
        "data": result_data,
        "period": period
    }

@app.get("/analytics/export")
def export_logs_csv(db: Session = Depends(lambda: next(get_db_session()))):
    import csv
    from io import StringIO
    
    # Fetch all logs for export
    logs = db.query(db_mod.MaintenanceLog).options(
        joinedload(db_mod.MaintenanceLog.vehicle)
    ).order_by(db_mod.MaintenanceLog.performed_date.desc()).all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['ID', 'Vehicle', 'Task', 'Date', 'Cost', 'Mileage', 'Notes'])
    
    # Rows
    for log in logs:
        writer.writerow([
            log.id,
            log.vehicle.name if log.vehicle else "Unknown",
            log.task_name,
            log.performed_date.strftime("%Y-%m-%d"),
            f"{log.cost:.2f}",
            log.performed_at_mileage,
            log.notes or ""
        ])
        
    output.seek(0)
    
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=maintenance_logs_export.csv"
    return response

@app.get("/analytics/logs")
def get_global_logs(db: Session = Depends(lambda: next(get_db_session()))):
    # Fetch all logs, joined with Vehicle to get names
    logs = db.query(db_mod.MaintenanceLog).options(
        joinedload(db_mod.MaintenanceLog.vehicle)
    ).order_by(db_mod.MaintenanceLog.performed_date.desc()).all()
    
    # Custom serialization to include vehicle name
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "vehicle_id": log.vehicle_id,
            "vehicle_name": log.vehicle.name if log.vehicle else "Unknown",
            "task_name": log.task_name,
            "performed_date": log.performed_date,
            "cost": log.cost,
            "performed_at_mileage": log.performed_at_mileage
        })
    return result

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

@app.get("/auth/me")
def read_users_me(current_user: UserCreate = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        # Don't return password obviously
    }

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
    print(f"LOGIN ATTEMPT: {user.email}")
    
    # Check what DB we are actually using
    try:
        db_name = db.bind.url.database
        host = db.bind.url.host
        print(f"LOGIN DB: {host}/{db_name}")
    except:
        print("LOGIN DB: Could not determine DB URL")

    db_user = db.query(db_mod.User).filter(db_mod.User.email == user.email).first()
    
    if not db_user:
        print("LOGIN FAIL: User not found in DB")
        raise HTTPException(status_code=401, detail="User not found")
        
    if not verify_password(user.password, db_user.hashed_password):
        print(f"LOGIN FAIL: Password mismatch for {user.email}")
        # print(f"  Input: {user.password}")
        # print(f"  Hash:  {db_user.hashed_password}")
        raise HTTPException(status_code=401, detail="Password mismatch")
    
    print("LOGIN SUCCESS")
    
    # Create Login Log
    try:
        log_entry = db_mod.LoginLog(
            user_id=db_user.id,
            email=db_user.email,
            login_time=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"Failed to create login log: {e}")
        # Don't fail the login just because logging failed

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
