"""
Full Recruitment Management Router
Handles job postings, applications, candidate management, and recruitment analytics
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from app.dependencies import get_current_user
from app.error_handlers import check_user_permissions, log_user_action, ValidationError
from app.database import engine
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from enum import Enum
import uuid
import json

router = APIRouter(
    prefix="/recruitment",
    tags=["recruitment"]
)

class JobStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    SELECTED = "selected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    HIRED = "hired"

class InterviewType(str, Enum):
    PHONE = "phone"
    VIDEO = "video"
    IN_PERSON = "in_person"
    TECHNICAL = "technical"
    HR = "hr"
    FINAL = "final"

# Pydantic Models
class JobCreate(BaseModel):
    title: str
    department: str
    location: str
    description: str
    job_type: Optional[str] = "full_time"  # full_time, part_time, contract, internship
    experience_level: Optional[str] = "mid"  # entry, mid, senior, executive
    requirements: Optional[List[str]] = []
    responsibilities: Optional[List[str]] = []
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    benefits: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    remote_allowed: bool = False
    workflow_mode: Optional[str] = "flexible"
    requisition_status: Optional[str] = "pending_approval"

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    benefits: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    remote_allowed: Optional[bool] = None
    status: Optional[JobStatus] = None

class ApplicationCreate(BaseModel):
    job_id: int
    candidate_name: str
    candidate_email: EmailStr
    candidate_phone: str
    cover_letter: Optional[str] = None
    experience_years: Optional[int] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    expected_salary: Optional[float] = None
    notice_period: Optional[str] = None
    source: Optional[str] = "direct"  # direct, referral, linkedin, job_board

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    rating: Optional[int] = None  # 1-5 scale
    interview_feedback: Optional[str] = None

class InterviewSchedule(BaseModel):
    application_id: int
    interview_type: InterviewType
    scheduled_at: datetime
    interviewer_ids: List[int]
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None

# Mock data
MOCK_JOBS = {}
MOCK_APPLICATIONS = {}
MOCK_INTERVIEWS = {}
MOCK_CANDIDATES = {}

def generate_id():
    return len(MOCK_JOBS) + len(MOCK_APPLICATIONS) + len(MOCK_INTERVIEWS) + 1

@router.get("/jobs")
@router.get("/jobs/")
async def get_jobs(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    department: Optional[str] = None,
    location: Optional[str] = None,
    employment_type: Optional[str] = None
):
    """Get all job postings from database with filtering"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager", "employee"])
    
    try:
        with engine.connect() as conn:
            # Build query with filters
            query_parts = ["SELECT * FROM job_postings WHERE 1=1"]
            params = {}
            
            if status:
                query_parts.append("AND status = :status")
                params["status"] = status
            if department:
                query_parts.append("AND LOWER(department) = LOWER(:department)")
                params["department"] = department
            if location:
                query_parts.append("AND LOWER(location) LIKE LOWER(:location)")
                params["location"] = f"%{location}%"
            if employment_type:
                query_parts.append("AND employment_type = :employment_type")
                params["employment_type"] = employment_type
            
            query_parts.append("ORDER BY created_at DESC")
            query_parts.append("LIMIT :limit OFFSET :skip")
            params["limit"] = limit
            params["skip"] = skip
            
            query = text(" ".join(query_parts))
            result = conn.execute(query, params)
            rows = result.fetchall()
            
            # Get total count
            count_query_parts = ["SELECT COUNT(*) FROM job_postings WHERE 1=1"]
            if status:
                count_query_parts.append("AND status = :status")
            if department:
                count_query_parts.append("AND LOWER(department) = LOWER(:department)")
            if location:
                count_query_parts.append("AND LOWER(location) LIKE LOWER(:location)")
            if employment_type:
                count_query_parts.append("AND employment_type = :employment_type")
            
            count_query = text(" ".join(count_query_parts))
            count_params = {k: v for k, v in params.items() if k not in ['limit', 'skip']}
            total = conn.execute(count_query, count_params).scalar()
            
            jobs = []
            for row in rows:
                # Safely parse JSON fields
                try:
                    required_skills = json.loads(row[21]) if row[21] and isinstance(row[21], str) else (row[21] if isinstance(row[21], list) else [])
                except (json.JSONDecodeError, TypeError):
                    required_skills = []
                
                try:
                    requirements = json.loads(row[6]) if row[6] and isinstance(row[6], str) else (row[6] if isinstance(row[6], list) else None)
                except (json.JSONDecodeError, TypeError):
                    requirements = row[6]
                
                jobs.append({
                    "id": row[0],
                    "title": row[1],
                    "department": row[2],
                    "location": row[3],
                    "employment_type": row[4],
                    "description": row[5],
                    "requirements": requirements,
                    "salary_min": float(row[7]) if row[7] else None,
                    "salary_max": float(row[8]) if row[8] else None,
                    "status": row[9],
                    "posted_by": row[10],
                    "posted_date": str(row[11]) if row[11] else None,
                    "closing_date": str(row[12]) if row[12] else None,
                    "workflow_mode": row[13],
                    "current_step": row[14],
                    "requisition_status": row[15],
                    "application_link_code": row[16],
                    "qr_code_url": row[17],
                    "allow_linkedin_apply": row[18],
                    "allow_bulk_upload": row[19],
                    "blind_hiring_enabled": row[20],
                    "required_skills": required_skills,
                    "min_experience_years": row[22],
                    "max_experience_years": row[23],
                    "remote_allowed": row[24],
                    "hiring_manager_id": row[25],
                    "created_at": str(row[26]) if row[26] else None,
                    "updated_at": str(row[27]) if row[27] else None
                })
            
            return {
                "success": True,
                "data": {
                    "jobs": jobs,
                    "total": total,
                    "filters_applied": {
                        "status": status,
                        "department": department,
                        "location": location,
                        "employment_type": employment_type
                    }
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")

@router.post("/jobs")
@router.post("/jobs/")
async def create_job(
    job: JobCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new job posting in database"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr"])
    
    try:
        with engine.connect() as conn:
            # Get employee_id for the current user
            # First try to get from users table
            user_query = text("SELECT employee_id FROM users WHERE id = :user_id")
            user_result = conn.execute(user_query, {"user_id": current_user.get("id")})
            user_row = user_result.fetchone()
            employee_id = user_row[0] if user_row and user_row[0] else None
            
            # If no employee_id in users table, try to find employee by email
            if not employee_id:
                email_query = text("SELECT id FROM employees WHERE email = :email LIMIT 1")
                email_result = conn.execute(email_query, {"email": current_user.get("email")})
                email_row = email_result.fetchone()
                employee_id = email_row[0] if email_row else None
            
            # If still no employee_id, create a basic employee record
            if not employee_id:
                create_emp_query = text("""
                    INSERT INTO employees (first_name, last_name, email, department, position, status)
                    VALUES (:first_name, :last_name, :email, :department, :position, 'active')
                    RETURNING id
                """)
                emp_result = conn.execute(create_emp_query, {
                    "first_name": current_user.get("email", "").split("@")[0],
                    "last_name": "User",
                    "email": current_user.get("email"),
                    "department": job.department or "HR",
                    "position": "HR Manager"
                })
                employee_id = emp_result.fetchone()[0]
                
                # Update users table with new employee_id
                update_user_query = text("UPDATE users SET employee_id = :employee_id WHERE id = :user_id")
                conn.execute(update_user_query, {"employee_id": employee_id, "user_id": current_user.get("id")})
            
            # Convert lists to JSON strings for database storage
            requirements_str = json.dumps(job.requirements) if job.requirements else None
            
            # Insert into database
            insert_query = text("""
                INSERT INTO job_postings (
                    title, department, location, employment_type, description, 
                    requirements, salary_min, salary_max, status, posted_by,
                    workflow_mode, requisition_status, remote_allowed,
                    posted_date, current_step
                )
                VALUES (
                    :title, :department, :location, :job_type, :description,
                    :requirements, :salary_min, :salary_max, :status, :posted_by,
                    :workflow_mode, :requisition_status, :remote_allowed,
                    CURRENT_DATE, :current_step
                )
                RETURNING id, title, department, location, employment_type, description,
                          requirements, salary_min, salary_max, status, posted_by,
                          posted_date, workflow_mode, current_step, requisition_status,
                          remote_allowed, created_at
            """)
            
            result = conn.execute(insert_query, {
                "title": job.title,
                "department": job.department,
                "location": job.location,
                "job_type": job.job_type,
                "description": job.description,
                "requirements": requirements_str,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "status": job.requisition_status if job.requisition_status == "pending_approval" else "draft",
                "posted_by": employee_id,
                "workflow_mode": job.workflow_mode,
                "requisition_status": job.requisition_status,
                "remote_allowed": job.remote_allowed,
                "current_step": 0
            })
            
            conn.commit()
            
            row = result.fetchone()
            
            new_job = {
                "id": row[0],
                "title": row[1],
                "department": row[2],
                "location": row[3],
                "employment_type": row[4],
                "description": row[5],
                "requirements": row[6],
                "salary_min": float(row[7]) if row[7] else None,
                "salary_max": float(row[8]) if row[8] else None,
                "status": row[9],
                "posted_by": row[10],
                "posted_date": str(row[11]) if row[11] else None,
                "workflow_mode": row[12],
                "current_step": row[13],
                "requisition_status": row[14],
                "remote_allowed": row[15],
                "created_at": str(row[16]) if row[16] else None
            }
            
            log_user_action(
                current_user.get("id"),
                "create_job",
                "job",
                {"job_id": new_job["id"], "title": job.title}
            )
            
            return {
                "success": True,
                "message": "Job created successfully",
                "data": new_job
            }
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        import traceback
        error_detail = f"Failed to create job: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # Log to console for debugging
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@router.patch("/jobs/{job_id}/approve")
async def approve_job(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Approve job requisition and make it active"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager"])
    
    try:
        with engine.connect() as conn:
            # Update job status to approved and active
            update_query = text("""
                UPDATE job_postings 
                SET requisition_status = 'approved',
                    status = 'active',
                    current_step = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :job_id
                RETURNING id, title, requisition_status, status, current_step
            """)
            
            result = conn.execute(update_query, {"job_id": job_id})
            conn.commit()
            
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Job not found")
            
            log_user_action(
                current_user.get("id"),
                "approve_job",
                "job",
                {"job_id": job_id, "title": row[1]}
            )
            
            return {
                "success": True,
                "message": f"Job '{row[1]}' approved successfully",
                "data": {
                    "id": row[0],
                    "title": row[1],
                    "requisition_status": row[2],
                    "status": row[3],
                    "current_step": row[4]
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve job: {str(e)}")

@router.patch("/jobs/{job_id}/advance")
async def advance_job_step(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Advance job to next workflow step"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager"])
    
    try:
        with engine.connect() as conn:
            # Get current step
            select_query = text("SELECT current_step FROM job_postings WHERE id = :job_id")
            result = conn.execute(select_query, {"job_id": job_id})
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Job not found")
            
            current_step = row[0] or 0
            new_step = min(9, current_step + 1)  # Cap at step 9 (Onboarding)
            
            # Update to next step
            update_query = text("""
                UPDATE job_postings 
                SET current_step = :new_step,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :job_id
                RETURNING id, title, current_step
            """)
            
            result = conn.execute(update_query, {"job_id": job_id, "new_step": new_step})
            conn.commit()
            
            row = result.fetchone()
            
            log_user_action(
                current_user.get("id"),
                "advance_job_step",
                "job",
                {"job_id": job_id, "new_step": new_step}
            )
            
            return {
                "success": True,
                "message": f"Job advanced to step {new_step}",
                "data": {
                    "id": row[0],
                    "title": row[1],
                    "current_step": row[2]
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to advance job step: {str(e)}")

@router.patch("/jobs/{job_id}/revert")
async def revert_job_step(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Revert job to previous workflow step"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager"])
    
    try:
        with engine.connect() as conn:
            # Get current step
            select_query = text("SELECT current_step FROM job_postings WHERE id = :job_id")
            result = conn.execute(select_query, {"job_id": job_id})
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Job not found")
            
            current_step = row[0] or 0
            new_step = max(0, current_step - 1)  # Don't go below step 0
            
            # Update to previous step
            update_query = text("""
                UPDATE job_postings 
                SET current_step = :new_step,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :job_id
                RETURNING id, title, current_step
            """)
            
            result = conn.execute(update_query, {"job_id": job_id, "new_step": new_step})
            conn.commit()
            
            row = result.fetchone()
            
            log_user_action(
                current_user.get("id"),
                "revert_job_step",
                "job",
                {"job_id": job_id, "new_step": new_step}
            )
            
            return {
                "success": True,
                "message": f"Job reverted to step {new_step}",
                "data": {
                    "id": row[0],
                    "title": row[1],
                    "current_step": row[2]
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revert job step: {str(e)}")

@router.get("/jobs/{job_id}")
async def get_job(
    job_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get specific job posting"""
    if job_id not in MOCK_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = MOCK_JOBS[job_id]
    
    # Increment view count
    job["views_count"] = job.get("views_count", 0) + 1
    job["last_viewed_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "data": job
    }

@router.put("/jobs/{job_id}")
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update job posting"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr"])
    
    if job_id not in MOCK_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = MOCK_JOBS[job_id]
    
    # Update fields
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "application_deadline" and value:
            job[field] = value.isoformat()
        else:
            job[field] = value
    
    job["updated_at"] = datetime.now().isoformat()
    job["updated_by"] = current_user.get("id")
    
    log_user_action(
        current_user.get("id"),
        "update_job",
        "job",
        {"job_id": job_id, "updated_fields": list(update_data.keys())}
    )
    
    return {
        "success": True,
        "message": "Job updated successfully",
        "data": job
    }

@router.post("/jobs/{job_id}/applications")
async def create_application(
    job_id: int,
    application: ApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Submit job application"""
    if job_id not in MOCK_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = MOCK_JOBS[job_id]
    if job.get("status") != JobStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Job is not accepting applications")
    
    # Check application deadline
    if job.get("application_deadline"):
        deadline = datetime.fromisoformat(job["application_deadline"])
        if datetime.now() > deadline:
            raise HTTPException(status_code=400, detail="Application deadline has passed")
    
    application_id = generate_id()
    
    new_application = {
        "id": application_id,
        "job_id": job_id,
        "job_title": job.get("title"),
        "candidate_name": application.candidate_name,
        "candidate_email": application.candidate_email,
        "candidate_phone": application.candidate_phone,
        "cover_letter": application.cover_letter,
        "experience_years": application.experience_years,
        "current_company": application.current_company,
        "current_position": application.current_position,
        "expected_salary": application.expected_salary,
        "notice_period": application.notice_period,
        "source": application.source,
        "status": ApplicationStatus.APPLIED,
        "rating": None,
        "notes": "",
        "interview_feedback": "",
        "applied_at": datetime.now().isoformat(),
        "applied_by": current_user.get("id") if current_user.get("role") != "candidate" else None
    }
    
    MOCK_APPLICATIONS[application_id] = new_application
    
    # Update job applications count
    job["applications_count"] = job.get("applications_count", 0) + 1
    
    log_user_action(
        current_user.get("id"),
        "create_application",
        "application",
        {"application_id": application_id, "job_id": job_id, "candidate": application.candidate_name}
    )
    
    return {
        "success": True,
        "message": "Application submitted successfully",
        "data": new_application
    }

@router.get("/applications")
async def get_applications(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    job_id: Optional[int] = None,
    status: Optional[ApplicationStatus] = None,
    candidate_email: Optional[str] = None
):
    """Get applications with filtering"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager"])
    
    applications = list(MOCK_APPLICATIONS.values())
    
    # Apply filters
    if job_id:
        applications = [app for app in applications if app.get("job_id") == job_id]
    if status:
        applications = [app for app in applications if app.get("status") == status]
    if candidate_email:
        applications = [app for app in applications if candidate_email.lower() in app.get("candidate_email", "").lower()]
    
    # Sort by applied_at descending
    applications.sort(key=lambda x: x.get("applied_at", ""), reverse=True)
    
    # Apply pagination
    paginated_applications = applications[skip:skip + limit]
    
    return {
        "success": True,
        "data": {
            "applications": paginated_applications,
            "total": len(applications),
            "filters_applied": {
                "job_id": job_id,
                "status": status,
                "candidate_email": candidate_email
            }
        }
    }

@router.put("/applications/{application_id}")
async def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update application status and notes"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager"])
    
    if application_id not in MOCK_APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = MOCK_APPLICATIONS[application_id]
    
    # Update fields
    update_data = application_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        application[field] = value
    
    application["updated_at"] = datetime.now().isoformat()
    application["updated_by"] = current_user.get("id")
    
    log_user_action(
        current_user.get("id"),
        "update_application",
        "application",
        {"application_id": application_id, "new_status": application_update.status}
    )
    
    return {
        "success": True,
        "message": "Application updated successfully",
        "data": application
    }

@router.post("/interviews")
async def schedule_interview(
    interview: InterviewSchedule,
    current_user: dict = Depends(get_current_user)
):
    """Schedule interview for application"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager"])
    
    if interview.application_id not in MOCK_APPLICATIONS:
        raise HTTPException(status_code=404, detail="Application not found")
    
    interview_id = generate_id()
    
    new_interview = {
        "id": interview_id,
        "application_id": interview.application_id,
        "interview_type": interview.interview_type,
        "scheduled_at": interview.scheduled_at.isoformat(),
        "interviewer_ids": interview.interviewer_ids,
        "location": interview.location,
        "meeting_link": interview.meeting_link,
        "notes": interview.notes,
        "status": "scheduled",
        "created_by": current_user.get("id"),
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_INTERVIEWS[interview_id] = new_interview
    
    # Update application status
    application = MOCK_APPLICATIONS[interview.application_id]
    application["status"] = ApplicationStatus.INTERVIEW_SCHEDULED
    application["updated_at"] = datetime.now().isoformat()
    
    log_user_action(
        current_user.get("id"),
        "schedule_interview",
        "interview",
        {"interview_id": interview_id, "application_id": interview.application_id}
    )
    
    return {
        "success": True,
        "message": "Interview scheduled successfully",
        "data": new_interview
    }

@router.get("/analytics")
async def get_recruitment_analytics(
    current_user: dict = Depends(get_current_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get recruitment analytics"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr"])
    
    # Calculate analytics
    total_jobs = len(MOCK_JOBS)
    active_jobs = len([job for job in MOCK_JOBS.values() if job.get("status") == JobStatus.ACTIVE])
    total_applications = len(MOCK_APPLICATIONS)
    
    # Application status breakdown
    status_breakdown = {}
    for app in MOCK_APPLICATIONS.values():
        status = app.get("status", "unknown")
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    # Department wise job distribution
    dept_breakdown = {}
    for job in MOCK_JOBS.values():
        dept = job.get("department", "unknown")
        dept_breakdown[dept] = dept_breakdown.get(dept, 0) + 1
    
    # Source effectiveness
    source_breakdown = {}
    for app in MOCK_APPLICATIONS.values():
        source = app.get("source", "unknown")
        source_breakdown[source] = source_breakdown.get(source, 0) + 1
    
    return {
        "success": True,
        "data": {
            "overview": {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "total_applications": total_applications,
                "applications_per_job": round(total_applications / max(total_jobs, 1), 2)
            },
            "application_status_breakdown": status_breakdown,
            "department_breakdown": dept_breakdown,
            "source_effectiveness": source_breakdown,
            "recent_activity": {
                "jobs_posted_this_week": len([job for job in MOCK_JOBS.values() 
                                            if datetime.fromisoformat(job.get("created_at", "2024-01-01T00:00:00")) > 
                                            datetime.now() - timedelta(days=7)]),
                "applications_this_week": len([app for app in MOCK_APPLICATIONS.values() 
                                             if datetime.fromisoformat(app.get("applied_at", "2024-01-01T00:00:00")) > 
                                             datetime.now() - timedelta(days=7)])
            }
        }
    }

@router.get("/health")
async def recruitment_health_check():
    """Recruitment service health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "recruitment",
        "total_jobs": len(MOCK_JOBS),
        "total_applications": len(MOCK_APPLICATIONS)
    }

# Initialize sample data
def initialize_sample_data():
    """Initialize sample recruitment data"""
    sample_jobs = [
        {
            "id": 1,
            "title": "Senior Software Engineer",
            "department": "Engineering",
            "location": "Bangalore, India",
            "job_type": "full_time",
            "experience_level": "senior",
            "description": "We are looking for a Senior Software Engineer to join our team.",
            "requirements": ["5+ years experience", "Python/JavaScript", "Cloud platforms"],
            "responsibilities": ["Design and develop software", "Mentor junior developers", "Code reviews"],
            "salary_min": 1200000,
            "salary_max": 1800000,
            "benefits": ["Health insurance", "Flexible hours", "Remote work"],
            "remote_allowed": True,
            "status": JobStatus.ACTIVE,
            "created_by": 1,
            "created_at": datetime.now().isoformat(),
            "applications_count": 5,
            "views_count": 25
        }
    ]
    
    for job in sample_jobs:
        MOCK_JOBS[job["id"]] = job

# Initialize sample data
initialize_sample_data()