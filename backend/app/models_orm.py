"""
SQLAlchemy ORM Models for HR Management System
This file contains all database table models
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Float, Text, Time, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .database import Base

# ============================================
# CORE MODELS
# ============================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="employee")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employees = relationship("Employee", back_populates="user")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String)
    last_name = Column(String)
    employee_id = Column(String, unique=True, index=True)
    department = Column(String)
    position = Column(String)
    date_of_joining = Column(Date)
    phone = Column(String)
    address = Column(Text)
    emergency_contact = Column(String)
    profile_image_url = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="employees")
    attendance_records = relationship("Attendance", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    asset_requests = relationship("AssetRequest", back_populates="employee")
    documents = relationship("EmployeeDocument", back_populates="employee")
    onboarding_tasks = relationship("OnboardingTask", back_populates="employee")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    check_in = Column(DateTime)
    check_out = Column(DateTime, nullable=True)
    status = Column(String, default="present")
    work_hours = Column(Float, default=0.0)
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    leave_type = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    reason = Column(Text)
    status = Column(String, default="pending")
    applied_date = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_requests")
    approver = relationship("User", foreign_keys=[approved_by])

class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    priority = Column(String, default="normal")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    creator = relationship("User")

# ============================================
# ASSET MANAGEMENT
# ============================================

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String, unique=True)
    asset_type = Column(String)
    description = Column(Text)
    status = Column(String, default="available")
    assigned_to = Column(Integer, ForeignKey("employees.id"), nullable=True)
    purchase_date = Column(Date, nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    
    # Relationships
    assignee = relationship("Employee")

class AssetRequest(Base):
    __tablename__ = "asset_requests"
    
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
    
    # Relationships
    employee = relationship("Employee", back_populates="asset_requests")
    fulfiller = relationship("User", foreign_keys=[fulfilled_by])

class AssetAcknowledgment(Base):
    __tablename__ = "asset_acknowledgments"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    acknowledged_date = Column(DateTime, default=datetime.utcnow)
    signature_url = Column(String, nullable=True)
    terms_accepted = Column(Boolean, default=False)
    
    # Relationships
    employee = relationship("Employee")
    asset = relationship("Asset")

# ============================================
# INFRASTRUCTURE & IT
# ============================================

class InfrastructureRequest(Base):
    __tablename__ = "infrastructure_requests"
    
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
    
    # Relationships
    employee = relationship("Employee")
    assignee = relationship("User", foreign_keys=[assigned_to])

# ============================================
# PAYROLL
# ============================================

class SalaryStructure(Base):
    __tablename__ = "payroll"
    
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
    
    # Relationships
    employee = relationship("Employee")

# ============================================
# MEETINGS
# ============================================

class MeetingRoom(Base):
    __tablename__ = "meeting_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    capacity = Column(Integer)
    location = Column(String)
    amenities = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    
    # Relationships
    bookings = relationship("MeetingBooking", back_populates="room")

class MeetingBooking(Base):
    __tablename__ = "meeting_bookings"
    
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
    
    # Relationships
    room = relationship("MeetingRoom", back_populates="bookings")
    organizer = relationship("User")

# ============================================
# DOCUMENTS
# ============================================

class EmployeeDocument(Base):
    __tablename__ = "employee_documents"
    
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
    
    # Relationships
    employee = relationship("Employee", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    verifier = relationship("User", foreign_keys=[verified_by])

# ============================================
# LEARNING & DEVELOPMENT
# ============================================

class LearningModule(Base):
    __tablename__ = "learning_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    content_url = Column(String, nullable=True)
    duration_minutes = Column(Integer)
    category = Column(String)
    is_mandatory = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User")

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    module_id = Column(Integer, ForeignKey("learning_modules.id"))
    status = Column(String, default="not_started")
    progress_percentage = Column(Integer, default=0)
    started_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)
    
    # Relationships
    employee = relationship("Employee")
    module = relationship("LearningModule")

# ============================================
# ENGAGEMENT
# ============================================

class Survey(Base):
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    questions = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    closes_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User")

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    responses = Column(JSON, default={})
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    survey = relationship("Survey")
    employee = relationship("Employee")

# ============================================
# ONBOARDING
# ============================================

class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"
    
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
    
    # Relationships
    employee = relationship("Employee", back_populates="onboarding_tasks")
    assignee = relationship("User")

# ============================================
# ATTENDANCE EXTENSIONS
# ============================================

class AttendanceCorrection(Base):
    __tablename__ = "attendance_corrections"
    
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
    
    # Relationships
    attendance = relationship("Attendance")
    employee = relationship("Employee")
    approver = relationship("User", foreign_keys=[approved_by])

# ============================================
# PERFORMANCE
# ============================================

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    review_period = Column(String)
    rating = Column(Float)
    comments = Column(Text)
    goals = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")
    reviewer = relationship("User")

# ============================================
# RECRUITMENT
# ============================================

class JobPosting(Base):
    __tablename__ = "job_postings"
    
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

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"))
    candidate_name = Column(String)
    candidate_email = Column(String)
    resume_url = Column(String)
    status = Column(String, default="applied")
    applied_date = Column(DateTime, default=datetime.utcnow)
    ai_fit_score = Column(Float, default=0.0)
    
    # Relationships
    job_posting = relationship("JobPosting")

# ============================================
# NOTIFICATIONS
# ============================================

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    type = Column(String, default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    link = Column(String, nullable=True)
    
    # Relationships
    recipient = relationship("User")
