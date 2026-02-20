#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Configuration Verification Script
Checks if the consolidated .env file is properly configured
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if filepath.exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {filepath}")
        return False

def check_env_variable(var_name, required=True):
    """Check if an environment variable is set"""
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if any(keyword in var_name.lower() for keyword in ['password', 'secret', 'key', 'token']):
            display_value = '***' + value[-4:] if len(value) > 4 else '***'
        else:
            display_value = value
        print(f"✓ {var_name}: {display_value}")
        return True
    else:
        status = "✗ REQUIRED" if required else "⚠ OPTIONAL"
        print(f"{status} {var_name}: Not set")
        return not required

def main():
    print("=" * 70)
    print("HR MANAGEMENT SYSTEM - ENVIRONMENT CONFIGURATION VERIFICATION")
    print("=" * 70)
    print()
    
    # Check for .env file
    print("1. Checking for .env files...")
    print("-" * 70)
    
    root_env = Path.cwd() / '.env'
    env_example = Path.cwd() / '.env.example'
    backend_env = Path.cwd() / 'backend' / '.env'
    frontend_env = Path.cwd() / 'frontend' / '.env'
    
    has_root_env = check_file_exists(root_env, "Root .env file")
    check_file_exists(env_example, ".env.example template")
    
    # Check for old .env files (should not exist)
    if backend_env.exists():
        print(f"⚠ WARNING: Old backend/.env file still exists. Consider removing it.")
    else:
        print(f"✓ backend/.env correctly removed (using root .env)")
        
    if frontend_env.exists():
        print(f"⚠ WARNING: Old frontend/.env file still exists. Consider removing it.")
    else:
        print(f"✓ frontend/.env correctly removed (using root .env)")
    
    print()
    
    if not has_root_env:
        print("✗ FAILED: Root .env file not found!")
        print("\nTo fix this:")
        print("  1. Copy .env.example to .env")
        print("  2. Update the values with your configuration")
        print("\nCommand: cp .env.example .env")
        sys.exit(1)
    
    # Load environment variables
    load_dotenv(root_env)
    
    # Check required variables
    print("2. Checking required environment variables...")
    print("-" * 70)
    
    all_ok = True
    
    # Database
    print("\nDatabase Configuration:")
    all_ok &= check_env_variable("DATABASE_URL", required=True)
    check_env_variable("POSTGRES_DB", required=False)
    check_env_variable("POSTGRES_USER", required=False)
    check_env_variable("POSTGRES_PASSWORD", required=False)
    
    # Backend
    print("\nBackend Configuration:")
    all_ok &= check_env_variable("SECRET_KEY", required=True)
    all_ok &= check_env_variable("ENVIRONMENT", required=True)
    check_env_variable("DEBUG", required=False)
    check_env_variable("BACKEND_PORT", required=False)
    check_env_variable("CORS_ORIGINS", required=False)
    
    # Frontend
    print("\nFrontend Configuration:")
    all_ok &= check_env_variable("VITE_API_BASE_URL", required=True)
    check_env_variable("FRONTEND_PORT", required=False)
    
    # Optional services
    print("\nOptional Services:")
    check_env_variable("SMTP_SERVER", required=False)
    check_env_variable("OPENAI_API_KEY", required=False)
    check_env_variable("GEMINI_API_KEY", required=False)
    check_env_variable("TWILIO_ACCOUNT_SID", required=False)
    
    print()
    print("=" * 70)
    
    if all_ok:
        print("✓ SUCCESS: All required environment variables are configured!")
        print("\nYou can now start the application:")
        print("  Backend:  cd backend && python main.py")
        print("  Frontend: cd frontend && npm run dev")
        print("\nOr use Docker:")
        print("  docker-compose up")
    else:
        print("✗ FAILED: Some required environment variables are missing!")
        print("\nPlease update your .env file with the missing values.")
        print("Refer to .env.example for all available options.")
        sys.exit(1)
    
    print("=" * 70)

if __name__ == "__main__":
    main()
