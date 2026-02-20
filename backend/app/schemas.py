# Simplified schemas - Basic Pydantic models for API validation
# No complex database relationships for now

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel, EmailStr, validator
from enum import Enum

# Basic API Response
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# Enums for better validation
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    ASSETS_TEAM = "assets_team"
    CANDIDATE = "candidate"

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    PENDING_HR = "pending_hr"
    ESCALATED = "escalated"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    WFH = "wfh"
    ON_LEAVE = "on_leave"

# Auth Schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.EMPLOYEE
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None

class TokenRefresh(BaseModel):
    refresh_token: str

# Employee Schemas
class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    department: str
    position: str
    phone: Optional[str] = None
    manager_id: Optional[int] = None
    joining_date: Optional[date] = None
    gender: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and len(v) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v and v.lower() not in ['male', 'female']:
            raise ValueError('Gender must be either "male" or "female"')
        return v.lower() if v else v

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    manager_id: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    wedding_anniversary_date: Optional[date] = None
    
    @validator('gender')
    def validate_gender(cls, v):
        if v and v.lower() not in ['male', 'female']:
            raise ValueError('Gender must be either "male" or "female"')
        return v.lower() if v else v

class EmployeeBulkImport(BaseModel):
    employees: List[EmployeeCreate]
    validate_emails: bool = True
    send_welcome_emails: bool = False

# Attendance Schemas
class AttendanceCreate(BaseModel):
    status: AttendanceStatus
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_base64: Optional[str] = None
    work_mode: Optional[str] = "office"  # office, wfh, client_site
    notes: Optional[str] = None

class AttendanceUpdate(BaseModel):
    check_out: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None

