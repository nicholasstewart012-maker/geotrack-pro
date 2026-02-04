import database as db_mod
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Security Config
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

app = FastAPI(title="Vehicle Maintenance API Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
