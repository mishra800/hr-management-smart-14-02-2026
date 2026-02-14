"""
Notifications Management Router
Handles in-app notifications, email notifications, and notification preferences
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from app.dependencies import get_current_user
from app.error_handlers import check_user_permissions, log_user_action
from app.database import get_db
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import threading
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    LEAVE_REQUEST = "leave_request"
    ATTENDANCE_ALERT = "attendance_alert"
    SYSTEM_UPDATE = "system_update"
    REMINDER = "reminder"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    recipient_ids: Optional[List[int]] = None
    recipient_roles: Optional[List[str]] = None
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None

class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    notification_types: Dict[str, bool] = {}

# Response Models for API Safety
class NotificationOut(BaseModel):
    id: str
    title: str
    message: str
    type: str
    priority: str
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    is_read: bool
    is_archived: bool
    read_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

class NotificationListResponse(BaseModel):
    notifications: List[NotificationOut]
    total: int
    skip: int
    limit: int
    has_more: bool

class NotificationPreferencesOut(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    whatsapp_enabled: bool = False
    phone_number: str = ""
    whatsapp_number: str = ""

# Thread-safe notification service
class NotificationService:
    def __init__(self):
        self._lock = threading.RLock()
        self._id_counter = 0
    
    def generate_notification_id(self) -> str:
        """Generate thread-safe unique notification ID"""
        with self._lock:
            # Use UUID for guaranteed uniqueness across workers
            return str(uuid.uuid4())
    
    def get_user_notifications(self, db, user_id: int, user_role: str, 
                             skip: int = 0, limit: int = 50, 
                             unread_only: bool = False, 
                             type_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get notifications for user with efficient database queries"""
        try:
            # Build query conditions
            query_conditions = {}
            
            # Filter by recipient (either direct ID or role-based)
            # In real implementation, this would be a proper database query
            # For now, using mock database with efficient filtering
            
            notifications = db.find_many("notifications", {})
            
            # Filter for current user
            user_notifications = []
            for notification in notifications:
                # Check if user is recipient
                recipient_ids = notification.get("recipient_ids", [])
                recipient_roles = notification.get("recipient_roles", [])
                
                if user_id in recipient_ids or user_role in recipient_roles:
                    # Apply filters
                    if unread_only and notification.get("is_read", False):
                        continue
                    if type_filter and notification.get("type") != type_filter:
                        continue
                    
                    # Check if notification is expired
                    expires_at = notification.get("expires_at")
                    if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                        continue
                    
                    user_notifications.append(notification)
            
            # Sort by created_at (most recent first) - efficient in-memory sort
            user_notifications.sort(
                key=lambda x: x.get("created_at", ""), 
                reverse=True
            )
            
            # Apply pagination
            total = len(user_notifications)
            paginated = user_notifications[skip:skip + limit]
            
            return {
                "notifications": paginated,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return {
                "notifications": [],
                "total": 0,
                "skip": skip,
                "limit": limit,
                "has_more": False
            }
    
    def create_notification(self, db, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification with thread-safe ID generation"""
        try:
            notification_id = self.generate_notification_id()
            
            new_notification = {
                "id": notification_id,
                "title": notification_data["title"],
                "message": notification_data["message"],
                "type": notification_data["type"],
                "priority": notification_data["priority"],
                "recipient_ids": notification_data.get("recipient_ids", []),
                "recipient_roles": notification_data.get("recipient_roles", []),
                "action_url": notification_data.get("action_url"),
                "expires_at": notification_data.get("expires_at"),
                "created_by": notification_data["created_by"],
                "created_at": datetime.now(),
                "is_read": False,
                "is_archived": False
            }
            
            # Store in database
            db.insert("notifications", new_notification)
            
            return new_notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise HTTPException(status_code=500, detail="Failed to create notification")

# Global notification service instance
notification_service = NotificationService()

@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    type_filter: Optional[NotificationType] = None,
    db = Depends(get_db)
):
    """Get notifications for current user with proper response model"""
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    result = notification_service.get_user_notifications(
        db=db,
        user_id=user_id,
        user_role=user_role,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        type_filter=type_filter.value if type_filter else None
    )
    
    # Convert to response model format
    notifications_out = []
    for notification in result["notifications"]:
        notifications_out.append(NotificationOut(
            id=notification["id"],
            title=notification["title"],
            message=notification["message"],
            type=notification["type"],
            priority=notification["priority"],
            action_url=notification.get("action_url"),
            expires_at=notification.get("expires_at"),
            created_at=notification["created_at"],
            is_read=notification.get("is_read", False),
            is_archived=notification.get("is_archived", False),
            read_at=notification.get("read_at"),
            archived_at=notification.get("archived_at")
        ))
    
    return NotificationListResponse(
        notifications=notifications_out,
        total=result["total"],
        skip=result["skip"],
        limit=result["limit"],
        has_more=result["has_more"]
    )

@router.post("/", response_model=Dict[str, Any])
async def create_notification(
    notification: NotificationCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create new notification (Admin/HR only)"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr"])
    
    try:
        notification_data = {
            "title": notification.title,
            "message": notification.message,
            "type": notification.type.value,
            "priority": notification.priority.value,
            "recipient_ids": notification.recipient_ids or [],
            "recipient_roles": notification.recipient_roles or [],
            "action_url": notification.action_url,
            "expires_at": notification.expires_at.isoformat() if notification.expires_at else None,
            "created_by": current_user.get("id")
        }
        
        new_notification = notification_service.create_notification(db, notification_data)
        
        log_user_action(
            current_user.get("id"),
            "create_notification",
            "notification",
            {"notification_id": new_notification["id"], "title": notification.title}
        )
        
        return {
            "success": True,
            "message": "Notification created successfully",
            "data": new_notification
        }
        
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create notification")

@router.put("/{notification_id}")
async def update_notification(
    notification_id: str,
    update_data: NotificationUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update notification (mark as read/archived)"""
    try:
        notification = db.find_one("notifications", {"id": notification_id})
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        user_id = current_user.get("id")
        
        # Check if user has access to this notification
        if (user_id not in notification.get("recipient_ids", []) and 
            current_user.get("role") not in notification.get("recipient_roles", [])):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare updates
        updates = {"updated_at": datetime.now()}
        
        if update_data.is_read is not None:
            updates["is_read"] = update_data.is_read
            updates["read_at"] = datetime.now() if update_data.is_read else None
        
        if update_data.is_archived is not None:
            updates["is_archived"] = update_data.is_archived
            updates["archived_at"] = datetime.now() if update_data.is_archived else None
        
        # Update in database
        success = db.update("notifications", notification_id, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update notification")
        
        # Get updated notification
        updated_notification = db.find_one("notifications", {"id": notification_id})
        
        return {
            "success": True,
            "message": "Notification updated successfully",
            "data": updated_notification
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification")

@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get unread notification count for current user"""
    try:
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        
        # Get all notifications for user
        notifications = db.find_many("notifications", {})
        
        unread_count = 0
        for notification in notifications:
            # Check if user is recipient
            if (user_id in notification.get("recipient_ids", []) or 
                user_role in notification.get("recipient_roles", [])):
                
                # Check if unread and not expired
                if not notification.get("is_read", False):
                    expires_at = notification.get("expires_at")
                    if not expires_at or datetime.fromisoformat(expires_at) > datetime.now():
                        unread_count += 1
        
        return {"unread_count": unread_count}
        
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return {"unread_count": 0}

@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark specific notification as read"""
    try:
        notification = db.find_one("notifications", {"id": notification_id})
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        user_id = current_user.get("id")
        
        # Check if user has access to this notification
        if (user_id not in notification.get("recipient_ids", []) and 
            current_user.get("role") not in notification.get("recipient_roles", [])):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update notification
        updates = {
            "is_read": True,
            "read_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        success = db.update("notifications", notification_id, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to mark notification as read")
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")

@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark all notifications as read for current user"""
    try:
        user_id = current_user.get("id")
        user_role = current_user.get("role")
        updated_count = 0
        
        # Get all notifications for user
        notifications = db.find_many("notifications", {})
        
        for notification in notifications:
            # Check if user is recipient and notification is unread
            if (user_id in notification.get("recipient_ids", []) or 
                user_role in notification.get("recipient_roles", [])):
                
                if not notification.get("is_read", False):
                    updates = {
                        "is_read": True,
                        "read_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    success = db.update("notifications", notification["id"], updates)
                    if success:
                        updated_count += 1
        
        return {
            "success": True,
            "message": f"Marked {updated_count} notifications as read"
        }
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notifications as read")

@router.get("/preferences", response_model=NotificationPreferencesOut)
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get notification preferences for current user"""
    try:
        user_id = current_user.get("id")
        preferences = db.find_one("notification_preferences", {"user_id": user_id})
        
        if not preferences:
            # Return default preferences
            return NotificationPreferencesOut(
                email_enabled=True,
                sms_enabled=False,
                whatsapp_enabled=False,
                phone_number="",
                whatsapp_number=""
            )
        
        return NotificationPreferencesOut(
            email_enabled=preferences.get("email_enabled", True),
            sms_enabled=preferences.get("sms_enabled", False),
            whatsapp_enabled=preferences.get("whatsapp_enabled", False),
            phone_number=preferences.get("phone_number", ""),
            whatsapp_number=preferences.get("whatsapp_number", "")
        )
        
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        return NotificationPreferencesOut()

@router.patch("/preferences")
async def update_notification_preferences_patch(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update notification preferences for current user (PATCH method)"""
    try:
        user_id = current_user.get("id")
        
        preference_data = {
            "user_id": user_id,
            "email_notifications": preferences.email_notifications,
            "push_notifications": preferences.push_notifications,
            "sms_notifications": preferences.sms_notifications,
            "notification_types": preferences.notification_types,
            "updated_at": datetime.now()
        }
        
        # Check if preferences exist
        existing = db.find_one("notification_preferences", {"user_id": user_id})
        
        if existing:
            success = db.update("notification_preferences", existing["id"], preference_data)
        else:
            db.insert("notification_preferences", preference_data)
            success = True
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return {
            "success": True,
            "message": "Notification preferences updated successfully",
            "data": preference_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

@router.put("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update notification preferences for current user"""
    return await update_notification_preferences_patch(preferences, current_user, db)

@router.post("/test-notification")
async def send_test_notification(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Send test notification (Admin/HR only)"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr"])
    
    try:
        notification_data = {
            "title": "Test Notification",
            "message": f"This is a test notification sent by {current_user.get('first_name', 'Admin')} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "type": "info",
            "priority": "medium",
            "recipient_ids": [current_user.get("id")],
            "recipient_roles": [],
            "action_url": None,
            "expires_at": None,
            "created_by": current_user.get("id")
        }
        
        test_notification = notification_service.create_notification(db, notification_data)
        
        return {
            "success": True,
            "message": "Test notification sent successfully",
            "data": test_notification
        }
        
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test notification")

@router.get("/stats")
async def get_notification_stats(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get notification statistics"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr"])
    
    try:
        # Get all notifications
        all_notifications = db.find_many("notifications", {})
        
        total_notifications = len(all_notifications)
        
        # Count active notifications (not expired)
        active_notifications = 0
        type_breakdown = {}
        recent_activity = 0
        
        week_ago = datetime.now() - timedelta(days=7)
        
        for notification in all_notifications:
            # Check if active (not expired)
            expires_at = notification.get("expires_at")
            if not expires_at or datetime.fromisoformat(expires_at) > datetime.now():
                active_notifications += 1
            
            # Count by type
            ntype = notification.get("type", "unknown")
            type_breakdown[ntype] = type_breakdown.get(ntype, 0) + 1
            
            # Count recent activity
            created_at = notification.get("created_at")
            if created_at and isinstance(created_at, datetime) and created_at > week_ago:
                recent_activity += 1
            elif created_at and isinstance(created_at, str):
                try:
                    created_datetime = datetime.fromisoformat(created_at)
                    if created_datetime > week_ago:
                        recent_activity += 1
                except:
                    pass
        
        return {
            "success": True,
            "data": {
                "total_notifications": total_notifications,
                "active_notifications": active_notifications,
                "expired_notifications": total_notifications - active_notifications,
                "type_breakdown": type_breakdown,
                "recent_activity": recent_activity
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification statistics")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete notification (Admin only)"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin"])
    
    try:
        notification = db.find_one("notifications", {"id": notification_id})
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        success = db.delete("notifications", notification_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete notification")
        
        log_user_action(
            current_user.get("id"),
            "delete_notification",
            "notification",
            {"notification_id": notification_id, "title": notification.get("title")}
        )
        
        return {
            "success": True,
            "message": "Notification deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete notification")

@router.get("/health")
async def notifications_health_check(db = Depends(get_db)):
    """Notifications service health check"""
    try:
        # Test database connection
        notifications_count = db.count("notifications")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "notifications",
            "total_notifications": notifications_count
        }
        
    except Exception as e:
        logger.error(f"Notifications health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "service": "notifications",
            "error": str(e)
        }

# Initialize sample notifications on startup
def initialize_sample_notifications(db):
    """Initialize sample notifications for testing"""
    try:
        # Check if notifications already exist
        existing_count = db.count("notifications")
        if existing_count > 0:
            logger.info(f"Notifications already initialized: {existing_count} notifications found")
            return
        
        sample_notifications = [
            {
                "id": str(uuid.uuid4()),
                "title": "Welcome to HR System",
                "message": "Welcome to the new HR Management System. Please complete your profile.",
                "type": "info",
                "priority": "medium",
                "recipient_roles": ["employee"],
                "recipient_ids": [],
                "created_by": 1,
                "created_at": datetime.now(),
                "is_read": False,
                "is_archived": False
            },
            {
                "id": str(uuid.uuid4()),
                "title": "System Maintenance",
                "message": "Scheduled maintenance will occur this weekend. Please save your work.",
                "type": "warning",
                "priority": "high",
                "recipient_roles": ["employee", "manager", "hr", "admin"],
                "recipient_ids": [],
                "action_url": "/announcements",
                "created_by": 1,
                "created_at": datetime.now() - timedelta(hours=2),
                "is_read": False,
                "is_archived": False
            }
        ]
        
        for notification in sample_notifications:
            db.insert("notifications", notification)
        
        logger.info(f"Initialized {len(sample_notifications)} sample notifications")
        
    except Exception as e:
        logger.error(f"Error initializing sample notifications: {e}")

# Initialize sample data when module is imported
try:
    from app.database import get_db
    db = get_db()
    initialize_sample_notifications(db)
except Exception as e:
    logger.warning(f"Could not initialize sample notifications: {e}")