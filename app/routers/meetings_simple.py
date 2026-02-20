from fastapi import APIRouter, Body
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"]
)

class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_date: str
    start_time: str
    end_time: str
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_type: Optional[str] = "meeting"
    agenda: Optional[str] = None
    attendee_ids: Optional[List[int]] = []

@router.post("/")
def create_meeting(meeting: MeetingCreate):
    """Create a new meeting"""
    return {
        "success": True,
        "message": "Meeting created successfully",
        "data": {
            "id": 999,
            "title": meeting.title,
            "description": meeting.description,
            "meeting_date": meeting.meeting_date,
            "start_time": meeting.start_time,
            "end_time": meeting.end_time,
            "location": meeting.location,
            "meeting_link": meeting.meeting_link,
            "meeting_type": meeting.meeting_type,
            "agenda": meeting.agenda,
            "attendee_ids": meeting.attendee_ids,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
    }

@router.post("/check-conflicts")
def check_meeting_conflicts(data: dict = Body(...)):
    """Check for meeting conflicts"""
    return {
        "success": True,
        "conflicts": []
    }

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

@router.get("/upcoming")
def get_upcoming_meetings():
    """Get upcoming meetings"""
    return [
        {
            "id": 1,
            "title": "Team Standup",
            "description": "Daily team sync meeting",
            "meeting_date": "2026-02-21",
            "start_time": "09:00",
            "end_time": "09:30",
            "location": "Conference Room A",
            "meeting_type": "standup",
            "status": "scheduled"
        },
        {
            "id": 2,
            "title": "Client Meeting",
            "description": "Quarterly review with client",
            "meeting_date": "2026-02-22",
            "start_time": "14:00",
            "end_time": "15:00",
            "meeting_link": "https://meet.google.com/abc-defg-hij",
            "meeting_type": "meeting",
            "status": "scheduled"
        }
    ]

@router.get("/past")
def get_past_meetings():
    """Get past meetings"""
    return [
        {
            "id": 10,
            "title": "Sprint Planning",
            "description": "Planning for next sprint",
            "meeting_date": "2026-02-15",
            "start_time": "10:00",
            "end_time": "11:30",
            "location": "Conference Room B",
            "meeting_type": "meeting",
            "status": "completed"
        }
    ]

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
    return [
        {
            "id": 1,
            "meeting_id": meeting_id,
            "content": f"Sample meeting notes for meeting {meeting_id}",
            "note_type": "general",
            "created_by": "admin@company.com",
            "created_at": "2025-01-28T10:00:00",
            "updated_at": "2025-01-28T11:30:00"
        }
    ]

@router.post("/{meeting_id}/notes")
def add_meeting_note(meeting_id: int, note: dict = Body(...)):
    """Add meeting note"""
    return {
        "success": True,
        "message": "Note added successfully",
        "data": {
            "id": 999,
            "meeting_id": meeting_id,
            "content": note.get("content"),
            "note_type": note.get("note_type", "general"),
            "created_at": datetime.now().isoformat()
        }
    }

@router.get("/{meeting_id}/action-items")
def get_meeting_action_items(meeting_id: int):
    """Get meeting action items"""
    return [
        {
            "id": 1,
            "meeting_id": meeting_id,
            "title": "Follow up with client on proposal",
            "description": "Send proposal document",
            "assigned_to": "john@company.com",
            "due_date": "2025-02-01",
            "priority": "high",
            "status": "pending"
        },
        {
            "id": 2,
            "meeting_id": meeting_id,
            "title": "Update project timeline",
            "description": "Revise timeline based on discussion",
            "assigned_to": "sarah@company.com",
            "due_date": "2025-01-30",
            "priority": "medium",
            "status": "completed"
        }
    ]

@router.post("/{meeting_id}/action-items")
def create_action_item(meeting_id: int, action_item: dict = Body(...)):
    """Create action item"""
    return {
        "success": True,
        "message": "Action item created successfully",
        "data": {
            "id": 999,
            "meeting_id": meeting_id,
            "title": action_item.get("title"),
            "description": action_item.get("description"),
            "assigned_to": action_item.get("assigned_to"),
            "due_date": action_item.get("due_date"),
            "priority": action_item.get("priority", "medium"),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
    }

@router.post("/{meeting_id}/attendance/join")
def mark_meeting_attendance(meeting_id: int):
    """Mark attendance when joining meeting"""
    return {
        "success": True,
        "message": "Attendance marked"
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