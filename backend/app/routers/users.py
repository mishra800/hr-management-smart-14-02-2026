from fastapi import APIRouter, Depends, HTTPException
from app import schemas
from app.dependencies import get_current_user
from app.database import engine
from sqlalchemy import text

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users from database - Protected endpoint"""
    # Check if user has permission to view all users
    if current_user.get("role") not in ["admin", "super_admin", "hr"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view all users")
    
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT id, email, username, full_name, role, is_active, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            
            result = conn.execute(query)
            rows = result.fetchall()
            
            users = []
            for row in rows:
                users.append({
                    "id": row[0],
                    "email": row[1],
                    "username": row[2],
                    "full_name": row[3],
                    "role": row[4],
                    "is_active": row[5],
                    "created_at": str(row[6]) if row[6] else None
                })
            
            return schemas.APIResponse(
                success=True,
                message="Users retrieved successfully",
                data=users
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

@router.get("/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/me/profile")
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile with employee information from database"""
    try:
        with engine.connect() as conn:
            # Get employee data for current user
            query = text("""
                SELECT 
                    e.id,
                    e.employee_id,
                    e.first_name,
                    e.last_name,
                    e.email,
                    e.department,
                    e.position,
                    e.phone,
                    e.gender,
                    e.address,
                    e.emergency_contact_name,
                    e.emergency_contact_phone,
                    e.date_of_birth,
                    e.wedding_anniversary_date,
                    e.profile_completion_percentage
                FROM employees e
                WHERE e.user_id = :user_id
            """)
            
            result = conn.execute(query, {"user_id": current_user["id"]})
            row = result.fetchone()
            
            if row:
                employee_data = {
                    "id": row[0],
                    "employee_id": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "email": row[4],
                    "department": row[5],
                    "position": row[6],
                    "phone": row[7],
                    "gender": row[8],
                    "address": row[9],
                    "emergency_contact_name": row[10],
                    "emergency_contact_phone": row[11],
                    "date_of_birth": str(row[12]) if row[12] else None,
                    "wedding_anniversary_date": str(row[13]) if row[13] else None,
                    "profile_completion_percentage": row[14]
                }
            else:
                # Default profile data if no employee record exists
                employee_data = {
                    "first_name": "",
                    "last_name": "",
                    "department": "",
                    "position": "",
                    "phone": "",
                    "gender": "",
                    "address": "",
                    "emergency_contact_name": "",
                    "emergency_contact_phone": "",
                    "date_of_birth": None,
                    "wedding_anniversary_date": None,
                    "profile_completion_percentage": 0
                }
            
            profile_data = {
                "id": current_user["id"],
                "user_id": current_user["id"],
                "email": current_user["email"],
                "role": current_user["role"],
                "employee": employee_data
            }
            
            return profile_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")