from fastapi import APIRouter, Depends
from datetime import datetime
import random
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/learning",
    tags=["learning"]
)

@router.get("/youtube/videos")
def get_youtube_videos(current_user: dict = Depends(get_current_user)):
    """Get recommended YouTube learning videos"""
    
    videos = [
        {
            "id": "dQw4w9WgXcQ",
            "title": "Python Best Practices for Beginners",
            "channel": "Tech Education Hub",
            "duration": "15:30",
            "views": "125K",
            "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "description": "Learn essential Python best practices",
            "category": "Programming"
        },
        {
            "id": "abc123def456",
            "title": "React Hooks Explained",
            "channel": "Frontend Masters",
            "duration": "22:45",
            "views": "89K",
            "thumbnail": "https://img.youtube.com/vi/abc123def456/maxresdefault.jpg",
            "description": "Complete guide to React Hooks",
            "category": "Frontend"
        },
        {
            "id": "xyz789uvw012",
            "title": "Leadership Skills for Tech Managers",
            "channel": "Management Insights",
            "duration": "18:20",
            "views": "67K",
            "thumbnail": "https://img.youtube.com/vi/xyz789uvw012/maxresdefault.jpg",
            "description": "Essential leadership skills for technical managers",
            "category": "Leadership"
        },
        {
            "id": "def456ghi789",
            "title": "Database Design Fundamentals",
            "channel": "Data Academy",
            "duration": "28:15",
            "views": "156K",
            "thumbnail": "https://img.youtube.com/vi/def456ghi789/maxresdefault.jpg",
            "description": "Learn database design principles",
            "category": "Database"
        }
    ]
    
    return {"videos": videos}

@router.get("/courses")
def get_learning_courses(current_user: dict = Depends(get_current_user)):
    """Get available learning courses"""
    
    courses = [
        {
            "id": 1,
            "title": "Advanced Python Programming",
            "description": "Master advanced Python concepts and techniques",
            "instructor": "Dr. Sarah Johnson",
            "duration": "8 weeks",
            "level": "Advanced",
            "enrolled": False,
            "progress": 0,
            "rating": 4.8,
            "students": 1250,
            "category": "Programming"
        },
        {
            "id": 2,
            "title": "Project Management Essentials",
            "description": "Learn fundamental project management skills",
            "instructor": "Michael Chen",
            "duration": "6 weeks",
            "level": "Intermediate",
            "enrolled": True,
            "progress": 65,
            "rating": 4.6,
            "students": 890,
            "category": "Management"
        },
        {
            "id": 3,
            "title": "Cloud Architecture with AWS",
            "description": "Design scalable cloud solutions using AWS",
            "instructor": "Emily Rodriguez",
            "duration": "10 weeks",
            "level": "Advanced",
            "enrolled": False,
            "progress": 0,
            "rating": 4.9,
            "students": 2100,
            "category": "Cloud"
        },
        {
            "id": 4,
            "title": "Data Science Fundamentals",
            "description": "Introduction to data science and analytics",
            "instructor": "David Kim",
            "duration": "12 weeks",
            "level": "Beginner",
            "enrolled": True,
            "progress": 25,
            "rating": 4.7,
            "students": 1800,
            "category": "Data Science"
        }
    ]
    
    return {"courses": courses}

@router.get("/my-progress")
def get_learning_progress(current_user: dict = Depends(get_current_user)):
    """Get user's learning progress"""
    
    return {
        "total_courses": 4,
        "completed_courses": 1,
        "in_progress": 2,
        "total_hours": 45.5,
        "certificates_earned": 3,
        "current_streak": 7,
        "monthly_goal": 20,
        "monthly_progress": 15.5,
        "recent_activity": [
            {
                "course": "Project Management Essentials",
                "activity": "Completed Module 4: Risk Management",
                "date": "2025-01-27",
                "points": 50
            },
            {
                "course": "Data Science Fundamentals", 
                "activity": "Started Module 2: Data Visualization",
                "date": "2025-01-26",
                "points": 25
            },
            {
                "course": "Advanced Python Programming",
                "activity": "Earned Certificate of Completion",
                "date": "2025-01-25",
                "points": 100
            }
        ]
    }

@router.post("/enroll/{course_id}")
def enroll_in_course(
    course_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Enroll in a learning course"""
    
    return {
        "success": True,
        "message": f"Successfully enrolled in course {course_id}",
        "enrollment_id": random.randint(10000, 99999),
        "enrolled_at": datetime.now().isoformat()
    }

@router.post("/progress/{course_id}")
def update_course_progress(
    course_id: int,
    progress_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update progress for a course"""
    
    return {
        "success": True,
        "message": "Progress updated successfully",
        "course_id": course_id,
        "new_progress": progress_data.get("progress", 0),
        "updated_at": datetime.now().isoformat()
    }

@router.get("/recommendations")
def get_learning_recommendations(current_user: dict = Depends(get_current_user)):
    """Get personalized learning recommendations"""
    
    recommendations = [
        {
            "type": "course",
            "title": "Advanced React Patterns",
            "reason": "Based on your frontend development role",
            "priority": "High",
            "estimated_time": "6 weeks"
        },
        {
            "type": "skill",
            "title": "TypeScript",
            "reason": "Popular in your department",
            "priority": "Medium",
            "estimated_time": "4 weeks"
        },
        {
            "type": "certification",
            "title": "AWS Solutions Architect",
            "reason": "Aligns with company cloud strategy",
            "priority": "High",
            "estimated_time": "8 weeks"
        },
        {
            "type": "soft_skill",
            "title": "Technical Communication",
            "reason": "Recommended for senior developers",
            "priority": "Medium",
            "estimated_time": "3 weeks"
        }
    ]
    
    return {"recommendations": recommendations}

@router.get("/leaderboard")
def get_learning_leaderboard(current_user: dict = Depends(get_current_user)):
    """Get learning leaderboard"""
    
    leaderboard = [
        {"rank": 1, "name": "Sarah Johnson", "points": 2850, "courses_completed": 12},
        {"rank": 2, "name": "Michael Chen", "points": 2650, "courses_completed": 11},
        {"rank": 3, "name": "Emily Davis", "points": 2400, "courses_completed": 10},
        {"rank": 4, "name": "David Wilson", "points": 2200, "courses_completed": 9},
        {"rank": 5, "name": "Current User", "points": 1950, "courses_completed": 8}
    ]
    
    return {
        "leaderboard": leaderboard,
        "user_rank": 5,
        "user_points": 1950
    }