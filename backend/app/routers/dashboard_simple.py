from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app import models
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/stats")
def get_dashboard_stats(current_user: models.User = Depends(get_current_user)):
    """Get basic dashboard statistics"""
    return {
        "success": True,
        "message": "Dashboard stats retrieved",
        "data": {
            "total_employees": 25,
            "present_today": 20,
            "on_leave": 3,
            "pending_requests": 5,
            "total_users": 30,
            "open_jobs": 5,
            "pending_applications": 12,
            "active_surveys": 2,
            "recent_hires": 3,
            "application_rate": 85.5,
            "timestamp": datetime.now().isoformat()
        }
    }

@router.get("/activities")
def get_recent_activities(current_user: models.User = Depends(get_current_user)):
    """Get recent activities for dashboard feed"""
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
        },
        {
            "type": "recruitment",
            "message": "New application received for Developer position",
            "timestamp": datetime.now().isoformat(),
            "icon": "user-plus"
        },
        {
            "type": "performance",
            "message": "Q4 performance reviews started",
            "timestamp": datetime.now().isoformat(),
            "icon": "trending-up"
        }
    ]
    
    return {
        "success": True,
        "message": "Recent activities retrieved",
        "data": activities
    }

@router.get("/notifications")
def get_notifications(current_user: models.User = Depends(get_current_user)):
    """Get user notifications"""
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
        },
        {
            "id": 3,
            "type": "performance",
            "title": "Performance Review Due",
            "message": "Your Q4 performance review is due next week",
            "is_read": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return {
        "success": True,
        "message": "Notifications retrieved",
        "data": notifications
    }

@router.get("/calendar")
def get_calendar_events(current_user: models.User = Depends(get_current_user)):
    """Get upcoming calendar events for dashboard"""
    events = [
        {
            "id": "1",
            "title": "Team Meeting",
            "date": "2024-12-20",
            "type": "meeting",
            "icon": "calendar",
            "description": "Weekly team sync meeting"
        },
        {
            "id": "2",
            "title": "John's Birthday",
            "date": "2024-12-22",
            "type": "birthday",
            "icon": "gift",
            "description": "Celebrate John's birthday"
        },
        {
            "id": "3",
            "title": "Christmas Holiday",
            "date": "2024-12-25",
            "type": "holiday",
            "icon": "star",
            "description": "Christmas Day - Office Closed"
        },
        {
            "id": "4",
            "title": "Project Deadline",
            "date": "2024-12-28",
            "type": "deadline",
            "icon": "clock",
            "description": "Q4 project deliverables due"
        },
        {
            "id": "5",
            "title": "New Year Holiday",
            "date": "2025-01-01",
            "type": "holiday",
            "icon": "star",
            "description": "New Year's Day - Office Closed"
        }
    ]
    
    return {
        "success": True,
        "message": "Calendar events retrieved",
        "data": events
    }

@router.get("/employee-stats")
def get_employee_dashboard_stats(current_user: models.User = Depends(get_current_user)):
    """Get employee-specific dashboard statistics"""
    return {
        "success": True,
        "message": "Employee stats retrieved",
        "data": {
            "leave_balance": 12,
            "pending_tasks": 3,
            "learning_hours": 8.5,
            "next_holiday": "Christmas (25 Dec)",
            "employee_id": 1,
            "department": "Engineering",
            "position": "Software Developer"
        }
    }

@router.get("/team-stats")
def get_team_dashboard_stats(current_user: models.User = Depends(get_current_user)):
    """Get team-specific dashboard statistics for managers"""
    # Only managers and above can access team stats
    if current_user.role not in ["manager", "admin", "hr"]:
        return {
            "success": False,
            "message": "Access denied - Manager role required",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Team stats retrieved",
        "data": {
            "team_size": 12,
            "open_positions": 3,
            "interviews_today": 2,
            "team_attendance_rate": 95.5,
            "pending_reviews": 4,
            "team_workload": [
                {"name": "Alice", "load": 95, "status": "Overloaded"},
                {"name": "Bob", "load": 45, "status": "Underutilized"},
                {"name": "Charlie", "load": 75, "status": "Optimal"},
                {"name": "Diana", "load": 88, "status": "High"}
            ]
        }
    }

@router.get("/candidate-stats")
def get_candidate_dashboard_stats(current_user: models.User = Depends(get_current_user)):
    """Get candidate-specific dashboard statistics"""
    return {
        "success": True,
        "message": "Candidate stats retrieved",
        "data": {
            "total_applications": 5,
            "pending_applications": 2,
            "interview_scheduled": 1,
            "applications": [
                {
                    "id": 1,
                    "job_title": "Software Developer",
                    "company": "TechCorp",
                    "status": "interview",
                    "applied_date": "2024-12-15T10:00:00",
                    "location": "Remote"
                },
                {
                    "id": 2,
                    "job_title": "Frontend Developer",
                    "company": "WebSolutions",
                    "status": "applied",
                    "applied_date": "2024-12-10T14:30:00",
                    "location": "New York"
                }
            ]
        }
    }

@router.get("/health")
def dashboard_health_check():
    """Dashboard service health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard"
    }