"""
Initialize Role Capabilities in Database
Run this script to set up the initial role capabilities in the system_settings table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models  # Consolidated SQLAlchemy ORM models
import json

def initialize_capabilities():
    """Initialize default role capabilities in database"""
    db = SessionLocal()
    
    try:
        # Check if capabilities already exist
        existing = db.query(models.SystemSetting).filter(
            models.SystemSetting.setting_key == 'role_capabilities'
        ).first()
        
        if existing:
            print("✅ Role capabilities already exist in database")
            print(f"   Setting ID: {existing.id}")
            print(f"   Last updated: {existing.updated_at}")
            return
        
        # Define default capabilities
        modules = [
            'dashboard', 'recruitment', 'onboarding', 'employees', 'attendance',
            'leave', 'performance', 'engagement', 'learning', 'payroll',
            'analysis', 'career', 'assets', 'announcements'
        ]
        
        default_capabilities = {
            "super_admin": {module: {"enabled": True, "permissions": ["read", "write", "delete"]} for module in modules},
            "admin": {module: {"enabled": True, "permissions": ["read", "write", "delete"]} for module in modules},
            "hr": {module: {"enabled": True, "permissions": ["read", "write"]} for module in modules},
            "manager": {
                module: {
                    "enabled": module in ['dashboard', 'recruitment', 'employees', 'attendance', 'leave', 'performance', 'engagement', 'analysis', 'assets', 'announcements'],
                    "permissions": ["read", "write"] if module in ['dashboard', 'recruitment', 'employees', 'attendance', 'leave', 'performance', 'engagement', 'analysis', 'assets', 'announcements'] else []
                } for module in modules
            },
            "assets_team": {
                module: {
                    "enabled": module in ['dashboard', 'assets', 'announcements'],
                    "permissions": ["read", "write"] if module in ['dashboard', 'assets', 'announcements'] else []
                } for module in modules
            },
            "employee": {
                module: {
                    "enabled": module in ['dashboard', 'attendance', 'leave', 'performance', 'engagement', 'learning', 'career', 'assets', 'announcements'],
                    "permissions": ["read"] if module in ['dashboard', 'attendance', 'leave', 'performance', 'engagement', 'learning', 'career', 'assets', 'announcements'] else []
                } for module in modules
            },
            "candidate": {
                module: {
                    "enabled": module == 'dashboard',
                    "permissions": ["read"] if module == 'dashboard' else []
                } for module in modules
            }
        }
        
        # Create the setting
        setting = models.SystemSetting(
            setting_key='role_capabilities',
            setting_value=json.dumps(default_capabilities),
            description='Role-based module capabilities and permissions',
            category='security',
            is_active=True
        )
        
        db.add(setting)
        db.commit()
        
        print("✅ Successfully initialized role capabilities in database")
        print(f"   Setting ID: {setting.id}")
        print(f"   Roles configured: {len(default_capabilities)}")
        print(f"   Modules per role: {len(modules)}")
        
    except Exception as e:
        print(f"❌ Error initializing capabilities: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Initializing Role Capabilities...")
    print("=" * 50)
    initialize_capabilities()
    print("=" * 50)
    print("✅ Done!")
