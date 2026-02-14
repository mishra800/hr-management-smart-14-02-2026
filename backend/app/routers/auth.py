from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy import text
from app import schemas
from app.database import get_db, engine
from app.auth_utils import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/register")
def register_user(user: schemas.UserCreate) -> schemas.APIResponse:
    """Register a new user in the database and create employee record"""
    try:
        with engine.connect() as conn:
            # Check if user already exists
            check_query = text("SELECT id FROM users WHERE email = :email")
            result = conn.execute(check_query, {"email": user.email})
            if result.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Insert new user
            insert_user_query = text("""
                INSERT INTO users (email, username, hashed_password, full_name, role, is_active, created_at, updated_at)
                VALUES (:email, :username, :hashed_password, :full_name, :role, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id, email, role
            """)
            
            full_name = f"{user.first_name or 'User'} {user.last_name or ''}".strip()
            
            result = conn.execute(insert_user_query, {
                "email": user.email,
                "username": user.email.split('@')[0],
                "hashed_password": get_password_hash(user.password),
                "full_name": full_name,
                "role": user.role
            })
            
            new_user = result.fetchone()
            user_id = new_user[0]
            
            # Create corresponding employee record
            insert_employee_query = text("""
                INSERT INTO employees (
                    user_id, 
                    employee_id, 
                    first_name, 
                    last_name, 
                    email, 
                    department, 
                    position, 
                    hire_date,
                    status,
                    profile_completion_percentage,
                    wfh_status,
                    onboarding_status,
                    it_setup_status,
                    created_at, 
                    updated_at
                )
                VALUES (
                    :user_id,
                    :employee_id,
                    :first_name,
                    :last_name,
                    :email,
                    :department,
                    :position,
                    CURRENT_DATE,
                    'active',
                    20,
                    'office',
                    'initiated',
                    'pending',
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                RETURNING id
            """)
            
            # Generate employee ID (e.g., EMP001, EMP002, etc.)
            emp_count_query = text("SELECT COUNT(*) FROM employees")
            emp_count = conn.execute(emp_count_query).scalar()
            employee_id = f"EMP{str(emp_count + 1).zfill(3)}"
            
            result = conn.execute(insert_employee_query, {
                "user_id": user_id,
                "employee_id": employee_id,
                "first_name": user.first_name or "User",
                "last_name": user.last_name or "",
                "email": user.email,
                "department": "General",  # Default department
                "position": user.role.replace('_', ' ').title()  # Convert role to position
            })
            
            employee_record_id = result.fetchone()[0]
            
            # Commit all changes
            conn.commit()
            
            return schemas.APIResponse(
                success=True,
                message="User registered successfully",
                data={
                    "id": user_id,
                    "email": new_user[1],
                    "role": new_user[2],
                    "employee_id": employee_id,
                    "employee_record_id": employee_record_id
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=None)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user from database"""
    try:
        with engine.connect() as conn:
            # Query user from database
            query = text("""
                SELECT id, email, hashed_password, role, is_active, full_name
                FROM users
                WHERE email = :email
            """)
            result = conn.execute(query, {"email": form_data.username})
            user = result.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found. Please check your email address.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify password
            if not verify_password(form_data.password, user[2]):  # user[2] is hashed_password
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Check if active
            if not user[4]:  # user[4] is is_active
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is inactive",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user[1]}, expires_delta=access_token_expires  # user[1] is email
            )
            
            return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me")
def read_users_me() -> dict:
    """Get current user info (placeholder)"""
    return {
        "id": 1,
        "email": "admin@company.com",
        "role": "admin",
        "is_active": True
    }