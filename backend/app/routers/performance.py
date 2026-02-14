"""
Performance Management Router
Handles performance reviews, goals, feedback, and performance analytics
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from app.dependencies import get_current_user
from app.error_handlers import check_user_permissions, log_user_action, ValidationError
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator
from enum import Enum

router = APIRouter(
    prefix="/performance",
    tags=["performance"]
)

class ReviewCycle(str, Enum):
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUAL = "annual"

class ReviewStatus(str, Enum):
    NOT_STARTED = "not_started"
    SELF_REVIEW = "self_review"
    MANAGER_REVIEW = "manager_review"
    PEER_REVIEW = "peer_review"
    COMPLETED = "completed"
    APPROVED = "approved"

class GoalStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class GoalPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Pydantic Models
class GoalCreate(BaseModel):
    title: str
    description: str
    category: str  # performance, learning, project, behavioral
    priority: GoalPriority
    target_date: date
    success_criteria: List[str]
    key_results: Optional[List[str]] = None
    assigned_to: Optional[int] = None  # If manager assigns to employee
    
    @validator('target_date')
    def validate_target_date(cls, v):
        if v <= date.today():
            raise ValueError('Target date must be in the future')
        return v

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[GoalPriority] = None
    target_date: Optional[date] = None
    success_criteria: Optional[List[str]] = None
    key_results: Optional[List[str]] = None
    status: Optional[GoalStatus] = None
    progress_percentage: Optional[int] = None
    notes: Optional[str] = None

class ReviewCreate(BaseModel):
    employee_id: int
    review_period_start: date
    review_period_end: date
    review_cycle: ReviewCycle
    template_id: Optional[int] = None

class ReviewUpdate(BaseModel):
    self_review: Optional[Dict[str, Any]] = None
    manager_review: Optional[Dict[str, Any]] = None
    peer_reviews: Optional[List[Dict[str, Any]]] = None
    overall_rating: Optional[int] = None  # 1-5 scale
    strengths: Optional[List[str]] = None
    areas_for_improvement: Optional[List[str]] = None
    development_plan: Optional[List[str]] = None
    status: Optional[ReviewStatus] = None
    comments: Optional[str] = None

class FeedbackCreate(BaseModel):
    recipient_id: int
    feedback_type: str  # positive, constructive, peer, upward
    content: str
    category: Optional[str] = None  # communication, technical, leadership, etc.
    is_anonymous: bool = False

# Mock data
MOCK_GOALS = {}
MOCK_REVIEWS = {}
MOCK_FEEDBACK = {}
MOCK_TEMPLATES = {}

def generate_id():
    return len(MOCK_GOALS) + len(MOCK_REVIEWS) + len(MOCK_FEEDBACK) + 1

@router.get("/goals")
async def get_goals(
    current_user: dict = Depends(get_current_user),
    employee_id: Optional[int] = None,
    status: Optional[GoalStatus] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get goals for employee"""
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    # Determine which goals to show
    if employee_id:
        # Check permissions to view other's goals
        if user_role not in ["admin", "super_admin", "hr", "manager"] and user_id != employee_id:
            raise HTTPException(status_code=403, detail="Cannot view other employee's goals")
        target_employee_id = employee_id
    else:
        target_employee_id = user_id
    
    # Filter goals
    goals = []
    for goal in MOCK_GOALS.values():
        if goal.get("employee_id") == target_employee_id:
            if status and goal.get("status") != status:
                continue
            if category and goal.get("category") != category:
                continue
            goals.append(goal)
    
    # Sort by created_at descending
    goals.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Apply pagination
    paginated_goals = goals[skip:skip + limit]
    
    return {
        "success": True,
        "data": {
            "goals": paginated_goals,
            "total": len(goals),
            "summary": {
                "active": len([g for g in goals if g.get("status") == GoalStatus.ACTIVE]),
                "completed": len([g for g in goals if g.get("status") == GoalStatus.COMPLETED]),
                "overdue": len([g for g in goals if g.get("status") == GoalStatus.OVERDUE])
            }
        }
    }

