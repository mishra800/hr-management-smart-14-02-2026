from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
import random
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"]
)

@router.get("/insights")
def get_insights(current_user: dict = Depends(get_current_user)):
    """Get executive HR analytics insights"""
    
    # Mock data for demonstration
    return {
        "attrition_risk": random.choice(["Low", "Medium", "High"]),
        "hiring_velocity": f"{random.randint(12, 25)} days",
        "employee_sentiment": random.choice(["Positive", "Neutral", "Negative"]),
        "top_performers": [
            "John Smith",
            "Sarah Johnson", 
            "Michael Chen",
            "Emily Davis",
            "David Wilson"
        ],
        "skill_gaps": ["Python", "Cloud Architecture", "AI/ML", "Leadership", "DevOps"],
        "total_employees": 150,
        "active_recruitments": 8,
        "pending_reviews": 12,
        "satisfaction_score": round(random.uniform(3.5, 4.8), 1)
    }

@router.get("/workforce-planning")
def get_workforce_planning(current_user: dict = Depends(get_current_user)):
    """Get workforce planning insights"""
    
    return {
        "skill_shortages": [
            {"skill": "React Native", "shortage_count": 5, "urgency": "High"},
            {"skill": "DevOps (AWS)", "shortage_count": 3, "urgency": "Medium"},
            {"skill": "Data Engineering", "shortage_count": 2, "urgency": "Medium"},
            {"skill": "UI/UX Design", "shortage_count": 4, "urgency": "High"},
            {"skill": "Machine Learning", "shortage_count": 2, "urgency": "Low"}
        ],
        "future_hiring_needs": [
            {"role": "Senior Frontend Engineer", "count": 8, "quarter": "Q3 2025"},
            {"role": "Product Manager", "count": 2, "quarter": "Q4 2025"},
            {"role": "QA Automation Engineer", "count": 4, "quarter": "Q3 2025"},
            {"role": "Data Scientist", "count": 3, "quarter": "Q2 2025"}
        ],
        "bench_surplus": [
            {"role": "Junior Java Developer", "count": 12, "risk": "High Bench Time"},
            {"role": "Manual Tester", "count": 5, "risk": "Medium Bench Time"},
            {"role": "Support Engineer", "count": 3, "risk": "Low Bench Time"}
        ],
        "market_trends": {
            "hottest_skill": "Generative AI",
            "avg_time_to_hire": "18 Days",
            "salary_inflation": "12% YoY",
            "remote_work_preference": "85%",
            "top_hiring_challenge": "Skill Shortage"
        }
    }

@router.get("/department-metrics")
def get_department_metrics(current_user: dict = Depends(get_current_user)):
    """Get department-wise metrics"""
    
    departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]
    
    metrics = []
    for dept in departments:
        metrics.append({
            "department": dept,
            "headcount": random.randint(15, 45),
            "avg_rating": round(random.uniform(3.2, 4.7), 1),
            "attrition_rate": f"{random.randint(5, 18)}%",
            "satisfaction_score": round(random.uniform(3.0, 4.5), 1),
            "budget_utilization": f"{random.randint(75, 95)}%"
        })
    
    return {"departments": metrics}

@router.get("/trends")
def get_trends(current_user: dict = Depends(get_current_user)):
    """Get HR trends and analytics"""
    
    # Generate mock trend data for the last 6 months
    months = ["Aug 2024", "Sep 2024", "Oct 2024", "Nov 2024", "Dec 2024", "Jan 2025"]
    
    return {
        "hiring_trends": [
            {"month": month, "hires": random.randint(8, 25), "applications": random.randint(50, 150)}
            for month in months
        ],
        "attrition_trends": [
            {"month": month, "departures": random.randint(2, 12), "rate": f"{random.randint(3, 15)}%"}
            for month in months
        ],
        "satisfaction_trends": [
            {"month": month, "score": round(random.uniform(3.5, 4.5), 1)}
            for month in months
        ],
        "performance_trends": [
            {"month": month, "avg_rating": round(random.uniform(3.8, 4.3), 1)}
            for month in months
        ]
    }