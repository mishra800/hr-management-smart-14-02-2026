from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"]
)

@router.get("/")
def get_meetings():
    """Get all meetings"""
    return {
        "success": True,
        "message": "Meetings retrieved",
        "data": [
            {
                "id": 1,
                "title": "Team Standup",
                "description": "Daily team sync meeting",
                "start_time": "2024-12-20T09:00:00",
                "end_time": "2024-12-20T09:30:00",
                "attendees": ["john@example.com", "jane@example.com"],
                "status": "scheduled"
            }
        ]
    }

@router.get("/rooms")
def get_meeting_rooms():
    """Get meeting rooms"""
    return {
        "success": True,
        "message": "Meeting rooms retrieved",
        "data": [
            {
                "id": 1,
                "name": "Conference Room A",
                "capacity": 10,
                "equipment": ["Projector", "Whiteboard"],
                "available": True
            },
            {
                "id": 2,
                "name": "Conference Room B",
                "capacity": 6,
                "equipment": ["TV Screen", "Video Conference"],
                "available": False
            }
        ]
    }

@router.get("/analytics")
def get_meeting_analytics():
    """Get meeting analytics"""
    return {
        "success": True,
        "data": {
            "total_meetings": 45,
            "meetings_this_month": 12,
            "average_duration": 45,
            "most_used_room": "Conference Room A",
            "meeting_types": {
                "team_meeting": 15,
                "client_call": 8,
                "interview": 5,
                "training": 3,
                "other": 14
            },
            "attendance_rate": 85.5
        }
    }

@router.get("/{meeting_id}/notes")
def get_meeting_notes(meeting_id: int):
    """Get meeting notes"""
    return {
        "success": True,
        "data": {
            "meeting_id": meeting_id,
            "notes": f"Sample meeting notes for meeting {meeting_id}",
            "created_by": "admin@company.com",
            "created_at": "2025-01-28T10:00:00",
            "updated_at": "2025-01-28T11:30:00"
        }
    }

@router.get("/{meeting_id}/action-items")
def get_meeting_action_items(meeting_id: int):
    """Get meeting action items"""
    return {
        "success": True,
        "data": [
            {
                "id": 1,
                "meeting_id": meeting_id,
                "description": "Follow up with client on proposal",
                "assigned_to": "john@company.com",
                "due_date": "2025-02-01",
                "status": "pending"
            },
            {
                "id": 2,
                "meeting_id": meeting_id,
                "description": "Update project timeline",
                "assigned_to": "sarah@company.com",
                "due_date": "2025-01-30",
                "status": "completed"
            }
        ]
    }

@router.get("/schedule")
def get_meeting_schedule():
    """Get meeting schedule"""
    return {
        "success": True,
        "message": "Meeting schedule retrieved",
        "data": {
            "today": [
                {"time": "09:00", "title": "Team Standup", "room": "Conference Room A"},
                {"time": "14:00", "title": "Client Meeting", "room": "Conference Room B"}
            ],
            "upcoming": [
                {"date": "2024-12-21", "count": 3},
                {"date": "2024-12-22", "count": 1}
            ]
        }
    }