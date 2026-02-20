from fastapi import APIRouter, HTTPException, Depends
from app import schemas
from app.database import get_db
from app.dependencies import get_current_user
from app import models
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)

# Mock announcements data
MOCK_ANNOUNCEMENTS = {
    1: {
        "id": 1,
        "title": "Welcome to the New HR System",
        "content": "We're excited to introduce our new HR management system. Please explore the features and let us know your feedback.",
        "posted_by": 1,
        "author_name": "HR Admin",
        "priority": "high",
        "category": "general",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "expires_at": None
    },
    2: {
        "id": 2,
        "title": "Holiday Schedule Update",
        "content": "Please note the updated holiday schedule for the upcoming quarter. Check the calendar for details.",
        "posted_by": 2,
        "author_name": "HR Manager",
        "priority": "normal",
        "category": "hr",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "expires_at": None
    }
}

# Mock acknowledgments data
MOCK_ACKNOWLEDGMENTS = {}

@router.get("/with-status")
def get_announcements_with_status(current_user: models.User = Depends(get_current_user)):
    """Get all active announcements with acknowledgment status"""
    active_announcements = [
        ann for ann in MOCK_ANNOUNCEMENTS.values() 
        if ann.get("is_active", True)
    ]
    
    # Handle both dict and User object for current_user
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    
    # Add acknowledgment status for each announcement
    for ann in active_announcements:
        ack_key = f"{user_id}_{ann['id']}"
        acknowledgment = MOCK_ACKNOWLEDGMENTS.get(ack_key)
        ann["acknowledged"] = acknowledgment is not None
        ann["acknowledged_at"] = acknowledgment.get("acknowledged_at") if acknowledgment else None
    
    # Sort by priority and date
    priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
    active_announcements.sort(
        key=lambda x: (priority_order.get(x.get("priority", "normal"), 2), x.get("created_at", ""))
    )
    
    return active_announcements

@router.get("/stats")
def get_announcement_stats(current_user: models.User = Depends(get_current_user)):
    """Get announcement statistics - Admin/HR only"""
    # Handle both dict and User object for current_user
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    
    if user_role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only admin or HR can view stats")
    
    total_announcements = len(MOCK_ANNOUNCEMENTS)
    active_announcements = len([ann for ann in MOCK_ANNOUNCEMENTS.values() if ann.get("is_active", True)])
    
    # Calculate acknowledgment rates for recent announcements
    recent_announcement_stats = []
    for ann in list(MOCK_ANNOUNCEMENTS.values())[-5:]:  # Last 5 announcements
        total_employees = 10  # Mock total employee count
        acknowledged_count = len([ack for ack in MOCK_ACKNOWLEDGMENTS.values() 
                                if ack.get("announcement_id") == ann["id"]])
        acknowledgment_rate = int((acknowledged_count / total_employees) * 100) if total_employees > 0 else 0
        
        recent_announcement_stats.append({
            "id": ann["id"],
            "title": ann["title"],
            "acknowledgment_rate": acknowledgment_rate,
            "acknowledged_count": acknowledged_count,
            "total_employees": total_employees
        })
    
    return {
        "total_announcements": total_announcements,
        "active_announcements": active_announcements,
        "inactive_announcements": total_announcements - active_announcements,
        "recent_announcement_stats": recent_announcement_stats
    }

@router.post("/{announcement_id}/acknowledge")
def acknowledge_announcement(announcement_id: int, current_user: models.User = Depends(get_current_user)):
    """Acknowledge an announcement"""
    if announcement_id not in MOCK_ANNOUNCEMENTS:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    announcement = MOCK_ANNOUNCEMENTS[announcement_id]
    if not announcement.get("is_active", True):
        raise HTTPException(status_code=400, detail="Cannot acknowledge inactive announcement")
    
    # Check if already acknowledged
    ack_key = f"{current_user.id}_{announcement_id}"
    if ack_key in MOCK_ACKNOWLEDGMENTS:
        return schemas.APIResponse(
            success=True,
            message="Announcement already acknowledged",
            data={"already_acknowledged": True}
        )
    
    # Create acknowledgment
    MOCK_ACKNOWLEDGMENTS[ack_key] = {
        "user_id": current_user.id,
        "announcement_id": announcement_id,
        "acknowledged_at": datetime.now().isoformat()
    }
    
    return schemas.APIResponse(
        success=True,
        message="Announcement acknowledged successfully",
        data={"acknowledged": True}
    )

