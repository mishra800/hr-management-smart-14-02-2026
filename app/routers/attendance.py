from fastapi import APIRouter, HTTPException, Depends, Query
from app import schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.attendance_service import AttendanceService
from datetime import datetime, date
from typing import List

router = APIRouter(
    prefix="/attendance",
    tags=["attendance"]
)

# Mock attendance data
MOCK_ATTENDANCE = {}

@router.post("/checkin")
def check_in(attendance: schemas.AttendanceCreate, current_user: dict = Depends(get_current_user)):
    """Employee check-in - Protected endpoint"""
    db = get_db()
    
    employee_id = current_user.get("id", 1)
    today = date.today()
    
    # Check if already checked in today
    attendance_key = f"{employee_id}_{today}"
    if attendance_key in MOCK_ATTENDANCE:
        existing = MOCK_ATTENDANCE[attendance_key]
        if existing.get("check_in"):
            raise HTTPException(status_code=400, detail="Already checked in today")
    
    # Create attendance record
    attendance_record = {
        "id": len(MOCK_ATTENDANCE) + 1,
        "employee_id": employee_id,
        "date": today.isoformat(),
        "status": attendance.status,
        "check_in": datetime.now().isoformat(),
        "check_out": None,
        "latitude": attendance.latitude,
        "longitude": attendance.longitude,
        "location_address": "Office Location",
        "verification_method": getattr(attendance, 'verification_method', 'manual'),
        "work_mode": getattr(attendance, 'work_mode', 'office')
    }
    
    MOCK_ATTENDANCE[attendance_key] = attendance_record
    
    return schemas.APIResponse(
        success=True,
        message="Check-in successful",
        data=attendance_record
    )

@router.post("/checkout")
def check_out(attendance_update: schemas.AttendanceUpdate, current_user: dict = Depends(get_current_user)):
    """Employee check-out - Protected endpoint"""
    employee_id = current_user.get("id", 1)
    today = date.today()
    attendance_key = f"{employee_id}_{today}"
    
    if attendance_key not in MOCK_ATTENDANCE:
        raise HTTPException(status_code=404, detail="No check-in record found for today")
    
    attendance_record = MOCK_ATTENDANCE[attendance_key]
    if attendance_record.get("check_out"):
        raise HTTPException(status_code=400, detail="Already checked out today")
    
    attendance_record["check_out"] = datetime.now().isoformat()
    attendance_record["updated_at"] = datetime.now().isoformat()
    
    return schemas.APIResponse(
        success=True,
        message="Checked out successfully",
        data=attendance_record
    )

@router.get("/today")
def get_today_attendance(current_user: dict = Depends(get_current_user)):
    """Get today's attendance for current user - Protected endpoint"""
    employee_id = current_user.get("id", 1)
    today = date.today()
    attendance_key = f"{employee_id}_{today}"
    
    attendance_record = MOCK_ATTENDANCE.get(attendance_key)
    
    return schemas.APIResponse(
        success=True,
        message="Today's attendance retrieved",
        data=attendance_record
    )

@router.get("/history")
def get_attendance_history():
    """Get attendance history"""
    # Return all attendance records for demo
    attendance_list = list(MOCK_ATTENDANCE.values())
    
    return schemas.APIResponse(
        success=True,
        message="Attendance history retrieved",
        data=attendance_list
    )

@router.get("/stats")
def get_attendance_stats():
    """Get attendance statistics"""
    total_days = len(MOCK_ATTENDANCE)
    present_days = len([a for a in MOCK_ATTENDANCE.values() if a.get("status") == "present"])
    
    stats = {
        "total_working_days": 22,  # Mock data
        "present_days": present_days,
        "absent_days": total_days - present_days,
        "attendance_percentage": (present_days / 22 * 100) if total_days > 0 else 0
    }
    
    return schemas.APIResponse(
        success=True,
        message="Attendance stats retrieved",
        data=stats
    )
# Enhanced endpoints for Dhanush Group procedures

