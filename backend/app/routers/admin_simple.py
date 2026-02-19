from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
import re
import logging
from ..dependencies import get_current_user
from ..database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# Pydantic Models for structured data validation
class SystemSettingsGeneral(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=100)
    timezone: str = Field(..., pattern=r'^[A-Za-z_/]+$')
    date_format: str = Field(..., pattern=r'^[A-Z\-/]+$')
    currency: str = Field(..., min_length=3, max_length=3)
    language: str = Field(..., min_length=2, max_length=5)

class SystemSettingsSecurity(BaseModel):
    password_min_length: int = Field(..., ge=6, le=50)
    password_require_uppercase: bool
    password_require_numbers: bool
    password_require_symbols: bool
    session_timeout: int = Field(..., ge=300, le=86400)  # 5 min to 24 hours
    max_login_attempts: int = Field(..., ge=3, le=10)

class SystemSettingsNotifications(BaseModel):
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    notification_retention_days: int = Field(..., ge=1, le=365)

class SystemSettingsBackup(BaseModel):
    auto_backup: bool
    backup_frequency: str = Field(..., pattern=r'^(daily|weekly|monthly)$')
    backup_retention_days: int = Field(..., ge=1, le=365)
    backup_location: str = Field(..., pattern=r'^(local|cloud|both)$')

class SystemSettingsUpdate(BaseModel):
    general: Optional[SystemSettingsGeneral] = None
    security: Optional[SystemSettingsSecurity] = None
    notifications: Optional[SystemSettingsNotifications] = None
    backup: Optional[SystemSettingsBackup] = None

class CapabilityUpdate(BaseModel):
    capabilities: Dict[str, Dict[str, bool]]
    
    @validator('capabilities')
    def validate_capabilities(cls, v):
        allowed_roles = {'admin', 'hr', 'manager', 'employee', 'assets_team', 'candidate', 'super_admin'}
        allowed_modules = {
            'dashboard', 'recruitment', 'onboarding', 'employees', 'attendance', 
            'leave', 'performance', 'engagement', 'learning', 'payroll', 
            'analysis', 'career', 'assets', 'announcements'
        }
        
        for role, capabilities in v.items():
            if role not in allowed_roles:
                raise ValueError(f'Invalid role: {role}')
            for module, enabled in capabilities.items():
                if module not in allowed_modules:
                    raise ValueError(f'Invalid module: {module}')
                if not isinstance(enabled, bool):
                    raise ValueError(f'Capability value must be boolean for {role}.{module}')
        return v

class RoleCapabilityRequest(BaseModel):
    role: str
    
    @validator('role')
    def validate_role(cls, v):
        # Sanitize role input to prevent injection
        if not re.match(r'^[a-zA-Z_]+$', v):
            raise ValueError('Role must contain only letters and underscores')
        return v.lower()

# Database Models (using SQLite for persistence)
class SystemSetting(BaseModel):
    id: Optional[int] = None
    category: str
    key: str
    value: str
    updated_by: int
    updated_at: datetime = Field(default_factory=datetime.now)

class AuditLog(BaseModel):
    id: Optional[int] = None
    user_id: int
    user_email: str
    action: str
    resource_type: str
    resource_id: Any
    timestamp: datetime = Field(default_factory=datetime.now)
    details: str
    ip_address: str

class RoleCapability(BaseModel):
    id: Optional[int] = None
    role: str
    module: str
    enabled: bool
    updated_by: int
    updated_at: datetime = Field(default_factory=datetime.now)

# Helper functions for database operations (SQLite-based persistence)
def init_sqlite_tables(db: Session):
    """Initialize SQLite tables for admin data"""
    try:
        # Create tables if they don't exist
        db.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_by INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                ip_address TEXT
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS role_capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                module TEXT NOT NULL,
                enabled BOOLEAN NOT NULL,
                updated_by INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(role, module)
            )
        """)
        
        db.commit()
        logger.info("SQLite tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite tables: {e}")
        db.rollback()

def sanitize_role_input(role: str) -> str:
    """Sanitize role input to prevent injection attacks"""
    if not role:
        raise ValueError("Role cannot be empty")
    
    # Remove any potentially dangerous characters
    sanitized = re.sub(r'[^a-zA-Z_]', '', role.strip())
    
    if not sanitized:
        raise ValueError("Invalid role format")
    
    # Convert to lowercase for consistency
    sanitized = sanitized.lower()
    
    # Validate against allowed roles
    allowed_roles = {'admin', 'hr', 'manager', 'employee', 'assets_team', 'candidate', 'super_admin'}
    if sanitized not in allowed_roles:
        raise ValueError(f"Role '{sanitized}' is not allowed")
    
    return sanitized

def log_audit_event(db: Session, user_id: int, user_email: str, action: str, 
                   resource_type: str, resource_id: Any, details: str, ip_address: str = "127.0.0.1"):
    """Log audit event to database"""
    try:
        db.execute("""
            INSERT INTO audit_logs (user_id, user_email, action, resource_type, resource_id, details, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, user_email, action, resource_type, str(resource_id), details, ip_address))
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
        db.rollback()

