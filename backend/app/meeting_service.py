from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time, timedelta
from . import models, schemas
import uuid
from sqlalchemy import and_, or_, func
from fastapi import HTTPException

class MeetingService:
    def __init__(self, db: Session, notification_service=None):
        self.db = db
        self.notification_service = notification_service

    def create_meeting(self, meeting_data: schemas.MeetingCreate, created_by: int) -> models.Meeting:
        """Create a new meeting with attendees"""
        # Create the meeting
        db_meeting = models.Meeting(
            title=meeting_data.title,
            description=meeting_data.description,
            meeting_date=meeting_data.meeting_date,
            start_time=datetime.strptime(meeting_data.start_time, "%H:%M").time(),
            end_time=datetime.strptime(meeting_data.end_time, "%H:%M").time(),
            location=meeting_data.location,
            meeting_link=meeting_data.meeting_link,
            meeting_type=meeting_data.meeting_type,
            is_recurring=meeting_data.is_recurring,
            recurrence_pattern=meeting_data.recurrence_pattern,
            recurrence_end_date=meeting_data.recurrence_end_date,
            agenda=meeting_data.agenda,
            created_by=created_by
        )
        
        self.db.add(db_meeting)
        self.db.commit()
        self.db.refresh(db_meeting)
        
        return db_meeting

    def get_meetings(self, user_id: int, filters: Dict[str, Any] = None) -> List[models.Meeting]:
        """Get meetings for a user with optional filters"""
        query = self.db.query(models.Meeting).filter(
            or_(
                models.Meeting.created_by == user_id,
                models.Meeting.attendees.any(models.MeetingAttendee.user_id == user_id)
            )
        )
        
        if filters:
            if filters.get('status'):
                query = query.filter(models.Meeting.status == filters['status'])
            if filters.get('date_from'):
                query = query.filter(models.Meeting.meeting_date >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(models.Meeting.meeting_date <= filters['date_to'])
            if filters.get('meeting_type'):
                query = query.filter(models.Meeting.meeting_type == filters['meeting_type'])
        
        return query.order_by(models.Meeting.meeting_date.desc(), models.Meeting.start_time.desc()).all()

    def get_meeting_by_id(self, meeting_id: int, user_id: int) -> models.Meeting:
        """Get a specific meeting if user has access"""
        meeting = self.db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Check access
        is_attendee = any(att.user_id == user_id for att in meeting.attendees)
        if meeting.created_by != user_id and not is_attendee:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return meeting

    def update_meeting(self, meeting_id: int, meeting_data: schemas.MeetingUpdate, user_id: int) -> models.Meeting:
        """Update meeting details"""
        meeting = self.get_meeting_by_id(meeting_id, user_id)
        
        # Check if user can edit
        if meeting.created_by != user_id:
            raise HTTPException(status_code=403, detail="Only meeting organizer can edit")
        
        # Update fields
        for field, value in meeting_data.dict(exclude_unset=True).items():
            if field in ['start_time', 'end_time'] and value:
                value = datetime.strptime(value, "%H:%M").time()
            setattr(meeting, field, value)
        
        meeting.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(meeting)
        
        return meeting

    def cancel_meeting(self, meeting_id: int, user_id: int, reason: str = None) -> models.Meeting:
        """Cancel a meeting"""
        meeting = self.get_meeting_by_id(meeting_id, user_id)
        
        if meeting.created_by != user_id:
            raise HTTPException(status_code=403, detail="Only meeting organizer can cancel")
        
        meeting.status = "cancelled"
        meeting.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(meeting)
        
        return meeting

    def get_upcoming_meetings(self, user_id: int, days_ahead: int = 7) -> List[models.Meeting]:
        """Get upcoming meetings for a user"""
        end_date = date.today() + timedelta(days=days_ahead)
        
        return self.db.query(models.Meeting).filter(
            and_(
                models.Meeting.meeting_date >= date.today(),
                models.Meeting.meeting_date <= end_date,
                models.Meeting.status == "scheduled",
                or_(
                    models.Meeting.created_by == user_id,
                    models.Meeting.attendees.any(models.MeetingAttendee.user_id == user_id)
                )
            )
        ).order_by(models.Meeting.meeting_date, models.Meeting.start_time).all()

    def get_past_meetings(self, user_id: int, days_back: int = 30) -> List[models.Meeting]:
        """Get past/completed meetings for a user"""
        start_date = date.today() - timedelta(days=days_back)
        
        return self.db.query(models.Meeting).filter(
            and_(
                models.Meeting.meeting_date < date.today(),
                models.Meeting.meeting_date >= start_date,
                or_(
                    models.Meeting.created_by == user_id,
                    models.Meeting.attendees.any(models.MeetingAttendee.user_id == user_id)
                )
            )
        ).order_by(models.Meeting.meeting_date.desc(), models.Meeting.start_time.desc()).all()

    def check_conflicts(self, user_id: int, meeting_date: date, start_time: time, end_time: time, exclude_meeting_id: int = None) -> List[models.Meeting]:
        """Check for meeting conflicts for a user"""
        query = self.db.query(models.Meeting).filter(
            and_(
                models.Meeting.meeting_date == meeting_date,
                models.Meeting.status == "scheduled",
                or_(
                    models.Meeting.created_by == user_id,
                    models.Meeting.attendees.any(models.MeetingAttendee.user_id == user_id)
                ),
                or_(
                    and_(models.Meeting.start_time <= start_time, models.Meeting.end_time > start_time),
                    and_(models.Meeting.start_time < end_time, models.Meeting.end_time >= end_time),
                    and_(models.Meeting.start_time >= start_time, models.Meeting.end_time <= end_time)
                )
            )
        )
        
        if exclude_meeting_id:
            query = query.filter(models.Meeting.id != exclude_meeting_id)
        
        return query.all()

    def get_meeting_analytics(self, user_id: int, date_from: date = None, date_to: date = None) -> Dict[str, Any]:
        """Get meeting analytics for a user"""
        if not date_from:
            date_from = date.today() - timedelta(days=30)
        if not date_to:
            date_to = date.today()
        
        # Base query for user's meetings
        base_query = self.db.query(models.Meeting).filter(
            and_(
                models.Meeting.meeting_date >= date_from,
                models.Meeting.meeting_date <= date_to,
                or_(
                    models.Meeting.created_by == user_id,
                    models.Meeting.attendees.any(models.MeetingAttendee.user_id == user_id)
                )
            )
        )
        
        total_meetings = base_query.count()
        
        return {
            "total_meetings": total_meetings,
            "date_range": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            }
        }