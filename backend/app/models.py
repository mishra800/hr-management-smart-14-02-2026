"""
Consolidated SQLAlchemy ORM Models for HR Management System
This file contains all database table models merged from models_orm.py and models_v2.py
Date: 2026-02-16
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Float, Text, Time, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .database import Base

# ============================================
# CORE MODELS - User & Employee
# ============================================

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
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
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String)
    last_name = Column(String)
    employee_id = Column(String, unique=True, index=True, nullable=True)
    department = Column(String)
    position = Column(String)
    date_of_joining = Column(Date)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)
    pan_number = Column(String, nullable=True)
    aadhaar_number = Column(String, nullable=True)
    profile_summary = Column(Text, nullable=True)
    wfh_status = Column(String, default="office")
    is_immediate_joiner = Column(Boolean, default=False)
    onboarding_status = Column(String, default="initiated")
    it_setup_status = Column(String, default="pending")
    
    # Relationships
    user = relationship("User", back_populates="employees")
    attendance_records = relationship("Attendance", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    asset_requests = relationship("AssetRequest", back_populates="employee")
    documents = relationship("EmployeeDocument", back_populates="employee")
    onboarding_tasks = relationship("OnboardingTask", back_populates="employee")

# ============================================
# ATTENDANCE MODELS
# ============================================

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = {'extend_existing': True}
    
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
    
    # Relationships
    attendance = relationship("Attendance")
    employee = relationship("Employee")
    approver = relationship("User", foreign_keys=[approved_by])

# ============================================
# LEAVE MANAGEMENT MODELS
# ============================================

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    __table_args__ = {'extend_existing': True}
    
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

# ============================================
# ANNOUNCEMENT MODELS
# ============================================

class Announcement(Base):
    __tablename__ = "announcements"
    __table_args__ = {'extend_existing': True}
    
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
# ASSET MANAGEMENT MODELS
# ============================================

class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String, unique=True, nullable=True)
    asset_type = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="available")
    assigned_to = Column(Integer, ForeignKey("employees.id"), nullable=True)
    purchase_date = Column(Date, nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    
    # Relationships
    assignee = relationship("Employee")

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
    
    # Relationships
    employee = relationship("Employee", back_populates="asset_requests")
    fulfiller = relationship("User", foreign_keys=[fulfilled_by])

class AssetAcknowledgment(Base):
    __tablename__ = "asset_acknowledgments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    infrastructure_request_id = Column(Integer, ForeignKey("infrastructure_requests.id"), nullable=True)
    employee_name = Column(String, nullable=False)
    employee_id_number = Column(String, nullable=False)
    department = Column(String, nullable=False)
    date_of_joining = Column(DateTime, nullable=False)
    laptop_received = Column(Boolean, default=False)
    laptop_serial_number = Column(String, nullable=True)
    laptop_model = Column(String, nullable=True)
    laptop_condition = Column(String, nullable=True)
    email_received = Column(Boolean, default=False)
    email_address = Column(String, nullable=True)
    email_password_received = Column(Boolean, default=False)
    wifi_access_received = Column(Boolean, default=False)
    wifi_credentials_received = Column(Boolean, default=False)
    id_card_received = Column(Boolean, default=False)
    id_card_number = Column(String, nullable=True)
    biometric_setup_completed = Column(Boolean, default=False)
    biometric_type = Column(String, nullable=True)
    monitor_received = Column(Boolean, default=False)
    monitor_serial_number = Column(String, nullable=True)
    keyboard_received = Column(Boolean, default=False)
    mouse_received = Column(Boolean, default=False)
    headset_received = Column(Boolean, default=False)
    mobile_received = Column(Boolean, default=False)
    mobile_number = Column(String, nullable=True)
    system_login_working = Column(Boolean, default=False)
    email_login_working = Column(Boolean, default=False)
    vpn_access_working = Column(Boolean, default=False)
    employee_signature = Column(String, default="Digital Confirmation")
    employee_comments = Column(Text, nullable=True)
    issues_reported = Column(Text, nullable=True)
    additional_requirements = Column(Text, nullable=True)
    status = Column(String, default="submitted")
    review_status = Column(String, default="pending")
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    admin_comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    acknowledgment_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")
    reviewer = relationship("User", foreign_keys=[reviewed_by])

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
    
    # Relationships
    employee = relationship("Employee")
    asset = relationship("Asset")
    resolver = relationship("User", foreign_keys=[resolved_by])

# ============================================
# INFRASTRUCTURE MODELS
# ============================================

class InfrastructureRequest(Base):
    __tablename__ = "infrastructure_requests"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    request_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    priority = Column(String, default="normal")
    status = Column(String, default="pending")
    requested_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    laptop_provided = Column(Boolean, default=False)
    email_setup_completed = Column(Boolean, default=False)
    wifi_setup_completed = Column(Boolean, default=False)
    id_card_provided = Column(Boolean, default=False)
    biometric_setup_completed = Column(Boolean, default=False)
    email_address_created = Column(String, nullable=True)
    id_card_number = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")
    assignee = relationship("User", foreign_keys=[assigned_to])

# ============================================
# PAYROLL MODELS
# ============================================

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
    
    # Relationships
    employee = relationship("Employee")

# Alias for backward compatibility
Payroll = SalaryStructure

# ============================================
# MEETING ROOM MODELS
# ============================================

class MeetingRoom(Base):
    __tablename__ = "meeting_rooms"
    __table_args__ = {'extend_existing': True}
    
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
    
    # Relationships
    room = relationship("MeetingRoom", back_populates="bookings")
    organizer = relationship("User")

# ============================================
# MEETING MODELS (Standalone Meetings)
# ============================================

class Meeting(Base):
    __tablename__ = "meetings"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    meeting_date = Column(Date, nullable=False)
    start_time = Column(String, nullable=False)  # Format: "HH:MM"
    end_time = Column(String, nullable=False)    # Format: "HH:MM"
    location = Column(String, nullable=True)
    meeting_link = Column(String, nullable=True)
    meeting_type = Column(String, default="meeting")
    agenda = Column(Text, nullable=True)
    status = Column(String, default="scheduled")  # scheduled, in-progress, completed, cancelled
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    attendees = relationship("MeetingAttendee", back_populates="meeting", cascade="all, delete-orphan")
    notes = relationship("MeetingNote", back_populates="meeting", cascade="all, delete-orphan")
    action_items = relationship("MeetingActionItem", back_populates="meeting", cascade="all, delete-orphan")

class MeetingAttendee(Base):
    __tablename__ = "meeting_attendees"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="invited")  # invited, accepted, declined, tentative
    joined_at = Column(DateTime, nullable=True)
    left_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="attendees")
    user = relationship("User")

class MeetingNote(Base):
    __tablename__ = "meeting_notes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    note_type = Column(String, default="general")  # general, action-item, decision, follow-up
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="notes")
    creator = relationship("User")

class MeetingActionItem(Base):
    __tablename__ = "meeting_action_items"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")  # pending, in-progress, completed, cancelled
    priority = Column(String, default="medium")  # low, medium, high, urgent
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="action_items")
    assignee = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])

# ============================================
# DOCUMENT MODELS
# ============================================

class EmployeeDocument(Base):
    __tablename__ = "employee_documents"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    document_type = Column(String)
    document_name = Column(String, nullable=True)
    document_url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    uploaded_date = Column(DateTime, default=datetime.utcnow)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_date = Column(DateTime, nullable=True)
    ocr_confidence = Column(Float, default=0.0)
    rejection_reason = Column(String, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    verifier = relationship("User", foreign_keys=[verified_by])

# ============================================
# LEARNING & DEVELOPMENT MODELS
# ============================================

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
    
    # Relationships
    creator = relationship("User")

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
    
    # Relationships
    employee = relationship("Employee")
    module = relationship("LearningModule")

# ============================================
# ENGAGEMENT MODELS
# ============================================

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
    
    # Relationships
    creator = relationship("User")

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    responses = Column(JSON, default={})
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    survey = relationship("Survey")
    employee = relationship("Employee")

# ============================================
# ONBOARDING MODELS
# ============================================

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
    
    # Relationships
    employee = relationship("Employee", back_populates="onboarding_tasks")
    assignee = relationship("User")

# ============================================
# PERFORMANCE MODELS
# ============================================

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    __table_args__ = {'extend_existing': True}
    
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
# RECRUITMENT MODELS
# ============================================

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

# Alias for backward compatibility
Job = JobPosting

class JobApplication(Base):
    __tablename__ = "job_applications"
    __table_args__ = {'extend_existing': True}
    
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

# Alias for backward compatibility
Application = JobApplication

# ============================================
# ADVANCED RECRUITMENT MODELS (from models_v2)
# ============================================

class TalentPool(Base):
    __tablename__ = "talent_pool"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=False)
    candidate_email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String)
    resume_url = Column(Text)
    skills = Column(JSONB, default=[])
    experience_years = Column(Integer)
    tags = Column(JSONB, default=[])
    source = Column(String)
    original_application_id = Column(Integer, ForeignKey("job_applications.id"))
    ai_fit_score = Column(Float, default=0.0)
    added_date = Column(DateTime, default=datetime.utcnow)
    last_contacted = Column(DateTime)
    status = Column(String, default="active")
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    original_application = relationship("JobApplication", foreign_keys=[original_application_id])
    creator = relationship("User", foreign_keys=[created_by])

class Agency(Base):
    __tablename__ = "agencies"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_person = Column(String)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    commission_percentage = Column(Float, default=10.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgencySubmission(Base):
    __tablename__ = "agency_submissions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    agency_id = Column(Integer, ForeignKey("agencies.id"))
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    job_id = Column(Integer, ForeignKey("job_postings.id"))
    submitted_date = Column(DateTime, default=datetime.utcnow)
    commission_amount = Column(Float)
    commission_paid = Column(Boolean, default=False)
    payment_date = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    agency = relationship("Agency")
    application = relationship("JobApplication")
    job = relationship("JobPosting")

# ============================================
# INTERVIEW MODELS
# ============================================

class InterviewerAvailability(Base):
    __tablename__ = "interviewer_availability"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    interviewer_id = Column(Integer, ForeignKey("users.id"))
    day_of_week = Column(Integer)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interviewer = relationship("User")

class Interview(Base):
    __tablename__ = "interviews"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    interviewer_id = Column(Integer, ForeignKey("users.id"))
    scheduled_time = Column(DateTime)
    meeting_link = Column(String, nullable=True)
    status = Column(String, default="scheduled")
    
    # Relationships
    application = relationship("JobApplication")
    interviewer = relationship("User")

class InterviewSlot(Base):
    __tablename__ = "interview_slots"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    slot_start = Column(DateTime, nullable=False)
    slot_end = Column(DateTime, nullable=False)
    is_booked = Column(Boolean, default=False)
    booked_by_application_id = Column(Integer, ForeignKey("job_applications.id"))
    meeting_link = Column(Text)
    meeting_platform = Column(String, default="zoom")
    calendar_event_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interview = relationship("Interview")
    application = relationship("JobApplication", foreign_keys=[booked_by_application_id])

class InterviewFeedbackTemplate(Base):
    __tablename__ = "interview_feedback_templates"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    questions = Column(JSONB, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User")

class InterviewFeedback(Base):
    __tablename__ = "interview_feedback"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    template_id = Column(Integer, ForeignKey("interview_feedback_templates.id"))
    responses = Column(JSONB, nullable=False)
    overall_rating = Column(Integer)
    recommendation = Column(String)
    notes = Column(Text)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interview = relationship("Interview")
    template = relationship("InterviewFeedbackTemplate")
    submitter = relationship("User")

class AIInterview(Base):
    __tablename__ = "ai_interviews"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    status = Column(String, default="pending")
    overall_score = Column(Float, default=0.0)
    emotional_tone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("JobApplication")
    logs = relationship("AIInterviewLog", back_populates="interview")

class AIInterviewLog(Base):
    __tablename__ = "ai_interview_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("ai_interviews.id"))
    question = Column(Text)
    candidate_response = Column(Text)
    ai_evaluation = Column(Text)
    score = Column(Float)
    sentiment = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interview = relationship("AIInterview", back_populates="logs")

# ============================================
# COLLABORATION MODELS
# ============================================

class ApplicationComment(Base):
    __tablename__ = "application_comments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    application = relationship("JobApplication")
    user = relationship("User")

class ApplicationStageHistory(Base):
    __tablename__ = "application_stage_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    from_stage = Column(String)
    to_stage = Column(String, nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("JobApplication")
    changer = relationship("User")

class CandidateCommunication(Base):
    __tablename__ = "candidate_communications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    type = Column(String)
    direction = Column(String)
    subject = Column(String)
    message = Column(Text)
    sent_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="sent")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("JobApplication")
    sender = relationship("User")

# ============================================
# BULK UPLOAD MODELS
# ============================================

class BulkUpload(Base):
    __tablename__ = "bulk_uploads"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"))
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    total_files = Column(Integer, default=0)
    successful_parses = Column(Integer, default=0)
    failed_parses = Column(Integer, default=0)
    status = Column(String, default="processing")
    error_log = Column(JSONB, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    job = relationship("JobPosting")
    uploader = relationship("User")

class BulkUploadFile(Base):
    __tablename__ = "bulk_upload_files"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    bulk_upload_id = Column(Integer, ForeignKey("bulk_uploads.id"))
    filename = Column(String)
    file_url = Column(Text)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    parse_status = Column(String, default="pending")
    parse_error = Column(Text)
    parsed_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bulk_upload = relationship("BulkUpload")
    application = relationship("JobApplication")

# ============================================
# NOTIFICATION MODELS
# ============================================

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}
    
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

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    whatsapp_enabled = Column(Boolean, default=False)
    phone_number = Column(String)
    whatsapp_number = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    subject = Column(String)
    message = Column(Text)
    status = Column(String, default="sent")
    error_message = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

# ============================================
# RBAC & AUDIT MODELS
# ============================================

class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    table_name = Column(String)
    record_id = Column(Integer)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

# ============================================
# ADDITIONAL MODELS
# ============================================

class LinkedInProfile(Base):
    __tablename__ = "linkedin_profiles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    linkedin_id = Column(String, unique=True)
    profile_url = Column(Text)
    profile_data = Column(JSONB)
    imported_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("JobApplication")

class ApplicationFormField(Base):
    __tablename__ = "application_form_fields"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"))
    field_name = Column(String, nullable=False)
    field_type = Column(String, nullable=False)
    field_label = Column(String, nullable=False)
    is_required = Column(Boolean, default=False)
    options = Column(JSONB)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("JobPosting")

class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    referred_by_employee_id = Column(Integer, ForeignKey("employees.id"))
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    referral_bonus_amount = Column(Float)
    bonus_paid = Column(Boolean, default=False)
    bonus_paid_date = Column(DateTime)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    referrer = relationship("Employee")
    application = relationship("JobApplication")

class SystemSetting(Base):
    __tablename__ = "system_settings"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, nullable=False, index=True)
    setting_value = Column(Text)
    description = Column(Text)
    category = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================
# END OF MODELS
# ============================================

# ============================================
# WFH & SHIFT MODELS
# ============================================

class Shift(Base):
    __tablename__ = "shifts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    shift_type = Column(String, default="morning")
    break_duration_minutes = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WFHRequest(Base):
    __tablename__ = "wfh_requests"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    request_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String, default="pending")
    manager_approval_email = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee")
    approver = relationship("User", foreign_keys=[approved_by])

# ============================================
# LEARNING ENROLLMENT MODEL
# ============================================

class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    course_id = Column(Integer, ForeignKey("learning_modules.id"))
    status = Column(String, default="enrolled")
    progress_percentage = Column(Integer, default=0)
    enrolled_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee")
    course = relationship("LearningModule")

# Alias for backward compatibility
Course = LearningModule

# ============================================
# END OF MODELS
# ============================================

# ============================================
# ONBOARDING ADDITIONAL MODELS
# ============================================

class OfferLetter(Base):
    __tablename__ = "offer_letters"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    content = Column(Text, nullable=False)
    status = Column(String, default="draft")
    generated_date = Column(DateTime, default=datetime.utcnow)
    sent_date = Column(DateTime, nullable=True)
    accepted_date = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee")

class InductionModule(Base):
    __tablename__ = "induction_modules"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    duration_minutes = Column(Integer, default=30)
    order = Column(Integer, default=0)
    is_mandatory = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================
# HOLIDAY MODEL
# ============================================

class Holiday(Base):
    __tablename__ = "holidays"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, default="national")
    is_optional = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================
# END OF ALL MODELS
# ============================================

# ============================================
# PAYROLL ADDITIONAL MODELS
# ============================================

class SalaryRevision(Base):
    __tablename__ = "salary_revisions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    previous_ctc = Column(Float)
    new_ctc = Column(Float)
    revision_date = Column(Date, nullable=False)
    reason = Column(Text)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")
    approver = relationship("User", foreign_keys=[approved_by])

# ============================================
# SKILLS MODELS
# ============================================

class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    proficiency = Column(String, default="beginner")
    years_of_experience = Column(Float, default=0.0)
    last_assessed = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")
    skill = relationship("Skill")

# ============================================
# ENGAGEMENT ADDITIONAL MODELS
# ============================================

class PulseSurvey(Base):
    __tablename__ = "pulse_surveys"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    mood = Column(String, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")

class Recognition(Base):
    __tablename__ = "recognitions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("employees.id"))
    message = Column(Text, nullable=False)
    category = Column(String, default="general")
    points = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("Employee", foreign_keys=[recipient_id])

class EngagementNotification(Base):
    __tablename__ = "engagement_notifications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class AnonymousFeedback(Base):
    __tablename__ = "anonymous_feedback"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    category = Column(String, default="general")
    sentiment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WellnessCheckin(Base):
    __tablename__ = "wellness_checkins"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    score = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")

class PhotoAlbum(Base):
    __tablename__ = "photo_albums"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User")

class PhotoGallery(Base):
    __tablename__ = "photo_gallery"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("photo_albums.id"))
    filename = Column(String, nullable=False)
    caption = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    album = relationship("PhotoAlbum")
    uploader = relationship("User")

class GameScore(Base):
    __tablename__ = "game_scores"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    game_type = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")

class TeamActivity(Base):
    __tablename__ = "team_activities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    activity_type = Column(String, default="general")
    scheduled_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    max_participants = Column(Integer, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User")

class ActivityParticipant(Base):
    __tablename__ = "activity_participants"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("team_activities.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    status = Column(String, default="registered")
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    activity = relationship("TeamActivity")
    employee = relationship("Employee")

# ============================================
# ASSESSMENT MODELS
# ============================================

class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, default=60)
    passing_score = Column(Float, default=70.0)
    questions = Column(JSONB, default=[])
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User")

class CandidateAssessment(Base):
    __tablename__ = "candidate_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    status = Column(String, default="pending")
    score = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # Relationships
    application = relationship("JobApplication")
    assessment = relationship("Assessment")

class ExamSession(Base):
    __tablename__ = "exam_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"))
    candidate_assessment_id = Column(Integer, ForeignKey("candidate_assessments.id"))
    session_token = Column(String, unique=True, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    answers = Column(JSONB, default={})
    
    # Relationships
    application = relationship("JobApplication")
    candidate_assessment = relationship("CandidateAssessment")

# ============================================
# MEETING ROOM BOOKING MODEL
# ============================================

class MeetingRoomBooking(Base):
    __tablename__ = "meeting_room_bookings"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("meeting_rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    attendee_count = Column(Integer, default=1)
    purpose = Column(Text, nullable=True)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    room = relationship("MeetingRoom")
    user = relationship("User")

# ============================================
# FINAL END OF ALL MODELS
# ============================================