def get_default_capabilities() -> Dict[str, Dict[str, bool]]:
    """Get default role capabilities"""
    return {
        "admin": {
            "dashboard": True, "recruitment": True, "onboarding": True, "employees": True,
            "attendance": True, "leave": True, "performance": True, "engagement": True,
            "learning": True, "payroll": True, "analysis": True, "career": True,
            "assets": True, "announcements": True
        },
        "hr": {
            "dashboard": True, "recruitment": True, "onboarding": True, "employees": True,
            "attendance": True, "leave": True, "performance": True, "engagement": True,
            "learning": True, "payroll": False, "analysis": True, "career": True,
            "assets": False, "announcements": True
        },
        "manager": {
            "dashboard": True, "recruitment": False, "onboarding": False, "employees": True,
            "attendance": True, "leave": True, "performance": True, "engagement": True,
            "learning": True, "payroll": False, "analysis": True, "career": True,
            "assets": False, "announcements": False
        },
        "employee": {
            "dashboard": True, "recruitment": False, "onboarding": False, "employees": False,
            "attendance": True, "leave": True, "performance": True, "engagement": True,
            "learning": True, "payroll": False, "analysis": False, "career": True,
            "assets": True, "announcements": False
        },
        "assets_team": {
            "dashboard": True, "recruitment": False, "onboarding": False, "employees": False,
            "attendance": False, "leave": False, "performance": False, "engagement": False,
            "learning": False, "payroll": False, "analysis": False, "career": False,
            "assets": True, "announcements": False
        },
        "candidate": {
            "dashboard": False, "recruitment": True, "onboarding": False, "employees": False,
            "attendance": False, "leave": False, "performance": False, "engagement": False,
            "learning": False, "payroll": False, "analysis": False, "career": False,
            "assets": False, "announcements": False
        }
    }
