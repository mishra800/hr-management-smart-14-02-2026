from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app import models
from app.database import engine
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/stats")
def get_dashboard_stats(current_user: models.User = Depends(get_current_user)):
    """Get real dashboard statistics from database"""
    try:
        with engine.connect() as conn:
            # Count total active employees
            total_employees = conn.execute(
                text("SELECT COUNT(*) FROM employees WHERE status = 'active'")
            ).scalar() or 0
            
            # Count employees present today
            present_today = conn.execute(
                text("""
                    SELECT COUNT(DISTINCT employee_id) 
                    FROM attendance 
                    WHERE DATE(check_in_time) = CURRENT_DATE 
                    AND check_out_time IS NULL
                """)
            ).scalar() or 0
            
            # Count employees on leave today
            on_leave = conn.execute(
                text("""
                    SELECT COUNT(DISTINCT employee_id) 
                    FROM leave_requests 
                    WHERE status = 'approved' 
                    AND CURRENT_DATE BETWEEN start_date AND end_date
                """)
            ).scalar() or 0
            
            # Count pending leave requests
            pending_requests = conn.execute(
                text("SELECT COUNT(*) FROM leave_requests WHERE status = 'pending'")
            ).scalar() or 0
            
            # Count total users
            total_users = conn.execute(
                text("SELECT COUNT(*) FROM users WHERE is_active = true")
            ).scalar() or 0
            
            # Count open job postings
            open_jobs = conn.execute(
                text("SELECT COUNT(*) FROM job_postings WHERE status = 'active'")
            ).scalar() or 0
            
            # Count pending applications
            pending_applications = conn.execute(
                text("SELECT COUNT(*) FROM applications WHERE status = 'pending'")
            ).scalar() or 0
            
            # Count recent hires (last 30 days)
            recent_hires = conn.execute(
                text("""
                    SELECT COUNT(*) FROM employees 
                    WHERE hire_date >= CURRENT_DATE - INTERVAL '30 days'
                """)
            ).scalar() or 0
            
            # Calculate attendance rate for today
            if total_employees > 0:
                attendance_rate = round((present_today / total_employees) * 100, 1)
            else:
                attendance_rate = 0.0
            
            return {
                "success": True,
                "message": "Dashboard stats retrieved",
                "data": {
                    "total_employees": total_employees,
                    "present_today": present_today,
                    "on_leave": on_leave,
                    "pending_requests": pending_requests,
                    "total_users": total_users,
                    "open_jobs": open_jobs,
                    "pending_applications": pending_applications,
                    "active_surveys": 0,  # Add survey table query if you have it
                    "recent_hires": recent_hires,
                    "attendance_rate": attendance_rate,
                    "timestamp": datetime.now().isoformat()
                }
            }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        # Return minimal data on error
        return {
            "success": False,
            "message": f"Error fetching stats: {str(e)}",
            "data": {
                "total_employees": 0,
                "present_today": 0,
                "on_leave": 0,
                "pending_requests": 0,
                "total_users": 0,
                "open_jobs": 0,
                "pending_applications": 0,
                "active_surveys": 0,
                "recent_hires": 0,
                "attendance_rate": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        }

@router.get("/activities")
def get_recent_activities(current_user: models.User = Depends(get_current_user)):
    """Get recent activities from database"""
    try:
        with engine.connect() as conn:
            activities = []
            
            # Get recent attendance check-ins (last 5)
            attendance_records = conn.execute(
                text("""
                    SELECT e.first_name, e.last_name, a.check_in_time
                    FROM attendance a
                    JOIN employees e ON a.employee_id = e.id
                    WHERE DATE(a.check_in_time) = CURRENT_DATE
                    ORDER BY a.check_in_time DESC
                    LIMIT 3
                """)
            ).fetchall()
            
            for record in attendance_records:
                activities.append({
                    "type": "attendance",
                    "message": f"{record[0]} {record[1]} checked in",
                    "timestamp": record[2].isoformat() if record[2] else datetime.now().isoformat(),
                    "icon": "clock"
                })
            
            # Get recent leave requests (last 3)
            leave_records = conn.execute(
                text("""
                    SELECT e.first_name, e.last_name, lr.created_at, lr.status
                    FROM leave_requests lr
                    JOIN employees e ON lr.employee_id = e.id
                    ORDER BY lr.created_at DESC
                    LIMIT 2
                """)
            ).fetchall()
            
            for record in leave_records:
                status_text = "requested" if record[3] == "pending" else record[3]
                activities.append({
                    "type": "leave",
                    "message": f"{record[0]} {record[1]} {status_text} leave",
                    "timestamp": record[2].isoformat() if record[2] else datetime.now().isoformat(),
                    "icon": "calendar"
                })
            
            # Get recent job applications (last 2)
            application_records = conn.execute(
                text("""
                    SELECT jp.title, a.created_at
                    FROM applications a
                    JOIN job_postings jp ON a.job_id = jp.id
                    ORDER BY a.created_at DESC
                    LIMIT 2
                """)
            ).fetchall()
            
            for record in application_records:
                activities.append({
                    "type": "recruitment",
                    "message": f"New application received for {record[0]}",
                    "timestamp": record[1].isoformat() if record[1] else datetime.now().isoformat(),
                    "icon": "user-plus"
                })
            
            # If no activities found, return a default message
            if not activities:
                activities.append({
                    "type": "info",
                    "message": "No recent activities",
                    "timestamp": datetime.now().isoformat(),
                    "icon": "info"
                })
            
            return {
                "success": True,
                "message": "Recent activities retrieved",
                "data": activities[:10]  # Limit to 10 most recent
            }
    except Exception as e:
        logger.error(f"Error fetching activities: {e}")
        return {
            "success": True,
            "message": "Activities retrieved (fallback)",
            "data": [
                {
                    "type": "info",
                    "message": "Activity feed temporarily unavailable",
                    "timestamp": datetime.now().isoformat(),
                    "icon": "info"
                }
            ]
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
    """Get upcoming calendar events from database"""
    try:
        with engine.connect() as conn:
            events = []
            
            # Get upcoming meetings (if meetings table exists)
            try:
                meeting_records = conn.execute(
                    text("""
                        SELECT title, scheduled_time, description
                        FROM meetings
                        WHERE scheduled_time >= CURRENT_TIMESTAMP
                        ORDER BY scheduled_time ASC
                        LIMIT 3
                    """)
                ).fetchall()
                
                for record in meeting_records:
                    events.append({
                        "id": str(len(events) + 1),
                        "title": record[0],
                        "date": record[1].isoformat() if record[1] else datetime.now().isoformat(),
                        "type": "meeting",
                        "icon": "calendar",
                        "description": record[2] or "Team meeting"
                    })
            except Exception:
                pass  # Meetings table might not exist
            
            # Get upcoming holidays/events
            # Add Christmas if it's coming up
            current_date = datetime.now()
            if current_date.month == 12 and current_date.day < 25:
                events.append({
                    "id": "christmas",
                    "title": "Christmas Holiday",
                    "date": f"{current_date.year}-12-25",
                    "type": "holiday",
                    "icon": "star",
                    "description": "Christmas Day - Office Closed"
                })
            
            # Add New Year if it's coming up
            if current_date.month == 12 or (current_date.month == 1 and current_date.day < 2):
                year = current_date.year if current_date.month == 12 else current_date.year
                events.append({
                    "id": "newyear",
                    "title": "New Year Holiday",
                    "date": f"{year + 1 if current_date.month == 12 else year}-01-01",
                    "type": "holiday",
                    "icon": "star",
                    "description": "New Year's Day - Office Closed"
                })
            
            # Get upcoming employee birthdays (if birth_date column exists)
            try:
                birthday_records = conn.execute(
                    text("""
                        SELECT first_name, last_name, birth_date
                        FROM employees
                        WHERE EXTRACT(MONTH FROM birth_date) = EXTRACT(MONTH FROM CURRENT_DATE)
                        AND EXTRACT(DAY FROM birth_date) >= EXTRACT(DAY FROM CURRENT_DATE)
                        AND status = 'active'
                        ORDER BY EXTRACT(DAY FROM birth_date)
                        LIMIT 2
                    """)
                ).fetchall()
                
                for record in birthday_records:
                    events.append({
                        "id": f"birthday_{record[0]}",
                        "title": f"{record[0]}'s Birthday",
                        "date": record[2].isoformat() if record[2] else datetime.now().isoformat(),
                        "type": "birthday",
                        "icon": "gift",
                        "description": f"Celebrate {record[0]}'s birthday"
                    })
            except Exception:
                pass  # birth_date column might not exist
            
            # If no events found, add a placeholder
            if not events:
                events.append({
                    "id": "1",
                    "title": "No upcoming events",
                    "date": datetime.now().isoformat(),
                    "type": "info",
                    "icon": "calendar",
                    "description": "Check back later for updates"
                })
            
            return {
                "success": True,
                "message": "Calendar events retrieved",
                "data": events[:5]  # Limit to 5 events
            }
    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        return {
            "success": True,
            "message": "Calendar events retrieved (fallback)",
            "data": [
                {
                    "id": "1",
                    "title": "Calendar temporarily unavailable",
                    "date": datetime.now().isoformat(),
                    "type": "info",
                    "icon": "calendar",
                    "description": "Check back later"
                }
            ]
        }

@router.get("/employee-stats")
def get_employee_dashboard_stats(current_user: models.User = Depends(get_current_user)):
    """Get employee-specific dashboard statistics from database"""
    try:
        with engine.connect() as conn:
            # Get employee record for current user
            employee = conn.execute(
                text("""
                    SELECT id, employee_id, department, position, hire_date
                    FROM employees
                    WHERE user_id = :user_id
                """),
                {"user_id": current_user.id}
            ).fetchone()
            
            if not employee:
                return {
                    "success": False,
                    "message": "Employee record not found",
                    "data": {}
                }
            
            employee_id = employee[0]
            
            # Calculate leave balance
            total_leave_days = 20  # Default annual leave
            used_leave = conn.execute(
                text("""
                    SELECT COALESCE(SUM(
                        EXTRACT(DAY FROM (end_date - start_date)) + 1
                    ), 0)
                    FROM leave_requests
                    WHERE employee_id = :employee_id
                    AND status = 'approved'
                    AND EXTRACT(YEAR FROM start_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                """),
                {"employee_id": employee_id}
            ).scalar() or 0
            
            leave_balance = max(0, total_leave_days - int(used_leave))
            
            # Count pending tasks (if tasks table exists)
            try:
                pending_tasks = conn.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM tasks
                        WHERE assigned_to = :employee_id
                        AND status IN ('pending', 'in_progress')
                    """),
                    {"employee_id": employee_id}
                ).scalar() or 0
            except Exception:
                pending_tasks = 0
            
            # Calculate learning hours (if learning_records table exists)
            try:
                learning_hours = conn.execute(
                    text("""
                        SELECT COALESCE(SUM(duration_hours), 0)
                        FROM learning_records
                        WHERE employee_id = :employee_id
                        AND EXTRACT(MONTH FROM completed_date) = EXTRACT(MONTH FROM CURRENT_DATE)
                    """),
                    {"employee_id": employee_id}
                ).scalar() or 0
            except Exception:
                learning_hours = 0
            
            # Get next holiday
            next_holiday = "Check calendar for upcoming holidays"
            current_date = datetime.now()
            if current_date.month == 12 and current_date.day < 25:
                next_holiday = "Christmas (25 Dec)"
            elif current_date.month == 12 and current_date.day >= 25:
                next_holiday = "New Year (1 Jan)"
            
            return {
                "success": True,
                "message": "Employee stats retrieved",
                "data": {
                    "leave_balance": leave_balance,
                    "pending_tasks": pending_tasks,
                    "learning_hours": float(learning_hours),
                    "next_holiday": next_holiday,
                    "employee_id": employee[1],
                    "department": employee[2] or "General",
                    "position": employee[3] or "Employee"
                }
            }
    except Exception as e:
        logger.error(f"Error fetching employee stats: {e}")
        return {
            "success": False,
            "message": f"Error fetching employee stats: {str(e)}",
            "data": {
                "leave_balance": 0,
                "pending_tasks": 0,
                "learning_hours": 0,
                "next_holiday": "N/A",
                "employee_id": 0,
                "department": "N/A",
                "position": "N/A"
            }
        }

@router.get("/team-stats")
def get_team_dashboard_stats(current_user: models.User = Depends(get_current_user)):
    """Get team-specific dashboard statistics for managers from database"""
    # Only managers and above can access team stats
    if current_user.role not in ["manager", "admin", "hr", "super_admin", "hr_admin"]:
        return {
            "success": False,
            "message": "Access denied - Manager role required",
            "data": {}
        }
    
    try:
        with engine.connect() as conn:
            # Get manager's department
            manager_dept = conn.execute(
                text("""
                    SELECT department
                    FROM employees
                    WHERE user_id = :user_id
                """),
                {"user_id": current_user.id}
            ).scalar()
            
            # Count team size (employees in same department)
            if manager_dept:
                team_size = conn.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM employees
                        WHERE department = :department
                        AND status = 'active'
                    """),
                    {"department": manager_dept}
                ).scalar() or 0
            else:
                # If no department, count all active employees
                team_size = conn.execute(
                    text("SELECT COUNT(*) FROM employees WHERE status = 'active'")
                ).scalar() or 0
            
            # Count open positions
            open_positions = conn.execute(
                text("SELECT COUNT(*) FROM job_postings WHERE status = 'active'")
            ).scalar() or 0
            
            # Count interviews today (if interviews table exists)
            try:
                interviews_today = conn.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM interviews
                        WHERE DATE(scheduled_time) = CURRENT_DATE
                    """)
                ).scalar() or 0
            except Exception:
                interviews_today = 0
            
            # Calculate team attendance rate
            if team_size > 0:
                present_count = conn.execute(
                    text("""
                        SELECT COUNT(DISTINCT a.employee_id)
                        FROM attendance a
                        JOIN employees e ON a.employee_id = e.id
                        WHERE DATE(a.check_in_time) = CURRENT_DATE
                        AND a.check_out_time IS NULL
                        AND e.status = 'active'
                    """)
                ).scalar() or 0
                team_attendance_rate = round((present_count / team_size) * 100, 1)
            else:
                team_attendance_rate = 0.0
            
            # Count pending reviews (if performance_reviews table exists)
            try:
                pending_reviews = conn.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM performance_reviews
                        WHERE status = 'pending'
                    """)
                ).scalar() or 0
            except Exception:
                pending_reviews = 0
            
            # Get team workload (simplified - based on task count if tasks table exists)
            team_workload = []
            try:
                workload_data = conn.execute(
                    text("""
                        SELECT e.first_name, COUNT(t.id) as task_count
                        FROM employees e
                        LEFT JOIN tasks t ON e.id = t.assigned_to AND t.status IN ('pending', 'in_progress')
                        WHERE e.status = 'active'
                        AND (:department IS NULL OR e.department = :department)
                        GROUP BY e.id, e.first_name
                        ORDER BY task_count DESC
                        LIMIT 4
                    """),
                    {"department": manager_dept}
                ).fetchall()
                
                for record in workload_data:
                    name = record[0]
                    task_count = record[1]
                    # Estimate load percentage (assuming 10 tasks = 100% load)
                    load = min(100, (task_count / 10) * 100)
                    
                    if load > 90:
                        status = "Overloaded"
                    elif load < 50:
                        status = "Underutilized"
                    elif load >= 70:
                        status = "High"
                    else:
                        status = "Optimal"
                    
                    team_workload.append({
                        "name": name,
                        "load": int(load),
                        "status": status
                    })
            except Exception:
                # Fallback if tasks table doesn't exist
                pass
            
            # If no workload data, provide placeholder
            if not team_workload:
                team_workload = [
                    {"name": "Team Member 1", "load": 75, "status": "Optimal"},
                    {"name": "Team Member 2", "load": 60, "status": "Optimal"}
                ]
            
            return {
                "success": True,
                "message": "Team stats retrieved",
                "data": {
                    "team_size": team_size,
                    "open_positions": open_positions,
                    "interviews_today": interviews_today,
                    "team_attendance_rate": team_attendance_rate,
                    "pending_reviews": pending_reviews,
                    "team_workload": team_workload
                }
            }
    except Exception as e:
        logger.error(f"Error fetching team stats: {e}")
        return {
            "success": False,
            "message": f"Error fetching team stats: {str(e)}",
            "data": {
                "team_size": 0,
                "open_positions": 0,
                "interviews_today": 0,
                "team_attendance_rate": 0.0,
                "pending_reviews": 0,
                "team_workload": []
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