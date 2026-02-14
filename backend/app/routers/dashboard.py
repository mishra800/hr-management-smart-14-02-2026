from fastapi import APIRouter
from app import schemas
from datetime import datetime

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/stats")
def get_dashboard_stats():
    """Get basic dashboard statistics"""
    # Mock data for now
    stats = schemas.DashboardStats(
        total_employees=25,
        present_today=20,
        on_leave=3,
        pending_requests=5
    )
    
    return schemas.APIResponse(
        success=True,
        message="Dashboard stats retrieved",
        data=stats.dict()
    )

@router.get("/activities")
def get_dashboard_activities():
    """Get recent activity feed (alias for recent-activity)"""
    return get_recent_activity()

@router.get("/recent-activity")
def get_recent_activity():
    """Get recent activity feed"""
    # Mock recent activities
    activities = [
        {
            "type": "attendance",
            "message": "John Doe checked in",
            "timestamp": datetime.now().isoformat(),
            "icon": "clock"
        },
        {
            "type": "leave",
            "message": "Jane Smith requested leave",
            "timestamp": datetime.now().isoformat(),
            "icon": "calendar"
        },
        {
            "type": "announcement",
            "message": "New company policy announced",
            "timestamp": datetime.now().isoformat(),
            "icon": "megaphone"
        }
    ]
    
    return schemas.APIResponse(
        success=True,
        message="Recent activity retrieved",
        data=activities
    )

@router.get("/calendar")
def get_dashboard_calendar():
    """Get calendar events for dashboard"""
    # Mock calendar events
    calendar_events = [
        {
            "id": 1,
            "title": "Team Meeting",
            "date": datetime.now().isoformat(),
            "type": "meeting",
            "description": "Weekly team sync"
        },
        {
            "id": 2,
            "title": "Project Deadline",
            "date": (datetime.now()).isoformat(),
            "type": "deadline",
            "description": "Q1 project deliverables due"
        },
        {
            "id": 3,
            "title": "Company Holiday",
            "date": (datetime.now()).isoformat(),
            "type": "holiday",
            "description": "Republic Day"
        }
    ]
    
    return schemas.APIResponse(
        success=True,
        message="Calendar events retrieved",
        data=calendar_events
    )

@router.get("/notifications")
def get_notifications():
    """Get user notifications"""
    # Mock notifications
    notifications = [
        {
            "id": 1,
            "type": "leave_request",
            "title": "Leave Request Pending",
            "message": "You have 2 leave requests pending approval",
            "is_read": False,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": 2,
            "type": "announcement",
            "title": "New Policy Update",
            "message": "Please review the updated remote work policy",
            "is_read": False,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return schemas.APIResponse(
        success=True,
        message="Notifications retrieved",
        data=notifications
    )