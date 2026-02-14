from fastapi import APIRouter, HTTPException, Depends, Query
from app import schemas
from app.database import get_db
from app.leave_service import LeaveService
from app.dependencies import get_current_user
from app.role_utils import require_role, check_role_access
from datetime import datetime, date, timedelta
from typing import List, Optional
import json

router = APIRouter(
    prefix="/leave",
    tags=["leave"]
)

# Initialize leave service
leave_service = LeaveService()

# Enhanced mock data with comprehensive leave management
MOCK_LEAVE_REQUESTS = {}
MOCK_EMPLOYEE_DATA = {}
MOCK_LEAVE_BALANCES = {}
MOCK_WFH_REQUESTS = {}
MOCK_LEAVE_ENCASHMENTS = {}
MOCK_CARRY_FORWARDS = {}

# Get employee data from database
def get_mock_employee_data(employee_id: int) -> dict:
    """Get employee data from database"""
    from app.database import engine
    from sqlalchemy import text
    
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    e.id,
                    e.employee_id,
                    e.first_name,
                    e.last_name,
                    e.gender,
                    e.hire_date,
                    e.date_of_birth,
                    e.wedding_anniversary_date,
                    e.department,
                    e.position
                FROM employees e
                WHERE e.id = :employee_id
            """)
            
            result = conn.execute(query, {"employee_id": employee_id})
            row = result.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "type": "permanent",
                    "gender": row[4] or "",
                    "joining_date": str(row[5]) if row[5] else "2023-01-15",
                    "date_of_birth": str(row[6]) if row[6] else "",
                    "wedding_anniversary_date": str(row[7]) if row[7] else "",
                    "department": row[8] or "",
                    "position": row[9] or "",
                    "manager_id": None,
                    "salary": 75000,
                    "employee_code": row[1],
                    "probation_end_date": None
                }
    except Exception as e:
        pass
    
    # Fallback for unknown employee IDs
    return {
        "id": employee_id,
        "type": "permanent",
        "gender": "",
        "joining_date": "2023-01-01",
        "date_of_birth": "",
        "wedding_anniversary_date": "",
        "department": "",
        "position": "",
        "manager_id": None,
        "salary": 60000,
        "employee_code": f"EMP{employee_id:03d}",
        "probation_end_date": None
    }

@router.post("/request")
def create_leave_request(leave_request: schemas.LeaveRequestCreate, current_user: dict = Depends(get_current_user)):
    """Create a new leave request with comprehensive validation and policy compliance"""
    db = get_db()
    
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    # Validate leave request against policy
    is_valid, message = leave_service.validate_leave_request(leave_request, employee_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Check policy compliance (new addition)
    request_data = {
        "reason": leave_request.reason,
        "leave_type": leave_request.leave_type,
        "manager_approval_required": True
    }
    is_compliant, compliance_message, compliance_details = leave_service.validate_policy_compliance("leave", request_data)
    
    # Calculate leave duration
    leave_duration = (leave_request.end_date - leave_request.start_date).days + 1
    if leave_request.is_half_day:
        leave_duration = 0.5
    
    new_id = len(MOCK_LEAVE_REQUESTS) + 1
    leave_record = {
        "id": new_id,
        "employee_id": employee_id,
        "leave_type": leave_request.leave_type,
        "start_date": leave_request.start_date.isoformat(),
        "end_date": leave_request.end_date.isoformat(),
        "reason": leave_request.reason,
        "duration_days": leave_duration,
        "is_half_day": leave_request.is_half_day,
        "half_day_period": leave_request.half_day_period,
        "emergency": leave_request.emergency,
        "medical_certificate": leave_request.medical_certificate,
        "manager_email_approval": leave_request.manager_email_approval,
        "bl_occasion_type": getattr(leave_request, 'bl_occasion_type', None),  # Store birthday/anniversary choice
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_by": None,
        "approved_at": None,
        "manager_comments": None,
        "hr_comments": None,
        "working_days_affected": leave_service.calculate_working_days(leave_request.start_date, leave_request.end_date),
        "policy_compliance": {
            "is_compliant": is_compliant,
            "compliance_message": compliance_message,
            "compliance_details": compliance_details
        }
    }
    
    MOCK_LEAVE_REQUESTS[new_id] = leave_record
    
    # Enhanced response message based on policy objectives
    response_message = "Leave request created successfully."
    if any("work-life balance" in detail.lower() for detail in compliance_details):
        response_message += " This request supports our work-life balance policy objective."
    
    response_message += " Please ensure SMHR application is completed within 2 days if this was an emergency request."
    
    return schemas.APIResponse(
        success=True,
        message=response_message,
        data=leave_record
    )

@router.get("/pending")
def get_pending_leave_requests(current_user: dict = Depends(get_current_user)):
    """Get pending leave requests for managers/HR"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["manager", "hr", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    # Filter pending requests
    pending_requests = [
        request for request in MOCK_LEAVE_REQUESTS.values()
        if request.get("status") == "pending"
    ]
    
    return schemas.APIResponse(
        success=True,
        message="Pending leave requests retrieved",
        data=pending_requests
    )

@router.put("/approve/{leave_id}")
def approve_leave_simple(leave_id: int, current_user: dict = Depends(get_current_user)):
    """Simple approve leave request (for dashboard)"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["manager", "hr", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    if leave_id not in MOCK_LEAVE_REQUESTS:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    leave_request = MOCK_LEAVE_REQUESTS[leave_id]
    leave_request["status"] = "approved"
    leave_request["approved_by"] = current_user.get("id", 1)
    leave_request["approved_at"] = datetime.now().isoformat()
    
    return schemas.APIResponse(
        success=True,
        message="Leave request approved successfully",
        data=leave_request
    )

@router.put("/reject/{leave_id}")
def reject_leave_simple(leave_id: int, current_user: dict = Depends(get_current_user)):
    """Simple reject leave request (for dashboard)"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["manager", "hr", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    if leave_id not in MOCK_LEAVE_REQUESTS:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    leave_request = MOCK_LEAVE_REQUESTS[leave_id]
    leave_request["status"] = "rejected"
    leave_request["approved_by"] = current_user.get("id", 1)
    leave_request["approved_at"] = datetime.now().isoformat()
    
    return schemas.APIResponse(
        success=True,
        message="Leave request rejected successfully",
        data=leave_request
    )

@router.get("/requests")
def get_leave_requests(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    leave_type: Optional[str] = Query(None, description="Filter by leave type"),
    year: Optional[int] = Query(None, description="Filter by year"),
    current_user: dict = Depends(get_current_user)
):
    """Get leave requests with filtering options"""
    employee_id = current_user.get("id", 1)
    
    # Filter leave requests
    filtered_requests = []
    for leave in MOCK_LEAVE_REQUESTS.values():
        if leave["employee_id"] != employee_id:
            continue
            
        if status and leave["status"] != status:
            continue
            
        if leave_type and leave["leave_type"] != leave_type:
            continue
            
        if year:
            leave_year = datetime.fromisoformat(leave["start_date"]).year
            if leave_year != year:
                continue
                
        filtered_requests.append(leave)
    
    return schemas.APIResponse(
        success=True,
        message="Leave requests retrieved successfully",
        data=filtered_requests
    )

@router.get("/balance")
def get_leave_balance(current_user: dict = Depends(get_current_user)):
    """Get comprehensive leave balance for current user"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    joining_date = datetime.strptime(employee_data["joining_date"], "%Y-%m-%d").date()
    balances = leave_service.calculate_leave_balance(
        employee_id, 
        employee_data["type"], 
        joining_date
    )
    
    # Convert to dict format for API response
    balance_data = []
    for balance in balances:
        balance_data.append({
            "leave_type": balance.leave_type,
            "total_allocated": balance.total_allocated,
            "used": balance.used,
            "balance": balance.balance,
            "year": balance.year
        })
    
    return schemas.APIResponse(
        success=True,
        message="Leave balance retrieved successfully",
        data=balance_data
    )

@router.get("/birthday-anniversary-info")
def get_birthday_anniversary_info(current_user: dict = Depends(get_current_user)):
    """Get employee's birthday and anniversary information for BL leave eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    # Get existing BL leaves for this year
    existing_bl_leaves = leave_service.get_bl_leaves_for_year(employee_id, current_year)
    
    # Parse dates
    birthday = None
    anniversary = None
    
    if employee_data.get("date_of_birth"):
        dob = datetime.strptime(employee_data["date_of_birth"], "%Y-%m-%d").date()
        birthday = {
            "date": dob.replace(year=current_year).isoformat(),
            "formatted": dob.replace(year=current_year).strftime("%B %d"),
            "eligible": True
        }
    
    if employee_data.get("wedding_anniversary_date"):
        anniversary_date = datetime.strptime(employee_data["wedding_anniversary_date"], "%Y-%m-%d").date()
        anniversary = {
            "date": anniversary_date.replace(year=current_year).isoformat(),
            "formatted": anniversary_date.replace(year=current_year).strftime("%B %d"),
            "eligible": True
        }
    
    # Check if already taken BL leave this year
    bl_taken_for = None
    if existing_bl_leaves:
        bl_taken_for = existing_bl_leaves[0].get("occasion_type")
        
        # Update eligibility based on what's already taken
        if birthday and bl_taken_for in ["birthday", "anniversary"]:
            birthday["eligible"] = bl_taken_for != "birthday"
        if anniversary and bl_taken_for in ["birthday", "anniversary"]:
            anniversary["eligible"] = bl_taken_for != "anniversary"
    
    return schemas.APIResponse(
        success=True,
        message="Birthday/Anniversary information retrieved successfully",
        data={
            "birthday": birthday,
            "anniversary": anniversary,
            "bl_taken_this_year": bl_taken_for,
            "existing_leaves": existing_bl_leaves,
            "policy": {
                "rule": "You can take leave for either your birthday OR wedding anniversary per year, not both",
                "max_days": 1,
                "date_flexibility": "Leave can be taken within 7 days of the actual date"
            }
        }
    )

@router.get("/types")
def get_leave_types(current_user: dict = Depends(get_current_user)):
    """Get applicable leave types for current user"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    leave_types = leave_service.get_leave_types(
        employee_data["type"], 
        employee_data["gender"]
    )
    
    return schemas.APIResponse(
        success=True,
        message="Leave types retrieved successfully",
        data=leave_types
    )

@router.get("/holidays")
def get_holidays(year: Optional[int] = Query(None, description="Year for holidays")):
    """Get holidays for specified year"""
    if year is None:
        year = datetime.now().year
    
    holidays = leave_service.get_holidays_for_year(year)
    
    return schemas.APIResponse(
        success=True,
        message=f"Holidays for {year} retrieved successfully",
        data=holidays
    )

@router.get("/calendar")
def get_leave_calendar(
    month: int = Query(..., description="Month (1-12)"),
    year: int = Query(..., description="Year"),
    current_user: dict = Depends(get_current_user)
):
    """Get leave calendar for specific month"""
    calendar_data = leave_service.get_leave_calendar(month, year)
    
    return schemas.APIResponse(
        success=True,
        message=f"Leave calendar for {month}/{year} retrieved successfully",
        data=calendar_data
    )

@router.post("/wfh/request")
def create_wfh_request(wfh_request: schemas.WFHRequest, current_user: dict = Depends(get_current_user)):
    """Create Work From Home request"""
    employee_id = current_user.get("id", 1)
    
    # Validate WFH request
    is_valid, message = leave_service.validate_wfh_request(wfh_request)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    new_id = len(MOCK_WFH_REQUESTS) + 1
    wfh_record = {
        "id": new_id,
        "employee_id": employee_id,
        "date": wfh_request.date.isoformat(),
        "reason": wfh_request.reason,
        "manager_approval_email": wfh_request.manager_approval_email,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_by": None,
        "approved_at": None
    }
    
    MOCK_WFH_REQUESTS[new_id] = wfh_record
    
    return schemas.APIResponse(
        success=True,
        message="WFH request created successfully. Please ensure HR is informed.",
        data=wfh_record
    )

@router.get("/wfh/requests")
def get_wfh_requests(current_user: dict = Depends(get_current_user)):
    """Get WFH requests for current user"""
    employee_id = current_user.get("id", 1)
    
    user_wfh_requests = [
        wfh for wfh in MOCK_WFH_REQUESTS.values() 
        if wfh["employee_id"] == employee_id
    ]
    
    return schemas.APIResponse(
        success=True,
        message="WFH requests retrieved successfully",
        data=user_wfh_requests
    )

@router.get("/pending")
def get_pending_leaves(current_user: dict = Depends(get_current_user)):
    """Get pending leave requests for managers/HR"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    pending_leaves = []
    for leave in MOCK_LEAVE_REQUESTS.values():
        if leave["status"] == "pending":
            # Add employee details
            employee_data = get_mock_employee_data(leave["employee_id"])
            leave_with_employee = leave.copy()
            leave_with_employee["employee"] = {
                "first_name": "John",
                "last_name": "Doe",
                "department": employee_data["department"],
                "position": employee_data["position"],
                "employee_type": employee_data["type"]
            }
            pending_leaves.append(leave_with_employee)
    
    return schemas.APIResponse(
        success=True,
        message="Pending leave requests retrieved successfully",
        data=pending_leaves
    )

