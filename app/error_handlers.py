"""
Comprehensive Error Handling for HR Management System
Provides consistent error responses and logging
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import traceback

# Configure logger
logger = logging.getLogger(__name__)

class ErrorResponse:
    """Standardized error response format"""
    
    @staticmethod
    def create_error_response(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }
        }

class ValidationError(HTTPException):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        self.field = field
        self.details = details or {}
        super().__init__(status_code=422, detail=message)

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(status_code=401, detail=message)

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail=message)

class BusinessLogicError(HTTPException):
    """Custom business logic error"""
    def __init__(self, message: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        self.error_code = error_code
        super().__init__(status_code=400, detail=message)

class ResourceNotFoundError(HTTPException):
    """Custom resource not found error"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(status_code=404, detail=message)

# Error handlers for FastAPI app
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    
    # Extract field-level errors
    field_errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        field_errors[field] = error["msg"]
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse.create_error_response(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            details={
                "field_errors": field_errors,
                "raw_errors": exc.errors()
            },
            status_code=422
        )
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_SERVER_ERROR"
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.create_error_response(
            error_code=error_codes.get(exc.status_code, "HTTP_ERROR"),
            message=str(exc.detail),
            status_code=exc.status_code
        )
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="An internal server error occurred",
            details={
                "error_type": type(exc).__name__,
                "error_message": str(exc)
            },
            status_code=500
        )
    )

# Utility functions for common error scenarios
def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate required fields in data"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )

def validate_email_format(email: str) -> None:
    """Validate email format"""
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError(
            message="Invalid email format",
            field="email"
        )

def validate_phone_format(phone: str) -> None:
    """Validate phone format"""
    import re
    # Basic phone validation - can be enhanced
    phone_pattern = r'^\+?[\d\s\-\(\)]{10,}$'
    if not re.match(phone_pattern, phone):
        raise ValidationError(
            message="Invalid phone format",
            field="phone"
        )

def validate_date_range(start_date, end_date) -> None:
    """Validate date range"""
    if start_date > end_date:
        raise ValidationError(
            message="Start date cannot be after end date",
            details={"start_date": str(start_date), "end_date": str(end_date)}
        )

def check_user_permissions(user_role: str, required_roles: list) -> None:
    """Check if user has required permissions"""
    if user_role not in required_roles:
        raise AuthorizationError(
            message=f"Access denied. Required roles: {', '.join(required_roles)}"
        )

def log_user_action(user_id: int, action: str, resource: str, details: Dict[str, Any] = None):
    """Log user actions for audit trail"""
    logger.info(f"User {user_id} performed {action} on {resource}", extra={
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    })

# Database error handling
class DatabaseError(Exception):
    """Custom database error"""
    def __init__(self, message: str, operation: str = None):
        self.operation = operation
        super().__init__(message)

def handle_database_error(operation: str):
    """Decorator to handle database errors"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Database error in {operation}: {str(e)}")
                raise DatabaseError(
                    message=f"Database operation failed: {operation}",
                    operation=operation
                )
        return wrapper
    return decorator

# External service error handling
class ExternalServiceError(Exception):
    """Custom external service error"""
    def __init__(self, service: str, message: str):
        self.service = service
        super().__init__(message)

def handle_external_service_error(service_name: str):
    """Decorator to handle external service errors"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"External service error ({service_name}): {str(e)}")
                raise ExternalServiceError(
                    service=service_name,
                    message=f"External service unavailable: {service_name}"
                )
        return wrapper
    return decorator

# Retry mechanism
import time
from functools import wraps

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Retry decorator for handling transient failures"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator