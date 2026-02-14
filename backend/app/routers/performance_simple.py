from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/performance",
    tags=["performance"]
)

@router.get("/reviews")
def get_performance_reviews():
    """Get performance reviews"""
    return {
        "success": True,
        "message": "Performance reviews retrieved",
        "data": [
            {
                "id": 1,
                "employee_id": 1,
                "reviewer_id": 2,
                "period": "Q4 2024",
                "status": "completed",
                "overall_rating": 4.2,
                "created_at": datetime.now().isoformat()
            }
        ]
    }

@router.get("/goals")
def get_goals():
    """Get performance goals"""
    return {
        "success": True,
        "message": "Goals retrieved",
        "data": [
            {
                "id": 1,
                "employee_id": 1,
                "title": "Complete project X",
                "description": "Finish the main project deliverables",
                "status": "in_progress",
                "due_date": "2024-12-31"
            }
        ]
    }

@router.get("/stats")
def get_performance_stats():
    """Get performance statistics"""
    return {
        "success": True,
        "message": "Performance stats retrieved",
        "data": {
            "total_reviews": 25,
            "completed_reviews": 20,
            "pending_reviews": 5,
            "average_rating": 4.1,
            "goals_completed": 85
        }
    }