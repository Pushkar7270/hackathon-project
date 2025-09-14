from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, date, timezone, timedelta
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
if not mongo_url or not db_name:
    raise RuntimeError("Missing MONGO_URL or DB_NAME in environment variables")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper functions
def prepare_for_mongo(data):
    """Convert date objects to MongoDB native date type"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = datetime.combine(value, datetime.min.time())
            elif isinstance(value, datetime):
                data[key] = value
    return data

def parse_from_mongo(item):
    """Parse MongoDB native date type back to date objects"""
    if isinstance(item, dict):
        for key, value in item.items():
            if key == 'date' and isinstance(value, datetime):
                item[key] = value.date()
    return item

# Models
class Teacher(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    teacher_id: str
    name: str
    password_hash: str

class TeacherLogin(BaseModel):
    teacher_id: str
    password: str

class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    name: str
    image_path: Optional[str] = None
    class_name: str = "Class 5"

class AttendanceRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    date: date
    status: str  # "present" or "absent"
    marked_by: str = "manual"  # "manual" or "face_recognition"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AttendanceCreate(BaseModel):
    student_id: str
    date: str  # ISO date string
    status: str

class AttendanceUpdate(BaseModel):
    attendance_records: List[AttendanceCreate]

class StudentWithAttendance(BaseModel):
    id: str
    student_id: str
    name: str
    image_path: Optional[str]
    class_name: str
    daily_attendance: bool
    monthly_percentage: float
    overall_percentage: float

class StudentStatus(BaseModel):
    id: str
    student_id: str
    name: str
    image_path: Optional[str]
    overall_percentage: float
    monthly_stats: Dict[str, int]
    absent_dates: List[str]

# Authentication functions
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

# Initialize default teacher
async def init_default_teacher():
    existing_teacher = await db.teachers.find_one({"teacher_id": "Ramandeep@singh"})
    if not existing_teacher:
        teacher = Teacher(
            teacher_id="Ramandeep@singh",
            name="Ramandeep Singh",
            password_hash=hash_password("456123")
        )
        await db.teachers.insert_one(teacher.model_dump())

# Initialize sample students
async def init_sample_students():
    students_data = [
        {"student_id": "STU001", "name": "Karandeep Singh", "image_path": "/karandeep.jpeg"},
        {"student_id": "STU002", "name": "Priya Kaur", "image_path": "/images/student2.jpg"},
        {"student_id": "STU003", "name": "Rajesh Kumar", "image_path": "/images/student3.jpg"},
        {"student_id": "STU004", "name": "Simran Dhillon", "image_path": "/images/student4.jpg"},
        {"student_id": "STU005", "name": "Harmanpreet Singh", "image_path": "/images/student5.jpg"}
    ]
    
    for student_data in students_data:
        existing = await db.students.find_one({"student_id": student_data["student_id"]})
        if not existing:
            student = Student(**student_data)
            await db.students.insert_one(student.model_dump())
    
    # Initialize sample attendance data for the past 30 days
    import random
    
    students = await db.students.find().to_list(100)
    base_date = date.today() - timedelta(days=30)
    
    for student in students:
        for i in range(30):
            attendance_date = base_date + timedelta(days=i)
            existing = await db.attendance.find_one({
                "student_id": student["student_id"],
                "date": datetime.combine(attendance_date, datetime.min.time())
            })
            
            if not existing:
                # 85% chance of being present
                status = "present" if random.random() < 0.85 else "absent"
                attendance = AttendanceRecord(
                    student_id=student["student_id"],
                    date=attendance_date,
                    status=status
                )
                attendance_dict = prepare_for_mongo(attendance.dict())
                await db.attendance.insert_one(attendance_dict)

# Routes
@api_router.post("/login")
async def login(login_data: TeacherLogin):
    teacher = await db.teachers.find_one({"teacher_id": login_data.teacher_id})
    if not teacher or not verify_password(login_data.password, teacher["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"success": True, "teacher_id": teacher["teacher_id"], "name": teacher["name"]}

@api_router.get("/students", response_model=List[Student])
async def get_students():
    students = await db.students.find().to_list(100)
    return [Student(**student) for student in students]

@api_router.get("/students/{student_id}/attendance")
async def get_student_attendance(student_id: str, date_filter: Optional[str] = None):
    query = {"student_id": student_id}
    if date_filter:
        query["date"] = datetime.fromisoformat(date_filter)
    
    attendance_records = await db.attendance.find(query).to_list(100)
    return [parse_from_mongo(record) for record in attendance_records]

@api_router.get("/attendance/{date_str}")
async def get_attendance_by_date(date_str: str):
    students = await db.students.find().to_list(100)
    result = []
    date_obj = datetime.fromisoformat(date_str)
    month_ago = date_obj - timedelta(days=30)
    
    for student in students:
        # Get attendance for specific date
        attendance = await db.attendance.find_one({
            "student_id": student["student_id"],
            "date": date_obj
        })
        
        # Monthly percentage (last 30 days)
        monthly_records = await db.attendance.find({
            "student_id": student["student_id"],
            "date": {"$gte": month_ago, "$lte": date_obj}
        }).to_list(100)
        
        monthly_present = len([r for r in monthly_records if r["status"] == "present"])
        monthly_total = len(monthly_records)
        monthly_percentage = (monthly_present / monthly_total * 100) if monthly_total > 0 else 0
        
        # Overall percentage (all time)
        overall_records = await db.attendance.find({
            "student_id": student["student_id"]
        }).to_list(1000)
        overall_present = len([r for r in overall_records if r["status"] == "present"])
        overall_total = len(overall_records)
        overall_percentage = (overall_present / overall_total * 100) if overall_total > 0 else 0
        
        student_attendance = StudentWithAttendance(
            id=student["id"],
            student_id=student["student_id"],
            name=student["name"],
            image_path=student.get("image_path"),
            class_name=student.get("class_name", "Class 5"),
            daily_attendance=attendance["status"] == "present" if attendance else False,
            monthly_percentage=round(monthly_percentage, 1),
            overall_percentage=round(overall_percentage, 1)
        )
        result.append(student_attendance)
    
    return result

@api_router.post("/attendance")
async def mark_attendance(attendance_data: AttendanceUpdate):
    try:
        for record in attendance_data.attendance_records:
            date_obj = datetime.fromisoformat(record.date)
            new_record = AttendanceRecord(
                student_id=record.student_id,
                date=date_obj.date(),
                status=record.status
            )
            record_dict = prepare_for_mongo(new_record.model_dump())
            await db.attendance.replace_one(
                {"student_id": record.student_id, "date": date_obj},
                record_dict,
                upsert=True
            )
        return {"success": True, "message": f"Updated attendance for {len(attendance_data.attendance_records)} students"}
    except Exception as e:
        logging.error(f"Error marking attendance: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark attendance")

@api_router.get("/student-status/{student_id}")
async def get_student_status(student_id: str):
    student = await db.students.find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all attendance records
    attendance_records = await db.attendance.find({"student_id": student_id}).to_list(1000)
    
    if not attendance_records:
        return StudentStatus(
            id=student["id"],
            student_id=student["student_id"],
            name=student["name"],
            image_path=student.get("image_path"),
            overall_percentage=0,
            monthly_stats={"present": 0, "absent": 0, "total": 0},
            absent_dates=[]
        )
    
    present_count = len([r for r in attendance_records if r["status"] == "present"])
    total_count = len(attendance_records)
    overall_percentage = (present_count / total_count * 100) if total_count > 0 else 0
    
    absent_dates = [r["date"].isoformat() if isinstance(r["date"], datetime) else str(r["date"]) for r in attendance_records if r["status"] == "absent"]
    
    return StudentStatus(
        id=student["id"],
        student_id=student["student_id"],
        name=student["name"],
        image_path=student.get("image_path"),
        overall_percentage=round(overall_percentage, 1),
        monthly_stats={
            "present": present_count,
            "absent": total_count - present_count,
            "total": total_count
        },
        absent_dates=absent_dates
    )

# External API for face recognition system
@api_router.post("/external/mark-attendance")
async def external_mark_attendance(student_id: str, status: str = "present"):
    """API endpoint for external face recognition system to mark attendance"""
    try:
        today = datetime.combine(date.today(), datetime.min.time())
        record = AttendanceRecord(
            student_id=student_id,
            date=today.date(),
            status=status,
            marked_by="face_recognition"
        )
        record_dict = prepare_for_mongo(record.dict())
        await db.attendance.replace_one(
            {"student_id": student_id, "date": today},
            record_dict,
            upsert=True
        )
        return {"success": True, "message": f"Attendance marked for {student_id}"}
    except Exception as e:
        logging.error(f"Error in external mark attendance: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark attendance externally")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@app.on_event("startup")
async def lifespan():
    await init_default_teacher()
    await init_sample_students()
    logger.info("Application startup complete")