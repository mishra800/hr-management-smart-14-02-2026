from fastapi import APIRouter, Depends
from datetime import datetime
import random
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/engagement",
    tags=["engagement"]
)

@router.get("/engagement-metrics")
def get_engagement_metrics(current_user: dict = Depends(get_current_user)):
    """Get employee engagement metrics"""
    
    return {
        "overall_score": round(random.uniform(3.5, 4.5), 1),
        "participation_rate": f"{random.randint(75, 95)}%",
        "satisfaction_score": round(random.uniform(3.2, 4.8), 1),
        "response_rate": f"{random.randint(60, 90)}%",
        "metrics": [
            {
                "category": "Work-Life Balance",
                "score": round(random.uniform(3.0, 4.5), 1),
                "trend": random.choice(["up", "down", "stable"])
            },
            {
                "category": "Career Development",
                "score": round(random.uniform(3.2, 4.3), 1),
                "trend": random.choice(["up", "down", "stable"])
            },
            {
                "category": "Management Support",
                "score": round(random.uniform(3.5, 4.6), 1),
                "trend": random.choice(["up", "down", "stable"])
            },
            {
                "category": "Team Collaboration",
                "score": round(random.uniform(3.8, 4.7), 1),
                "trend": random.choice(["up", "down", "stable"])
            },
            {
                "category": "Recognition & Rewards",
                "score": round(random.uniform(2.8, 4.2), 1),
                "trend": random.choice(["up", "down", "stable"])
            }
        ],
        "recent_surveys": [
            {
                "id": 1,
                "title": "Q4 Employee Satisfaction Survey",
                "status": "active",
                "responses": random.randint(45, 85),
                "total_employees": 100,
                "end_date": "2025-02-15"
            },
            {
                "id": 2,
                "title": "Remote Work Feedback",
                "status": "completed",
                "responses": random.randint(70, 95),
                "total_employees": 100,
                "end_date": "2024-12-30"
            }
        ]
    }

@router.post("/feedback")
def submit_feedback(
    feedback_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit employee feedback"""
    
    # Mock feedback submission
    return {
        "success": True,
        "message": "Feedback submitted successfully",
        "feedback_id": random.randint(1000, 9999),
        "submitted_at": datetime.now().isoformat()
    }

@router.get("/surveys")
def get_available_surveys(current_user: dict = Depends(get_current_user)):
    """Get available surveys for the current user"""
    
    surveys = [
        {
            "id": 1,
            "title": "Q4 Employee Satisfaction Survey",
            "description": "Help us understand your experience working here",
            "status": "active",
            "deadline": "2025-02-15",
            "estimated_time": "5-10 minutes",
            "completed": False
        },
        {
            "id": 2,
            "title": "Remote Work Policy Feedback",
            "description": "Share your thoughts on our remote work policies",
            "status": "active", 
            "deadline": "2025-02-28",
            "estimated_time": "3-5 minutes",
            "completed": False
        },
        {
            "id": 3,
            "title": "Learning & Development Survey",
            "description": "Tell us about your learning and development needs",
            "status": "draft",
            "deadline": "2025-03-15",
            "estimated_time": "8-12 minutes",
            "completed": False
        }
    ]
    
    return {"surveys": surveys}

@router.get("/pulse-survey")
def get_pulse_survey(current_user: dict = Depends(get_current_user)):
    """Get quick pulse survey questions"""
    
    questions = [
        {
            "id": 1,
            "question": "How satisfied are you with your current role?",
            "type": "rating",
            "scale": 5
        },
        {
            "id": 2,
            "question": "How likely are you to recommend this company as a great place to work?",
            "type": "rating",
            "scale": 10
        },
        {
            "id": 3,
            "question": "What's the biggest challenge you're facing at work right now?",
            "type": "text",
            "optional": True
        }
    ]
    
    return {
        "survey_id": "pulse_" + str(random.randint(1000, 9999)),
        "title": "Weekly Pulse Check",
        "questions": questions
    }

@router.post("/pulse-survey")
def submit_pulse_survey(
    survey_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit pulse survey responses"""
    
    return {
        "success": True,
        "message": "Pulse survey submitted successfully",
        "response_id": random.randint(10000, 99999),
        "submitted_at": datetime.now().isoformat()
    }

@router.get("/team-engagement")
def get_team_engagement(current_user: dict = Depends(get_current_user)):
    """Get team engagement metrics for managers"""
    
    if current_user.get("role") not in ["manager", "admin", "hr"]:
        return {"error": "Access denied - Manager role required"}
    
    return {
        "team_score": round(random.uniform(3.5, 4.5), 1),
        "team_size": random.randint(8, 15),
        "response_rate": f"{random.randint(70, 95)}%",
        "top_concerns": [
            "Work-life balance",
            "Career development opportunities", 
            "Recognition and feedback",
            "Workload management"
        ],
        "engagement_trends": [
            {"month": "Oct 2024", "score": round(random.uniform(3.5, 4.2), 1)},
            {"month": "Nov 2024", "score": round(random.uniform(3.6, 4.3), 1)},
            {"month": "Dec 2024", "score": round(random.uniform(3.7, 4.4), 1)},
            {"month": "Jan 2025", "score": round(random.uniform(3.8, 4.5), 1)}
        ]
    }