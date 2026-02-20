from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter(
    prefix="/predictive-analytics",
    tags=["predictive-analytics"]
)

@router.get("/overview")
def get_analytics_overview():
    """Get predictive analytics overview"""
    return {
        "total_employees": 247,
        "predicted_attrition_rate": 12.5,
        "avg_performance_score": 8.2,
        "hiring_forecast": 15,
        "cost_savings": 125000,
        "accuracy_score": 87.3
    }

@router.get("/attrition")
def get_attrition_predictions():
    """Get attrition risk predictions"""
    return [
        {
            "employee_id": 1,
            "name": "John Doe",
            "department": "Engineering",
            "risk_score": 85,
            "factors": ["Low engagement", "No promotion in 2 years"]
        },
        {
            "employee_id": 2,
            "name": "Jane Smith",
            "department": "Marketing",
            "risk_score": 72,
            "factors": ["High workload", "Limited growth opportunities"]
        },
        {
            "employee_id": 3,
            "name": "Mike Johnson",
            "department": "Sales",
            "risk_score": 68,
            "factors": ["Below average performance", "Team conflicts"]
        }
    ]

@router.get("/performance")
def get_performance_forecasts():
    """Get performance forecasts"""
    return [
        {
            "employee_id": 1,
            "name": "Alice Brown",
            "current_score": 7.8,
            "predicted_score": 8.5,
            "trend": "improving"
        },
        {
            "employee_id": 2,
            "name": "Bob Wilson",
            "current_score": 8.2,
            "predicted_score": 7.9,
            "trend": "declining"
        },
        {
            "employee_id": 3,
            "name": "Carol Davis",
            "current_score": 9.1,
            "predicted_score": 9.3,
            "trend": "stable"
        }
    ]

@router.get("/hiring")
def get_hiring_predictions():
    """Get hiring forecasts"""
    return [
        {
            "department": "Engineering",
            "current_headcount": 45,
            "predicted_need": 8,
            "timeline": "3 months"
        },
        {
            "department": "Sales",
            "current_headcount": 32,
            "predicted_need": 5,
            "timeline": "2 months"
        },
        {
            "department": "Marketing",
            "current_headcount": 18,
            "predicted_need": 2,
            "timeline": "4 months"
        }
    ]