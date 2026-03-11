from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
from . import models, schemas
from fastapi import HTTPException

class MeetingService:
    def __init__(self, db: Session, notification_service=None):
        self.db = db
        self.notification_service = notification_service
        
    def create_meeting(self, meeting_data: schemas.MeetingCreate, created_by: int):
        """Create a new meeting"""
        # Create meeting
        db_meeting = models.Meeting(
            title=meeting_data.title,
            description=meeting_data.description,
            meeting_date=meeting_data.meeting_date,
            start_time=meeting_data.start_time,
            end_time=meeting_data.end_time,
            location=meeting_data.location,
            meeting_link=meeting_data.meeting_link,
            meeting_type=meeting_data.meeting_type,
            agenda=meeting_data.agenda,
            created_by=created_by,
            status="scheduled"
        )
        
        self.db.add(db_meeting)
        self.db.commit()
        self.db.refresh(db_meeting)
        
        # Add attendees
        if meeting_data.attendee_ids:
            for user_id in meeting_data.attendee_ids:
                attendee = models.MeetingAttendee(
                    meeting_id=db_meeting.id,
                    user_id=user_id,
                    status="invited"
                )
                self.db.add(attendee)
        
        # Add creator as attendee
        creator_attendee = models.MeetingAttendee(
            meeting_id=db_meeting.id,
            user_id=created_by,
            status="accepted"
        )
        self.db.add(creator_attendee)
        
        self.db.commit()
        self.db.refresh(db_meeting)
        
        # Send notifications
        if self.notification_service and meeting_data.attendee_ids:
            for user_id in meeting_data.attendee_ids:
                try:
                    self.notification_service.create_notification(
                        user_id=user_id,
                        title="New Meeting Invitation",
                        message=f"You've been invited to: {meeting_data.title}",
                        notification_type="meeting",
                        related_id=db_meeting.id
                    )
                except:
                    pass
        
        return db_meeting
        
    def get_meetings(self, user_id: int, filters: Optional[Dict] = None):
        """Get meetings for a user with optional filters"""
        query = self.db.query(models.Meeting).join(
            models.MeetingAttendee,
            models.Meeting.id == models.MeetingAttendee.meeting_id
        ).filter(
            or_(
                models.Meeting.created_by == user_id,
                models.MeetingAttendee.user_id == user_id
            )
        )
        
        if filters:
            if 'status' in filters:
                query = query.filter(models.Meeting.status == filters['status'])
            if 'date_from' in filters:
                query = query.filter(models.Meeting.meeting_date >= filters['date_from'])
            if 'date_to' in filters:
                query = query.filter(models.Meeting.meeting_date <= filters['date_to'])
            if 'meeting_type' in filters:
                query = query.filter(models.Meeting.meeting_type == filters['meeting_type'])
        
        return query.distinct().order_by(models.Meeting.meeting_date.desc()).all()
    
    def get_upcoming_meetings(self, user_id: int, days_ahead: int = 7):
        """Get upcoming meetings for a user"""
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        return self.db.query(models.Meeting).join(
            models.MeetingAttendee,
            models.Meeting.id == models.MeetingAttendee.meeting_id
        ).filter(
            or_(
                models.Meeting.created_by == user_id,
                models.MeetingAttendee.user_id == user_id
            ),
            models.Meeting.meeting_date >= today,
            models.Meeting.meeting_date <= end_date,
            models.Meeting.status.in_(["scheduled", "in-progress"])
        ).distinct().order_by(models.Meeting.meeting_date, models.Meeting.start_time).all()
    
    def get_past_meetings(self, user_id: int, days_back: int = 30):
        """Get past meetings for a user"""
        today = date.today()
        start_date = today - timedelta(days=days_back)
        
        return self.db.query(models.Meeting).join(
            models.MeetingAttendee,
            models.Meeting.id == models.MeetingAttendee.meeting_id
        ).filter(
            or_(
                models.Meeting.created_by == user_id,
                models.MeetingAttendee.user_id == user_id
            ),
            models.Meeting.meeting_date < today,
            models.Meeting.meeting_date >= start_date
        ).distinct().order_by(models.Meeting.meeting_date.desc()).all()
        
    def get_meeting_by_id(self, meeting_id: int, user_id: int):
        """Get a specific meeting"""
        meeting = self.db.query(models.Meeting).filter(
            models.Meeting.id == meeting_id
        ).first()
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Check if user has access
        is_attendee = self.db.query(models.MeetingAttendee).filter(
            models.MeetingAttendee.meeting_id == meeting_id,
            models.MeetingAttendee.user_id == user_id
        ).first()
        
        if meeting.created_by != user_id and not is_attendee:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return meeting
    
    def update_meeting(self, meeting_id: int, meeting_update: schemas.MeetingUpdate, user_id: int):
        """Update a meeting"""
        meeting = self.get_meeting_by_id(meeting_id, user_id)
        
        if meeting.created_by != user_id:
            raise HTTPException(status_code=403, detail="Only the meeting creator can update it")
        
        update_data = meeting_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meeting, field, value)
        
        meeting.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(meeting)
        
        return meeting
    
    def cancel_meeting(self, meeting_id: int, user_id: int, reason: Optional[str] = None):
        """Cancel a meeting"""
        meeting = self.get_meeting_by_id(meeting_id, user_id)
        
        if meeting.created_by != user_id:
            raise HTTPException(status_code=403, detail="Only the meeting creator can cancel it")
        
        meeting.status = "cancelled"
        meeting.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(meeting)
        
        # Notify attendees
        if self.notification_service:
            attendees = self.db.query(models.MeetingAttendee).filter(
                models.MeetingAttendee.meeting_id == meeting_id
            ).all()
            
            for attendee in attendees:
                if attendee.user_id != user_id:
                    try:
                        self.notification_service.create_notification(
                            user_id=attendee.user_id,
                            title="Meeting Cancelled",
                            message=f"Meeting '{meeting.title}' has been cancelled" + (f": {reason}" if reason else ""),
                            notification_type="meeting",
                            related_id=meeting_id
                        )
                    except:
                        pass
        
        return meeting
    
    def check_conflicts(self, user_id: int, meeting_date: date, start_time, end_time, exclude_meeting_id: Optional[int] = None):
        """Check for meeting conflicts"""
        query = self.db.query(models.Meeting).join(
            models.MeetingAttendee,
            models.Meeting.id == models.MeetingAttendee.meeting_id
        ).filter(
            or_(
                models.Meeting.created_by == user_id,
                models.MeetingAttendee.user_id == user_id
            ),
            models.Meeting.meeting_date == meeting_date,
            models.Meeting.status.in_(["scheduled", "in-progress"])
        )
        
        if exclude_meeting_id:
            query = query.filter(models.Meeting.id != exclude_meeting_id)
        
        meetings = query.all()
        
        conflicts = []
        for meeting in meetings:
            # Simple time overlap check
            if (start_time < meeting.end_time and end_time > meeting.start_time):
                conflicts.append(meeting)
        
        return conflicts
    
    def add_attendees(self, meeting_id: int, user_ids: List[int], requester_id: int):
        """Add attendees to a meeting"""
        meeting = self.get_meeting_by_id(meeting_id, requester_id)
        
        for user_id in user_ids:
            # Check if already an attendee
            existing = self.db.query(models.MeetingAttendee).filter(
                models.MeetingAttendee.meeting_id == meeting_id,
                models.MeetingAttendee.user_id == user_id
            ).first()
            
            if not existing:
                attendee = models.MeetingAttendee(
                    meeting_id=meeting_id,
                    user_id=user_id,
                    status="invited"
                )
                self.db.add(attendee)
                
                # Send notification
                if self.notification_service:
                    try:
                        self.notification_service.create_notification(
                            user_id=user_id,
                            title="Meeting Invitation",
                            message=f"You've been added to: {meeting.title}",
                            notification_type="meeting",
                            related_id=meeting_id
                        )
                    except:
                        pass
        
        self.db.commit()
    
    def update_attendee_status(self, meeting_id: int, user_id: int, status: str, requester_id: int):
        """Update attendee status"""
        if user_id != requester_id:
            raise HTTPException(status_code=403, detail="Can only update your own status")
        
        attendee = self.db.query(models.MeetingAttendee).filter(
            models.MeetingAttendee.meeting_id == meeting_id,
            models.MeetingAttendee.user_id == user_id
        ).first()
        
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found")
        
        attendee.status = status
        self.db.commit()
    
    def mark_attendance(self, meeting_id: int, user_id: int, action: str):
        """Mark when user joins/leaves meeting"""
        attendee = self.db.query(models.MeetingAttendee).filter(
            models.MeetingAttendee.meeting_id == meeting_id,
            models.MeetingAttendee.user_id == user_id
        ).first()
        
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found")
        
        if action == "join":
            attendee.joined_at = datetime.utcnow()
        elif action == "leave":
            attendee.left_at = datetime.utcnow()
        
        self.db.commit()
    
    def get_meeting_notes(self, meeting_id: int, user_id: int):
        """Get notes for a meeting"""
        # Verify access
        self.get_meeting_by_id(meeting_id, user_id)
        
        return self.db.query(models.MeetingNote).filter(
            models.MeetingNote.meeting_id == meeting_id,
            or_(
                models.MeetingNote.is_private == False,
                models.MeetingNote.created_by == user_id
            )
        ).order_by(models.MeetingNote.created_at).all()
    
    def add_meeting_note(self, meeting_id: int, user_id: int, content: str, note_type: str = "general", is_private: bool = False):
        """Add a note to a meeting"""
        # Verify access
        self.get_meeting_by_id(meeting_id, user_id)
        
        note = models.MeetingNote(
            meeting_id=meeting_id,
            created_by=user_id,
            content=content,
            note_type=note_type,
            is_private=is_private
        )
        
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        
        return note
    
    def get_action_items(self, meeting_id: Optional[int] = None, assigned_to: Optional[int] = None, status: Optional[str] = None):
        """Get action items"""
        query = self.db.query(models.MeetingActionItem)
        
        if meeting_id:
            query = query.filter(models.MeetingActionItem.meeting_id == meeting_id)
        if assigned_to:
            query = query.filter(models.MeetingActionItem.assigned_to == assigned_to)
        if status:
            query = query.filter(models.MeetingActionItem.status == status)
        
        return query.order_by(models.MeetingActionItem.due_date).all()
    
    def create_action_item(self, meeting_id: int, action_item: schemas.MeetingActionItemCreate, created_by: int):
        """Create an action item"""
        # Verify access
        self.get_meeting_by_id(meeting_id, created_by)
        
        db_action_item = models.MeetingActionItem(
            meeting_id=meeting_id,
            title=action_item.title,
            description=action_item.description,
            assigned_to=action_item.assigned_to,
            created_by=created_by,
            priority=action_item.priority,
            due_date=action_item.due_date,
            status="pending"
        )
        
        self.db.add(db_action_item)
        self.db.commit()
        self.db.refresh(db_action_item)
        
        # Send notification
        if self.notification_service:
            try:
                self.notification_service.create_notification(
                    user_id=action_item.assigned_to,
                    title="New Action Item",
                    message=f"You've been assigned: {action_item.title}",
                    notification_type="task",
                    related_id=db_action_item.id
                )
            except:
                pass
        
        return db_action_item
    
    def update_action_item_status(self, action_item_id: int, status: str, user_id: int):
        """Update action item status"""
        action_item = self.db.query(models.MeetingActionItem).filter(
            models.MeetingActionItem.id == action_item_id
        ).first()
        
        if not action_item:
            raise HTTPException(status_code=404, detail="Action item not found")
        
        if action_item.assigned_to != user_id and action_item.created_by != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        action_item.status = status
        if status == "completed":
            action_item.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(action_item)
        
        return action_item
    
    def get_meeting_analytics(self, user_id: int, date_from: Optional[date] = None, date_to: Optional[date] = None):
        """Get meeting analytics for a user"""
        query = self.db.query(models.Meeting).join(
            models.MeetingAttendee,
            models.Meeting.id == models.MeetingAttendee.meeting_id
        ).filter(
            or_(
                models.Meeting.created_by == user_id,
                models.MeetingAttendee.user_id == user_id
            )
        )
        
        if date_from:
            query = query.filter(models.Meeting.meeting_date >= date_from)
        if date_to:
            query = query.filter(models.Meeting.meeting_date <= date_to)
        
        meetings = query.distinct().all()
        
        total_meetings = len(meetings)
        meetings_organized = len([m for m in meetings if m.created_by == user_id])
        
        # Count attended meetings
        attended_meetings = self.db.query(models.MeetingAttendee).filter(
            models.MeetingAttendee.user_id == user_id,
            models.MeetingAttendee.joined_at.isnot(None)
        ).count()
        
        # Calculate attendance rate
        invited_meetings = self.db.query(models.MeetingAttendee).filter(
            models.MeetingAttendee.user_id == user_id
        ).count()
        
        attendance_rate = round((attended_meetings / invited_meetings * 100) if invited_meetings > 0 else 0, 1)
        
        # Type breakdown
        type_breakdown = {}
        for meeting in meetings:
            type_breakdown[meeting.meeting_type] = type_breakdown.get(meeting.meeting_type, 0) + 1
        
        # Status breakdown
        status_breakdown = {}
        for meeting in meetings:
            status_breakdown[meeting.status] = status_breakdown.get(meeting.status, 0) + 1
        
        return {
            "total_meetings": total_meetings,
            "meetings_organized": meetings_organized,
            "meetings_attended": attended_meetings,
            "attendance_rate": attendance_rate,
            "type_breakdown": type_breakdown,
            "status_breakdown": status_breakdown
        }