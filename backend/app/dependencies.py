from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import text
from app import auth_utils
from app.database import engine
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current authenticated user from JWT token and database"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify and decode token
        payload = auth_utils.verify_token(token)
        if not payload:
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
            
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in token validation: {e}")
        raise credentials_exception
    
    # Get user from database
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT id, email, username, full_name, role, is_active
                FROM users
                WHERE email = :email
            """)
            result = conn.execute(query, {"email": email})
            user_row = result.fetchone()
            
            if not user_row:
                logger.warning(f"User not found in database: {email}")
                raise credentials_exception
            
            # Convert to dict
            user = {
                "id": user_row[0],
                "email": user_row[1],
                "username": user_row[2],
                "full_name": user_row[3],
                "role": user_row[4],
                "is_active": user_row[5]
            }
            
            # Check if user is active
            if not user.get("is_active", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Inactive user account"
                )
            
            return user
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error fetching user: {e}")
        raise credentials_exception

def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user (additional check)"""
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_roles(allowed_roles: list):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

# Common role dependencies
require_admin = require_roles(["admin", "super_admin"])
require_hr = require_roles(["admin", "super_admin", "hr"])
require_manager = require_roles(["admin", "super_admin", "hr", "manager"])

def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """Get current user if token is provided, otherwise return None"""
    if not token:
        return None
    
    try:
        return get_current_user(token)
    except HTTPException:
        return None
