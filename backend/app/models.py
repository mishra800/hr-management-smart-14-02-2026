# Simplified models - Pydantic models for API validation
# No database models for now - will be implemented later

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum

# Status Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    EMPLOYEE = "employee"
    CANDIDATE = "candidate"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    LATE = "late"

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class ShiftType(str, Enum):
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"
    FLEXIBLE = "flexible"

# Shift Model
class ShiftBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    shift_type: ShiftType = ShiftType.MORNING
    break_duration_minutes: int = 60

class ShiftCreate(ShiftBase):
    pass

class Shift(ShiftBase):
    id: int
    
    class Config:
        from_attributes = True

# WFH Request Model
class WFHRequestBase(BaseModel):
    employee_id: int
    date: date
    reason: str
    manager_approval_email: bool = False

class WFHRequestCreate(WFHRequestBase):
    pass

class WFHRequest(WFHRequestBase):
    id: int
    status: str = "pending"
    created_at: datetime
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Basic Pydantic Models for API validation
class UserBase(BaseModel):
    email: str
    role: UserRole = UserRole.EMPLOYEE
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    department: str
    position: str
    date_of_joining: datetime
    date_of_birth: Optional[datetime] = None
    wedding_anniversary_date: Optional[datetime] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    profile_summary: Optional[str] = None
    profile_image_url: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    user_id: int

class Employee(EmployeeBase):
    id: int
    user_id: int
    profile_completion_percentage: int = 0
    
    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    employee_id: int
    date: datetime
    status: AttendanceStatus
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None
    location_address: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    
    class Config:
        from_attributes = True

class LeaveRequestBase(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    duration_days: int = 1

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveRequest(LeaveRequestBase):
    id: int
    status: LeaveStatus = LeaveStatus.PENDING
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnnouncementBase(BaseModel):
    title: str
    content: str
    priority: str = "normal"
    category: str = "general"

class AnnouncementCreate(AnnouncementBase):
    posted_by: int

class Announcement(AnnouncementBase):
    id: int
    posted_by: int
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

class AssetBase(BaseModel):
    name: str
    type: str
    serial_number: str
    status: str = "available"
    specifications: Optional[Dict[str, Any]] = None
    location: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    assigned_to: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response models for API endpoints
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class DashboardStats(BaseModel):
    total_employees: int
    present_today: int
    on_leave: int
    pending_requests: int


# ============================================
# SQLALCHEMY ORM MODELS (for database tables)
# ============================================

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Float, Text, JSON
from sqlalchemy.orm import relationship
from .database import Base

# Import datetime if not already imported
try:
    from datetime import datetime
except:
    pass

# Asset Request Model
class AssetRequest(Base):
    __tablename__ = "asset_requests"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    asset_type = Column(String)
    description = Column(Text)
    priority = Column(String, default="normal")
    status = Column(String, default="pending")
    requested_date = Column(DateTime, default=datetime.utcnow)
    fulfilled_date = Column(DateTime, nullable=True)
    fulfilled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

# Infrastructure Request Model
class InfrastructureRequest(Base):
    __tablename__ = "infrastructure_requests"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    request_type = Column(String)
    description = Column(Text)
    priority = Column(String, default="normal")
    status = Column(String, default="pending")
    requested_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)

# Salary Structure Model
class SalaryStructure(Base):
    __tablename__ = "payroll"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    basic_salary = Column(Float)
    hra = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    other_allowances = Column(Float, default=0.0)
    gross_salary = Column(Float)
    tax_deductions = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    net_salary = Column(Float)
    payment_month = Column(String)
    payment_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

# Meeting Room Model
class MeetingRoom(Base):
    __tablename__ = "meeting_rooms"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    capacity = Column(Integer)
    location = Column(String)
    amenities = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)

# Meeting Booking Model
class MeetingBooking(Base):
    __tablename__ = "meeting_bookings"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("meeting_rooms.id"))
    booked_by = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    attendees = Column(JSON, default=[])
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)

# Employee Document Model
class EmployeeDocument(Base):
    __tablename__ = "employee_documents"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    document_type = Column(String)
    document_name = Column(String)
    file_path = Column(String)
    uploaded_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_date = Column(DateTime, nullable=True)

# Learning Module Model
class LearningModule(Base):
    __tablename__ = "learning_modules"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    content_url = Column(String, nullable=True)
    duration_minutes = Column(Integer)
    category = Column(String)
    is_mandatory = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

# Learning Progress Model
class LearningProgress(Base):
    __tablename__ = "learning_progress"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    module_id = Column(Integer, ForeignKey("learning_modules.id"))
    status = Column(String, default="not_started")
    progress_percentage = Column(Integer, default=0)
    started_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)

# Survey Model
class Survey(Base):
    __tablename__ = "surveys"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    questions = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    closes_at = Column(DateTime, nullable=True)

# Survey Response Model
class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    responses = Column(JSON, default={})
    submitted_at = Column(DateTime, default=datetime.utcnow)

# Onboarding Task Model
class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    task_name = Column(String)
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="pending")
    due_date = Column(Date, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    priority = Column(String, default="normal")
    category = Column(String, nullable=True)

# Attendance Correction Model
class AttendanceCorrection(Base):
    __tablename__ = "attendance_corrections"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, ForeignKey("attendance.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    correction_type = Column(String)
    original_value = Column(String)
    corrected_value = Column(String)
    reason = Column(Text)
    status = Column(String, default="pending")
    requested_date = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_date = Column(DateTime, nullable=True)

# Job Posting Model (for career module)
class JobPosting(Base):
    __tablename__ = "job_postings"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    department = Column(String)
    location = Column(String)
    posted_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    required_skills = Column(JSON, default=[])
    min_experience_years = Column(Integer, nullable=True)
    max_experience_years = Column(Integer, nullable=True)


# Additional missing models
class AssetComplaint(Base):
    __tablename__ = "asset_complaints"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    complaint_type = Column(String)
    description = Column(Text)
    priority = Column(String, default="normal")
    status = Column(String, default="open")
    reported_date = Column(DateTime, default=datetime.utcnow)
    resolved_date = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)

# Alias for Payroll (same as SalaryStructure)
Payroll = SalaryStructure

# Alias for Job (same as JobPosting)
Job = JobPosting