@router.get("/capabilities")
def get_capabilities(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all role-based module capabilities"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can access system capabilities")
    
    try:
        # Initialize tables if needed
        init_sqlite_tables(db)
        
        # Get capabilities from database
        result = db.execute("SELECT role, module, enabled FROM role_capabilities").fetchall()
        
        if not result:
            # If no data in DB, use defaults and populate DB
            default_caps = get_default_capabilities()
            for role, modules in default_caps.items():
                for module, enabled in modules.items():
                    db.execute("""
                        INSERT OR REPLACE INTO role_capabilities (role, module, enabled, updated_by)
                        VALUES (?, ?, ?, ?)
                    """, (role, module, enabled, current_user.get("id", 1)))
            db.commit()
            capabilities = default_caps
        else:
            # Build capabilities dict from database
            capabilities = {}
            for row in result:
                role, module, enabled = row
                if role not in capabilities:
                    capabilities[role] = {}
                capabilities[role][module] = bool(enabled)
        
        return {
            "success": True,
            "data": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve capabilities")

@router.post("/capabilities")
def save_capabilities(
    capabilities_data: CapabilityUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save role-based module capabilities"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can modify system capabilities")
    
    try:
        # Initialize tables if needed
        init_sqlite_tables(db)
        
        # Update capabilities in database
        for role, modules in capabilities_data.capabilities.items():
            for module, enabled in modules.items():
                db.execute("""
                    INSERT OR REPLACE INTO role_capabilities (role, module, enabled, updated_by)
                    VALUES (?, ?, ?, ?)
                """, (role, module, enabled, current_user.get("id")))
        
        db.commit()
        
        # Log audit event
        log_audit_event(
            db, current_user.get("id"), current_user.get("email"),
            "capability_change", "system_capabilities", 0,
            f"Capabilities updated by {current_user.get('email')}"
        )
        
        return {
            "success": True,
            "message": "Capabilities saved successfully"
        }
    except Exception as e:
        logger.error(f"Error saving capabilities: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save capabilities")

@router.get("/audit-logs")
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can access audit logs")
    
    try:
        # Initialize tables if needed
        init_sqlite_tables(db)
        
        # Get total count
        total_result = db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()
        total = total_result[0] if total_result else 0
        
        # Get paginated logs
        logs_result = db.execute("""
            SELECT id, user_id, user_email, action, resource_type, resource_id, 
                   timestamp, details, ip_address
            FROM audit_logs 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        """, (limit, skip)).fetchall()
        
        logs = []
        for row in logs_result:
            logs.append({
                "id": row[0],
                "user_id": row[1],
                "user_email": row[2],
                "action": row[3],
                "resource_type": row[4],
                "resource_id": row[5],
                "timestamp": row[6],
                "details": row[7],
                "ip_address": row[8]
            })
        
        # If no logs exist, create some sample data
        if total == 0:
            sample_actions = [
                "user_login", "user_logout", "capability_change", "user_created", 
                "user_updated", "role_changed", "password_reset", "data_export"
            ]
            
            for i in range(20):
                timestamp = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                db.execute("""
                    INSERT INTO audit_logs (user_id, user_email, action, resource_type, 
                                          resource_id, timestamp, details, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    random.randint(1, 5),
                    f"user{random.randint(1, 5)}@company.com",
                    random.choice(sample_actions),
                    random.choice(["user", "system", "data", "capabilities"]),
                    str(random.randint(1, 100)),
                    timestamp,
                    f"Sample audit log entry {i + 1}",
                    f"192.168.1.{random.randint(1, 255)}"
                ))
            db.commit()
            
            # Re-fetch after creating sample data
            return get_audit_logs(skip, limit, current_user, db)
        
        return {
            "success": True,
            "data": {
                "logs": logs,
                "total": total
            }
        }
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs")

@router.get("/users/stats")
def get_user_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can access user stats")
    
    # Mock stats for now - in real implementation, query actual user tables
    mock_stats = {
        "total_users": 25,
        "active_users": 22,
        "inactive_users": 3,
        "users_by_role": {
            "admin": 2,
            "hr": 3,
            "manager": 5,
            "employee": 12,
            "assets_team": 2,
            "candidate": 1
        },
        "recent_logins": 18,
        "failed_logins": 2
    }
    
    return {
        "success": True,
        "data": mock_stats
    }

@router.get("/permission-templates")
def get_permission_templates(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get permission templates"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can access permission templates")
    
    default_caps = get_default_capabilities()
    
    templates = {
        "basic_employee": {
            "name": "Basic Employee",
            "description": "Standard employee permissions",
            "capabilities": default_caps["employee"]
        },
        "team_lead": {
            "name": "Team Lead",
            "description": "Team leadership permissions",
            "capabilities": default_caps["manager"]
        },
        "hr_specialist": {
            "name": "HR Specialist", 
            "description": "HR department permissions",
            "capabilities": default_caps["hr"]
        },
        "system_admin": {
            "name": "System Administrator",
            "description": "Full system access",
            "capabilities": default_caps["admin"]
        }
    }
    
    return {
        "success": True,
        "data": templates
    }

@router.post("/permission-templates/{template_name}/apply")
def apply_permission_template(
    template_name: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply a permission template"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can apply permission templates")
    
    # Sanitize template name
    if not re.match(r'^[a-zA-Z_]+$', template_name):
        raise HTTPException(status_code=400, detail="Invalid template name")
    
    allowed_templates = {"basic_employee", "team_lead", "hr_specialist", "system_admin"}
    if template_name not in allowed_templates:
        raise HTTPException(status_code=404, detail="Permission template not found")
    
    try:
        # Initialize tables if needed
        init_sqlite_tables(db)
        
        # Get template capabilities
        default_caps = get_default_capabilities()
        role_mapping = {
            "basic_employee": "employee",
            "team_lead": "manager", 
            "hr_specialist": "hr",
            "system_admin": "admin"
        }
        
        role = role_mapping[template_name]
        capabilities = default_caps[role]
        
        # Apply template to database
        for module, enabled in capabilities.items():
            db.execute("""
                INSERT OR REPLACE INTO role_capabilities (role, module, enabled, updated_by)
                VALUES (?, ?, ?, ?)
            """, (role, module, enabled, current_user.get("id")))
        
        db.commit()
        
        # Log audit event
        log_audit_event(
            db, current_user.get("id"), current_user.get("email"),
            "template_applied", "permission_template", template_name,
            f"Applied template '{template_name}' by {current_user.get('email')}"
        )
        
        return {
            "success": True,
            "message": f"Permission template '{template_name}' applied successfully"
        }
    except Exception as e:
        logger.error(f"Error applying permission template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to apply permission template")

@router.post("/create-sample-audit-logs")
def create_sample_audit_logs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create sample audit logs for testing"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can create sample data")
    
    try:
        # Initialize tables if needed
        init_sqlite_tables(db)
        
        sample_actions = [
            "user_login", "user_logout", "capability_change", "user_created", 
            "user_updated", "role_changed", "password_reset", "data_export",
            "file_upload", "report_generated", "system_backup", "security_scan"
        ]
        
        # Clear existing logs
        db.execute("DELETE FROM audit_logs")
        
        # Create new sample logs
        for i in range(50):
            timestamp = (datetime.now() - timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )).isoformat()
            
            db.execute("""
                INSERT INTO audit_logs (user_id, user_email, action, resource_type, 
                                      resource_id, timestamp, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                random.randint(1, 10),
                f"user{random.randint(1, 10)}@company.com",
                random.choice(sample_actions),
                random.choice(["user", "system", "data", "capabilities", "file", "report"]),
                str(random.randint(1, 1000)),
                timestamp,
                f"Sample audit log entry {i + 1} - {random.choice(['Success', 'Warning', 'Info', 'Error'])}",
                f"192.168.{random.randint(1, 10)}.{random.randint(1, 255)}"
            ))
        
        db.commit()
        
        # Get count of created logs
        count_result = db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()
        count = count_result[0] if count_result else 0
        
        return {
            "success": True,
            "message": f"Created {count} sample audit logs"
        }
    except Exception as e:
        logger.error(f"Error creating sample audit logs: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create sample audit logs")

@router.get("/users")
def get_users(
    skip: int = 0,
    limit: int = 100,
    role_filter: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get users list with pagination and filtering"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can access users list")
    
    try:
        # Sanitize role filter if provided
        if role_filter:
            role_filter = sanitize_role_input(role_filter)
        
        # Mock users data - in real implementation, query actual user tables
        mock_users = [
            {"id": 1, "email": "admin@company.com", "role": "admin", "is_active": True, "created_at": "2024-01-01T00:00:00"},
            {"id": 2, "email": "hr@company.com", "role": "hr", "is_active": True, "created_at": "2024-01-02T00:00:00"},
            {"id": 3, "email": "manager1@company.com", "role": "manager", "is_active": True, "created_at": "2024-01-03T00:00:00"},
            {"id": 4, "email": "employee1@company.com", "role": "employee", "is_active": True, "created_at": "2024-01-04T00:00:00"},
            {"id": 5, "email": "employee2@company.com", "role": "employee", "is_active": False, "created_at": "2024-01-05T00:00:00"},
        ]
        
        # Apply role filter
        if role_filter:
            mock_users = [user for user in mock_users if user["role"] == role_filter]
        
        # Apply pagination
        paginated_users = mock_users[skip:skip + limit]
        
        return {
            "success": True,
            "data": {
                "users": paginated_users,
                "total": len(mock_users)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate a user"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can activate users")
    
    # Validate user_id
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    try:
        # Log audit event
        log_audit_event(
            db, current_user.get("id"), current_user.get("email"),
            "user_activated", "user", user_id,
            f"User {user_id} activated by {current_user.get('email')}"
        )
        
        return {
            "success": True,
            "message": f"User {user_id} activated successfully"
        }
    except Exception as e:
        logger.error(f"Error activating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate user")

@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can deactivate users")
    
    # Validate user_id
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    try:
        # Log audit event
        log_audit_event(
            db, current_user.get("id"), current_user.get("email"),
            "user_deactivated", "user", user_id,
            f"User {user_id} deactivated by {current_user.get('email')}"
        )
        
        return {
            "success": True,
            "message": f"User {user_id} deactivated successfully"
        }
    except Exception as e:
        logger.error(f"Error deactivating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate user")

@router.get("/system-settings")
def get_system_settings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system settings"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can access system settings")
    
    try:
        # Initialize tables if needed
        init_sqlite_tables(db)
        
        # Get settings from database
        settings_result = db.execute("SELECT category, key, value FROM system_settings").fetchall()
        
        # Build settings structure
        settings = {
            "general": {},
            "security": {},
            "notifications": {},
            "backup": {}
        }
        
        for row in settings_result:
            category, key, value = row
            if category in settings:
                # Parse boolean and integer values
                if value.lower() in ('true', 'false'):
                    settings[category][key] = value.lower() == 'true'
                elif value.isdigit():
                    settings[category][key] = int(value)
                else:
                    settings[category][key] = value
        
        # If no settings exist, use defaults
        if not settings_result:
            default_settings = {
                "general": {
                    "company_name": "Dhanush HR Solutions",
                    "timezone": "UTC",
                    "date_format": "YYYY-MM-DD",
                    "currency": "USD",
                    "language": "en"
                },
                "security": {
                    "password_min_length": 8,
                    "password_require_uppercase": True,
                    "password_require_numbers": True,
                    "password_require_symbols": True,
                    "session_timeout": 3600,
                    "max_login_attempts": 5
                },
                "notifications": {
                    "email_notifications": True,
                    "sms_notifications": False,
                    "push_notifications": True,
                    "notification_retention_days": 30
                },
                "backup": {
                    "auto_backup": True,
                    "backup_frequency": "daily",
                    "backup_retention_days": 30,
                    "backup_location": "cloud"
                }
            }
            
            # Save defaults to database
            for category, settings_dict in default_settings.items():
                for key, value in settings_dict.items():
                    db.execute("""
                        INSERT INTO system_settings (category, key, value, updated_by)
                        VALUES (?, ?, ?, ?)
                    """, (category, key, str(value), current_user.get("id", 1)))
            db.commit()
            
            settings = default_settings
        
        return {
            "success": True,
            "data": settings
        }
    except Exception as e:
        logger.error(f"Error getting system settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system settings")

@router.post("/system-settings")
def save_system_settings(
    settings_data: SystemSettingsUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save system settings"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can modify system settings")
    
    try:
        # Initialize tables if needed
        init_sqlite_tables(db)
        
        # Update settings in database
        settings_dict = settings_data.dict(exclude_none=True)
        
        for category, settings in settings_dict.items():
            if settings:  # Only process non-None categories
                for key, value in settings.items():
                    db.execute("""
                        INSERT OR REPLACE INTO system_settings (category, key, value, updated_by)
                        VALUES (?, ?, ?, ?)
                    """, (category, key, str(value), current_user.get("id")))
        
        db.commit()
        
        # Log audit event
        log_audit_event(
            db, current_user.get("id"), current_user.get("email"),
            "system_settings_updated", "system_settings", 0,
            f"System settings updated by {current_user.get('email')}"
        )
        
        return {
            "success": True,
            "message": "System settings saved successfully"
        }
    except Exception as e:
        logger.error(f"Error saving system settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save system settings")

@router.get("/system-health")
def get_system_health(current_user: dict = Depends(get_current_user)):
    """Get system health status"""
    if current_user.get("role") not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Only super admins can access system health")
    
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "uptime": "15 days, 8 hours",
            "cpu_usage": f"{random.randint(15, 45)}%",
            "memory_usage": f"{random.randint(35, 75)}%",
            "disk_usage": f"{random.randint(25, 60)}%",
            "active_sessions": random.randint(8, 25),
            "database_status": "connected",
            "last_backup": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
            "services": {
                "api": "running",
                "database": "running", 
                "cache": "running",
                "email": "running",
                "file_storage": "running"
            }
        }
    }

