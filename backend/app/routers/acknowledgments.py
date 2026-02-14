"""
Asset Acknowledgment API Routes
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any, Optional
from pydantic import BaseModel, field_validator
from datetime import datetime

from ..database import get_db
from ..dependencies import get_current_user
from ..models_v2 import User, Employee  # Use models_v2 for SQLAlchemy models
from ..asset_acknowledgment_service import AssetAcknowledgmentService
from ..role_utils import require_role

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/acknowledgments", tags=["acknowledgments"])

def get_employee_from_user_safe(current_user: User, db: Session) -> Employee:
    """Helper function to get employee from current user - returns None if not found (for admin users)"""
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    return employee

def get_employee_from_user(current_user: User, db: Session) -> Employee:
    """Helper function to get employee from current user with proper error handling"""
    employee = get_employee_from_user_safe(current_user, db)
    
    if not employee:
        logger.warning(f"Employee profile not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Employee profile not found")
    
    return employee

def create_response(success: bool, message: str = None, data: Any = None, error: str = None) -> Dict[str, Any]:
    """Create consistent API response format"""
    response = {"success": success}
    
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    if error:
        response["error"] = error
        
    return response

def safe_get_result_success(result: Any) -> bool:
    """Safely check if service result indicates success, handling None and empty dict cases"""
    if result is None:
        return False
    if not isinstance(result, dict):
        return False
    return result.get("success", False)

def safe_get_result_message(result: Any, default_message: str = "Unknown error") -> str:
    """Safely get message from service result"""
    if result is None or not isinstance(result, dict):
        return default_message
    return result.get("message", default_message)
    return response

class AcknowledgmentCreate(BaseModel):
    employee_name: str
    employee_id_number: str
    department: str
    date_of_joining: datetime
    
    # Received Items - exactly matching database schema
    laptop_received: bool = False
    laptop_serial_number: Optional[str] = None
    laptop_model: Optional[str] = None
    laptop_condition: Optional[str] = None
    
    email_received: bool = False
    email_address: Optional[str] = None
    email_password_received: bool = False
    
    wifi_access_received: bool = False
    wifi_credentials_received: bool = False
    
    id_card_received: bool = False
    id_card_number: Optional[str] = None
    
    biometric_setup_completed: bool = False
    biometric_type: Optional[str] = None
    
    # Additional Items
    monitor_received: bool = False
    monitor_serial_number: Optional[str] = None
    keyboard_received: bool = False
    mouse_received: bool = False
    headset_received: bool = False
    mobile_received: bool = False
    mobile_number: Optional[str] = None
    
    # Login Status
    system_login_working: bool = False
    email_login_working: bool = False
    vpn_access_working: bool = False
    
    # Comments
    employee_comments: Optional[str] = None
    issues_reported: Optional[str] = None
    additional_requirements: Optional[str] = None
    
    class Config:
        # Ensure all fields are validated
        validate_assignment = True
        # Allow extra fields to be ignored instead of raising error
        extra = "ignore"

class AcknowledgmentReview(BaseModel):
    review_status: str  # approved, needs_action
    admin_comments: Optional[str] = None
    
    @field_validator('review_status')
    @classmethod
    def validate_review_status(cls, v):
        # Handle None or empty values
        if not v:
            raise ValueError('review_status is required and cannot be empty')
        
        # Convert to lowercase for case-insensitive validation
        v_lower = v.lower() if isinstance(v, str) else str(v).lower()
        allowed_statuses = ['approved', 'needs_action']
        if v_lower not in allowed_statuses:
            raise ValueError(f'review_status must be one of: {", ".join(allowed_statuses)} (case-insensitive)')
        return v_lower  # Return the normalized lowercase value

@router.post("/submit")
async def submit_acknowledgment(
    acknowledgment_data: AcknowledgmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit asset acknowledgment form"""
    try:
        # Get employee ID from current user using helper function
        employee = get_employee_from_user(current_user, db)
        
        service = AssetAcknowledgmentService(db)
        
        # Use model_dump() instead of deprecated dict() method
        result = service.create_acknowledgment(
            employee_id=employee.id,
            acknowledgment_data=acknowledgment_data.model_dump()
        )
        
        # Use safe helper to check result
        if not safe_get_result_success(result):
            error_message = safe_get_result_message(result, "Failed to create acknowledgment")
            logger.error(f"Failed to create acknowledgment for employee {employee.id}: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        logger.info(f"Acknowledgment created successfully for employee {employee.id}, ID: {result.get('acknowledgment_id') if isinstance(result, dict) else 'unknown'}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in submit_acknowledgment: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your acknowledgment")

@router.get("/check-pending")
async def check_pending_acknowledgment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if employee has pending infrastructure setup to acknowledge"""
    try:
        employee = get_employee_from_user(current_user, db)
        
        service = AssetAcknowledgmentService(db)
        result = service.check_pending_acknowledgment(employee.id)
        
        # Ensure result is valid
        if result is None:
            logger.error(f"Service returned None for check_pending_acknowledgment for employee {employee.id}")
            raise HTTPException(status_code=500, detail="Service error: Invalid response")
        
        logger.info(f"Checked pending acknowledgment for employee {employee.id}")
        return create_response(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking pending acknowledgment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check pending acknowledgments")

@router.get("/my-acknowledgments")
async def get_my_acknowledgments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get acknowledgments for current employee"""
    try:
        employee = get_employee_from_user(current_user, db)
        
        service = AssetAcknowledgmentService(db)
        result = service.get_employee_acknowledgments(employee.id)
        
        # Ensure result is valid
        if result is None:
            logger.error(f"Service returned None for get_employee_acknowledgments for employee {employee.id}")
            raise HTTPException(status_code=500, detail="Service error: Invalid response")
        
        logger.info(f"Retrieved acknowledgments for employee {employee.id}")
        return create_response(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving employee acknowledgments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve acknowledgments")

@router.get("/pending")
async def get_pending_acknowledgments(
    current_user: User = Depends(require_role(["admin", "hr", "super_admin", "hr_manager"])),
    db: Session = Depends(get_db)
):
    """Get all pending acknowledgments for admin review"""
    try:
        service = AssetAcknowledgmentService(db)
        result = service.get_pending_acknowledgments()
        
        # Ensure result is valid
        if result is None:
            logger.error("Service returned None for get_pending_acknowledgments")
            raise HTTPException(status_code=500, detail="Service error: Invalid response")
        
        logger.info(f"Admin {current_user.id} retrieved pending acknowledgments")
        return create_response(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving pending acknowledgments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve pending acknowledgments")

@router.get("/{acknowledgment_id}")
async def get_acknowledgment_details(
    acknowledgment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed acknowledgment information with proper authorization"""
    try:
        service = AssetAcknowledgmentService(db)
        result = service.get_acknowledgment_details(acknowledgment_id)
        
        # Ensure result is valid and handle error cases
        if result is None:
            logger.error(f"Service returned None for get_acknowledgment_details for ID {acknowledgment_id}")
            raise HTTPException(status_code=500, detail="Service error: Invalid response")
        
        if not isinstance(result, dict):
            logger.error(f"Service returned invalid type for get_acknowledgment_details: {type(result)}")
            raise HTTPException(status_code=500, detail="Service error: Invalid response format")
        
        if "error" in result:
            logger.warning(f"Acknowledgment {acknowledgment_id} not found")
            raise HTTPException(status_code=404, detail=result["error"])
        
        # Authorization check: Check admin status FIRST before trying to get employee
        is_admin_or_hr = current_user.role in ["admin", "hr", "super_admin", "hr_manager"]
        
        if is_admin_or_hr:
            # Admin/HR users can access any acknowledgment without needing employee profile
            logger.info(f"Admin/HR user {current_user.id} accessed acknowledgment {acknowledgment_id}")
            return create_response(success=True, data=result)
        else:
            # Regular employees can only access their own acknowledgments
            # Only try to get employee profile for non-admin users
            employee = get_employee_from_user_safe(current_user, db)
            if not employee:
                logger.warning(f"Non-admin user {current_user.id} has no employee profile")
                raise HTTPException(
                    status_code=403, 
                    detail="Access denied. You must have an employee profile to access acknowledgments."
                )
            
            is_own_acknowledgment = result.get("employee_id") == employee.id
            if not is_own_acknowledgment:
                logger.warning(f"Employee {employee.id} attempted unauthorized access to acknowledgment {acknowledgment_id}")
                raise HTTPException(
                    status_code=403, 
                    detail="Access denied. You can only view your own acknowledgments."
                )
            
            logger.info(f"Employee {employee.id} accessed their acknowledgment {acknowledgment_id}")
            return create_response(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving acknowledgment details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve acknowledgment details")

@router.post("/{acknowledgment_id}/review")
async def review_acknowledgment(
    acknowledgment_id: int,
    review_data: AcknowledgmentReview,
    current_user: User = Depends(require_role(["admin", "hr", "super_admin", "hr_manager"])),
    db: Session = Depends(get_db)
):
    """Admin reviews acknowledgment"""
    try:
        service = AssetAcknowledgmentService(db)
        
        result = service.review_acknowledgment(
            acknowledgment_id=acknowledgment_id,
            reviewer_id=current_user.id,
            review_status=review_data.review_status,
            admin_comments=review_data.admin_comments
        )
        
        # Use safe helper to check result
        if not safe_get_result_success(result):
            error_message = safe_get_result_message(result, "Failed to review acknowledgment")
            logger.error(f"Failed to review acknowledgment {acknowledgment_id}: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        logger.info(f"Admin {current_user.id} reviewed acknowledgment {acknowledgment_id} with status: {review_data.review_status}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing acknowledgment {acknowledgment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to review acknowledgment")