from fastapi import APIRouter, HTTPException, Depends
from app import schemas
from app.database import get_db, engine
from app.dependencies import get_current_user
from datetime import datetime
from typing import List
from sqlalchemy import text

router = APIRouter(
    prefix="/employees",
    tags=["employees"]
)

@router.get("/")
def get_employees(current_user: dict = Depends(get_current_user)):
    """Get all employees from database - Protected endpoint"""
    # Check if user has permission to view employees
    if current_user.get("role") not in ["admin", "super_admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view employees")
    
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    e.id,
                    e.user_id,
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
                    e.profile_completion_percentage,
                    e.status,
                    e.hire_date,
                    e.created_at,
                    u.role
                FROM employees e
                LEFT JOIN users u ON e.user_id = u.id
                ORDER BY e.created_at DESC
            """)
            
            result = conn.execute(query)
            rows = result.fetchall()
            
            employees = []
            for row in rows:
                employees.append({
                    "id": row[0],
                    "user_id": row[1],
                    "employee_id": row[2],
                    "first_name": row[3],
                    "last_name": row[4],
                    "email": row[5],
                    "department": row[6],
                    "position": row[7],
                    "phone": row[8],
                    "gender": row[9],
                    "address": row[10],
                    "emergency_contact_name": row[11],
                    "emergency_contact_phone": row[12],
                    "date_of_birth": str(row[13]) if row[13] else None,
                    "wedding_anniversary_date": str(row[14]) if row[14] else None,
                    "profile_completion_percentage": row[15],
                    "status": row[16],
                    "hire_date": str(row[17]) if row[17] else None,
                    "created_at": str(row[18]) if row[18] else None,
                    "role": row[19]
                })
            
            return schemas.APIResponse(
                success=True,
                message="Employees retrieved successfully",
                data=employees
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employees: {str(e)}")

@router.get("/{employee_id}")
def get_employee(employee_id: int, current_user: dict = Depends(get_current_user)):
    """Get employee by ID from database - Protected endpoint"""
    # Users can view their own profile, managers/hr/admin can view others
    if current_user.get("role") not in ["admin", "super_admin", "hr", "manager"] and current_user.get("id") != employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view this employee")
    
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    e.id,
                    e.user_id,
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
                    e.profile_completion_percentage,
                    e.status,
                    e.hire_date,
                    e.created_at,
                    u.role
                FROM employees e
                LEFT JOIN users u ON e.user_id = u.id
                WHERE e.id = :employee_id
            """)
            
            result = conn.execute(query, {"employee_id": employee_id})
            row = result.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Employee not found")
            
            employee = {
                "id": row[0],
                "user_id": row[1],
                "employee_id": row[2],
                "first_name": row[3],
                "last_name": row[4],
                "email": row[5],
                "department": row[6],
                "position": row[7],
                "phone": row[8],
                "gender": row[9],
                "address": row[10],
                "emergency_contact_name": row[11],
                "emergency_contact_phone": row[12],
                "date_of_birth": str(row[13]) if row[13] else None,
                "wedding_anniversary_date": str(row[14]) if row[14] else None,
                "profile_completion_percentage": row[15],
                "status": row[16],
                "hire_date": str(row[17]) if row[17] else None,
                "created_at": str(row[18]) if row[18] else None,
                "role": row[19]
            }
            
            return schemas.APIResponse(
                success=True,
                message="Employee retrieved successfully",
                data=employee
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employee: {str(e)}")

@router.post("/create-with-account")
def create_employee_with_account(employee_data: dict, current_user: dict = Depends(get_current_user)):
    """Create new employee with user account in database - Protected endpoint"""
    # Only admin, super_admin, and hr can create employees
    if current_user.get("role") not in ["admin", "super_admin", "hr"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to create employees")
    
    try:
        with engine.connect() as conn:
            # Generate password if not provided
            password = employee_data.get("password")
            if not password:
                import random
                import string
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            from app.auth_utils import get_password_hash
            
            # Create user account first
            insert_user_query = text("""
                INSERT INTO users (email, username, hashed_password, full_name, role, is_active, created_at, updated_at)
                VALUES (:email, :username, :hashed_password, :full_name, :role, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id, email, role
            """)
            
            full_name = f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}".strip()
            
            result = conn.execute(insert_user_query, {
                "email": employee_data.get("email"),
                "username": employee_data.get("email").split('@')[0],
                "hashed_password": get_password_hash(password),
                "full_name": full_name,
                "role": employee_data.get("role", "employee")
            })
            
            user_row = result.fetchone()
            user_id = user_row[0]
            
            # Generate employee ID
            emp_count_query = text("SELECT COUNT(*) FROM employees")
            emp_count = conn.execute(emp_count_query).scalar()
            employee_id = f"EMP{str(emp_count + 1).zfill(3)}"
            
            # Create employee record
            insert_employee_query = text("""
                INSERT INTO employees (
                    user_id,
                    employee_id,
                    first_name,
                    last_name,
                    email,
                    department,
                    position,
                    phone,
                    hire_date,
                    status,
                    profile_completion_percentage,
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
                    :phone,
                    CURRENT_DATE,
                    'active',
                    60,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                RETURNING id, employee_id, first_name, last_name, email, department, position, phone
            """)
            
            result = conn.execute(insert_employee_query, {
                "user_id": user_id,
                "employee_id": employee_id,
                "first_name": employee_data.get("first_name"),
                "last_name": employee_data.get("last_name"),
                "email": employee_data.get("email"),
                "department": employee_data.get("department"),
                "position": employee_data.get("position"),
                "phone": employee_data.get("phone", "")
            })
            
            emp_row = result.fetchone()
            conn.commit()
            
            new_employee = {
                "id": emp_row[0],
                "employee_id": emp_row[1],
                "first_name": emp_row[2],
                "last_name": emp_row[3],
                "email": emp_row[4],
                "department": emp_row[5],
                "position": emp_row[6],
                "phone": emp_row[7],
                "created_by": current_user.get("id")
            }
            
            user_account = {
                "id": user_id,
                "email": user_row[1],
                "role": user_row[2],
                "is_active": True
            }
            
            # Return employee data with login credentials
            return schemas.APIResponse(
                success=True,
                message="Employee and user account created successfully",
                data={
                    "employee": new_employee,
                    "user_account": user_account,
                    "login_credentials": {
                        "email": employee_data.get("email"),
                        "password": password,
                        "temporary_password": True,
                        "first_login_required": True
                    }
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create employee with account: {str(e)}")

@router.post("/")
def create_employee(employee: schemas.EmployeeCreate, current_user: dict = Depends(get_current_user)):
    """Create new employee in database - Protected endpoint"""
    # Only admin, super_admin, and hr can create employees
    if current_user.get("role") not in ["admin", "super_admin", "hr"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to create employees")
    
    try:
        with engine.connect() as conn:
            # Generate employee ID
            emp_count_query = text("SELECT COUNT(*) FROM employees")
            emp_count = conn.execute(emp_count_query).scalar()
            employee_id = f"EMP{str(emp_count + 1).zfill(3)}"
            
            # Insert employee
            insert_query = text("""
                INSERT INTO employees (
                    employee_id,
                    first_name,
                    last_name,
                    email,
                    department,
                    position,
                    phone,
                    hire_date,
                    status,
                    profile_completion_percentage,
                    created_at,
                    updated_at
                )
                VALUES (
                    :employee_id,
                    :first_name,
                    :last_name,
                    :email,
                    :department,
                    :position,
                    :phone,
                    CURRENT_DATE,
                    'active',
                    50,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                RETURNING id, employee_id, first_name, last_name, email, department, position, phone, profile_completion_percentage, created_at
            """)
            
            result = conn.execute(insert_query, {
                "employee_id": employee_id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email": employee.email,
                "department": employee.department,
                "position": employee.position,
                "phone": employee.phone
            })
            
            row = result.fetchone()
            conn.commit()
            
            new_employee = {
                "id": row[0],
                "employee_id": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "email": row[4],
                "department": row[5],
                "position": row[6],
                "phone": row[7],
                "profile_completion_percentage": row[8],
                "created_at": str(row[9]),
                "created_by": current_user.get("id")
            }
            
            return schemas.APIResponse(
                success=True,
                message="Employee created successfully",
                data=new_employee
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create employee: {str(e)}")

@router.put("/{employee_id}")
def update_employee(employee_id: int, employee_update: schemas.EmployeeUpdate, current_user: dict = Depends(get_current_user)):
    """Update employee in database - Protected endpoint"""
    # Users can update their own profile, managers/hr/admin can update others
    if current_user.get("role") not in ["admin", "super_admin", "hr", "manager"] and current_user.get("id") != employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update this employee")
    
    try:
        with engine.connect() as conn:
            # Check if employee exists
            check_query = text("SELECT id FROM employees WHERE id = :employee_id")
            result = conn.execute(check_query, {"employee_id": employee_id})
            if not result.fetchone():
                raise HTTPException(status_code=404, detail="Employee not found")
            
            # Build update query dynamically based on provided fields
            update_fields = []
            params = {"employee_id": employee_id}
            
            update_data = employee_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            update_query = text(f"""
                UPDATE employees
                SET {', '.join(update_fields)}
                WHERE id = :employee_id
                RETURNING id, employee_id, first_name, last_name, email, department, position, phone, updated_at
            """)
            
            result = conn.execute(update_query, params)
            row = result.fetchone()
            conn.commit()
            
            updated_employee = {
                "id": row[0],
                "employee_id": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "email": row[4],
                "department": row[5],
                "position": row[6],
                "phone": row[7],
                "updated_at": str(row[8]),
                "updated_by": current_user.get("id")
            }
            
            return schemas.APIResponse(
                success=True,
                message="Employee updated successfully",
                data=updated_employee
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update employee: {str(e)}")

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, current_user: dict = Depends(get_current_user)):
    """Delete employee from database - Protected endpoint"""
    # Only admin and super_admin can delete employees
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to delete employees")
    
    try:
        with engine.connect() as conn:
            # Check if employee exists
            check_query = text("SELECT id FROM employees WHERE id = :employee_id")
            result = conn.execute(check_query, {"employee_id": employee_id})
            if not result.fetchone():
                raise HTTPException(status_code=404, detail="Employee not found")
            
            # Delete employee (or mark as inactive)
            delete_query = text("""
                UPDATE employees
                SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
                WHERE id = :employee_id
            """)
            
            conn.execute(delete_query, {"employee_id": employee_id})
            conn.commit()
            
            return schemas.APIResponse(
                success=True,
                message="Employee deleted successfully"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete employee: {str(e)}")
@router.put("/me/profile")
def update_my_profile(profile_update: schemas.EmployeeUpdate, current_user: dict = Depends(get_current_user)):
    """Update current user's profile in database"""
    user_id = current_user.get("id")
    
    try:
        with engine.connect() as conn:
            # Check if employee record exists for this user
            check_query = text("SELECT id FROM employees WHERE user_id = :user_id")
            result = conn.execute(check_query, {"user_id": user_id})
            employee_row = result.fetchone()
            
            if not employee_row:
                # Create employee record if it doesn't exist
                emp_count_query = text("SELECT COUNT(*) FROM employees")
                emp_count = conn.execute(emp_count_query).scalar()
                employee_id = f"EMP{str(emp_count + 1).zfill(3)}"
                
                insert_query = text("""
                    INSERT INTO employees (
                        user_id,
                        employee_id,
                        email,
                        first_name,
                        last_name,
                        department,
                        position,
                        phone,
                        gender,
                        address,
                        hire_date,
                        status,
                        profile_completion_percentage,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :user_id,
                        :employee_id,
                        :email,
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                        CURRENT_DATE,
                        'active',
                        0,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    RETURNING id
                """)
                
                result = conn.execute(insert_query, {
                    "user_id": user_id,
                    "employee_id": employee_id,
                    "email": current_user.get("email")
                })
                employee_row = result.fetchone()
            
            employee_db_id = employee_row[0]
            
            # Build update query
            update_fields = []
            params = {"employee_id": employee_db_id}
            
            update_data = profile_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value
            
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                
                update_query = text(f"""
                    UPDATE employees
                    SET {', '.join(update_fields)}
                    WHERE id = :employee_id
                    RETURNING id, employee_id, first_name, last_name, email, department, position, phone, gender, profile_completion_percentage
                """)
                
                result = conn.execute(update_query, params)
                row = result.fetchone()
                conn.commit()
                
                employee = {
                    "id": row[0],
                    "employee_id": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "email": row[4],
                    "department": row[5],
                    "position": row[6],
                    "phone": row[7],
                    "gender": row[8],
                    "profile_completion_percentage": row[9]
                }
            else:
                # Just fetch current data
                fetch_query = text("""
                    SELECT id, employee_id, first_name, last_name, email, department, position, phone, gender, profile_completion_percentage
                    FROM employees
                    WHERE id = :employee_id
                """)
                result = conn.execute(fetch_query, {"employee_id": employee_db_id})
                row = result.fetchone()
                
                employee = {
                    "id": row[0],
                    "employee_id": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "email": row[4],
                    "department": row[5],
                    "position": row[6],
                    "phone": row[7],
                    "gender": row[8],
                    "profile_completion_percentage": row[9]
                }
            
            return schemas.APIResponse(
                success=True,
                message="Profile updated successfully",
                data={
                    "employee": employee,
                    "profile_completion": employee["profile_completion_percentage"]
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.get("/me/profile-status")
def get_my_profile_status(current_user: dict = Depends(get_current_user)):
    """Get current user's profile completion status from database"""
    user_id = current_user.get("id")
    
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT first_name, last_name, department, phone, gender, profile_completion_percentage
                FROM employees
                WHERE user_id = :user_id
            """)
            
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()
            
            if not row:
                return schemas.APIResponse(
                    success=True,
                    message="Profile status retrieved",
                    data={
                        "profile_completion": 0,
                        "missing_fields": ["first_name", "last_name", "department", "phone", "gender"]
                    }
                )
            
            required_fields = {
                "first_name": row[0],
                "last_name": row[1],
                "department": row[2],
                "phone": row[3],
                "gender": row[4]
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            completed_fields = len(required_fields) - len(missing_fields)
            completion_percentage = int((completed_fields / len(required_fields)) * 100)
            
            return schemas.APIResponse(
                success=True,
                message="Profile status retrieved",
                data={
                    "profile_completion": completion_percentage,
                    "missing_fields": missing_fields
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile status: {str(e)}")