@router.get("/procedures")
def get_attendance_procedures():
    """Get comprehensive attendance procedures and office operating particulars"""
    procedures = {
        "biometric_system": {
            "title": "Biometric System Usage",
            "requirements": [
                "Use biometric system authorized by Dhanush management",
                "Ensure proper Login and Logout through biometric system", 
                "Report biometric issues to HR team immediately",
                "Maintain proper record keeping without fail"
            ],
            "troubleshooting": {
                "access_denied": "Report to HR immediately for resolution",
                "login_failed": "Contact HR for manual entry assistance",
                "logout_failed": "HR assistance for manual logout recording",
                "system_down": "Emergency manual attendance with HR supervision"
            }
        },
        "office_timings": {
            "office_hours": "10:00 AM – 7:00 PM (9 hours)",
            "grace_period": "15 minutes up to 3 times per month",
            "work_days": "Monday – Friday",
            "saturday_policy": "Work from Home / Work from Office on need basis",
            "saturday_valid_cases": [
                "Client visits", "Team meetings", "Demos",
                "Meetings with management", "Emergency project deliverables"
            ]
        },
        "working_hours": {
            "half_day_minimum": "5 hours from login to logout",
            "full_day_minimum": "9 hours from login to logout", 
            "same_day_requirement": "Login and logout must be on same day"
        },
        "disciplinary_actions": {
            "late_login_threshold": "4th late login onwards",
            "penalty": "Half day leave deduction per late login",
            "no_balance_consequence": "Leave without pay (LOP)"
        },
        "remote_procedures": {
            "shift_timing_changes": {
                "hr_intimation_required": True,
                "manager_approval_required": True
            },
            "official_travel": {
                "advance_notice": "At least 1 day before travel",
                "manager_email_approval_required": True,
                "hr_database_recording": True
            }
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Attendance procedures retrieved successfully",
        data=procedures
    )

@router.post("/validate-procedures")
def validate_attendance_procedures(
    validation_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate attendance against Dhanush Group procedures"""
    db = get_db()
    attendance_service = AttendanceService(db)
    
    employee_id = current_user.get("id", 1)
    
    result = attendance_service.validate_attendance_procedures(employee_id, validation_data)
    
    return schemas.APIResponse(
        success=result["is_valid"],
        message="Attendance procedure validation completed",
        data=result
    )

@router.post("/validate-working-hours")
def validate_working_hours(
    hours_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate working hours for half day/full day determination"""
    db = get_db()
    attendance_service = AttendanceService(db)
    
    login_time = datetime.fromisoformat(hours_data.get("login_time"))
    logout_time = datetime.fromisoformat(hours_data.get("logout_time")) if hours_data.get("logout_time") else None
    
    result = attendance_service.validate_working_hours(login_time, logout_time)
    
    return schemas.APIResponse(
        success=result["is_valid"],
        message=result["message"],
        data=result
    )

@router.post("/request-shift-change")
def request_shift_timing_change(
    shift_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Request shift timing change with manager approval and HR intimation"""
    db = get_db()
    attendance_service = AttendanceService(db)
    
    employee_id = current_user.get("id", 1)
    
    result = attendance_service.request_shift_timing_change(employee_id, shift_data)
    
    return schemas.APIResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.post("/request-official-travel")
def request_official_travel(
    travel_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Request official travel with advance notice and manager approval"""
    db = get_db()
    attendance_service = AttendanceService(db)
    
    employee_id = current_user.get("id", 1)
    
    result = attendance_service.request_official_travel(employee_id, travel_data)
    
    return schemas.APIResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.get("/late-login-penalty/{employee_id}")
def check_late_login_penalty(
    employee_id: int,
    late_logins: int = Query(..., description="Number of late logins this month"),
    current_user: dict = Depends(get_current_user)
):
    """Check late login penalty as per disciplinary actions"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"] and current_user.get("id") != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db = get_db()
    attendance_service = AttendanceService(db)
    
    result = attendance_service.check_late_login_penalty(employee_id, late_logins)
    
    return schemas.APIResponse(
        success=True,
        message="Late login penalty check completed",
        data=result
    )

@router.post("/report-biometric-issue")
def report_biometric_issue(
    issue_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Report biometric system issues to HR team"""
    db = get_db()
    attendance_service = AttendanceService(db)
    
    employee_id = current_user.get("id", 1)
    
    result = attendance_service.report_biometric_issue(employee_id, issue_data)
    
    return schemas.APIResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )

@router.post("/saturday-work-eligibility")
def check_saturday_work_eligibility(
    saturday_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Check Saturday work eligibility based on business need"""
    db = get_db()
    attendance_service = AttendanceService(db)
    
    employee_id = current_user.get("id", 1)
    saturday_date = datetime.strptime(saturday_data.get("date"), "%Y-%m-%d").date()
    reason = saturday_data.get("reason", "")
    
    result = attendance_service.get_saturday_work_eligibility(employee_id, saturday_date, reason)
    
    return schemas.APIResponse(
        success=result["eligible"],
        message=result["message"],
        data=result
    )

# ============================================
# PROFILE IMAGE ENDPOINTS
# ============================================

@router.get("/check-profile-image")
def check_profile_image(current_user: dict = Depends(get_current_user)):
    """Check if user has a profile image"""
    try:
        user_id = current_user.get("id")
        db = get_db()
        
        from sqlalchemy import text
        with db.connect() as conn:
            query = text("""
                SELECT profile_image 
                FROM employees 
                WHERE user_id = :user_id
            """)
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()
            
            if row and row[0]:
                # Check if file exists
                from pathlib import Path
                image_path = Path(row[0])
                if image_path.exists():
                    return schemas.APIResponse(
                        success=True,
                        message="Profile image found",
                        data={
                            "has_image": True,
                            "profile_image_url": f"/uploads/profile_images/user_{user_id}.jpg"
                        }
                    )
        
        return schemas.APIResponse(
            success=True,
            message="No profile image found",
            data={
                "has_image": False,
                "profile_image_url": None
            }
        )
    except Exception as e:
        return schemas.APIResponse(
            success=False,
            message=f"Error checking profile image: {str(e)}",
            data={
                "has_image": False,
                "profile_image_url": None
            }
        )

# ============================================
# WFH REQUEST ENDPOINTS
# ============================================

# Mock WFH requests data
MOCK_WFH_REQUESTS = {}

@router.post("/wfh-request")
def submit_wfh_request(
    wfh_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit Work From Home request"""
    employee_id = current_user.get("id", 1)
    request_date = datetime.strptime(wfh_data.get("request_date"), "%Y-%m-%d").date()
    reason = wfh_data.get("reason", "")
    
    # Check if request already exists for this date
    existing_key = f"{employee_id}_{request_date}"
    if existing_key in MOCK_WFH_REQUESTS:
        raise HTTPException(status_code=400, detail="WFH request already exists for this date")
    
    # Check if date is in the past
    if request_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot request WFH for past dates")
    
    # Create WFH request
    request_id = len(MOCK_WFH_REQUESTS) + 1
    wfh_request = {
        "id": request_id,
        "employee_id": employee_id,
        "employee": {
            "id": employee_id,
            "first_name": current_user.get("first_name", "John"),
            "last_name": current_user.get("last_name", "Doe"),
            "department": current_user.get("department", "IT"),
            "position": current_user.get("position", "Developer")
        },
        "request_date": request_date.isoformat(),
        "reason": reason,
        "status": "pending",
        "manager_comments": None,
        "created_at": datetime.now().isoformat(),
        "reviewed_at": None
    }
    
    MOCK_WFH_REQUESTS[request_id] = wfh_request
    
    return {
        "success": True,
        "message": "WFH request submitted successfully",
        "data": wfh_request
    }

@router.get("/wfh-requests")
def get_wfh_requests(current_user: dict = Depends(get_current_user)):
    """Get WFH requests for current user"""
    employee_id = current_user.get("id", 1)
    
    # Filter requests for current user
    user_requests = [
        request for request in MOCK_WFH_REQUESTS.values()
        if request["employee_id"] == employee_id
    ]
    
    # Sort by created_at descending
    user_requests.sort(key=lambda x: x["created_at"], reverse=True)
    
    return user_requests

@router.get("/wfh-requests/pending")
def get_pending_wfh_requests(current_user: dict = Depends(get_current_user)):
    """Get pending WFH requests for managers/HR/admin"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Only managers, HR, and admins can view pending requests.")
    
    # Filter pending requests
    pending_requests = [
        request for request in MOCK_WFH_REQUESTS.values()
        if request["status"] == "pending"
    ]
    
    # Sort by created_at ascending (oldest first)
    pending_requests.sort(key=lambda x: x["created_at"])
    
    return pending_requests

@router.put("/wfh-requests/{request_id}/approve")
def approve_wfh_request(
    request_id: int,
    approval_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject WFH request"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Only managers, HR, and admins can approve requests.")
    
    if request_id not in MOCK_WFH_REQUESTS:
        raise HTTPException(status_code=404, detail="WFH request not found")
    
    wfh_request = MOCK_WFH_REQUESTS[request_id]
    
    if wfh_request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request has already been reviewed")
    
    # Update request status
    status = approval_data.get("status", "approved")  # "approved" or "rejected"
    comments = approval_data.get("comments", "")
    
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")
    
    wfh_request["status"] = status
    wfh_request["manager_comments"] = comments
    wfh_request["reviewed_at"] = datetime.now().isoformat()
    wfh_request["reviewed_by"] = current_user.get("id", 1)
    
    return {
        "success": True,
        "message": f"WFH request {status} successfully",
        "data": wfh_request
    }


# ============================================
# PROFILE IMAGE ENDPOINTS
# ============================================

@router.post("/upload-profile-image")
def upload_profile_image(
    image_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Upload profile image for face recognition"""
    import base64
    import os
    from pathlib import Path
    
    try:
        # Get image data
        image_base64 = image_data.get("image", "")
        if not image_base64:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Remove data URL prefix if present
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_base64)
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads/profile_images")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save image with user ID as filename
        user_id = current_user.get("id")
        image_path = upload_dir / f"user_{user_id}.jpg"
        
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        
        # Update employee record with image path
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check if employee record exists
            check_query = text("SELECT id FROM employees WHERE user_id = :user_id")
            result = conn.execute(check_query, {"user_id": user_id})
            employee = result.fetchone()
            
            if employee:
                # Update profile image path
                update_query = text("""
                    UPDATE employees 
                    SET profile_image = :image_path,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = :user_id
                """)
                conn.execute(update_query, {
                    "image_path": str(image_path),
                    "user_id": user_id
                })
                conn.commit()
        
        return schemas.APIResponse(
            success=True,
            message="Profile image uploaded successfully",
            data={
                "image_path": str(image_path),
                "profile_image_url": f"/uploads/profile_images/user_{user_id}.jpg"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@router.get("/check-profile-image")
def check_profile_image(current_user: dict = Depends(get_current_user)):
    """Check if user has a profile image"""
    try:
        user_id = current_user.get("id")
        from app.database import engine
        
        from sqlalchemy import text
        with engine.connect() as conn:
            query = text("""
                SELECT profile_image 
                FROM employees 
                WHERE user_id = :user_id
            """)
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()
            
            if row and row[0]:
                # Check if file exists
                from pathlib import Path
                image_path = Path(row[0])
                if image_path.exists():
                    return schemas.APIResponse(
                        success=True,
                        message="Profile image found",
                        data={
                            "has_image": True,
                            "profile_image_url": f"/uploads/profile_images/user_{user_id}.jpg"
                        }
                    )
        
        return schemas.APIResponse(
            success=True,
            message="No profile image found",
            data={
                "has_image": False,
                "profile_image_url": None
            }
        )
    except Exception as e:
        return schemas.APIResponse(
            success=False,
            message=f"Error checking profile image: {str(e)}",
            data={
                "has_image": False,
                "profile_image_url": None
            }
        )
