import os
import traceback
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional

# --- SAFE MODE STARTUP ---
# catch critical import errors (like database, jose, passlib)
try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    from pydantic import BaseModel
    from sqlalchemy.orm import Session
    from datetime import datetime, timedelta
    import database as db_mod
except Exception as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    error_trace = traceback.format_exc()
    
    # Create a fallback app just to report the error
    app = FastAPI(title="Safe Mode (Crash Reporter)")
    
    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
    def catch_all(path_name: str):
        return JSONResponse(
            status_code=500,
            content={
                "status": "CRITICAL_BOOT_FAILURE", 
                "detail": str(e), 
                "traceback": error_trace
            }
        )
    # Stop further execution - the fallback 'app' is now the ASGI app
    # We do NOT raise here, we just let the module finish loading with this 'app'
    print("STARTING IN SAFE MODE DUE TO CRITICAL ERROR")
    app_is_safe_mode = True

else:
    app_is_safe_mode = False
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    app = FastAPI(title="Vehicle Maintenance API Pro", root_path="/api")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for debugging
        allow_credentials=True,
        allow_methods=["*"],

# Debugging: Catch global exceptions to print traceback in logs
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_msg = "".join(traceback.format_exception(None, exc, exc.__traceback__))
        print(f"GLOBAL ERROR: {error_msg}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "traceback": error_msg},
        )

    @app.on_event("startup")
    async def startup_event():
        print("BACKEND STARTING UP...")
        try:
            from database import engine
            print(f"Database URL configured (Is None? {os.getenv('DATABASE_URL') is None})")
        except Exception as e:
            print(f"Startup Import Error: {e}")

    @app.get("/health")
    def health_check():
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

    @app.on_event("startup")
    def startup_seed():
        db = db_mod.SessionLocal()
        try:
            # Seed default admin if not exists
            admin_email = "admin@geotrack.pro"
            existing = db.query(db_mod.User).filter(db_mod.User.email == admin_email).first()
            if not existing:
                print(f"Seeding admin user: {admin_email}")
                hashed_pw = get_password_hash("password123")
                admin_user = db_mod.User(
                    email=admin_email, 
                    hashed_password=hashed_pw, 
                    full_name="Fleet Manager"
                )
                db.add(admin_user)
                db.commit()
        except Exception as e:
            print(f"Startup seed error: {e}")
        finally:
            db.close()

    # Pydantic Schemas
    from pydantic import BaseModel

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

    # Helpers
    def get_password_hash(password):
        return pwd_context.hash(password)

    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Endpoints
    @app.get("/vehicles", response_model=List[Vehicle])
    def read_vehicles(db: Session = Depends(db_mod.get_db)):
        return db.query(db_mod.Vehicle).all()

    @app.post("/vehicles", response_model=Vehicle)
    def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(db_mod.get_db)):
        db_vehicle = db_mod.Vehicle(**vehicle.dict())
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle

    @app.post("/schedules")
    def create_schedule(schedule: ScheduleCreate, db: Session = Depends(db_mod.get_db)):
        db_schedule = db_mod.MaintenanceSchedule(**schedule.dict())
        db.add(db_schedule)
        db.commit()
        return {"status": "success"}

    @app.get("/schedules/{vehicle_id}")
    def get_schedules(vehicle_id: int, db: Session = Depends(db_mod.get_db)):
        return db.query(db_mod.MaintenanceSchedule).filter(db_mod.MaintenanceSchedule.vehicle_id == vehicle_id).all()

    @app.post("/logs")
    def create_log(log: LogCreate, db: Session = Depends(db_mod.get_db)):
        db_log = db_mod.MaintenanceLog(**log.dict())
        db.add(db_log)
        
        # Update the schedule's last performed value
        # Simplified: finding the first matching schedule
        schedule = db.query(db_mod.MaintenanceSchedule).filter(
            db_mod.MaintenanceSchedule.vehicle_id == log.vehicle_id,
            db_mod.MaintenanceSchedule.task_name == log.task_name
        ).first()
        
        if schedule:
            schedule.last_performed_value = log.performed_at_mileage if schedule.tracking_type == "miles" else log.performed_at_hours
            schedule.last_performed_date = datetime.utcnow()
        
        db.commit()
        return {"status": "success"}

    @app.get("/logs/{vehicle_id}")
    def get_vehicle_logs(vehicle_id: int, db: Session = Depends(db_mod.get_db)):
        return db.query(db_mod.MaintenanceLog).filter(db_mod.MaintenanceLog.vehicle_id == vehicle_id).order_by(db_mod.MaintenanceLog.performed_date.desc()).all()

    @app.get("/analytics/cost")
    def get_cost_analytics(db: Session = Depends(db_mod.get_db)):
        logs = db.query(db_mod.MaintenanceLog).all()
        total = sum(log.cost for log in logs)
        return {"total_maintenance_cost": total, "count": len(logs)}

    @app.get("/settings/all")
    def get_all_settings(db: Session = Depends(db_mod.get_db)):
        settings_list = db.query(db_mod.Setting).all()
        return {s.key: s.value for s in settings_list}

    @app.post("/settings")
    def update_settings(settings: dict, db: Session = Depends(db_mod.get_db)):
        for key, value in settings.items():
            db_setting = db_mod.Setting(key=key, value=str(value))
            db.merge(db_setting)
        db.commit()
        return {"status": "success"}

    @app.post("/auth/register", response_model=Token)
    def register(user: UserCreate, db: Session = Depends(db_mod.get_db)):
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
    def login(user: UserCreate, db: Session = Depends(db_mod.get_db)):
        db_user = db.query(db_mod.User).filter(db_mod.User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        access_token = create_access_token(data={"sub": db_user.email})
        return {"access_token": access_token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