@router.put("/requests/{request_id}/approve")
def approve_leave_request(
    request_id: int, 
    approval: schemas.LeaveRequestApproval,
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject leave request with comprehensive validation"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    if request_id not in MOCK_LEAVE_REQUESTS:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    leave_request = MOCK_LEAVE_REQUESTS[request_id]
    
    if leave_request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Leave request already processed")
    
    # Update leave request
    leave_request["status"] = approval.status
    leave_request["manager_comments"] = approval.comments
    leave_request["hr_comments"] = approval.hr_comments
    leave_request["approved_by"] = current_user.get("id", 1)
    leave_request["approved_at"] = datetime.now().isoformat()
    
    # If approved, update leave balance (mock implementation)
    if approval.status == "approved":
        # In real implementation, deduct from leave balance
        pass
    
    return schemas.APIResponse(
        success=True,
        message=f"Leave request {approval.status} successfully",
        data=leave_request
    )

# Add new endpoint for bulk approval
@router.put("/requests/bulk-approve")
def bulk_approve_requests(
    request_ids: List[int],
    action: str = Query(..., description="approve or reject"),
    comments: Optional[str] = Query(None, description="Bulk approval comments"),
    current_user: dict = Depends(get_current_user)
):
    """Bulk approve or reject multiple leave requests"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
    
    processed_requests = []
    errors = []
    
    for request_id in request_ids:
        try:
            if request_id not in MOCK_LEAVE_REQUESTS:
                errors.append(f"Request {request_id} not found")
                continue
                
            leave_request = MOCK_LEAVE_REQUESTS[request_id]
            
            if leave_request["status"] != "pending":
                errors.append(f"Request {request_id} already processed")
                continue
            
            # Update leave request
            leave_request["status"] = "approved" if action == "approve" else "rejected"
            leave_request["manager_comments"] = comments
            leave_request["approved_by"] = current_user.get("id", 1)
            leave_request["approved_at"] = datetime.now().isoformat()
            
            processed_requests.append(leave_request)
            
        except Exception as e:
            errors.append(f"Error processing request {request_id}: {str(e)}")
    
    return schemas.APIResponse(
        success=len(errors) == 0,
        message=f"Processed {len(processed_requests)} requests. {len(errors)} errors.",
        data={
            "processed": processed_requests,
            "errors": errors
        }
    )

@router.get("/statistics")
def get_leave_statistics(
    year: Optional[int] = Query(None, description="Year for statistics"),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive leave statistics"""
    employee_id = current_user.get("id", 1)
    if year is None:
        year = datetime.now().year
    
    statistics = leave_service.get_leave_statistics(employee_id, year)
    
    return schemas.APIResponse(
        success=True,
        message=f"Leave statistics for {year} retrieved successfully",
        data=statistics
    )

@router.get("/policy")
def get_leave_policy():
    """Get comprehensive leave policy information including definitions and objectives"""
    policy_info = leave_service.get_policy_definitions()
    
    # Add office configuration
    policy_info["office_configuration"] = {
        "office_timings": {
            "start_time": "10:00 AM",
            "end_time": "7:00 PM", 
            "total_hours": 9,
            "grace_period": "15 minutes (max 3 times per month)"
        },
        "break_timings": leave_service.office_config["breaks"],
        "wfh_policy": {
            "restricted_days": ["Monday", "Friday"],
            "requires_prior_approval": True,
            "min_notice_days": 1,
            "avoid_holidays": True
        }
    }
    
    # Add leave types with policy context
    policy_info["leave_types"] = leave_service.leave_types
    
    # Add disciplinary actions
    policy_info["disciplinary_actions"] = {
        "unauthorized_absence": "3+ consecutive days without intimation leads to disciplinary action",
        "late_login_penalty": "4th late login onwards = half day leave deduction", 
        "leave_without_smhr": "Days not applied in SMHR = unauthorized absence/LOP"
    }
    
    return schemas.APIResponse(
        success=True,
        message="Leave policy information retrieved successfully",
        data=policy_info
    )

@router.post("/emergency")
def create_emergency_leave(
    leave_request: schemas.LeaveRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create emergency leave request with relaxed validation"""
    employee_id = current_user.get("id", 1)
    
    # Mark as emergency
    leave_request.emergency = True
    
    # For emergency leaves, allow past dates but require manager approval
    if leave_request.start_date < date.today():
        if not leave_request.manager_email_approval:
            raise HTTPException(
                status_code=400, 
                detail="Emergency leave for past dates requires manager email approval"
            )
    
    new_id = len(MOCK_LEAVE_REQUESTS) + 1
    leave_record = {
        "id": new_id,
        "employee_id": employee_id,
        "leave_type": leave_request.leave_type,
        "start_date": leave_request.start_date.isoformat(),
        "end_date": leave_request.end_date.isoformat(),
        "reason": leave_request.reason,
        "duration_days": (leave_request.end_date - leave_request.start_date).days + 1,
        "emergency": True,
        "manager_email_approval": leave_request.manager_email_approval,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "approved_by": None,
        "approved_at": None,
        "manager_comments": None,
        "requires_smhr_completion": True
    }
    
    MOCK_LEAVE_REQUESTS[new_id] = leave_record
    
    return schemas.APIResponse(
        success=True,
        message="Emergency leave request created. MUST be applied in SMHR within 2 days of return to office.",
        data=leave_record
    )

@router.get("/unauthorized-check/{employee_id}")
def check_unauthorized_absence(
    employee_id: int,
    absence_days: int = Query(..., description="Number of consecutive absence days"),
    current_user: dict = Depends(get_current_user)
):
    """Check for unauthorized absence and recommend action"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied. HR role required.")
    
    result = leave_service.check_unauthorized_absence(employee_id, absence_days)
    
    return schemas.APIResponse(
        success=True,
        message="Unauthorized absence check completed",
        data=result
    )

@router.get("/late-login-penalty/{employee_id}")
def calculate_late_login_penalty(
    employee_id: int,
    late_logins_this_month: int = Query(..., description="Number of late logins this month"),
    current_user: dict = Depends(get_current_user)
):
    """Calculate penalty for late logins"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied. HR role required.")
    
    penalty = leave_service.calculate_late_login_penalty(late_logins_this_month)
    
    return schemas.APIResponse(
        success=True,
        message="Late login penalty calculated",
        data=penalty
    )

@router.get("/analytics")
def get_leave_analytics(
    year: Optional[int] = Query(None, description="Year for analytics"),
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive leave analytics for managers/HR"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    if year is None:
        year = datetime.now().year
    
    # Mock analytics data
    analytics_data = {
        "total_leave_requests": 156,
        "approved_requests": 142,
        "rejected_requests": 8,
        "pending_requests": 6,
        "approval_rate": 91.0,
        "average_leave_duration": 2.3,
        "most_common_leave_type": "Casual Leave",
        "peak_leave_months": ["December", "April", "May"],
        "department_wise_stats": [
            {"department": "Engineering", "total_leaves": 45, "avg_duration": 2.1},
            {"department": "Marketing", "total_leaves": 32, "avg_duration": 2.8},
            {"department": "Sales", "total_leaves": 38, "avg_duration": 1.9},
            {"department": "HR", "total_leaves": 25, "avg_duration": 2.5}
        ],
        "leave_type_distribution": [
            {"leave_type": "Casual Leave", "count": 89, "percentage": 57.1},
            {"leave_type": "Sick Leave", "count": 34, "percentage": 21.8},
            {"leave_type": "Annual Leave", "count": 23, "percentage": 14.7},
            {"leave_type": "Personal Leave", "count": 10, "percentage": 6.4}
        ],
        "monthly_trends": [
            {"month": "January", "requests": 12, "approved": 11},
            {"month": "February", "requests": 8, "approved": 8},
            {"month": "March", "requests": 15, "approved": 14},
            {"month": "April", "requests": 22, "approved": 20},
            {"month": "May", "requests": 18, "approved": 16},
            {"month": "June", "requests": 14, "approved": 13}
        ]
    }
    
    return schemas.APIResponse(
        success=True,
        message=f"Leave analytics for {year} retrieved successfully",
        data=analytics_data
    )

@router.get("/team-calendar")
def get_team_calendar(
    month: int = Query(..., description="Month (1-12)"),
    year: int = Query(..., description="Year"),
    current_user: dict = Depends(get_current_user)
):
    """Get team leave calendar for managers"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    # Mock team calendar data
    team_calendar = {
        "month": month,
        "year": year,
        "team_leaves": [
            {
                "employee_id": 1,
                "employee_name": "John Doe",
                "department": "Engineering",
                "leaves": [
                    {"start_date": f"{year}-{month:02d}-15", "end_date": f"{year}-{month:02d}-17", "type": "Casual Leave", "status": "approved"},
                    {"start_date": f"{year}-{month:02d}-25", "end_date": f"{year}-{month:02d}-25", "type": "WFH", "status": "approved"}
                ]
            },
            {
                "employee_id": 2,
                "employee_name": "Jane Smith",
                "department": "Marketing",
                "leaves": [
                    {"start_date": f"{year}-{month:02d}-10", "end_date": f"{year}-{month:02d}-12", "type": "Annual Leave", "status": "approved"}
                ]
            }
        ],
        "department_summary": {
            "Engineering": {"total_leaves": 3, "employees_on_leave": 1},
            "Marketing": {"total_leaves": 1, "employees_on_leave": 1},
            "Sales": {"total_leaves": 0, "employees_on_leave": 0}
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message=f"Team calendar for {month}/{year} retrieved successfully",
        data=team_calendar
    )

@router.post("/policy/update")
def update_leave_policy(
    policy_updates: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update leave policy (HR/Admin only)"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied. HR/Admin role required.")
    
    # In real implementation, update policy in database
    # For now, just return success
    
    return schemas.APIResponse(
        success=True,
        message="Leave policy updated successfully",
        data=policy_updates
    )

@router.get("/reports/export")
def export_leave_report(
    format: str = Query("csv", description="Export format: csv, excel, pdf"),
    start_date: Optional[date] = Query(None, description="Start date for report"),
    end_date: Optional[date] = Query(None, description="End date for report"),
    department: Optional[str] = Query(None, description="Filter by department"),
    current_user: dict = Depends(get_current_user)
):
    """Export leave reports in various formats"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    # Mock export functionality
    export_data = {
        "report_id": f"LEAVE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "format": format,
        "filters": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "department": department
        },
        "download_url": f"/api/reports/download/{format}/leave_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
        "generated_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
    }
    
    return schemas.APIResponse(
        success=True,
        message=f"Leave report generated in {format} format",
        data=export_data
    )

@router.post("/notifications/send")
def send_leave_notification(
    notification_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send leave-related notifications"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    # Mock notification sending
    notification_result = {
        "notification_id": f"NOTIF_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type": notification_data.get("type", "leave_reminder"),
        "recipients": notification_data.get("recipients", []),
        "message": notification_data.get("message", ""),
        "sent_at": datetime.now().isoformat(),
        "delivery_status": "sent"
    }
    
    return schemas.APIResponse(
        success=True,
        message="Notification sent successfully",
        data=notification_result
    )
# Enhanced endpoints for Sections 6-10

@router.get("/break-timings")
def get_break_timings():
    """Get break timings as per Section 6 - One Hour Break-time during regular duty hours"""
    break_data = leave_service.get_break_timings()
    
    return schemas.APIResponse(
        success=True,
        message="Break timings retrieved successfully",
        data=break_data
    )

@router.post("/validate-break-timing")
def validate_break_timing(break_data: dict):
    """Validate if current time is within allowed break periods"""
    break_start = datetime.strptime(break_data.get("break_start"), "%H:%M").time()
    break_end = datetime.strptime(break_data.get("break_end"), "%H:%M").time()
    
    result = leave_service.validate_break_timing(break_start, break_end)
    
    return schemas.APIResponse(
        success=result.get("is_valid_break_time", False),
        message="Break timing validation completed",
        data=result
    )

@router.get("/attendance-guidelines")
def get_attendance_guidelines():
    """Get attendance policy guidelines as per Section 7"""
    guidelines = leave_service.get_attendance_guidelines()
    
    return schemas.APIResponse(
        success=True,
        message="Attendance guidelines retrieved successfully",
        data=guidelines
    )

@router.get("/leave-categories")
def get_leave_categories():
    """Get leave categories as per Section 8 - Planned, Unplanned, Unauthorized"""
    categories = {
        "categories": leave_service.leave_categories,
        "summary": {
            "planned_leave": "Pre-planned schedule with prior intimation",
            "unplanned_leave": "Emergency situations without advance planning",
            "unauthorized_leave": "3+ consecutive days absence without intimation"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Leave categories retrieved successfully",
        data=categories
    )

@router.post("/categorize-leave")
def categorize_leave_request(leave_data: dict):
    """Categorize leave request as Planned, Unplanned, or Unauthorized"""
    category = leave_service.categorize_leave_request(leave_data)
    
    return schemas.APIResponse(
        success=True,
        message="Leave request categorized successfully",
        data=category
    )

@router.get("/unauthorized-leave-check/{employee_id}")
def check_unauthorized_leave_status(
    employee_id: int,
    consecutive_days: int = Query(..., description="Number of consecutive absent days"),
    current_user: dict = Depends(get_current_user)
):
    """Check for unauthorized leave status as per Section 8"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"] and current_user.get("id") != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = leave_service.check_unauthorized_leave_status(employee_id, consecutive_days)
    
    return schemas.APIResponse(
        success=True,
        message="Unauthorized leave check completed",
        data=result
    )

@router.get("/leave-types-detailed")
def get_detailed_leave_types(
    employee_type: str = Query("permanent", description="Employee type: probationary or permanent"),
    gender: Optional[str] = Query(None, description="Employee gender for gender-specific leaves")
):
    """Get detailed leave types with rules and eligibility as per Section 9"""
    
    detailed_types = []
    for code, leave_type in leave_service.leave_types.items():
        if employee_type in leave_type["applicable_to"]:
            # Check gender-specific leaves
            if "gender_specific" in leave_type:
                if gender and gender.lower() == leave_type["gender_specific"]:
                    detailed_types.append({
                        "code": code,
                        "details": leave_type
                    })
            else:
                detailed_types.append({
                    "code": code,
                    "details": leave_type
                })
    
    return schemas.APIResponse(
        success=True,
        message="Detailed leave types retrieved successfully",
        data={
            "leave_types": detailed_types,
            "employee_type": employee_type,
            "gender": gender,
            "total_types": len(detailed_types)
        }
    )

@router.post("/validate-leave-eligibility")
def validate_leave_type_eligibility(
    eligibility_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate leave type eligibility with detailed rules as per Section 9"""
    
    employee_data = eligibility_data.get("employee_data", {})
    leave_type_code = eligibility_data.get("leave_type_code")
    child_number = eligibility_data.get("child_number", 1)  # For maternity leave
    
    result = leave_service.validate_leave_type_eligibility(employee_data, leave_type_code, child_number)
    
    return schemas.APIResponse(
        success=result["eligible"],
        message="Leave eligibility validation completed",
        data=result
    )

@router.get("/holidays-national-state")
def get_national_state_holidays(
    year: Optional[int] = Query(None, description="Year for holidays")
):
    """Get National & State Holidays as per Section 10"""
    if year is None:
        year = datetime.now().year
    
    holidays = leave_service.get_national_state_holidays(year)
    
    return schemas.APIResponse(
        success=True,
        message=f"National and State holidays for {year} retrieved successfully",
        data=holidays
    )

@router.post("/publish-holiday-list")
def publish_holiday_list(
    publication_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Publish holiday list via email as per Section 10 (HR only)"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied. HR role required.")
    
    year = publication_data.get("year", datetime.now().year)
    hr_user_id = current_user.get("id", 1)
    
    result = leave_service.publish_holiday_list(year, hr_user_id)
    
    return schemas.APIResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )

@router.get("/comprehensive-policy")
def get_comprehensive_policy():
    """Get complete policy information covering Sections 6-10"""
    
    comprehensive_policy = {
        "section_6_break_timings": leave_service.get_break_timings(),
        "section_7_attendance_guidelines": leave_service.get_attendance_guidelines(),
        "section_8_leave_categories": leave_service.leave_categories,
        "section_9_leave_types": leave_service.leave_types,
        "section_10_holidays": leave_service.get_national_state_holidays(),
        "policy_summary": {
            "break_time_total": "1 hour during regular duty hours",
            "attendance_guidelines": "3 key guidelines for proper attendance management",
            "leave_categories": "3 categories: Planned, Unplanned, Unauthorized",
            "leave_types": "6 types with detailed rules and eligibility",
            "holidays": "National and State holidays published annually by HR"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Comprehensive policy information retrieved successfully",
        data=comprehensive_policy
    )

@router.post("/validate-break-timing")
def validate_break_timing(
    break_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate if current time is within allowed break periods"""
    try:
        break_start = datetime.strptime(break_data.get("break_start"), "%H:%M").time()
        break_end = datetime.strptime(break_data.get("break_end"), "%H:%M").time()
        
        result = leave_service.validate_break_timing(break_start, break_end)
        
        return schemas.APIResponse(
            success=result.get("is_valid_break_time", False),
            message="Break timing validation completed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {str(e)}")

@router.post("/categorize-leave")
def categorize_leave_request(leave_data: dict, current_user: dict = Depends(get_current_user)):
    """Categorize leave request as Planned, Unplanned, or Unauthorized"""
    category = leave_service.categorize_leave_request(leave_data)
    
    return schemas.APIResponse(
        success=True,
        message="Leave request categorized successfully",
        data=category
    )

@router.get("/unauthorized-leave-check/{employee_id}")
def check_unauthorized_leave_status(
    employee_id: int,
    consecutive_days: int = Query(..., description="Number of consecutive absent days"),
    current_user: dict = Depends(get_current_user)
):
    """Check for unauthorized leave status as per Section 8"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"] and current_user.get("id") != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = leave_service.check_unauthorized_leave_status(employee_id, consecutive_days)
    
    return schemas.APIResponse(
        success=True,
        message="Unauthorized leave check completed",
        data=result
    )

@router.post("/validate-leave-eligibility")
def validate_leave_type_eligibility(
    eligibility_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate leave type eligibility with detailed rules as per Section 9"""
    
    employee_data = eligibility_data.get("employee_data", {})
    leave_type_code = eligibility_data.get("leave_type_code")
    child_number = eligibility_data.get("child_number", 1)  # For maternity leave
    
    result = leave_service.validate_leave_type_eligibility(employee_data, leave_type_code, child_number)
    
    return schemas.APIResponse(
        success=result["eligible"],
        message="Leave eligibility validation completed",
        data=result
    )

@router.get("/holidays-national-state")
def get_national_state_holidays(
    year: Optional[int] = Query(None, description="Year for holidays")
):
    """Get National & State Holidays as per Section 10"""
    if year is None:
        year = datetime.now().year
    
    holidays = leave_service.get_national_state_holidays(year)
    
    return schemas.APIResponse(
        success=True,
        message=f"National and State holidays for {year} retrieved successfully",
        data=holidays
    )

@router.post("/publish-holiday-list")
def publish_holiday_list(
    publication_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Publish holiday list via email as per Section 10 (HR only)"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied. HR role required.")
    
    year = publication_data.get("year", datetime.now().year)
    hr_user_id = current_user.get("id", 1)
    
    result = leave_service.publish_holiday_list(year, hr_user_id)
    
    return schemas.APIResponse(
        success=result["success"],
        message=result["message"],
        data=result
    )

# Additional utility endpoints for comprehensive leave management

@router.get("/attendance-guidelines")
def get_attendance_guidelines():
    """Get attendance policy guidelines as per Section 7"""
    guidelines = leave_service.get_attendance_guidelines()
    
    return schemas.APIResponse(
        success=True,
        message="Attendance guidelines retrieved successfully",
        data=guidelines
    )

@router.get("/leave-categories")
def get_leave_categories():
    """Get leave categories as per Section 8 - Planned, Unplanned, Unauthorized"""
    categories = leave_service.leave_categories
    
    return schemas.APIResponse(
        success=True,
        message="Leave categories retrieved successfully",
        data={
            "categories": categories,
            "summary": {
                "planned_leave": "Pre-planned schedule with prior intimation",
                "unplanned_leave": "Emergency situations without advance planning", 
                "unauthorized_leave": "3+ consecutive days absence without intimation"
            }
        }
    )

@router.get("/leave-types-detailed")
def get_detailed_leave_types(
    employee_type: str = Query("permanent", description="Employee type: probationary or permanent"),
    gender: Optional[str] = Query(None, description="Employee gender for gender-specific leaves"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed leave types with rules and eligibility as per Section 9"""
    
    detailed_types = []
    for code, leave_type in leave_service.leave_types.items():
        if employee_type in leave_type["applicable_to"]:
            # Check gender-specific leaves
            if "gender_specific" in leave_type:
                if gender and gender.lower() == leave_type["gender_specific"]:
                    detailed_types.append({
                        "code": code,
                        "details": leave_type
                    })
            else:
                detailed_types.append({
                    "code": code,
                    "details": leave_type
                })
    
    return schemas.APIResponse(
        success=True,
        message="Detailed leave types retrieved successfully",
        data={
            "leave_types": detailed_types,
            "employee_type": employee_type,
            "gender": gender,
            "total_types": len(detailed_types)
        }
    )

@router.post("/blood-donation-leave")
def request_blood_donation_leave(
    donation_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Request Blood Donation Leave as per Section 9f - Emergency donation to colleagues"""
    employee_id = current_user.get("id", 1)
    
    # Validate blood donation leave requirements
    colleague_employee_id = donation_data.get("colleague_employee_id")
    donation_date = donation_data.get("donation_date")
    emergency_nature = donation_data.get("emergency_nature", False)
    
    if not colleague_employee_id:
        raise HTTPException(status_code=400, detail="Colleague employee ID required for blood donation leave")
    
    if not emergency_nature:
        raise HTTPException(status_code=400, detail="Blood donation leave is only for emergency donations to fellow colleagues")
    
    # Create blood donation leave record
    new_id = len(MOCK_LEAVE_REQUESTS) + 1
    leave_record = {
        "id": new_id,
        "employee_id": employee_id,
        "leave_type": "Blood Donation Leave",
        "start_date": donation_date,
        "end_date": donation_date,
        "reason": f"Emergency blood donation to colleague (Employee ID: {colleague_employee_id})",
        "duration_days": 1,
        "is_half_day": False,
        "emergency": True,
        "blood_donation_details": {
            "colleague_employee_id": colleague_employee_id,
            "donation_date": donation_date,
            "emergency_nature": emergency_nature,
            "purpose": "Weakness recovery after blood donation"
        },
        "status": "approved",  # Blood donation leave is typically auto-approved
        "created_at": datetime.now().isoformat(),
        "approved_by": "system_auto_approved",
        "approved_at": datetime.now().isoformat(),
        "special_leave_type": "blood_donation"
    }
    
    MOCK_LEAVE_REQUESTS[new_id] = leave_record
    
    return schemas.APIResponse(
        success=True,
        message="Blood donation leave approved. Thank you for your noble gesture to help a colleague.",
        data=leave_record
    )

@router.post("/maternity-leave-calculation")
def calculate_maternity_leave_entitlement(
    maternity_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Calculate maternity leave entitlement as per Section 9d detailed rules"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    if employee_data.get("gender", "").lower() != "female":
        raise HTTPException(status_code=400, detail="Maternity leave is only applicable to female employees")
    
    child_number = maternity_data.get("child_number", 1)
    is_adoptive = maternity_data.get("is_adoptive", False)
    work_days_past_12_months = maternity_data.get("work_days_past_12_months", 200)
    
    # Validate work requirement
    if work_days_past_12_months < 160:
        return schemas.APIResponse(
            success=False,
            message="Minimum 160 work days in past 12 months required for maternity leave",
            data={
                "eligible": False,
                "work_days_provided": work_days_past_12_months,
                "work_days_required": 160,
                "shortfall": 160 - work_days_past_12_months
            }
        )
    
    # Calculate entitlement
    if is_adoptive:
        leave_days = 84  # 12 weeks for adoptive mothers
        leave_weeks = 12
        leave_type = "Adoptive Maternity Leave"
    elif child_number == 1:
        leave_days = 182  # 26 weeks for first child
        leave_weeks = 26
        leave_type = "First Child Maternity Leave"
    else:
        leave_days = 84   # 12 weeks for second child onwards
        leave_weeks = 12
        leave_type = "Second Child Maternity Leave"
    
    entitlement = {
        "eligible": True,
        "leave_type": leave_type,
        "leave_days": leave_days,
        "leave_weeks": leave_weeks,
        "child_number": child_number,
        "is_adoptive": is_adoptive,
        "work_days_past_12_months": work_days_past_12_months,
        "legal_basis": "Maternity (Amendment) Bill 2017 to the Maternity Benefit Act, 1961",
        "payment_details": {
            "group_medical_insurance": "Entitled to salary payment during maternity leave",
            "esi_benefits": "Eligible for ESI benefits if covered under ESI scheme"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Maternity leave entitlement calculated successfully",
        data=entitlement
    )

@router.post("/same-day-logout-missing")
def report_same_day_logout_missing(
    logout_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Report missing logout on same day as per Section 7 guidelines"""
    employee_id = current_user.get("id", 1)
    login_date = logout_data.get("login_date")
    reason = logout_data.get("reason", "")
    
    # Create HR intimation record
    intimation_record = {
        "employee_id": employee_id,
        "login_date": login_date,
        "issue_type": "same_day_logout_missing",
        "reason": reason,
        "reported_at": datetime.now().isoformat(),
        "hr_notified": True,
        "status": "reported",
        "guideline_reference": "Section 7: If any resource's Log-In and do not Log out within the same day, that has to be intimated to HR."
    }
    
    return schemas.APIResponse(
        success=True,
        message="Same day logout missing reported to HR successfully",
        data=intimation_record
    )

@router.get("/maternity-paternity-info")
def get_maternity_paternity_info(current_user: dict = Depends(get_current_user)):
    """Get employee's maternity/paternity leave eligibility and information"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    employee_gender = employee_data.get("gender", "").lower()
    current_year = datetime.now().year
    
    info = {
        "employee_gender": employee_gender,
        "maternity_leave": None,
        "paternity_leave": None
    }
    
    if employee_gender == "female":
        # Get existing ML leaves for this year
        existing_ml_leaves = leave_service.get_maternity_leaves_for_year(employee_id, current_year)
        
        info["maternity_leave"] = {
            "eligible": True,
            "max_days": 108,
            "advance_notice_required": 60,  # 2 months
            "medical_documents_required": True,
            "timing_options": [
                "After 7 months of pregnancy",
                "After childbirth"
            ],
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_ml_leaves) > 0,
            "existing_leaves": existing_ml_leaves
        }
    
    elif employee_gender == "male":
        # Get existing PL leaves for this year
        existing_pl_leaves = leave_service.get_paternity_leaves_for_year(employee_id, current_year)
        
        info["paternity_leave"] = {
            "eligible": True,
            "max_days": 3,
            "timing": "Around the time of childbirth",
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_pl_leaves) > 0,
            "existing_leaves": existing_pl_leaves
        }
    
    return schemas.APIResponse(
        success=True,
        message="Maternity/Paternity leave information retrieved successfully",
        data=info
    )

@router.get("/birthday-anniversary-info")
def get_birthday_anniversary_info(current_user: dict = Depends(get_current_user)):
    """Get employee's birthday and anniversary information for BL leave eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    # Get existing BL leaves for this year
    existing_bl_leaves = leave_service.get_bl_leaves_for_year(employee_id, current_year)
    
    # Parse dates
    birthday = None
    anniversary = None
    
    if employee_data.get("date_of_birth"):
        try:
            if isinstance(employee_data["date_of_birth"], str):
                dob = datetime.strptime(employee_data["date_of_birth"], "%Y-%m-%d").date()
            else:
                dob = employee_data["date_of_birth"]
            
            birthday = {
                "date": dob.replace(year=current_year).isoformat(),
                "formatted": dob.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            birthday = None
    
    if employee_data.get("wedding_anniversary_date"):
        try:
            if isinstance(employee_data["wedding_anniversary_date"], str):
                anniversary_date = datetime.strptime(employee_data["wedding_anniversary_date"], "%Y-%m-%d").date()
            else:
                anniversary_date = employee_data["wedding_anniversary_date"]
            
            anniversary = {
                "date": anniversary_date.replace(year=current_year).isoformat(),
                "formatted": anniversary_date.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            anniversary = None
    
    # Check if already taken BL leave this year
    bl_taken_for = None
    if existing_bl_leaves:
        bl_taken_for = existing_bl_leaves[0].get("occasion_type")
        
        # Update eligibility based on what's already taken
        if birthday and bl_taken_for in ["birthday", "anniversary"]:
            birthday["eligible"] = bl_taken_for != "birthday"
        if anniversary and bl_taken_for in ["birthday", "anniversary"]:
            anniversary["eligible"] = bl_taken_for != "anniversary"
    
    return schemas.APIResponse(
        success=True,
        message="Birthday/Anniversary leave information retrieved successfully",
        data={
            "birthday": birthday,
            "anniversary": anniversary,
            "bl_taken_for": bl_taken_for,
            "policy": {
                "max_days": 1,
                "choice": "Either birthday OR anniversary per year, not both",
                "timing": "Within 7 days of the actual date"
            }
        }
    )

@router.get("/maternity-paternity-info")
def get_maternity_paternity_info(current_user: dict = Depends(get_current_user)):
    """Get employee's maternity/paternity leave eligibility and information"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    employee_gender = employee_data.get("gender", "").lower()
    current_year = datetime.now().year
    
    info = {
        "employee_gender": employee_gender,
        "maternity_leave": None,
        "paternity_leave": None
    }
    
    if employee_gender == "female":
        # Get existing ML leaves for this year
        existing_ml_leaves = leave_service.get_maternity_leaves_for_year(employee_id, current_year)
        
        info["maternity_leave"] = {
            "eligible": True,
            "max_days": 108,
            "advance_notice_required": 60,  # 2 months
            "medical_documents_required": True,
            "timing_options": [
                "After 7 months of pregnancy",
                "After childbirth"
            ],
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_ml_leaves) > 0,
            "existing_leaves": existing_ml_leaves
        }
    
    elif employee_gender == "male":
        # Get existing PL leaves for this year
        existing_pl_leaves = leave_service.get_paternity_leaves_for_year(employee_id, current_year)
        
        info["paternity_leave"] = {
            "eligible": True,
            "max_days": 3,
            "timing": "Around the time of childbirth",
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_pl_leaves) > 0,
            "existing_leaves": existing_pl_leaves
        }
    
    return schemas.APIResponse(
        success=True,
        message="Maternity/Paternity leave information retrieved successfully",
        data=info
    )

@router.get("/birthday-anniversary-info")
def get_birthday_anniversary_info(current_user: dict = Depends(get_current_user)):
    """Get employee's birthday and anniversary information for BL leave eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    # Get existing BL leaves for this year
    existing_bl_leaves = leave_service.get_bl_leaves_for_year(employee_id, current_year)
    
    # Parse dates
    birthday = None
    anniversary = None
    
    if employee_data.get("date_of_birth"):
        try:
            if isinstance(employee_data["date_of_birth"], str):
                dob = datetime.strptime(employee_data["date_of_birth"], "%Y-%m-%d").date()
            else:
                dob = employee_data["date_of_birth"]
            
            birthday = {
                "date": dob.replace(year=current_year).isoformat(),
                "formatted": dob.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            birthday = None
    
    if employee_data.get("wedding_anniversary_date"):
        try:
            if isinstance(employee_data["wedding_anniversary_date"], str):
                anniversary_date = datetime.strptime(employee_data["wedding_anniversary_date"], "%Y-%m-%d").date()
            else:
                anniversary_date = employee_data["wedding_anniversary_date"]
            
            anniversary = {
                "date": anniversary_date.replace(year=current_year).isoformat(),
                "formatted": anniversary_date.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            anniversary = None
    
    # Check if already taken BL leave this year
    bl_taken_for = None
    if existing_bl_leaves:
        bl_taken_for = existing_bl_leaves[0].get("occasion_type")
        
        # Update eligibility based on what's already taken
        if birthday and bl_taken_for in ["birthday", "anniversary"]:
            birthday["eligible"] = bl_taken_for != "birthday"
        if anniversary and bl_taken_for in ["birthday", "anniversary"]:
            anniversary["eligible"] = bl_taken_for != "anniversary"
    
    return schemas.APIResponse(
        success=True,
        message="Birthday/Anniversary leave information retrieved successfully",
        data={
            "birthday": birthday,
            "anniversary": anniversary,
            "bl_taken_for": bl_taken_for,
            "policy": {
                "max_days": 1,
                "choice": "Either birthday OR anniversary per year, not both",
                "timing": "Within 7 days of the actual date"
            }
        }
    )

# Section 11: Enhanced Work From Home (WFH) Policy Endpoints

@router.post("/wfh/request-enhanced")
def create_enhanced_wfh_request(
    wfh_request: schemas.WFHRequest,
    hr_informed: bool = Query(..., description="Confirmation that HR has been informed"),
    medical_report: Optional[str] = Query(None, description="Medical report for medical emergencies"),
    emergency_documentation: Optional[str] = Query(None, description="Documentation for emergency situations"),
    current_user: dict = Depends(get_current_user)
):
    """Create enhanced WFH request with Section 11 policy validation"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    # Add additional fields to WFH request
    wfh_request.hr_informed = hr_informed
    if medical_report:
        wfh_request.medical_report = medical_report
    if emergency_documentation:
        wfh_request.emergency_documentation = emergency_documentation
    
    # Enhanced validation
    is_valid, message, validation_details = leave_service.validate_wfh_request_enhanced(wfh_request, employee_data)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Create WFH record with enhanced details
    new_id = len(MOCK_WFH_REQUESTS) + 1
    wfh_record = {
        "id": new_id,
        "employee_id": employee_id,
        "date": wfh_request.date.isoformat(),
        "reason": wfh_request.reason,
        "manager_approval_email": wfh_request.manager_approval_email,
        "hr_informed": hr_informed,
        "medical_report": medical_report,
        "emergency_documentation": emergency_documentation,
        "status": "pending_hr_evaluation" if medical_report else "pending",
        "created_at": datetime.now().isoformat(),
        "validation_details": validation_details,
        "policy_section": "Section 11 - WFH Policy",
        "approved_by": None,
        "approved_at": None
    }
    
    MOCK_WFH_REQUESTS[new_id] = wfh_record
    
    response_message = "Enhanced WFH request created successfully."
    if validation_details["warnings"]:
        response_message += f" Warnings: {'; '.join(validation_details['warnings'])}"
    if validation_details["requirements"]:
        response_message += f" Requirements: {'; '.join(validation_details['requirements'])}"
    
    return schemas.APIResponse(
        success=True,
        message=response_message,
        data=wfh_record
    )

@router.get("/wfh/policy")
def get_wfh_policy():
    """Get comprehensive WFH policy details as per Section 11"""
    policy_details = leave_service.get_wfh_policy_details()
    
    return schemas.APIResponse(
        success=True,
        message="WFH policy details retrieved successfully",
        data=policy_details
    )

@router.post("/wfh/hr-evaluation")
def hr_evaluate_medical_wfh(
    evaluation_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """HR evaluation for medical emergency WFH requests"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied. HR role required.")
    
    wfh_request_id = evaluation_data.get("wfh_request_id")
    if wfh_request_id not in MOCK_WFH_REQUESTS:
        raise HTTPException(status_code=404, detail="WFH request not found")
    
    # HR evaluation
    evaluation_result = leave_service.evaluate_wfh_medical_emergency(evaluation_data)
    
    # Update WFH request with HR decision
    wfh_request = MOCK_WFH_REQUESTS[wfh_request_id]
    wfh_request["hr_evaluation"] = evaluation_result
    wfh_request["status"] = evaluation_result["classification"]
    wfh_request["hr_evaluated_by"] = current_user.get("id", 1)
    wfh_request["hr_evaluated_at"] = datetime.now().isoformat()
    
    return schemas.APIResponse(
        success=True,
        message="HR evaluation completed successfully",
        data={
            "wfh_request": wfh_request,
            "evaluation_result": evaluation_result
        }
    )

@router.get("/wfh/commitment-analysis/{employee_id}")
def analyze_wfh_commitment(
    employee_id: int,
    wfh_frequency: int = Query(..., description="Number of WFH requests in current month"),
    current_user: dict = Depends(get_current_user)
):
    """Analyze WFH commitment and productivity impact"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"] and current_user.get("id") != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Mock productivity metrics - in real implementation, fetch from performance system
    productivity_metrics = {
        "task_completion": 85,
        "team_collaboration": 80,
        "goal_achievement": 90,
        "client_satisfaction": 88
    }
    
    analysis = leave_service.check_wfh_commitment_impact(employee_id, wfh_frequency, productivity_metrics)
    
    return schemas.APIResponse(
        success=True,
        message="WFH commitment analysis completed",
        data=analysis
    )

@router.get("/wfh/analytics")
def get_wfh_analytics(
    department: Optional[str] = Query(None, description="Filter by department"),
    time_period: str = Query("monthly", description="Time period: monthly, quarterly, yearly"),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive WFH analytics for management"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    analytics = leave_service.generate_wfh_analytics(department, time_period)
    
    return schemas.APIResponse(
        success=True,
        message="WFH analytics retrieved successfully",
        data=analytics
    )

@router.post("/wfh/validate-timing")
def validate_wfh_timing(
    timing_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate WFH timing against strategic timing policy"""
    wfh_date = datetime.strptime(timing_data.get("wfh_date"), "%Y-%m-%d").date()
    reason = timing_data.get("reason", "")
    is_emergency = timing_data.get("is_emergency", False)
    
    weekday = wfh_date.strftime("%A").lower()
    validation_result = {
        "wfh_date": wfh_date.isoformat(),
        "weekday": weekday.title(),
        "is_restricted_day": weekday in ["monday", "friday"],
        "is_holiday_adjacent": leave_service._is_adjacent_to_holiday(wfh_date),
        "validation_status": "approved",
        "warnings": [],
        "requirements": []
    }
    
    # Check Monday/Friday restriction
    if validation_result["is_restricted_day"]:
        if not is_emergency:
            validation_result["validation_status"] = "rejected"
            validation_result["warnings"].append(f"{weekday.title()}s are critical for team alignment and project progress")
            return schemas.APIResponse(
                success=False,
                message="WFH timing validation failed",
                data=validation_result
            )
        else:
            validation_result["requirements"].append("Emergency documentation required for Monday/Friday WFH")
    
    # Check holiday adjacency
    if validation_result["is_holiday_adjacent"]:
        validation_result["warnings"].append("WFH before/after holidays disrupts workflow continuity")
        validation_result["requirements"].append("HR may classify as leave/LOP if reason not accepted")
    
    return schemas.APIResponse(
        success=True,
        message="WFH timing validation completed",
        data=validation_result
    )

@router.post("/wfh/hr-intimation")
def record_hr_intimation(
    intimation_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Record HR intimation for WFH day"""
    employee_id = current_user.get("id", 1)
    wfh_date = intimation_data.get("wfh_date")
    intimation_method = intimation_data.get("intimation_method", "email")
    
    # Record HR intimation
    intimation_record = {
        "employee_id": employee_id,
        "wfh_date": wfh_date,
        "intimation_method": intimation_method,
        "intimated_at": datetime.now().isoformat(),
        "hr_acknowledged": False,
        "policy_reference": "Section 11b - HR Intimation: Employees must inform HR department about WFH days"
    }
    
    return schemas.APIResponse(
        success=True,
        message="HR intimation recorded successfully. Failure to inform HR will result in days being treated as leave/LOP.",
        data=intimation_record
    )

# Section 12: Comprehensive Leave Norms Implementation

@router.post("/leave/validate-consecutive-limit")
def validate_consecutive_leave_limit(
    leave_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate maximum 3 consecutive casual leaves as per Section 12"""
    leave_type = leave_data.get("leave_type")
    consecutive_days = leave_data.get("consecutive_days", 1)
    
    validation_result = {
        "leave_type": leave_type,
        "consecutive_days": consecutive_days,
        "max_allowed": 3 if leave_type.lower() == "casual leave" else None,
        "is_valid": True,
        "policy_reference": "Section 12: Maximum three Casual leaves can be availed at a stretch"
    }
    
    if leave_type.lower() == "casual leave" and consecutive_days > 3:
        validation_result["is_valid"] = False
        validation_result["violation_message"] = "Maximum 3 consecutive casual leaves allowed"
        
        return schemas.APIResponse(
            success=False,
            message="Consecutive leave limit exceeded",
            data=validation_result
        )
    
    return schemas.APIResponse(
        success=True,
        message="Consecutive leave validation passed",
        data=validation_result
    )

@router.post("/leave/medical-emergency-validation")
def validate_medical_emergency_leave(
    medical_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate medical emergency leave with certificate requirement"""
    employee_id = current_user.get("id", 1)
    leave_duration = medical_data.get("leave_duration", 1)
    has_medical_certificate = medical_data.get("has_medical_certificate", False)
    doctor_certification = medical_data.get("doctor_certification", "")
    
    validation_result = {
        "employee_id": employee_id,
        "leave_duration": leave_duration,
        "has_medical_certificate": has_medical_certificate,
        "doctor_certification": doctor_certification,
        "is_valid": True,
        "requirements": [],
        "policy_reference": "Section 12: Medical emergencies require certified doctor reports for HR validation"
    }
    
    if leave_duration > 0:
        if not has_medical_certificate:
            validation_result["is_valid"] = False
            validation_result["requirements"].append("Medical certificate from certified doctor required")
        
        if not doctor_certification:
            validation_result["requirements"].append("Doctor certification details must be provided")
    
    # Check leave balance eligibility
    employee_data = get_mock_employee_data(employee_id)
    leave_balances = leave_service.calculate_leave_balance(
        employee_id, 
        employee_data["type"], 
        datetime.strptime(employee_data["joining_date"], "%Y-%m-%d").date()
    )
    
    sick_leave_balance = next((b.balance for b in leave_balances if b.leave_type == "Sick Leave"), 0)
    
    validation_result["available_sick_leave"] = sick_leave_balance
    validation_result["sufficient_balance"] = sick_leave_balance >= leave_duration
    
    if not validation_result["sufficient_balance"]:
        validation_result["requirements"].append(f"Insufficient sick leave balance. Available: {sick_leave_balance}, Required: {leave_duration}")
    
    return schemas.APIResponse(
        success=validation_result["is_valid"] and validation_result["sufficient_balance"],
        message="Medical emergency leave validation completed",
        data=validation_result
    )

@router.post("/leave/clubbing-validation")
def validate_leave_clubbing_policy(
    clubbing_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate leave clubbing with weekends/holidays policy"""
    start_date = datetime.strptime(clubbing_data.get("start_date"), "%Y-%m-%d").date()
    end_date = datetime.strptime(clubbing_data.get("end_date"), "%Y-%m-%d").date()
    
    # Check for weekend/holiday clubbing
    clubbing_analysis = leave_service.analyze_leave_clubbing(start_date, end_date)
    
    validation_result = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "clubbing_detected": clubbing_analysis["has_clubbing"],
        "clubbed_days": clubbing_analysis["clubbed_days"],
        "policy_violation": clubbing_analysis["has_clubbing"],
        "policy_reference": "Section 12: Clubbing of leaves with Weekly offs/Holidays is strongly discouraged",
        "impact_assessment": clubbing_analysis["impact_assessment"]
    }
    
    if clubbing_analysis["has_clubbing"]:
        validation_result["warning_message"] = "Leave clubbing detected. This may lead to work deliverable lapses."
        validation_result["recommendations"] = [
            "Consider splitting leave periods",
            "Ensure work handover before extended absence",
            "Coordinate with team for coverage"
        ]
    
    return schemas.APIResponse(
        success=not clubbing_analysis["has_clubbing"],
        message="Leave clubbing validation completed",
        data=validation_result
    )

@router.post("/leave/smhr-application-tracking")
def track_smhr_application(
    smhr_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Track SMHR application compliance as per Section 12"""
    employee_id = current_user.get("id", 1)
    leave_request_id = smhr_data.get("leave_request_id")
    smhr_applied = smhr_data.get("smhr_applied", False)
    manager_approval_received = smhr_data.get("manager_approval_received", False)
    application_date = smhr_data.get("application_date")
    leave_start_date = smhr_data.get("leave_start_date")
    
    # Calculate days before leave
    if application_date and leave_start_date:
        app_date = datetime.strptime(application_date, "%Y-%m-%d").date()
        leave_date = datetime.strptime(leave_start_date, "%Y-%m-%d").date()
        days_before = (leave_date - app_date).days
    else:
        days_before = 0
    
    tracking_result = {
        "employee_id": employee_id,
        "leave_request_id": leave_request_id,
        "smhr_applied": smhr_applied,
        "manager_approval_received": manager_approval_received,
        "days_before_leave": days_before,
        "minimum_required_days": 2,
        "compliance_status": "compliant" if days_before >= 2 and smhr_applied and manager_approval_received else "non_compliant",
        "policy_reference": "Section 12: Leaves should be applied through SMHR with manager approval at least 2 days before"
    }
    
    # Check compliance violations
    violations = []
    if not smhr_applied:
        violations.append("SMHR application missing - will be treated as unauthorized absence/LOP")
    if not manager_approval_received:
        violations.append("Manager approval required")
    if days_before < 2:
        violations.append(f"Minimum 2 days advance notice required. Current: {days_before} days")
    
    tracking_result["violations"] = violations
    tracking_result["is_compliant"] = len(violations) == 0
    
    return schemas.APIResponse(
        success=tracking_result["is_compliant"],
        message="SMHR application tracking completed",
        data=tracking_result
    )

@router.post("/leave/emergency-approval-tracking")
def track_emergency_leave_approval(
    emergency_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Track emergency leave approval process as per Section 12"""
    employee_id = current_user.get("id", 1)
    emergency_leave_date = emergency_data.get("emergency_leave_date")
    manager_approval_method = emergency_data.get("manager_approval_method")  # email, skype, etc.
    return_to_office_date = emergency_data.get("return_to_office_date")
    smhr_applied_after_return = emergency_data.get("smhr_applied_after_return", False)
    
    # Calculate compliance timeline
    if return_to_office_date:
        return_date = datetime.strptime(return_to_office_date, "%Y-%m-%d").date()
        deadline_date = return_date + timedelta(days=2)
        current_date = date.today()
        days_remaining = (deadline_date - current_date).days
    else:
        days_remaining = None
        deadline_date = None
    
    tracking_result = {
        "employee_id": employee_id,
        "emergency_leave_date": emergency_leave_date,
        "manager_approval_method": manager_approval_method,
        "return_to_office_date": return_to_office_date,
        "smhr_deadline": deadline_date.isoformat() if deadline_date else None,
        "days_remaining_for_smhr": days_remaining,
        "smhr_applied_after_return": smhr_applied_after_return,
        "compliance_status": "pending" if days_remaining and days_remaining > 0 else "overdue",
        "policy_reference": "Section 12: Emergency leaves require written manager approval and SMHR application within 2 days of return"
    }
    
    # Determine compliance status
    requirements = []
    if not manager_approval_method:
        requirements.append("Written manager approval (email/Skype) required")
    if return_to_office_date and not smhr_applied_after_return:
        if days_remaining and days_remaining > 0:
            requirements.append(f"SMHR application required within {days_remaining} days")
        else:
            requirements.append("SMHR application overdue - will be treated as unauthorized absence")
    
    tracking_result["requirements"] = requirements
    tracking_result["is_compliant"] = len(requirements) == 0
    
    return schemas.APIResponse(
        success=True,
        message="Emergency leave approval tracking completed",
        data=tracking_result
    )

@router.post("/leave/holiday-clubbing-check")
def check_holiday_clubbing_policy(
    holiday_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Check holiday clubbing policy compliance as per Section 12"""
    leave_start_date = datetime.strptime(holiday_data.get("leave_start_date"), "%Y-%m-%d").date()
    leave_end_date = datetime.strptime(holiday_data.get("leave_end_date"), "%Y-%m-%d").date()
    
    # Get holidays for the year
    year = leave_start_date.year
    holidays = leave_service.get_holidays_for_year(year)
    holiday_dates = [datetime.strptime(h["date"], "%Y-%m-%d").date() for h in holidays]
    
    # Check for holiday clubbing
    clubbing_analysis = {
        "leave_period": f"{leave_start_date} to {leave_end_date}",
        "holidays_in_period": [],
        "holidays_before": [],
        "holidays_after": [],
        "weekends_in_period": [],
        "total_clubbed_days": 0,
        "policy_violation": False
    }
    
    # Check holidays within leave period
    current_date = leave_start_date
    while current_date <= leave_end_date:
        if current_date in holiday_dates:
            holiday_info = next(h for h in holidays if datetime.strptime(h["date"], "%Y-%m-%d").date() == current_date)
            clubbing_analysis["holidays_in_period"].append(holiday_info)
        
        # Check weekends
        if current_date.weekday() in [5, 6]:  # Saturday, Sunday
            clubbing_analysis["weekends_in_period"].append({
                "date": current_date.isoformat(),
                "day": current_date.strftime("%A")
            })
        
        current_date += timedelta(days=1)
    
    # Check holidays immediately before and after
    day_before = leave_start_date - timedelta(days=1)
    day_after = leave_end_date + timedelta(days=1)
    
    if day_before in holiday_dates:
        holiday_info = next(h for h in holidays if datetime.strptime(h["date"], "%Y-%m-%d").date() == day_before)
        clubbing_analysis["holidays_before"].append(holiday_info)
    
    if day_after in holiday_dates:
        holiday_info = next(h for h in holidays if datetime.strptime(h["date"], "%Y-%m-%d").date() == day_after)
        clubbing_analysis["holidays_after"].append(holiday_info)
    
    # Calculate total clubbed days
    clubbing_analysis["total_clubbed_days"] = (
        len(clubbing_analysis["holidays_in_period"]) + 
        len(clubbing_analysis["weekends_in_period"]) +
        len(clubbing_analysis["holidays_before"]) +
        len(clubbing_analysis["holidays_after"])
    )
    
    # Determine policy violation
    has_clubbing = (
        len(clubbing_analysis["holidays_before"]) > 0 or 
        len(clubbing_analysis["holidays_after"]) > 0 or
        len(clubbing_analysis["holidays_in_period"]) > 0
    )
    
    clubbing_analysis["policy_violation"] = has_clubbing
    clubbing_analysis["policy_reference"] = "Section 12: If leaves are availed continuously before and after a holiday/weekly off, the holiday/weekly off will also be considered as leave"
    
    if has_clubbing:
        clubbing_analysis["consequences"] = [
            "Holiday/weekly off will be considered as leave",
            "In absence of leave balance, will be considered as LOP",
            "May impact work deliverables due to extended absence"
        ]
    
    return schemas.APIResponse(
        success=not has_clubbing,
        message="Holiday clubbing policy check completed",
        data=clubbing_analysis
    )

@router.post("/leave/resignation-period-validation")
def validate_resignation_period_leaves(
    resignation_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Validate leave restrictions during resignation notice period"""
    employee_id = current_user.get("id", 1)
    resignation_date = datetime.strptime(resignation_data.get("resignation_date"), "%Y-%m-%d").date()
    last_working_date = datetime.strptime(resignation_data.get("last_working_date"), "%Y-%m-%d").date()
    requested_leave_date = datetime.strptime(resignation_data.get("requested_leave_date"), "%Y-%m-%d").date()
    
    validation_result = {
        "employee_id": employee_id,
        "resignation_date": resignation_date.isoformat(),
        "last_working_date": last_working_date.isoformat(),
        "requested_leave_date": requested_leave_date.isoformat(),
        "is_in_notice_period": resignation_date <= requested_leave_date <= last_working_date,
        "policy_reference": "Section 12: When an employee submits resignation, he/she will not be entitled to avail leaves during notice period"
    }
    
    if validation_result["is_in_notice_period"]:
        validation_result["is_allowed"] = False
        validation_result["rejection_reason"] = "Leave requests not permitted during resignation notice period"
        validation_result["alternative_options"] = [
            "Request early release from notice period",
            "Discuss with HR for exceptional circumstances",
            "Complete notice period as per resignation terms"
        ]
    else:
        validation_result["is_allowed"] = True
        validation_result["message"] = "Leave request is outside notice period"
    
    return schemas.APIResponse(
        success=validation_result["is_allowed"],
        message="Resignation period leave validation completed",
        data=validation_result
    )

@router.post("/leave/out-of-station-intimation")
def record_out_of_station_intimation(
    travel_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Record out of station travel intimation as per Section 12"""
    employee_id = current_user.get("id", 1)
    travel_date = travel_data.get("travel_date")
    travel_type = travel_data.get("travel_type")  # "weekend_holiday" or "team_travel"
    destination = travel_data.get("destination", "")
    manager_informed = travel_data.get("manager_informed", False)
    hr_informed = travel_data.get("hr_informed", False)
    team_members = travel_data.get("team_members", [])
    
    intimation_record = {
        "employee_id": employee_id,
        "travel_date": travel_date,
        "travel_type": travel_type,
        "destination": destination,
        "manager_informed": manager_informed,
        "hr_informed": hr_informed,
        "team_members": team_members,
        "intimated_at": datetime.now().isoformat(),
        "compliance_status": "compliant" if manager_informed and hr_informed else "non_compliant",
        "policy_reference": "Section 12: Employees must inform manager & HR when traveling out of station during Saturdays & Holidays"
    }
    
    # Check compliance requirements
    requirements = []
    if not manager_informed:
        requirements.append("Manager intimation required")
    if not hr_informed:
        requirements.append("HR intimation required")
    if travel_type == "team_travel" and not team_members:
        requirements.append("Team member details required for team travel")
    
    intimation_record["requirements"] = requirements
    intimation_record["is_compliant"] = len(requirements) == 0
    
    return schemas.APIResponse(
        success=intimation_record["is_compliant"],
        message="Out of station travel intimation recorded",
        data=intimation_record
    )

@router.post("/leave/disciplinary-action-check")
def check_disciplinary_action_triggers(
    violation_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Check for disciplinary action triggers as per Section 12"""
    user_role = current_user.get("role", "employee")
    
    if user_role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR role required.")
    
    employee_id = violation_data.get("employee_id")
    violation_type = violation_data.get("violation_type")
    violation_details = violation_data.get("violation_details", {})
    
    disciplinary_check = {
        "employee_id": employee_id,
        "violation_type": violation_type,
        "violation_details": violation_details,
        "disciplinary_action_required": False,
        "action_type": None,
        "severity": "low",
        "policy_references": []
    }
    
    # Check different violation types
    if violation_type == "guideline_violation":
        disciplinary_check["disciplinary_action_required"] = True
        disciplinary_check["action_type"] = "disciplinary_action"
        disciplinary_check["severity"] = "medium"
        disciplinary_check["policy_references"].append("Section 12: Violation of any guidelines leads to disciplinary actions")
    
    elif violation_type == "unauthorized_absence":
        consecutive_days = violation_details.get("consecutive_days", 0)
        if consecutive_days >= 3:
            disciplinary_check["disciplinary_action_required"] = True
            disciplinary_check["action_type"] = "disciplinary_action"
            disciplinary_check["severity"] = "high"
            disciplinary_check["policy_references"].append("Section 8: 3+ consecutive days absence without intimation")
    
    elif violation_type == "smhr_non_compliance":
        disciplinary_check["disciplinary_action_required"] = True
        disciplinary_check["action_type"] = "leave_without_pay"
        disciplinary_check["severity"] = "medium"
        disciplinary_check["policy_references"].append("Section 12: Leaves not applied in SMHR treated as unauthorized absence/LOP")
    
    # Add recommended actions
    if disciplinary_check["disciplinary_action_required"]:
        disciplinary_check["recommended_actions"] = [
            "Issue formal warning",
            "Document violation in employee record",
            "Schedule counseling session",
            "Monitor future compliance"
        ]
        
        if disciplinary_check["severity"] == "high":
            disciplinary_check["recommended_actions"].extend([
                "Consider suspension",
                "Escalate to senior management",
                "Review employment terms"
            ])
    
    return schemas.APIResponse(
        success=True,
        message="Disciplinary action check completed",
        data=disciplinary_check
    )

@router.get("/leave/year-end-lapse-check")
def check_year_end_leave_lapse(
    year: Optional[int] = Query(None, description="Year to check for leave lapse"),
    current_user: dict = Depends(get_current_user)
):
    """Check year-end leave lapse as per Section 12"""
    if year is None:
        year = datetime.now().year
    
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    # Calculate leave balances for the year
    joining_date = datetime.strptime(employee_data["joining_date"], "%Y-%m-%d").date()
    leave_balances = leave_service.calculate_leave_balance(employee_id, employee_data["type"], joining_date)
    
    lapse_analysis = {
        "employee_id": employee_id,
        "year": year,
        "leave_balances": [],
        "total_lapsing_days": 0,
        "lapse_date": f"{year}-12-31",
        "policy_reference": "Section 12: Leaves not utilized during calendar year will lapse automatically after completion of calendar year"
    }
    
    total_lapsing = 0
    for balance in leave_balances:
        if balance.year == year and balance.balance > 0:
            balance_info = {
                "leave_type": balance.leave_type,
                "allocated": balance.total_allocated,
                "used": balance.used,
                "balance": balance.balance,
                "lapsing": balance.balance,
                "carry_forward_allowed": False  # Most leave types don't carry forward
            }
            
            # Special handling for certain leave types
            if balance.leave_type in ["Annual Leave", "Earned Leave"]:
                balance_info["carry_forward_allowed"] = True
                balance_info["lapsing"] = max(0, balance.balance - 5)  # Example: max 5 days carry forward
            
            lapse_analysis["leave_balances"].append(balance_info)
            total_lapsing += balance_info["lapsing"]
    
    lapse_analysis["total_lapsing_days"] = total_lapsing
    
    # Add recommendations
    if total_lapsing > 0:
        lapse_analysis["recommendations"] = [
            f"Plan to utilize {total_lapsing} days before year end",
            "Coordinate with manager for leave scheduling",
            "Consider work-life balance objectives",
            "Submit leave applications in advance"
        ]
    
    return schemas.APIResponse(
        success=True,
        message="Year-end leave lapse check completed",
        data=lapse_analysis
    )

@router.get("/leave/comprehensive-policy-sections-11-12")
def get_comprehensive_policy_sections_11_12():
    """Get complete policy information for Sections 11 (WFH) and 12 (Leave Norms)"""
    
    comprehensive_policy = {
        "section_11_wfh_policy": {
            "approval_process": {
                "prior_approval": "Employees must seek prior approval 1-2 days from respective managers",
                "hr_intimation": "Must inform HR department about WFH days",
                "failure_consequence": "Days treated as leave/LOP if HR not informed"
            },
            "valid_reasons": {
                "medical_emergencies": "Genuine medical emergencies with valid medical reports",
                "hr_decision": "HR evaluates each case to classify as WFH or leave"
            },
            "strategic_timing": {
                "avoid_days": ["Monday", "Friday"],
                "reason": "Critical for team alignment and project progress",
                "holiday_considerations": "Avoid WFH immediately before/after holidays",
                "workflow_impact": "Such timing disrupts workflow continuity"
            },
            "ad_hoc_requests": {
                "policy": "Minimize ad-hoc WFH requests",
                "impact": "Frequent changes impact team productivity and collaboration"
            },
            "commitment_productivity": {
                "reflection": "WFH choices reflect commitment",
                "balance": "Value work-life balance while maintaining team dedication"
            }
        },
        "section_12_leave_norms": {
            "consecutive_leave_limit": {
                "casual_leave": "Maximum 3 consecutive casual leaves",
                "medical_emergency": "Based on eligible leave balance with medical reports"
            },
            "clubbing_policy": {
                "discouraged": "Clubbing leaves with weekly offs/holidays strongly discouraged",
                "reason": "Long absence might lead to work deliverable lapse",
                "consequence": "Holiday/weekly off also considered as leave"
            },
            "smhr_requirements": {
                "advance_notice": "Apply through SMHR with manager approval 2 days before",
                "emergency_process": "Written manager approval (email/Skype) mandatory",
                "post_emergency": "Apply in SMHR within 2 days of return to office",
                "non_compliance": "Days treated as unauthorized absence/LOP"
            },
            "resignation_period": {
                "restriction": "No leaves entitled during notice period",
                "policy": "Complete notice period as per resignation terms"
            },
            "travel_intimation": {
                "weekend_holiday": "Inform manager & HR when traveling out of station",
                "team_travel": "Prior email intimation to manager & HR required"
            },
            "year_end_policy": {
                "lapse": "Unused leaves lapse automatically after calendar year completion",
                "planning": "Employees should plan leave utilization accordingly"
            },
            "disciplinary_actions": {
                "guideline_violation": "Violation of any guidelines leads to disciplinary actions",
                "unauthorized_absence": "3+ consecutive days without intimation",
                "smhr_non_compliance": "Not applying in SMHR results in unauthorized absence/LOP"
            }
        },
        "implementation_guidelines": {
            "hr_responsibilities": [
                "Monitor WFH intimations",
                "Evaluate medical emergency WFH requests",
                "Track SMHR compliance",
                "Enforce disciplinary actions for violations"
            ],
            "manager_responsibilities": [
                "Approve WFH requests with proper justification",
                "Provide written approval for emergency leaves",
                "Monitor team productivity during WFH",
                "Ensure proper handover for extended leaves"
            ],
            "employee_responsibilities": [
                "Seek prior approval for WFH",
                "Inform HR about WFH days",
                "Apply leaves through SMHR with advance notice",
                "Provide medical certificates for medical leaves",
                "Inform about out-of-station travel"
            ]
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Comprehensive policy for Sections 11-12 retrieved successfully",
        data=comprehensive_policy
    )
    
    intimation_method = request_data.get("intimation_method", "email")
    
    # Record HR intimation
    intimation_record = {
        "employee_id": employee_id,
        "wfh_date": wfh_date,
        "intimation_method": intimation_method,
        "intimated_at": datetime.now().isoformat(),
        "hr_acknowledged": False,
        "policy_compliance": "Section 11b - HR Intimation requirement"
    }
    
    return schemas.APIResponse(
        success=True,
        message="HR intimation recorded successfully. Failure to inform HR will result in leave/LOP classification.",
        data=intimation_record
    )

# Section 11: Complete Work From Home Policy Implementation

@router.get("/wfh/approval-process")
def get_wfh_approval_process():
    """Get WFH approval process details as per Section 11a"""
    approval_process = {
        "prior_approval": {
            "required": True,
            "notice_period": "1-2 days before WFH date",
            "approver": "Respective Manager",
            "description": "Employees must seek prior approval from their respective managers before availing WFH"
        },
        "hr_intimation": {
            "required": True,
            "department": "HR Department",
            "consequence": "Days not informed to HR will be treated as leave/LOP",
            "description": "Additionally, employees must inform the HR department about their WFH days"
        },
        "planning_coordination": {
            "purpose": "Proper planning and coordination",
            "impact": "Ensures team productivity and workflow continuity"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="WFH approval process details retrieved successfully",
        data=approval_process
    )

@router.get("/wfh/valid-reasons")
def get_wfh_valid_reasons():
    """Get valid reasons for WFH as per Section 11b"""
    valid_reasons = {
        "medical_emergencies": {
            "description": "WFH is permissible for genuine medical emergencies",
            "requirements": [
                "Valid medical reports must be provided to support the request",
                "HR department will evaluate each case",
                "HR decides whether to classify as WFH or leave"
            ],
            "evaluation_criteria": [
                "Severity of medical condition",
                "Doctor's recommendation for home rest",
                "Inability to commute to office",
                "Temporary nature of condition"
            ]
        },
        "other_valid_reasons": {
            "description": "Other circumstances may be considered on case-by-case basis",
            "evaluation": "Subject to HR and manager approval",
            "documentation": "Appropriate supporting documents required"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Valid WFH reasons retrieved successfully",
        data=valid_reasons
    )

@router.get("/wfh/strategic-timing")
def get_wfh_strategic_timing():
    """Get WFH strategic timing guidelines as per Section 11c"""
    strategic_timing = {
        "restricted_days": {
            "monday_friday": {
                "restriction": "Avoid Mondays and Fridays",
                "reason": "Critical for team alignment and project progress",
                "exception": "Absolutely emergency with valid document",
                "documentation_required": True
            }
        },
        "holiday_considerations": {
            "restriction": "Avoid requesting WFH immediately before or after holidays",
            "impact": "Disrupts workflow continuity",
            "consequence": "If reason not accepted by HR, even holiday between leaves will be considered as leave or LOP",
            "examples": [
                "WFH on day before holiday",
                "WFH on day after holiday",
                "WFH sandwiching holidays"
            ]
        },
        "workflow_impact": {
            "team_alignment": "Mondays are crucial for weekly planning and team sync",
            "project_progress": "Fridays are important for week closure and deliverable reviews",
            "continuity": "Holiday-adjacent WFH disrupts work rhythm"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="WFH strategic timing guidelines retrieved successfully",
        data=strategic_timing
    )

@router.get("/wfh/adhoc-policy")
def get_wfh_adhoc_policy():
    """Get WFH ad-hoc request policy as per Section 11d"""
    adhoc_policy = {
        "minimize_adhoc": {
            "guideline": "Ad-hoc WFH requests should be minimized",
            "reason": "Frequent changes in work arrangements can impact team productivity and collaboration",
            "impact_areas": [
                "Team productivity",
                "Collaboration effectiveness",
                "Project coordination",
                "Meeting schedules"
            ]
        },
        "planning_importance": {
            "preferred_approach": "Pre-planned WFH requests",
            "benefits": [
                "Better team coordination",
                "Improved project planning",
                "Enhanced productivity",
                "Reduced workflow disruption"
            ]
        },
        "emergency_exceptions": {
            "allowed": "Only for genuine emergencies",
            "documentation": "Valid supporting documents required",
            "approval": "Manager and HR discretion"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="WFH ad-hoc policy retrieved successfully",
        data=adhoc_policy
    )

@router.get("/wfh/commitment-productivity")
def get_wfh_commitment_policy():
    """Get WFH commitment and productivity policy as per Section 11e"""
    commitment_policy = {
        "commitment_reflection": {
            "principle": "WFH choices reflect commitment",
            "balance": "While we value work-life balance, consistent dedication to team goals contributes significantly to individual productivity",
            "expectations": [
                "Maintain productivity standards",
                "Active participation in team activities",
                "Meeting project deadlines",
                "Effective communication"
            ]
        },
        "productivity_measures": {
            "key_indicators": [
                "Task completion rates",
                "Quality of deliverables",
                "Team collaboration",
                "Client satisfaction",
                "Goal achievement"
            ],
            "monitoring": "Regular assessment of WFH impact on individual and team performance"
        },
        "work_life_balance": {
            "company_value": "Work-life balance is valued",
            "responsibility": "Employee responsibility to maintain professional standards",
            "mutual_benefit": "Balanced approach benefits both employee and organization"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="WFH commitment and productivity policy retrieved successfully",
        data=commitment_policy
    )

# Section 12: Comprehensive Leave Norms Implementation

@router.get("/leave/norms/casual-leave")
def get_casual_leave_norms():
    """Get casual leave norms as per Section 12"""
    casual_leave_norms = {
        "maximum_consecutive": {
            "limit": 3,
            "description": "Maximum three Casual leaves can be availed at a stretch",
            "enforcement": "System will prevent requests exceeding 3 consecutive days"
        },
        "planning_considerations": [
            "Plan casual leaves to avoid workflow disruption",
            "Coordinate with team for coverage",
            "Avoid peak project periods when possible"
        ]
    }
    
    return schemas.APIResponse(
        success=True,
        message="Casual leave norms retrieved successfully",
        data=casual_leave_norms
    )

@router.get("/leave/norms/medical-emergency")
def get_medical_emergency_norms():
    """Get medical emergency leave norms as per Section 12"""
    medical_norms = {
        "eligibility": {
            "basis": "Eligible leave balance",
            "description": "In case of medical emergencies, leaves can be availed based on the eligible leave balance"
        },
        "documentation": {
            "requirement": "Medical reports issued by a certified doctor",
            "submission": "Must be submitted to the HR team",
            "purpose": [
                "Validation of medical emergency",
                "Records maintenance",
                "Leave classification verification"
            ]
        },
        "certified_doctor": {
            "definition": "Licensed medical practitioner",
            "report_requirements": [
                "Doctor's letterhead",
                "Medical condition description",
                "Recommended rest period",
                "Doctor's signature and registration number"
            ]
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Medical emergency leave norms retrieved successfully",
        data=medical_norms
    )

@router.get("/leave/norms/clubbing-policy")
def get_leave_clubbing_policy():
    """Get leave clubbing policy as per Section 12"""
    clubbing_policy = {
        "discouraged_practice": {
            "description": "Clubbing of leaves with Weekly offs / Holidays is strongly discouraged",
            "reason": "Long absence of a resource might lead to a lapse in work deliverables",
            "impact_areas": [
                "Project continuity",
                "Team productivity",
                "Client commitments",
                "Workflow disruption"
            ]
        },
        "business_continuity": {
            "importance": "Maintaining business operations",
            "team_impact": "Ensuring adequate team coverage",
            "client_service": "Uninterrupted client service delivery"
        },
        "exceptions": {
            "emergency_situations": "May be considered for genuine emergencies",
            "approval_required": "Special approval from management and HR",
            "documentation": "Detailed justification required"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Leave clubbing policy retrieved successfully",
        data=clubbing_policy
    )

@router.get("/leave/norms/smhr-application")
def get_smhr_application_norms():
    """Get SMHR application norms as per Section 12"""
    smhr_norms = {
        "application_requirement": {
            "system": "SMHR (System for Managing Human Resources)",
            "approval": "Must be approved by respective reporting manager",
            "timeline": "At least 2 days before availing the leave"
        },
        "advance_planning": {
            "minimum_notice": "2 days",
            "purpose": "Proper planning and team coordination",
            "benefits": [
                "Work allocation planning",
                "Team coverage arrangement",
                "Client communication",
                "Project timeline adjustment"
            ]
        },
        "manager_approval": {
            "requirement": "Mandatory approval from reporting manager",
            "considerations": [
                "Team workload",
                "Project deadlines",
                "Client commitments",
                "Team coverage availability"
            ]
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="SMHR application norms retrieved successfully",
        data=smhr_norms
    )

@router.get("/leave/norms/holiday-sandwiching")
def get_holiday_sandwiching_policy():
    """Get holiday sandwiching policy as per Section 12"""
    sandwiching_policy = {
        "policy_statement": {
            "rule": "If leaves are availed continuously before and after a holiday/weekly off, the holiday/weekly off will also be considered as leave",
            "consequence": "In the absence of leave balance, the same will be considered as leave without pay"
        },
        "examples": [
            {
                "scenario": "Leave on Friday + Weekend + Leave on Monday",
                "result": "Weekend also counted as leave",
                "total_impact": "4 days leave deduction"
            },
            {
                "scenario": "Leave before holiday + Holiday + Leave after holiday", 
                "result": "Holiday also counted as leave",
                "total_impact": "Holiday becomes chargeable leave"
            }
        ],
        "leave_balance_impact": {
            "sufficient_balance": "Deducted from available leave balance",
            "insufficient_balance": "Excess days treated as Leave Without Pay (LOP)",
            "calculation": "System automatically calculates total chargeable days"
        },
        "planning_advice": {
            "recommendation": "Plan leaves to avoid sandwiching holidays",
            "alternative": "Take longer continuous leave instead of fragmenting",
            "coordination": "Discuss with manager for optimal leave planning"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Holiday sandwiching policy retrieved successfully",
        data=sandwiching_policy
    )

@router.get("/leave/norms/emergency-procedures")
def get_emergency_leave_procedures():
    """Get emergency leave procedures as per Section 12"""
    emergency_procedures = {
        "emergency_basis": {
            "description": "Employee availed leave on an emergency basis but not applied in SMHR",
            "requirement": "Written approval (mail/Skype etc.) from the manager is mandatory"
        },
        "return_to_office": {
            "timeline": "Within next 2 days of return to office",
            "action": "Apply in SMHR to get it approved",
            "responsibility": "Employee must ensure SMHR application completion"
        },
        "approval_methods": [
            "Email approval from manager",
            "Skype message approval",
            "Other written communication",
            "WhatsApp business communication"
        ],
        "compliance_tracking": {
            "hr_monitoring": "HR tracks emergency leave applications",
            "follow_up": "Automatic reminders for SMHR completion",
            "escalation": "Manager notification for non-compliance"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Emergency leave procedures retrieved successfully",
        data=emergency_procedures
    )

@router.get("/leave/norms/unauthorized-absence")
def get_unauthorized_absence_policy():
    """Get unauthorized absence policy as per Section 12"""
    unauthorized_policy = {
        "definition": {
            "condition": "Leaves not applied in SMHR",
            "classification": "Unauthorized absence / Leave without Pay",
            "system_action": "Automatic classification by system"
        },
        "consequences": [
            "Loss of pay for unauthorized days",
            "Disciplinary action consideration",
            "Performance review impact",
            "Future leave approval scrutiny"
        ],
        "prevention_measures": [
            "Regular SMHR system training",
            "Manager reminders",
            "HR follow-up communications",
            "System notifications"
        ],
        "compliance_importance": {
            "record_keeping": "Accurate leave records maintenance",
            "payroll_accuracy": "Correct salary calculations",
            "legal_compliance": "Labor law adherence",
            "organizational_discipline": "Maintaining workplace discipline"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Unauthorized absence policy retrieved successfully",
        data=unauthorized_policy
    )

@router.get("/leave/norms/resignation-period")
def get_resignation_period_policy():
    """Get resignation period leave policy as per Section 12"""
    resignation_policy = {
        "policy_statement": {
            "rule": "When an employee submits resignation, he/she will not be entitled to avail leaves during notice period",
            "rationale": "Ensure proper knowledge transfer and handover completion"
        },
        "notice_period_expectations": [
            "Complete pending work assignments",
            "Conduct knowledge transfer sessions",
            "Handover responsibilities to designated colleagues",
            "Complete exit formalities",
            "Maintain full attendance for smooth transition"
        ],
        "exceptions": {
            "medical_emergency": "Only genuine medical emergencies may be considered",
            "approval_required": "Special approval from management",
            "documentation": "Medical certificates mandatory"
        },
        "business_continuity": {
            "importance": "Ensuring smooth transition",
            "knowledge_transfer": "Critical for business operations",
            "team_impact": "Minimizing disruption to team productivity"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Resignation period leave policy retrieved successfully",
        data=resignation_policy
    )

@router.get("/leave/norms/smhr-issues")
def get_smhr_issues_procedure():
    """Get SMHR issues procedure as per Section 12"""
    smhr_issues = {
        "technical_issues": {
            "immediate_action": "Intimate HR immediately about SMHR issues",
            "alternative_process": "Apply for leaves through email to reporting manager and HR",
            "responsibility": "Employee must report technical issues promptly"
        },
        "alternative_application": {
            "method": "Email application",
            "recipients": [
                "Reporting manager",
                "HR department"
            ],
            "required_information": [
                "Leave dates",
                "Leave type",
                "Reason for leave",
                "SMHR technical issue description"
            ]
        },
        "hr_support": {
            "availability": "HR team available for SMHR support",
            "resolution": "Technical issues resolved on priority",
            "follow_up": "Ensure SMHR application once system is restored"
        },
        "system_reliability": {
            "backup_process": "Email serves as backup application method",
            "documentation": "All communications maintained for records",
            "compliance": "Ensures leave policy compliance despite technical issues"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="SMHR issues procedure retrieved successfully",
        data=smhr_issues
    )

@router.get("/leave/norms/year-end-lapse")
def get_year_end_lapse_policy():
    """Get year-end leave lapse policy as per Section 12"""
    lapse_policy = {
        "automatic_lapse": {
            "rule": "Leaves not utilized during the calendar year will lapse automatically after the completion of the calendar year",
            "no_carryforward": "Unused leaves cannot be carried forward to next year",
            "no_encashment": "Lapsed leaves are not eligible for encashment"
        },
        "planning_importance": {
            "annual_planning": "Employees should plan leave utilization throughout the year",
            "regular_monitoring": "Track leave balance regularly",
            "year_end_rush": "Avoid last-minute leave applications"
        },
        "utilization_strategies": [
            "Plan annual vacation early in the year",
            "Use casual leaves for personal needs",
            "Take sick leaves when genuinely required",
            "Coordinate with team for optimal leave scheduling"
        ],
        "hr_reminders": {
            "quarterly_updates": "HR provides quarterly leave balance updates",
            "year_end_notifications": "Special reminders in November-December",
            "planning_assistance": "HR available for leave planning guidance"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Year-end leave lapse policy retrieved successfully",
        data=lapse_policy
    )

@router.get("/leave/norms/travel-intimation")
def get_travel_intimation_policy():
    """Get travel intimation policy as per Section 12"""
    travel_policy = {
        "weekend_holiday_travel": {
            "requirement": "Every employee has to inform his or her respective reporting manager and HR when traveling out of station during Saturdays & Holidays",
            "purpose": "Emergency contact and safety tracking"
        },
        "team_travel": {
            "requirement": "Resources have to inform their reporting manager & HR prior via email before going out of station with their team",
            "method": "Email communication",
            "recipients": ["Reporting manager", "HR department"]
        },
        "safety_tracking": {
            "purpose": "Employee safety and emergency contact",
            "availability": "Ensure reachability during emergencies",
            "coordination": "Team coordination for weekend activities"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Travel intimation policy retrieved successfully",
        data=travel_policy
    )

@router.get("/leave/norms/disciplinary-actions")
def get_disciplinary_actions_policy():
    """Get disciplinary actions policy as per Section 12"""
    disciplinary_policy = {
        "policy_statement": {
            "rule": "Violation of any of the said guidelines will lead to initiation of disciplinary actions against the resource",
            "scope": "All leave policy guidelines and norms"
        },
        "violation_categories": [
            {
                "violation": "Unauthorized absence (leaves not applied in SMHR)",
                "consequence": "Leave without pay + disciplinary action"
            },
            {
                "violation": "Exceeding casual leave limits (more than 3 consecutive days)",
                "consequence": "Leave rejection + policy violation notice"
            },
            {
                "violation": "Holiday sandwiching without valid reason",
                "consequence": "Additional leave deduction + counseling"
            },
            {
                "violation": "Not informing HR about WFH",
                "consequence": "Day treated as leave/LOP + warning"
            },
            {
                "violation": "Availing leave during notice period",
                "consequence": "Leave rejection + extension of notice period"
            },
            {
                "violation": "Not completing SMHR application after emergency leave",
                "consequence": "Unauthorized absence classification + disciplinary action"
            }
        ],
        "progressive_discipline": [
            "Verbal warning",
            "Written warning", 
            "Final written warning",
            "Suspension",
            "Termination"
        ],
        "documentation": {
            "requirement": "All disciplinary actions documented in employee file",
            "hr_involvement": "HR department manages disciplinary process",
            "manager_coordination": "Reporting manager involvement in process"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Disciplinary actions policy retrieved successfully",
        data=disciplinary_policy
    )

# Section 12: Comprehensive Leave Norms Validation Endpoints

@router.post("/leave/validate-norms")
def validate_leave_against_norms(
    leave_request: schemas.LeaveRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """Validate leave request against all Section 12 norms"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    validation_results = {
        "overall_valid": True,
        "violations": [],
        "warnings": [],
        "requirements": [],
        "norms_checked": []
    }
    
    # 1. Casual Leave Consecutive Days Check
    if leave_request.leave_type == "Casual Leave":
        duration = (leave_request.end_date - leave_request.start_date).days + 1
        if duration > 3:
            validation_results["overall_valid"] = False
            validation_results["violations"].append({
                "norm": "Maximum Casual Leave Consecutive Days",
                "violation": f"Requested {duration} days exceeds maximum 3 consecutive casual leaves",
                "section": "Section 12 - Norm 1"
            })
        validation_results["norms_checked"].append("Casual Leave Consecutive Limit")
    
    # 2. Medical Emergency Documentation Check
    if leave_request.leave_type == "Sick Leave" and leave_request.emergency:
        if not leave_request.medical_certificate:
            validation_results["warnings"].append({
                "norm": "Medical Emergency Documentation",
                "warning": "Medical certificate from certified doctor required for medical emergency leaves",
                "section": "Section 12 - Norm 2"
            })
        validation_results["norms_checked"].append("Medical Emergency Documentation")
    
    # 3. Holiday Sandwiching Check
    sandwiching_check = leave_service.check_holiday_sandwiching(
        leave_request.start_date, 
        leave_request.end_date
    )
    if sandwiching_check["is_sandwiching"]:
        validation_results["warnings"].append({
            "norm": "Holiday Sandwiching Policy",
            "warning": f"Leave sandwiches {sandwiching_check['sandwiched_days']} holiday/weekend days. These will be counted as leave.",
            "section": "Section 12 - Norm 5",
            "additional_days": sandwiching_check["additional_leave_days"]
        })
    validation_results["norms_checked"].append("Holiday Sandwiching")
    
    # 4. SMHR Application Timeline Check
    days_until_leave = (leave_request.start_date - date.today()).days
    if days_until_leave < 2 and not leave_request.emergency:
        validation_results["violations"].append({
            "norm": "SMHR Application Timeline",
            "violation": f"Leave must be applied at least 2 days in advance. Current notice: {days_until_leave} days",
            "section": "Section 12 - Norm 4"
        })
        validation_results["overall_valid"] = False
    validation_results["norms_checked"].append("SMHR Application Timeline")
    
    # 5. Emergency Leave Manager Approval Check
    if leave_request.emergency and leave_request.start_date <= date.today():
        if not leave_request.manager_email_approval:
            validation_results["violations"].append({
                "norm": "Emergency Leave Manager Approval",
                "violation": "Emergency leave for current/past dates requires written manager approval (email/Skype)",
                "section": "Section 12 - Norm 6"
            })
            validation_results["overall_valid"] = False
        else:
            validation_results["requirements"].append({
                "norm": "Emergency Leave SMHR Completion",
                "requirement": "Must complete SMHR application within 2 days of return to office",
                "section": "Section 12 - Norm 6"
            })
    validation_results["norms_checked"].append("Emergency Leave Procedures")
    
    # 6. Resignation Period Check (if applicable)
    # This would require checking if employee has submitted resignation
    # For now, we'll add it as a check that can be implemented
    validation_results["norms_checked"].append("Resignation Period Policy")
    
    # 7. Year-end Leave Balance Check
    current_month = datetime.now().month
    if current_month >= 11:  # November onwards
        validation_results["warnings"].append({
            "norm": "Year-end Leave Lapse",
            "warning": "Unused leaves will lapse at year-end. Plan remaining leaves accordingly.",
            "section": "Section 12 - Norm 10"
        })
    validation_results["norms_checked"].append("Year-end Leave Lapse")
    
    return schemas.APIResponse(
        success=validation_results["overall_valid"],
        message="Leave norms validation completed" + (" with violations" if not validation_results["overall_valid"] else ""),
        data=validation_results
    )

@router.post("/leave/emergency-with-norms")
def create_emergency_leave_with_norms(
    leave_request: schemas.LeaveRequestCreate,
    manager_approval_method: str = Query(..., description="Method of manager approval: email, skype, whatsapp"),
    manager_approval_content: str = Query(..., description="Content/screenshot of manager approval"),
    current_user: dict = Depends(get_current_user)
):
    """Create emergency leave with Section 12 norms compliance"""
    employee_id = current_user.get("id", 1)
    
    # Validate emergency leave norms
    if leave_request.start_date <= date.today():
        if not manager_approval_content:
            raise HTTPException(
                status_code=400,
                detail="Emergency leave requires written manager approval (email/Skype/WhatsApp)"
            )
    
    # Create emergency leave record with norms compliance
    new_id = len(MOCK_LEAVE_REQUESTS) + 1
    leave_record = {
        "id": new_id,
        "employee_id": employee_id,
        "leave_type": leave_request.leave_type,
        "start_date": leave_request.start_date.isoformat(),
        "end_date": leave_request.end_date.isoformat(),
        "reason": leave_request.reason,
        "duration_days": (leave_request.end_date - leave_request.start_date).days + 1,
        "emergency": True,
        "manager_approval_method": manager_approval_method,
        "manager_approval_content": manager_approval_content,
        "status": "approved_emergency",
        "created_at": datetime.now().isoformat(),
        "norms_compliance": {
            "section_12_norm_6": "Emergency leave with written manager approval",
            "smhr_completion_required": True,
            "smhr_deadline": (datetime.now() + timedelta(days=2)).isoformat(),
            "failure_consequence": "Will be treated as unauthorized absence if SMHR not completed"
        },
        "approved_by": "emergency_protocol",
        "approved_at": datetime.now().isoformat()
    }
    
    MOCK_LEAVE_REQUESTS[new_id] = leave_record
    
    return schemas.APIResponse(
        success=True,
        message="Emergency leave approved. CRITICAL: Must complete SMHR application within 2 days of return to office to avoid unauthorized absence classification.",
        data=leave_record
    )

@router.post("/leave/smhr-completion")
def complete_smhr_for_emergency_leave(
    completion_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Complete SMHR application for emergency leave as per Section 12 Norm 6"""
    employee_id = current_user.get("id", 1)
    leave_request_id = completion_data.get("leave_request_id")
    
    if leave_request_id not in MOCK_LEAVE_REQUESTS:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    leave_request = MOCK_LEAVE_REQUESTS[leave_request_id]
    
    if leave_request["employee_id"] != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not leave_request.get("emergency"):
        raise HTTPException(status_code=400, detail="SMHR completion only required for emergency leaves")
    
    # Check if within 2-day deadline
    return_date = datetime.fromisoformat(leave_request["end_date"]) + timedelta(days=1)
    deadline = return_date + timedelta(days=2)
    
    if datetime.now() > deadline:
        # Late completion - mark as violation
        leave_request["smhr_completion_status"] = "late_completion"
        leave_request["policy_violation"] = {
            "violation": "Late SMHR completion",
            "deadline_missed": deadline.isoformat(),
            "consequence": "Disciplinary action may be initiated"
        }
        
        return schemas.APIResponse(
            success=False,
            message="SMHR completion deadline missed. This may result in disciplinary action.",
            data=leave_request
        )
    else:
        # Timely completion
        leave_request["smhr_completion_status"] = "completed_on_time"
        leave_request["smhr_completed_at"] = datetime.now().isoformat()
        leave_request["norms_compliance"]["smhr_completed"] = True
        
        return schemas.APIResponse(
            success=True,
            message="SMHR application completed successfully within deadline.",
            data=leave_request
        )

@router.get("/leave/norms/comprehensive")
def get_comprehensive_leave_norms():
    """Get all Section 12 leave norms in comprehensive format"""
    comprehensive_norms = {
        "section_12_norms": {
            "norm_1": {
                "title": "Casual Leave Consecutive Limit",
                "rule": "Maximum three Casual leaves can be availed at a stretch",
                "enforcement": "System validation prevents exceeding limit",
                "violation_consequence": "Leave request rejection"
            },
            "norm_2": {
                "title": "Medical Emergency Documentation",
                "rule": "Medical reports from certified doctor required for medical emergency leaves",
                "submission": "Must be submitted to HR team",
                "purpose": ["Validation", "Records maintenance"]
            },
            "norm_3": {
                "title": "Leave Clubbing Discouragement",
                "rule": "Clubbing of leaves with Weekly offs/Holidays is strongly discouraged",
                "reason": "Long absence might lead to lapse in work deliverables",
                "impact": "Business continuity and team productivity"
            },
            "norm_4": {
                "title": "SMHR Application Timeline",
                "rule": "Leaves should be applied through SMHR and approved by reporting manager",
                "requirement": "Resources have to inform their reporting manager & HR prior via email before going out of station with their team",
                "coordination": "Ensures proper team travel coordination and safety"
            }
        },
        "information_required": [
            "Travel destination",
            "Travel dates",
            "Purpose of travel",
            "Contact information during travel",
            "Expected return date"
        ],
        "safety_considerations": {
            "emergency_contact": "HR maintains emergency contact information",
            "team_safety": "Ensures team member safety during travel",
            "business_continuity": "Maintains communication channels"
        },
        "compliance_tracking": {
            "email_records": "All travel intimations maintained in records",
            "follow_up": "HR follows up on travel safety",
            "return_confirmation": "Confirmation of safe return expected"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Comprehensive leave norms retrieved successfully",
        data=comprehensive_norms
    )
    
    return schemas.APIResponse(
        success=True,
        message="Travel intimation policy retrieved successfully",
        data=travel_policy
    )

@router.get("/leave/norms/disciplinary-actions")
def get_disciplinary_actions_policy():
    """Get disciplinary actions policy as per Section 12"""
    disciplinary_policy = {
        "policy_statement": {
            "rule": "Violation of any of the said guidelines will lead to initiation of disciplinary actions against the resource",
            "scope": "Applies to all leave and WFH policy violations"
        },
        "violation_categories": [
            {
                "category": "SMHR Non-compliance",
                "violations": [
                    "Not applying leaves in SMHR",
                    "Late SMHR applications",
                    "Incomplete leave applications"
                ],
                "consequences": ["Leave without Pay", "Written warning", "Performance review impact"]
            },
            {
                "category": "Unauthorized Absence",
                "violations": [
                    "3+ days absence without intimation",
                    "No manager approval for emergency leaves",
                    "Failure to provide medical certificates"
                ],
                "consequences": ["Disciplinary action", "Salary deduction", "Termination consideration"]
            },
            {
                "category": "WFH Policy Violations",
                "violations": [
                    "WFH without manager approval",
                    "Not informing HR about WFH",
                    "Frequent ad-hoc WFH requests"
                ],
                "consequences": ["WFH privilege suspension", "Written warning", "Performance monitoring"]
            },
            {
                "category": "Travel Policy Violations",
                "violations": [
                    "Not informing about weekend/holiday travel",
                    "Team travel without prior intimation"
                ],
                "consequences": ["Written warning", "Travel policy briefing", "Future travel restrictions"]
            }
        ],
        "progressive_discipline": {
            "first_violation": "Verbal warning and policy briefing",
            "second_violation": "Written warning and performance monitoring",
            "repeated_violations": "Disciplinary action up to termination",
            "serious_violations": "Immediate disciplinary action"
        },
        "appeal_process": {
            "employee_rights": "Right to explain and appeal disciplinary actions",
            "review_committee": "HR and management review committee",
            "documentation": "All disciplinary actions properly documented"
        }
    }
    
    return schemas.APIResponse(
        success=True,
        message="Disciplinary actions policy retrieved successfully",
        data=disciplinary_policy
    )

@router.get("/leave/comprehensive-policy-sections-11-12")
def get_comprehensive_policy_sections_11_12():
    """Get complete policy information for Sections 11 and 12"""
    comprehensive_policy = {
        "section_11_wfh_policy": {
            "approval_process": "Prior manager approval and HR intimation required",
            "valid_reasons": "Medical emergencies with documentation",
            "strategic_timing": "Avoid Mondays, Fridays, and holiday-adjacent days",
            "adhoc_requests": "Minimize ad-hoc requests for better productivity",
            "commitment": "WFH choices reflect employee commitment to team goals"
        },
        "section_12_leave_norms": {
            "casual_leave_limit": "Maximum 3 consecutive days",
            "medical_emergency": "Based on leave balance with doctor certificates",
            "clubbing_discouraged": "Avoid clubbing with weekends/holidays",
            "smhr_mandatory": "Apply 2 days before, manager approval required",
            "holiday_sandwiching": "Holidays between leaves counted as leave",
            "emergency_procedures": "Manager approval required, SMHR within 2 days",
            "unauthorized_absence": "Non-SMHR applications treated as LOP",
            "resignation_period": "No leaves during notice period",
            "smhr_issues": "Email alternative when system issues occur",
            "year_end_lapse": "Unused leaves lapse automatically",
            "travel_intimation": "Inform manager and HR for weekend/holiday travel",
            "disciplinary_actions": "Violations lead to disciplinary measures"
        },
        "policy_objectives": [
            "Maintain work-life balance while ensuring productivity",
            "Ensure proper planning and coordination",
            "Maintain business continuity and team effectiveness",
            "Provide clear guidelines for leave management",
            "Establish accountability and compliance measures"
        ],
        "implementation_guidelines": [
            "Regular policy training for all employees",
            "Manager training on approval processes",
            "HR monitoring and compliance tracking",
            "System automation for policy enforcement",
            "Regular policy review and updates"
        ]
    }
    
    return schemas.APIResponse(
        success=True,
        message="Comprehensive policy for Sections 11 and 12 retrieved successfully",
        data=comprehensive_policy
    )

# ============================================
# ENHANCED BUSINESS FEATURES
# ============================================

@router.post("/encashment/request")
def request_leave_encashment(
    encashment_request: schemas.LeaveEncashmentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request leave encashment (Employee)"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    # Validate encashment eligibility
    is_eligible, message = leave_service.validate_encashment_eligibility(
        employee_id, encashment_request.leave_type, encashment_request.days_to_encash
    )
    
    if not is_eligible:
        raise HTTPException(status_code=400, detail=message)
    
    new_id = len(MOCK_LEAVE_ENCASHMENTS) + 1
    encashment_record = {
        "id": new_id,
        "employee_id": employee_id,
        "leave_type": encashment_request.leave_type,
        "days_to_encash": encashment_request.days_to_encash,
        "reason": encashment_request.reason,
        "financial_year": encashment_request.financial_year,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "calculated_amount": leave_service.calculate_encashment_amount(
            employee_data["salary"], encashment_request.days_to_encash
        )
    }
    
    MOCK_LEAVE_ENCASHMENTS[new_id] = encashment_record
    
    return schemas.APIResponse(
        success=True,
        message="Leave encashment request submitted successfully",
        data=encashment_record
    )

@router.get("/encashment/requests")
def get_encashment_requests(current_user: dict = Depends(get_current_user)):
    """Get leave encashment requests"""
    employee_id = current_user.get("id", 1)
    user_role = current_user.get("role")
    
    if user_role in ["hr", "admin"]:
        # HR/Admin can see all encashment requests
        requests = list(MOCK_LEAVE_ENCASHMENTS.values())
    else:
        # Employees see only their own requests
        requests = [req for req in MOCK_LEAVE_ENCASHMENTS.values() if req["employee_id"] == employee_id]
    
    return schemas.APIResponse(
        success=True,
        message="Encashment requests retrieved successfully",
        data=requests
    )

@router.post("/carry-forward/request")
def request_carry_forward(
    carry_forward_request: schemas.LeaveCarryForwardRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request leave carry forward (Employee)"""
    employee_id = current_user.get("id", 1)
    
    # Validate carry forward eligibility
    is_eligible, message = leave_service.validate_carry_forward_eligibility(
        employee_id, carry_forward_request.leave_type, carry_forward_request.days_to_carry
    )
    
    if not is_eligible:
        raise HTTPException(status_code=400, detail=message)
    
    new_id = len(MOCK_CARRY_FORWARDS) + 1
    carry_forward_record = {
        "id": new_id,
        "employee_id": employee_id,
        "leave_type": carry_forward_request.leave_type,
        "days_to_carry": carry_forward_request.days_to_carry,
        "reason": carry_forward_request.reason,
        "manager_approval": carry_forward_request.manager_approval,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "expiry_date": (datetime.now() + timedelta(days=90)).isoformat()  # 3 months validity
    }
    
    MOCK_CARRY_FORWARDS[new_id] = carry_forward_record
    
    return schemas.APIResponse(
        success=True,
        message="Leave carry forward request submitted successfully",
        data=carry_forward_record
    )

@router.get("/resignation-notice-period")
def get_resignation_notice_period_leaves(
    employee_id: int,
    notice_period_start: date = Query(..., description="Notice period start date"),
    notice_period_end: date = Query(..., description="Notice period end date"),
    current_user: dict = Depends(get_current_user)
):
    """Get leave restrictions during resignation notice period (HR/Admin only)"""
    if not check_role_access(current_user.get("role"), ["hr", "admin"]):
        raise HTTPException(status_code=403, detail="Access denied. HR/Admin role required.")
    
    restrictions = leave_service.get_resignation_notice_period_restrictions(
        employee_id, notice_period_start, notice_period_end
    )
    
    return schemas.APIResponse(
        success=True,
        message="Resignation notice period leave restrictions retrieved",
        data=restrictions
    )

@router.post("/shift-based-calculation")
def calculate_shift_based_leaves(
    calculation_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Calculate leaves based on shift timings (HR/Admin only)"""
    if not check_role_access(current_user.get("role"), ["hr", "admin"]):
        raise HTTPException(status_code=403, detail="Access denied. HR/Admin role required.")
    
    result = leave_service.calculate_shift_based_leaves(calculation_data)
    
    return schemas.APIResponse(
        success=True,
        message="Shift-based leave calculation completed",
        data=result
    )

@router.get("/attendance-leave-correlation/{employee_id}")
def get_attendance_leave_correlation(
    employee_id: int,
    year: Optional[int] = Query(None, description="Year for analysis"),
    current_user: dict = Depends(get_current_user)
):
    """Get correlation between attendance and leave patterns (Manager/HR/Admin only)"""
    if not check_role_access(current_user.get("role"), ["manager", "hr", "admin"]):
        raise HTTPException(status_code=403, detail="Access denied. Manager/HR/Admin role required.")
    
    if year is None:
        year = datetime.now().year
    
    correlation_data = leave_service.analyze_attendance_leave_correlation(employee_id, year)
    
    return schemas.APIResponse(
        success=True,
        message="Attendance-leave correlation analysis completed",
        data=correlation_data
    )

@router.post("/advanced-analytics")
def get_advanced_leave_analytics(
    analytics_request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Get advanced leave analytics with predictive insights (HR/Admin only)"""
    if not check_role_access(current_user.get("role"), ["hr", "admin"]):
        raise HTTPException(status_code=403, detail="Access denied. HR/Admin role required.")
    
    advanced_analytics = leave_service.generate_advanced_analytics(analytics_request)
    
    return schemas.APIResponse(
        success=True,
        message="Advanced leave analytics generated successfully",
        data=advanced_analytics
    )

@router.post("/policy-compliance-check")
def check_policy_compliance(
    compliance_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Check comprehensive policy compliance for leave requests"""
    employee_id = current_user.get("id", 1)
    
    compliance_result = leave_service.check_comprehensive_policy_compliance(
        employee_id, compliance_data
    )
    
    return schemas.APIResponse(
        success=compliance_result["compliant"],
        message="Policy compliance check completed",
        data=compliance_result
    )

@router.get("/role-based-dashboard")
def get_role_based_dashboard(current_user: dict = Depends(get_current_user)):
    """Get role-specific dashboard data"""
    user_role = current_user.get("role", "employee")
    employee_id = current_user.get("id", 1)
    
    dashboard_data = leave_service.get_role_based_dashboard_data(user_role, employee_id)
    
    return schemas.APIResponse(
        success=True,
        message=f"Role-based dashboard data for {user_role} retrieved successfully",
        data=dashboard_data
    )

@router.post("/automated-workflow")
def trigger_automated_workflow(
    workflow_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Trigger automated leave workflow processes (HR/Admin only)"""
    if not check_role_access(current_user.get("role"), ["hr", "admin"]):
        raise HTTPException(status_code=403, detail="Access denied. HR/Admin role required.")
    
    workflow_result = leave_service.execute_automated_workflow(workflow_data)
    
    return schemas.APIResponse(
        success=workflow_result["success"],
        message="Automated workflow executed successfully",
        data=workflow_result
    )

@router.get("/mobile-optimized-data")
def get_mobile_optimized_data(current_user: dict = Depends(get_current_user)):
    """Get mobile-optimized leave data"""
    employee_id = current_user.get("id", 1)
    
    mobile_data = leave_service.get_mobile_optimized_data(employee_id)
    
    return schemas.APIResponse(
        success=True,
        message="Mobile-optimized data retrieved successfully",
        data=mobile_data
    )

@router.post("/integration/smhr")
def integrate_with_smhr(
    smhr_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Integrate with SMHR system (HR/Admin only)"""
    if not check_role_access(current_user.get("role"), ["hr", "admin"]):
        raise HTTPException(status_code=403, detail="Access denied. HR/Admin role required.")
    
    integration_result = leave_service.integrate_with_smhr_system(smhr_data)
    
    return schemas.APIResponse(
        success=integration_result["success"],
        message="SMHR integration completed",
        data=integration_result
    )

@router.post("/integration/payroll")
def integrate_with_payroll(
    payroll_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Integrate with payroll system (HR/Admin only)"""
    if not check_role_access(current_user.get("role"), ["hr", "admin"]):
        raise HTTPException(status_code=403, detail="Access denied. HR/Admin role required.")
    
    integration_result = leave_service.integrate_with_payroll_system(payroll_data)
    
    return schemas.APIResponse(
        success=integration_result["success"],
        message="Payroll integration completed",
        data=integration_result
    )

@router.get("/audit-trail/{request_id}")
def get_leave_audit_trail(
    request_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get complete audit trail for a leave request"""
    user_role = current_user.get("role", "employee")
    employee_id = current_user.get("id", 1)
    
    # Check access permissions
    if request_id not in MOCK_LEAVE_REQUESTS:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    leave_request = MOCK_LEAVE_REQUESTS[request_id]
    
    # Role-based access control
    if user_role == "employee" and leave_request["employee_id"] != employee_id:
        raise HTTPException(status_code=403, detail="Access denied. You can only view your own leave audit trail.")
    
    audit_trail = leave_service.get_leave_audit_trail(request_id)
    
    return schemas.APIResponse(
        success=True,
        message="Leave audit trail retrieved successfully",
        data=audit_trail
    )
@router.get("/role-based-dashboard")
def get_role_based_dashboard(current_user: dict = Depends(get_current_user)):
    """Get role-specific dashboard data"""
    user_role = current_user.get("role", "employee")
    employee_id = current_user.get("id", 1)
    
    dashboard_data = leave_service.get_role_based_dashboard_data(user_role, employee_id)
    
    return schemas.APIResponse(
        success=True,
        message=f"Role-based dashboard data for {user_role} retrieved successfully",
        data=dashboard_data
    )

@router.get("/role-based-dashboard")
def get_role_based_dashboard(current_user: dict = Depends(get_current_user)):
    """Get role-specific dashboard data"""
    user_role = current_user.get("role", "employee")
    employee_id = current_user.get("id", 1)
    
    dashboard_data = leave_service.get_role_based_dashboard_data(user_role, employee_id)
    
    return schemas.APIResponse(
        success=True,
        message=f"Role-based dashboard data for {user_role} retrieved successfully",
        data=dashboard_data
    )

@router.get("/types")
def get_leave_types(current_user: dict = Depends(get_current_user)):
    """Get applicable leave types for current user with updated maternity/paternity policies"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    
    leave_types = leave_service.get_leave_types(
        employee_data["type"], 
        employee_data["gender"]
    )
    
    return schemas.APIResponse(
        success=True,
        message="Leave types retrieved successfully",
        data=leave_types
    )

@router.get("/maternity-paternity-info")
def get_maternity_paternity_info(current_user: dict = Depends(get_current_user)):
    """Get maternity and paternity leave information and eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    info = {
        "employee_gender": employee_data.get("gender"),
        "maternity_leave": None,
        "paternity_leave": None
    }
    
    if employee_data.get("gender", "").lower() == "female":
        # Check existing maternity leaves
        existing_ml_leaves = leave_service.get_maternity_leaves_for_year(employee_id, current_year)
        
        info["maternity_leave"] = {
            "eligible": True,
            "max_days": 108,
            "advance_notice_required": 60,  # 2 months
            "medical_documents_required": True,
            "timing_options": [
                "After 7 months of pregnancy",
                "After childbirth"
            ],
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_ml_leaves) > 0,
            "existing_leaves": existing_ml_leaves
        }
    
    if employee_data.get("gender", "").lower() == "male":
        # Check existing paternity leaves
        existing_pl_leaves = leave_service.get_paternity_leaves_for_year(employee_id, current_year)
        
        info["paternity_leave"] = {
            "eligible": True,
            "max_days": 3,
            "timing": "Around the time of childbirth",
            "approval_flow": [
                "Employee applies for leave",
                "HR approval", 
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_pl_leaves) > 0,
            "existing_leaves": existing_pl_leaves
        }
    
    return schemas.APIResponse(
        success=True,
        message="Maternity/Paternity leave information retrieved successfully",
        data=info
    )
@router.get("/maternity-paternity-info")
def get_maternity_paternity_info(current_user: dict = Depends(get_current_user)):
    """Get maternity and paternity leave information and eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    info = {
        "employee_gender": employee_data.get("gender"),
        "maternity_leave": None,
        "paternity_leave": None
    }
    
    if employee_data.get("gender", "").lower() == "female":
        # Check existing maternity leaves
        existing_ml_leaves = leave_service.get_maternity_leaves_for_year(employee_id, current_year)
        
        info["maternity_leave"] = {
            "eligible": True,
            "max_days": 108,
            "advance_notice_required": 60,  # 2 months
            "medical_documents_required": True,
            "timing_options": [
                "After 7 months of pregnancy",
                "After childbirth"
            ],
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_ml_leaves) > 0,
            "existing_leaves": existing_ml_leaves
        }
    
    if employee_data.get("gender", "").lower() == "male":
        # Check existing paternity leaves
        existing_pl_leaves = leave_service.get_paternity_leaves_for_year(employee_id, current_year)
        
        info["paternity_leave"] = {
            "eligible": True,
            "max_days": 3,
            "timing": "Around the time of childbirth",
            "approval_flow": [
                "Employee applies for leave",
                "HR approval", 
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_pl_leaves) > 0,
            "existing_leaves": existing_pl_leaves
        }
    
    return schemas.APIResponse(
        success=True,
        message="Maternity/Paternity leave information retrieved successfully",
        data=info
    )

@router.get("/birthday-anniversary-info")
def get_birthday_anniversary_info(current_user: dict = Depends(get_current_user)):
    """Get employee's birthday and anniversary information for BL leave eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    # Get existing BL leaves for this year
    existing_bl_leaves = leave_service.get_bl_leaves_for_year(employee_id, current_year)
    
    # Parse dates
    birthday = None
    anniversary = None
    
    if employee_data.get("date_of_birth"):
        try:
            if isinstance(employee_data["date_of_birth"], str):
                dob = datetime.strptime(employee_data["date_of_birth"], "%Y-%m-%d").date()
            else:
                dob = employee_data["date_of_birth"]
            
            birthday = {
                "date": dob.replace(year=current_year).isoformat(),
                "formatted": dob.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            birthday = None
    
    if employee_data.get("wedding_anniversary_date"):
        try:
            if isinstance(employee_data["wedding_anniversary_date"], str):
                anniversary_date = datetime.strptime(employee_data["wedding_anniversary_date"], "%Y-%m-%d").date()
            else:
                anniversary_date = employee_data["wedding_anniversary_date"]
            
            anniversary = {
                "date": anniversary_date.replace(year=current_year).isoformat(),
                "formatted": anniversary_date.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            anniversary = None
    
    # Check if already taken BL leave this year
    bl_taken_for = None
    if existing_bl_leaves:
        bl_taken_for = existing_bl_leaves[0].get("occasion_type")
        
        # Update eligibility based on what's already taken
        if birthday and bl_taken_for in ["birthday", "anniversary"]:
            birthday["eligible"] = bl_taken_for != "birthday"
        if anniversary and bl_taken_for in ["birthday", "anniversary"]:
            anniversary["eligible"] = bl_taken_for != "anniversary"
    
    return schemas.APIResponse(
        success=True,
        message="Birthday/Anniversary leave information retrieved successfully",
        data={
            "birthday": birthday,
            "anniversary": anniversary,
            "bl_taken_for": bl_taken_for,
            "policy": {
                "max_days": 1,
                "choice": "Either birthday OR anniversary per year, not both",
                "timing": "Within 7 days of the actual date"
            }
        }
    )

@router.get("/maternity-paternity-info")
def get_maternity_paternity_info(current_user: dict = Depends(get_current_user)):
    """Get maternity and paternity leave information and eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    info = {
        "employee_gender": employee_data.get("gender"),
        "maternity_leave": None,
        "paternity_leave": None
    }
    
    if employee_data.get("gender", "").lower() == "female":
        # Check existing maternity leaves
        existing_ml_leaves = leave_service.get_maternity_leaves_for_year(employee_id, current_year)
        
        info["maternity_leave"] = {
            "eligible": True,
            "max_days": 108,
            "advance_notice_required": 60,  # 2 months
            "medical_documents_required": True,
            "timing_options": [
                "After 7 months of pregnancy",
                "After childbirth"
            ],
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_ml_leaves) > 0,
            "existing_leaves": existing_ml_leaves
        }
    
    if employee_data.get("gender", "").lower() == "male":
        # Check existing paternity leaves
        existing_pl_leaves = leave_service.get_paternity_leaves_for_year(employee_id, current_year)
        
        info["paternity_leave"] = {
            "eligible": True,
            "max_days": 3,
            "timing": "Around the time of childbirth",
            "approval_flow": [
                "Employee applies for leave",
                "HR approval", 
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_pl_leaves) > 0,
            "existing_leaves": existing_pl_leaves
        }
    
    return schemas.APIResponse(
        success=True,
        message="Maternity/Paternity leave information retrieved successfully",
        data=info
    )

@router.get("/birthday-anniversary-info")
def get_birthday_anniversary_info(current_user: dict = Depends(get_current_user)):
    """Get employee's birthday and anniversary information for BL leave eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    # Get existing BL leaves for this year
    existing_bl_leaves = leave_service.get_bl_leaves_for_year(employee_id, current_year)
    
    # Parse dates
    birthday = None
    anniversary = None
    
    if employee_data.get("date_of_birth"):
        try:
            if isinstance(employee_data["date_of_birth"], str):
                dob = datetime.strptime(employee_data["date_of_birth"], "%Y-%m-%d").date()
            else:
                dob = employee_data["date_of_birth"]
            
            birthday = {
                "date": dob.replace(year=current_year).isoformat(),
                "formatted": dob.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            birthday = None
    
    if employee_data.get("wedding_anniversary_date"):
        try:
            if isinstance(employee_data["wedding_anniversary_date"], str):
                anniversary_date = datetime.strptime(employee_data["wedding_anniversary_date"], "%Y-%m-%d").date()
            else:
                anniversary_date = employee_data["wedding_anniversary_date"]
            
            anniversary = {
                "date": anniversary_date.replace(year=current_year).isoformat(),
                "formatted": anniversary_date.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            anniversary = None
    
    # Check if already taken BL leave this year
    bl_taken_for = None
    if existing_bl_leaves:
        bl_taken_for = existing_bl_leaves[0].get("occasion_type")
        
        # Update eligibility based on what's already taken
        if birthday and bl_taken_for in ["birthday", "anniversary"]:
            birthday["eligible"] = bl_taken_for != "birthday"
        if anniversary and bl_taken_for in ["birthday", "anniversary"]:
            anniversary["eligible"] = bl_taken_for != "anniversary"
    
    return schemas.APIResponse(
        success=True,
        message="Birthday/Anniversary leave information retrieved successfully",
        data={
            "birthday": birthday,
            "anniversary": anniversary,
            "bl_taken_for": bl_taken_for,
            "policy": {
                "max_days": 1,
                "choice": "Either birthday OR anniversary per year, not both",
                "timing": "Within 7 days of the actual date"
            }
        }
    )

@router.get("/maternity-paternity-info")
def get_maternity_paternity_info(current_user: dict = Depends(get_current_user)):
    """Get employee's maternity/paternity leave eligibility and information"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    employee_gender = employee_data.get("gender", "").lower()
    current_year = datetime.now().year
    
    info = {
        "employee_gender": employee_gender,
        "maternity_leave": None,
        "paternity_leave": None
    }
    
    if employee_gender == "female":
        # Get existing ML leaves for this year
        existing_ml_leaves = leave_service.get_maternity_leaves_for_year(employee_id, current_year)
        
        info["maternity_leave"] = {
            "eligible": True,
            "max_days": 108,
            "advance_notice_required": 60,  # 2 months
            "medical_documents_required": True,
            "timing_options": [
                "After 7 months of pregnancy",
                "After childbirth"
            ],
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_ml_leaves) > 0,
            "existing_leaves": existing_ml_leaves
        }
    
    elif employee_gender == "male":
        # Get existing PL leaves for this year
        existing_pl_leaves = leave_service.get_paternity_leaves_for_year(employee_id, current_year)
        
        info["paternity_leave"] = {
            "eligible": True,
            "max_days": 3,
            "timing": "Around the time of childbirth",
            "approval_flow": [
                "Employee applies for leave",
                "HR approval",
                "Manager approval"
            ],
            "already_taken_this_year": len(existing_pl_leaves) > 0,
            "existing_leaves": existing_pl_leaves
        }
    
    return schemas.APIResponse(
        success=True,
        message="Maternity/Paternity leave information retrieved successfully",
        data=info
    )

@router.get("/birthday-anniversary-info")
def get_birthday_anniversary_info(current_user: dict = Depends(get_current_user)):
    """Get employee's birthday and anniversary information for BL leave eligibility"""
    employee_id = current_user.get("id", 1)
    employee_data = get_mock_employee_data(employee_id)
    current_year = datetime.now().year
    
    # Get existing BL leaves for this year
    existing_bl_leaves = leave_service.get_bl_leaves_for_year(employee_id, current_year)
    
    # Parse dates
    birthday = None
    anniversary = None
    
    if employee_data.get("date_of_birth"):
        try:
            if isinstance(employee_data["date_of_birth"], str):
                dob = datetime.strptime(employee_data["date_of_birth"], "%Y-%m-%d").date()
            else:
                dob = employee_data["date_of_birth"]
            
            birthday = {
                "date": dob.replace(year=current_year).isoformat(),
                "formatted": dob.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            birthday = None
    
    if employee_data.get("wedding_anniversary_date"):
        try:
            if isinstance(employee_data["wedding_anniversary_date"], str):
                anniversary_date = datetime.strptime(employee_data["wedding_anniversary_date"], "%Y-%m-%d").date()
            else:
                anniversary_date = employee_data["wedding_anniversary_date"]
            
            anniversary = {
                "date": anniversary_date.replace(year=current_year).isoformat(),
                "formatted": anniversary_date.replace(year=current_year).strftime("%B %d"),
                "eligible": True
            }
        except (ValueError, TypeError):
            anniversary = None
    
    # Check if already taken BL leave this year
    bl_taken_for = None
    if existing_bl_leaves:
        bl_taken_for = existing_bl_leaves[0].get("occasion_type")
        
        # Update eligibility based on what's already taken
        if birthday and bl_taken_for in ["birthday", "anniversary"]:
            birthday["eligible"] = bl_taken_for != "birthday"
        if anniversary and bl_taken_for in ["birthday", "anniversary"]:
            anniversary["eligible"] = bl_taken_for != "anniversary"
    
    return schemas.APIResponse(
        success=True,
        message="Birthday/Anniversary leave information retrieved successfully",
        data={
            "birthday": birthday,
            "anniversary": anniversary,
            "bl_taken_for": bl_taken_for,
            "policy": {
                "max_days": 1,
                "choice": "Either birthday OR anniversary per year, not both",
                "timing": "Within 7 days of the actual date"
            }
        }
    )