@router.post("/goals")
async def create_goal(
    goal: GoalCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new goal"""
    goal_id = generate_id()
    user_id = current_user.get("id")
    
    # Determine employee_id
    if goal.assigned_to and current_user.get("role") in ["admin", "super_admin", "hr", "manager"]:
        employee_id = goal.assigned_to
    else:
        employee_id = user_id
    
    new_goal = {
        "id": goal_id,
        "employee_id": employee_id,
        "title": goal.title,
        "description": goal.description,
        "category": goal.category,
        "priority": goal.priority,
        "target_date": goal.target_date.isoformat(),
        "success_criteria": goal.success_criteria,
        "key_results": goal.key_results or [],
        "status": GoalStatus.ACTIVE,
        "progress_percentage": 0,
        "created_by": user_id,
        "created_at": datetime.now().isoformat(),
        "notes": ""
    }
    
    MOCK_GOALS[goal_id] = new_goal
    
    log_user_action(
        user_id,
        "create_goal",
        "goal",
        {"goal_id": goal_id, "title": goal.title, "employee_id": employee_id}
    )
    
    return {
        "success": True,
        "message": "Goal created successfully",
        "data": new_goal
    }

@router.put("/goals/{goal_id}")
async def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update goal"""
    if goal_id not in MOCK_GOALS:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal = MOCK_GOALS[goal_id]
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    # Check permissions
    if (goal.get("employee_id") != user_id and 
        user_role not in ["admin", "super_admin", "hr", "manager"]):
        raise HTTPException(status_code=403, detail="Cannot update this goal")
    
    # Update fields
    update_data = goal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "target_date" and value:
            goal[field] = value.isoformat()
        else:
            goal[field] = value
    
    goal["updated_at"] = datetime.now().isoformat()
    goal["updated_by"] = user_id
    
    log_user_action(
        user_id,
        "update_goal",
        "goal",
        {"goal_id": goal_id, "updated_fields": list(update_data.keys())}
    )
    
    return {
        "success": True,
        "message": "Goal updated successfully",
        "data": goal
    }

@router.get("/reviews")
async def get_reviews(
    current_user: dict = Depends(get_current_user),
    employee_id: Optional[int] = None,
    status: Optional[ReviewStatus] = None,
    review_cycle: Optional[ReviewCycle] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get performance reviews"""
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    # Determine which reviews to show
    if employee_id:
        # Check permissions
        if user_role not in ["admin", "super_admin", "hr", "manager"] and user_id != employee_id:
            raise HTTPException(status_code=403, detail="Cannot view other employee's reviews")
        target_employee_id = employee_id
    else:
        target_employee_id = user_id
    
    # Filter reviews
    reviews = []
    for review in MOCK_REVIEWS.values():
        if review.get("employee_id") == target_employee_id:
            if status and review.get("status") != status:
                continue
            if review_cycle and review.get("review_cycle") != review_cycle:
                continue
            reviews.append(review)
    
    # Sort by review_period_end descending
    reviews.sort(key=lambda x: x.get("review_period_end", ""), reverse=True)
    
    # Apply pagination
    paginated_reviews = reviews[skip:skip + limit]
    
    return {
        "success": True,
        "data": {
            "reviews": paginated_reviews,
            "total": len(reviews)
        }
    }

@router.post("/reviews")
async def create_review(
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new performance review"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager"])
    
    review_id = generate_id()
    
    new_review = {
        "id": review_id,
        "employee_id": review.employee_id,
        "review_period_start": review.review_period_start.isoformat(),
        "review_period_end": review.review_period_end.isoformat(),
        "review_cycle": review.review_cycle,
        "template_id": review.template_id,
        "status": ReviewStatus.NOT_STARTED,
        "self_review": {},
        "manager_review": {},
        "peer_reviews": [],
        "overall_rating": None,
        "strengths": [],
        "areas_for_improvement": [],
        "development_plan": [],
        "comments": "",
        "created_by": current_user.get("id"),
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_REVIEWS[review_id] = new_review
    
    log_user_action(
        current_user.get("id"),
        "create_review",
        "review",
        {"review_id": review_id, "employee_id": review.employee_id}
    )
    
    return {
        "success": True,
        "message": "Performance review created successfully",
        "data": new_review
    }

@router.put("/reviews/{review_id}")
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update performance review"""
    if review_id not in MOCK_REVIEWS:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review = MOCK_REVIEWS[review_id]
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    # Check permissions
    can_update = (
        review.get("employee_id") == user_id or  # Employee can update their own
        user_role in ["admin", "super_admin", "hr", "manager"]  # Managers/HR can update
    )
    
    if not can_update:
        raise HTTPException(status_code=403, detail="Cannot update this review")
    
    # Update fields
    update_data = review_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        review[field] = value
    
    review["updated_at"] = datetime.now().isoformat()
    review["updated_by"] = user_id
    
    log_user_action(
        user_id,
        "update_review",
        "review",
        {"review_id": review_id, "updated_fields": list(update_data.keys())}
    )
    
    return {
        "success": True,
        "message": "Review updated successfully",
        "data": review
    }

@router.post("/feedback")
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create feedback for employee"""
    feedback_id = generate_id()
    
    new_feedback = {
        "id": feedback_id,
        "recipient_id": feedback.recipient_id,
        "giver_id": current_user.get("id") if not feedback.is_anonymous else None,
        "feedback_type": feedback.feedback_type,
        "content": feedback.content,
        "category": feedback.category,
        "is_anonymous": feedback.is_anonymous,
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_FEEDBACK[feedback_id] = new_feedback
    
    log_user_action(
        current_user.get("id"),
        "create_feedback",
        "feedback",
        {"feedback_id": feedback_id, "recipient_id": feedback.recipient_id, "type": feedback.feedback_type}
    )
    
    return {
        "success": True,
        "message": "Feedback submitted successfully",
        "data": new_feedback
    }

@router.get("/feedback")
async def get_feedback(
    current_user: dict = Depends(get_current_user),
    recipient_id: Optional[int] = None,
    feedback_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get feedback"""
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    
    # Determine which feedback to show
    if recipient_id:
        # Check permissions
        if user_role not in ["admin", "super_admin", "hr", "manager"] and user_id != recipient_id:
            raise HTTPException(status_code=403, detail="Cannot view other employee's feedback")
        target_recipient_id = recipient_id
    else:
        target_recipient_id = user_id
    
    # Filter feedback
    feedback_list = []
    for feedback in MOCK_FEEDBACK.values():
        if feedback.get("recipient_id") == target_recipient_id:
            if feedback_type and feedback.get("feedback_type") != feedback_type:
                continue
            feedback_list.append(feedback)
    
    # Sort by created_at descending
    feedback_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Apply pagination
    paginated_feedback = feedback_list[skip:skip + limit]
    
    return {
        "success": True,
        "data": {
            "feedback": paginated_feedback,
            "total": len(feedback_list)
        }
    }

@router.get("/analytics")
async def get_performance_analytics(
    current_user: dict = Depends(get_current_user),
    department: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get performance analytics"""
    check_user_permissions(current_user.get("role"), ["admin", "super_admin", "hr", "manager"])
    
    # Calculate analytics
    total_goals = len(MOCK_GOALS)
    completed_goals = len([g for g in MOCK_GOALS.values() if g.get("status") == GoalStatus.COMPLETED])
    total_reviews = len(MOCK_REVIEWS)
    completed_reviews = len([r for r in MOCK_REVIEWS.values() if r.get("status") == ReviewStatus.COMPLETED])
    
    # Goal completion rate by category
    category_stats = {}
    for goal in MOCK_GOALS.values():
        category = goal.get("category", "unknown")
        if category not in category_stats:
            category_stats[category] = {"total": 0, "completed": 0}
        category_stats[category]["total"] += 1
        if goal.get("status") == GoalStatus.COMPLETED:
            category_stats[category]["completed"] += 1
    
    # Calculate completion rates
    for category in category_stats:
        total = category_stats[category]["total"]
        completed = category_stats[category]["completed"]
        category_stats[category]["completion_rate"] = round((completed / max(total, 1)) * 100, 2)
    
    # Review ratings distribution
    rating_distribution = {}
    for review in MOCK_REVIEWS.values():
        rating = review.get("overall_rating")
        if rating:
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
    
    return {
        "success": True,
        "data": {
            "overview": {
                "total_goals": total_goals,
                "completed_goals": completed_goals,
                "goal_completion_rate": round((completed_goals / max(total_goals, 1)) * 100, 2),
                "total_reviews": total_reviews,
                "completed_reviews": completed_reviews,
                "review_completion_rate": round((completed_reviews / max(total_reviews, 1)) * 100, 2)
            },
            "goal_category_stats": category_stats,
            "review_rating_distribution": rating_distribution,
            "recent_activity": {
                "goals_created_this_month": len([g for g in MOCK_GOALS.values() 
                                               if datetime.fromisoformat(g.get("created_at", "2024-01-01T00:00:00")) > 
                                               datetime.now() - timedelta(days=30)]),
                "reviews_completed_this_month": len([r for r in MOCK_REVIEWS.values() 
                                                   if r.get("status") == ReviewStatus.COMPLETED and
                                                   datetime.fromisoformat(r.get("updated_at", "2024-01-01T00:00:00")) > 
                                                   datetime.now() - timedelta(days=30)])
            }
        }
    }

@router.get("/health")
async def performance_health_check():
    """Performance service health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "performance",
        "total_goals": len(MOCK_GOALS),
        "total_reviews": len(MOCK_REVIEWS),
        "total_feedback": len(MOCK_FEEDBACK)
    }

# Initialize sample data
def initialize_sample_data():
    """Initialize sample performance data"""
    sample_goals = [
        {
            "id": 1,
            "employee_id": 1,
            "title": "Complete React.js Certification",
            "description": "Complete online React.js certification course",
            "category": "learning",
            "priority": GoalPriority.MEDIUM,
            "target_date": (date.today() + timedelta(days=90)).isoformat(),
            "success_criteria": ["Pass certification exam", "Build sample project"],
            "key_results": ["Score 80% or above", "Deploy project to production"],
            "status": GoalStatus.ACTIVE,
            "progress_percentage": 30,
            "created_by": 1,
            "created_at": datetime.now().isoformat(),
            "notes": "Making good progress"
        }
    ]
    
    for goal in sample_goals:
        MOCK_GOALS[goal["id"]] = goal

# Initialize sample data
initialize_sample_data()