class AttendanceQuery(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    employee_id: Optional[int] = None
    status: Optional[AttendanceStatus] = None
    department: Optional[str] = None

# Leave Schemas
class LeaveRequestCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    is_half_day: Optional[bool] = False
    half_day_period: Optional[str] = None  # morning, afternoon
    emergency: Optional[bool] = False
    medical_certificate: Optional[str] = None  # base64 encoded file
    manager_email_approval: Optional[str] = None  # for emergency cases
    contact_number: Optional[str] = None  # Emergency contact
    alternate_contact: Optional[str] = None  # Alternate emergency contact
    medical_reason_details: Optional[str] = None  # For sick leave
    family_member_relation: Optional[str] = None  # For bereavement leave
    expected_delivery_date: Optional[date] = None  # For maternity leave
    child_number: Optional[int] = None  # For maternity leave (1st, 2nd child)
    adoption_date: Optional[date] = None  # For adoption maternity leave
    bl_occasion_type: Optional[str] = None  # For Birthday/Anniversary leave: "birthday" or "anniversary"
    # New fields for enhanced maternity/paternity leave
    pregnancy_stage: Optional[str] = None  # "after_7_months" or "after_childbirth" for maternity leave
    child_birth_date: Optional[date] = None  # For paternity leave - when child was born
    spouse_name: Optional[str] = None  # For paternity leave
    hospital_name: Optional[str] = None  # For maternity/paternity leave
    doctor_certificate: Optional[str] = None  # Medical certificate from doctor
    advance_notice_days: Optional[int] = None  # Number of days in advance the request is made

class LeaveRequestApproval(BaseModel):
    status: str  # approved, rejected, pending_hr, escalated
    comments: Optional[str] = None
    hr_comments: Optional[str] = None
    manager_id: Optional[int] = None
    hr_id: Optional[int] = None
    approval_level: Optional[str] = None  # manager, hr, admin
    requires_hr_review: Optional[bool] = False

class LeaveBalance(BaseModel):
    employee_id: int
    leave_type: str
    total_allocated: float
    used: float
    balance: float
    year: int
    carry_forward: Optional[float] = 0.0
    encashable: Optional[float] = 0.0
    pro_rata_calculation: Optional[bool] = False

class LeaveType(BaseModel):
    code: str
    name: str
    max_days_per_year: float
    max_consecutive_days: int
    applicable_to: List[str]
    gender_specific: Optional[str] = None
    requires_medical_certificate: bool = False
    carry_forward: bool = False
    encashable: bool = False
    rules: Optional[str] = None

class Holiday(BaseModel):
    id: int
    name: str
    date: date
    type: str  # national, regional, company
    is_optional: bool = False
    description: Optional[str] = None

class WFHRequest(BaseModel):
    date: date
    reason: str
    manager_approval_email: Optional[str] = None
    is_emergency: Optional[bool] = False
    medical_certificate: Optional[str] = None  # For medical emergencies

class LeaveAnalytics(BaseModel):
    total_requests: int
    approved_requests: int
    rejected_requests: int
    pending_requests: int
    most_used_leave_type: str
    average_leave_duration: float
    department_wise_stats: Dict[str, Any]
    monthly_trends: List[Dict[str, Any]]

class BulkLeaveApproval(BaseModel):
    leave_request_ids: List[int]
    action: str  # approve, reject
    comments: Optional[str] = None
    hr_comments: Optional[str] = None

class LeaveEncashmentRequest(BaseModel):
    leave_type: str
    days_to_encash: float
    reason: str
    financial_year: int

class LeaveCarryForwardRequest(BaseModel):
    leave_type: str
    days_to_carry: float
    reason: str
    manager_approval: bool = False

class LeaveType(BaseModel):
    id: int
    name: str
    code: str
    max_days_per_year: float
    max_consecutive_days: Optional[int] = None
    requires_medical_certificate: Optional[bool] = False
    applicable_to: List[str] = ["probationary", "permanent"]  # employee types
    carry_forward: Optional[bool] = False
    encashable: Optional[bool] = False

class Holiday(BaseModel):
    id: int
    name: str
    date: date
    type: str  # national, state, company
    is_optional: Optional[bool] = False

class WFHRequest(BaseModel):
    date: date
    reason: str
    manager_approval_email: Optional[bool] = False

class EmergencyLeaveRequest(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    emergency_type: str
    manager_email_approval: Optional[bool] = False
    medical_certificate: Optional[bool] = False
    contact_number: str
    emergency_contact: Optional[str] = None

class LeaveAnalytics(BaseModel):
    total_leave_requests: int
    approved_requests: int
    rejected_requests: int
    pending_requests: int
    approval_rate: float
    average_leave_duration: float
    most_common_leave_type: str
    peak_leave_months: List[str]

class BulkApprovalRequest(BaseModel):
    request_ids: List[int]
    action: str  # approve or reject
    comments: Optional[str] = None

class LeavePolicy(BaseModel):
    grace_period_minutes: int = 15
    max_grace_periods_per_month: int = 3
    office_start_time: time
    office_end_time: time
    lunch_break_start: time
    lunch_break_end: time
    minimum_half_day_hours: int = 5
    minimum_full_day_hours: int = 9

# Maternity/Paternity Leave Schemas
class MaternityLeaveRequest(BaseModel):
    expected_delivery_date: date
    requested_start_date: date
    leave_type: str = "maternity"  # "pre_delivery" or "post_delivery"
    medical_certificate_url: Optional[str] = None
    doctor_name: str
    hospital_name: str
    reason: Optional[str] = None
    emergency_contact_name: str
    emergency_contact_number: str

class PaternityLeaveRequest(BaseModel):
    child_birth_date: date
    requested_start_date: date
    requested_end_date: date
    medical_certificate_url: Optional[str] = None
    hospital_name: str
    reason: Optional[str] = None

class MaternityPaternityLeaveOut(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    leave_type: str  # "maternity" or "paternity"
    requested_start_date: date
    requested_end_date: date
    total_days: int
    status: str  # "pending_hr", "pending_manager", "approved", "rejected"
    hr_approval_status: Optional[str] = None
    hr_approved_by: Optional[int] = None
    hr_approved_at: Optional[datetime] = None
    hr_comments: Optional[str] = None
    manager_approval_status: Optional[str] = None
    manager_approved_by: Optional[int] = None
    manager_approved_at: Optional[datetime] = None
    manager_comments: Optional[str] = None
    medical_certificate_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class MaternityPaternityApproval(BaseModel):
    action: str  # "approve" or "reject"
    comments: Optional[str] = None

# Announcement Schemas
class AnnouncementCreate(BaseModel):
    title: str
    content: str
    priority: str = "normal"
    category: str = "general"

# Asset Schemas
class AssetCreate(BaseModel):
    name: str
    type: str
    serial_number: str
    specifications: Optional[Dict[str, Any]] = None

class AssetAssign(BaseModel):
    employee_id: int

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_employees: int
    present_today: int
    on_leave: int
    pending_requests: int

# Generic List Response
class ListResponse(BaseModel):
    items: List[Any]
    total: int
    page: int = 1
    per_page: int = 10

# Admin-specific schemas
class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[str] = None

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    by_role: Dict[str, int]
    recent_logins: Dict[str, Any]
    security_stats: Dict[str, Any]

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    user_email: str
    action: str
    resource_type: str
    resource_id: int
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    risk_level: str
    details: Optional[str] = None

class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    skip: int
    limit: int

class CapabilitiesResponse(BaseModel):
    capabilities: Dict[str, Any]

class RoleCapabilitiesResponse(BaseModel):
    role: str
    capabilities: Dict[str, Any]

class SystemSettingsResponse(BaseModel):
    settings: Dict[str, Any]

class PermissionTemplatesResponse(BaseModel):
    templates: Dict[str, Any]

class UserActivationResponse(BaseModel):
    success: bool
    message: str
    user_id: int
    user_email: str

class PermissionValidationResponse(BaseModel):
    user_role: str
    module: str
    action: str
    has_permission: bool

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    service: str


# ============================================
# ADDITIONAL PYDANTIC SCHEMAS FOR MISSING ENDPOINTS
# ============================================

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date

# Asset Request Schemas
class AssetRequestBase(BaseModel):
    asset_type: str
    description: str
    priority: Optional[str] = "normal"

class AssetRequestCreate(AssetRequestBase):
    pass

class AssetRequestOut(AssetRequestBase):
    id: int
    employee_id: int
    status: str
    requested_date: datetime
    fulfilled_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Infrastructure Request Schemas
class InfrastructureRequestBase(BaseModel):
    request_type: str
    description: str
    priority: Optional[str] = "normal"

class InfrastructureRequestCreate(InfrastructureRequestBase):
    pass

class InfrastructureRequestOut(InfrastructureRequestBase):
    id: int
    employee_id: int
    status: str
    requested_date: datetime
    
    class Config:
        from_attributes = True

# Meeting Schemas
class MeetingRoomBase(BaseModel):
    name: str
    capacity: int
    location: str
    amenities: Optional[List[str]] = []

class MeetingRoomCreate(MeetingRoomBase):
    pass

class MeetingRoomOut(MeetingRoomBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_date: date
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_type: Optional[str] = "meeting"
    agenda: Optional[str] = None
    attendee_ids: Optional[List[int]] = []

class MeetingCreate(MeetingBase):
    pass

class MeetingAttendeeOut(BaseModel):
    id: int
    user_id: int
    status: str
    
    class Config:
        from_attributes = True

class MeetingOut(MeetingBase):
    id: int
    created_by: int
    status: str
    created_at: datetime
    attendees: Optional[List[MeetingAttendeeOut]] = []
    
    class Config:
        from_attributes = True

class MeetingAttendeeCreate(BaseModel):
    user_ids: List[int]

class AttendeeStatusUpdate(BaseModel):
    status: str

class MeetingNoteCreate(BaseModel):
    content: str
    note_type: Optional[str] = "general"
    is_private: Optional[bool] = False

class MeetingNoteOut(BaseModel):
    id: int
    meeting_id: int
    created_by: int
    content: str
    note_type: str
    is_private: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class MeetingActionItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: int
    due_date: Optional[date] = None
    priority: Optional[str] = "medium"

class MeetingActionItemOut(BaseModel):
    id: int
    meeting_id: int
    title: str
    description: Optional[str] = None
    assigned_to: int
    created_by: int
    status: str
    priority: str
    due_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Document Schemas
class EmployeeDocumentBase(BaseModel):
    document_type: str
    document_name: str

class EmployeeDocumentCreate(EmployeeDocumentBase):
    pass

class EmployeeDocumentOut(EmployeeDocumentBase):
    id: int
    employee_id: int
    file_path: str
    uploaded_date: datetime
    is_verified: bool
    
    class Config:
        from_attributes = True

# Learning Schemas
class CourseBase(BaseModel):
    title: str
    description: str
    duration_minutes: int
    category: str
    is_mandatory: Optional[bool] = False

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Engagement Schemas
class SurveyBase(BaseModel):
    title: str
    description: str
    questions: List[Dict]
    is_anonymous: Optional[bool] = False

class SurveyCreate(SurveyBase):
    pass

class SurveyOut(SurveyBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Career Schemas
class JobBase(BaseModel):
    title: str
    description: str
    department: str
    location: str

class JobCreate(JobBase):
    pass

class JobOut(JobBase):
    id: int
    posted_date: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Onboarding Schemas
class OnboardingTaskBase(BaseModel):
    task_name: str
    description: str
    due_date: Optional[date] = None
    priority: Optional[str] = "normal"

class OnboardingTaskCreate(OnboardingTaskBase):
    pass

class OnboardingTaskOut(OnboardingTaskBase):
    id: int
    employee_id: int
    status: str
    completed_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Attendance Extension Schemas
class AttendanceCorrectionBase(BaseModel):
    attendance_id: int
    correction_type: str
    corrected_value: str
    reason: str

class AttendanceCorrectionCreate(AttendanceCorrectionBase):
    pass

class AttendanceCorrectionOut(AttendanceCorrectionBase):
    id: int
    employee_id: int
    original_value: str
    status: str
    requested_date: datetime
    
    class Config:
        from_attributes = True

# Predictive Analytics Schemas
class AttritionPredictionOut(BaseModel):
    employee_id: int
    employee_name: str
    risk_score: float
    risk_level: str
    factors: List[str]
    recommendations: List[str]
    
    class Config:
        from_attributes = True


# Additional missing schemas
class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    meeting_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_type: Optional[str] = None
    agenda: Optional[str] = None
    status: Optional[str] = None

class EnrollmentOut(BaseModel):
    id: int
    employee_id: int
    module_id: int
    status: str
    progress_percentage: int
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SurveyResponseOut(BaseModel):
    id: int
    survey_id: int
    employee_id: Optional[int] = None
    responses: Dict
    submitted_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceCorrectionApproval(BaseModel):
    status: str
    notes: Optional[str] = None

class MeetingRoomBookingOut(BaseModel):
    id: int
    room_id: int
    booked_by: int
    title: str
    start_time: datetime
    end_time: datetime
    status: str
    
    class Config:
        from_attributes = True

class PerformanceForecastOut(BaseModel):
    employee_id: int
    employee_name: str
    predicted_rating: float
    confidence: float
    factors: List[str]
    
    class Config:
        from_attributes = True