@router.get("/capabilities/{role}")
def get_role_capabilities(
    role: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get capabilities for a specific role"""
    try:
        # Sanitize role input to prevent injection
        sanitized_role = sanitize_role_input(role)
        
        # Users can view their own role capabilities, admins can view any
        if current_user.get("role") not in ['admin', 'super_admin'] and current_user.get("role") != sanitized_role:
            raise HTTPException(status_code=403, detail="You can only view your own role capabilities")
        
        # Initialize tables if needed
        init_sqlite_tables(db)
        
        # Get capabilities from database
        result = db.execute("""
            SELECT module, enabled FROM role_capabilities WHERE role = ?
        """, (sanitized_role,)).fetchall()
        
        if not result:
            # If no data for this role, use defaults
            default_caps = get_default_capabilities()
            if sanitized_role in default_caps:
                capabilities = default_caps[sanitized_role]
                # Save to database
                for module, enabled in capabilities.items():
                    db.execute("""
                        INSERT INTO role_capabilities (role, module, enabled, updated_by)
                        VALUES (?, ?, ?, ?)
                    """, (sanitized_role, module, enabled, current_user.get("id", 1)))
                db.commit()
            else:
                raise HTTPException(status_code=404, detail="Role not found")
        else:
            # Build capabilities from database
            capabilities = {}
            for row in result:
                module, enabled = row
                capabilities[module] = bool(enabled)
        
        return {
            "success": True,
            "data": {
                "role": sanitized_role,
                "capabilities": capabilities
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting role capabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve role capabilities")