@router.put("/{announcement_id}/toggle-status")
def toggle_announcement_status(announcement_id: int, current_user: models.User = Depends(get_current_user)):
    """Toggle announcement active status - Admin/HR only"""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only admin or HR can toggle announcement status")
    
    if announcement_id not in MOCK_ANNOUNCEMENTS:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    announcement = MOCK_ANNOUNCEMENTS[announcement_id]
    current_status = announcement.get("is_active", True)
    new_status = not current_status
    
    announcement["is_active"] = new_status
    announcement["updated_at"] = datetime.now().isoformat()
    
    status_text = "activated" if new_status else "deactivated"
    
    return schemas.APIResponse(
        success=True,
        message=f"Announcement {status_text} successfully",
        data={"is_active": new_status}
    )
def get_announcements(current_user: models.User = Depends(get_current_user)):
    """Get all active announcements"""
    active_announcements = [
        ann for ann in MOCK_ANNOUNCEMENTS.values() 
        if ann.get("is_active", True)
    ]
    
    # Sort by priority and date
    priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
    active_announcements.sort(
        key=lambda x: (priority_order.get(x.get("priority", "normal"), 2), x.get("created_at", ""))
    )
    
    return schemas.APIResponse(
        success=True,
        message="Announcements retrieved successfully",
        data=active_announcements
    )

@router.get("/{announcement_id}")
def get_announcement(announcement_id: int, current_user: models.User = Depends(get_current_user)):
    """Get specific announcement"""
    announcement = MOCK_ANNOUNCEMENTS.get(announcement_id)
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return schemas.APIResponse(
        success=True,
        message="Announcement retrieved successfully",
        data=announcement
    )

@router.post("/")
def create_announcement(announcement: schemas.AnnouncementCreate, current_user: models.User = Depends(get_current_user)):
    """Create new announcement - Admin/HR only"""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only admin or HR can create announcements")
    
    db = get_db()
    
    new_id = max(MOCK_ANNOUNCEMENTS.keys()) + 1 if MOCK_ANNOUNCEMENTS else 1
    new_announcement = {
        "id": new_id,
        "title": announcement.title,
        "content": announcement.content,
        "posted_by": current_user.id,
        "priority": announcement.priority,
        "category": announcement.category,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "expires_at": None
    }
    
    MOCK_ANNOUNCEMENTS[new_id] = new_announcement
    
    return schemas.APIResponse(
        success=True,
        message="Announcement created successfully",
        data=new_announcement
    )

@router.put("/{announcement_id}")
def update_announcement(announcement_id: int, announcement_update: schemas.AnnouncementCreate, current_user: models.User = Depends(get_current_user)):
    """Update announcement - Admin/HR only"""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only admin or HR can update announcements")
    
    if announcement_id not in MOCK_ANNOUNCEMENTS:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    announcement = MOCK_ANNOUNCEMENTS[announcement_id]
    
    announcement.update({
        "title": announcement_update.title,
        "content": announcement_update.content,
        "priority": announcement_update.priority,
        "category": announcement_update.category,
        "updated_at": datetime.now().isoformat()
    })
    
    return schemas.APIResponse(
        success=True,
        message="Announcement updated successfully",
        data=announcement
    )

@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, current_user: models.User = Depends(get_current_user)):
    """Delete announcement - Admin/HR only"""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only admin or HR can delete announcements")
    
    if announcement_id not in MOCK_ANNOUNCEMENTS:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Soft delete by setting is_active to False
    MOCK_ANNOUNCEMENTS[announcement_id]["is_active"] = False
    MOCK_ANNOUNCEMENTS[announcement_id]["deleted_at"] = datetime.now().isoformat()
    
    return schemas.APIResponse(
        success=True,
        message="Announcement deleted successfully"
    )

@router.get("/categories/list")
def get_announcement_categories(current_user: models.User = Depends(get_current_user)):
    """Get list of announcement categories"""
    categories = [
        {"value": "general", "label": "General"},
        {"value": "hr", "label": "Human Resources"},
        {"value": "it", "label": "Information Technology"},
        {"value": "finance", "label": "Finance"},
        {"value": "policy", "label": "Policy Updates"},
        {"value": "events", "label": "Events"}
    ]
    
    return schemas.APIResponse(
        success=True,
        message="Categories retrieved successfully",
        data=categories
    )