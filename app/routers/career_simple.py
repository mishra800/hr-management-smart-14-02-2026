from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/career",
    tags=["career"]
)

@router.get("/development-plans")
def get_development_plans():
    """Get career development plans"""
    return {
        "success": True,
        "message": "Development plans retrieved",
        "data": [
            {
                "id": 1,
                "employee_id": 1,
                "title": "Senior Developer Track",
                "description": "Path to senior developer role",
                "status": "active",
                "progress": 65,
                "created_at": datetime.now().isoformat()
            }
        ]
    }

@router.get("/skills")
def get_skills():
    """Get skills assessment"""
    return {
        "success": True,
        "message": "Skills retrieved",
        "data": [
            {
                "id": 1,
                "name": "JavaScript",
                "category": "Programming",
                "level": "Advanced",
                "proficiency": 85
            },
            {
                "id": 2,
                "name": "Python",
                "category": "Programming", 
                "level": "Intermediate",
                "proficiency": 70
            }
        ]
    }

@router.get("/opportunities")
def get_career_opportunities():
    """Get career opportunities"""
    return {
        "success": True,
        "message": "Career opportunities retrieved",
        "data": [
            {
                "id": 1,
                "title": "Senior Developer Position",
                "department": "Engineering",
                "requirements": ["5+ years experience", "Leadership skills"],
                "available": True
            }
        ]
    }