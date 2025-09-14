from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, date, timezone
import hashlib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

# Helper functions
def prepare_for_mongo(data):
    """Convert date objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Parse ISO strings back to date objects from MongoDB"""
    if isinstance(item, dict):
        for key, value in item.items():
            if key == 'date' and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value).date()
                except:
                    pass
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
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

# Initialize default teacher
async def init_default_teacher():
    existing_teacher = await db.teachers.find_one({"teacher_id": "abcd@"})
    if not existing_teacher:
        teacher = Teacher(
            teacher_id="abcd@",
            name="Default Teacher",
            password_hash=hash_password("1234")
        )
        await db.teachers.insert_one(teacher.dict())

# Initialize sample students
async def init_sample_students():
    students_data = [
        {"student_id": "STU001", "name": "Arjun Singh", "image_path": "/images/student1.jpg"},
        {"student_id": "STU002", "name": "Priya Kaur", "image_path": "/images/student2.jpg"},
        {"student_id": "STU003", "name": "Rajesh Kumar", "image_path": "/images/student3.jpg"},
        {"student_id": "STU004", "name": "Simran Dhillon", "image_path": "/images/student4.jpg"},
        {"student_id": "STU005", "name": "Harmanpreet Singh", "image_path": "/images/student5.jpg"}
    ]
    
    for student_data in students_data:
        existing = await db.students.find_one({"student_id": student_data["student_id"]})
        if not existing:
            student = Student(**student_data)
            await db.students.insert_one(student.dict())
    
    # Initialize sample attendance data for the past 30 days
    import random
    from datetime import timedelta
    
    students = await db.students.find().to_list(100)
    base_date = date.today() - timedelta(days=30)
    
    for student in students:
        for i in range(30):
            attendance_date = base_date + timedelta(days=i)
            existing = await db.attendance.find_one({
                "student_id": student["student_id"],
                "date": attendance_date.isoformat()
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
        query["date"] = date_filter
    
    attendance_records = await db.attendance.find(query).to_list(100)
    return [parse_from_mongo(record) for record in attendance_records]

@api_router.get("/attendance/{date_str}")
async def get_attendance_by_date(date_str: str):
    students = await db.students.find().to_list(100)
    result = []
    
    for student in students:
        # Get attendance for specific date
        attendance = await db.attendance.find_one({
            "student_id": student["student_id"],
            "date": date_str
        })
        
        # Calculate monthly percentage (last 30 days)
        monthly_records = await db.attendance.find({
            "student_id": student["student_id"]
        }).to_list(100)
        
        monthly_present = len([r for r in monthly_records if r["status"] == "present"])
        monthly_total = len(monthly_records)
        monthly_percentage = (monthly_present / monthly_total * 100) if monthly_total > 0 else 0
        
        # Calculate overall percentage (all time)
        overall_percentage = monthly_percentage  # For demo, using same as monthly
        
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
            # Delete existing record for this student and date
            await db.attendance.delete_one({
                "student_id": record.student_id,
                "date": record.date
            })
            
            # Insert new record
            new_record = AttendanceRecord(
                student_id=record.student_id,
                date=datetime.fromisoformat(record.date).date(),
                status=record.status
            )
            record_dict = prepare_for_mongo(new_record.dict())
            await db.attendance.insert_one(record_dict)
        
        return {"success": True, "message": f"Updated attendance for {len(attendance_data.attendance_records)} students"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/student-status/{student_id}")
async def get_student_status(student_id: str):
    student = await db.students.find_one({"student_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all attendance records
    attendance_records = await db.attendance.find({"student_id": student_id}).to_list(100)
    
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
    
    absent_dates = [r["date"] for r in attendance_records if r["status"] == "absent"]
    
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
        today = date.today()
        
        # Delete existing record for today
        await db.attendance.delete_one({
            "student_id": student_id,
            "date": today.isoformat()
        })
        
        # Insert new record
        record = AttendanceRecord(
            student_id=student_id,
            date=today,
            status=status,
            marked_by="face_recognition"
        )
        record_dict = prepare_for_mongo(record.dict())
        await db.attendance.insert_one(record_dict)
        
        return {"success": True, "message": f"Attendance marked for {student_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.on_event("startup")
async def startup_event():
    await init_default_teacher()
    await init_sample_students()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()