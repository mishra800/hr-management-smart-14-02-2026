#!/usr/bin/env python3
"""
Pre-startup check script to verify all requirements are met
"""
import os
import sys
from dotenv import load_dotenv

print("=" * 70)
print("Backend Startup Verification")
print("=" * 70)

# Load .env file
print("\n[1/4] Loading environment variables...")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

if not DATABASE_URL:
    print("✗ FAILED: DATABASE_URL not found in environment")
    print("\nPlease ensure root .env file exists with:")
    print("DATABASE_URL=postgresql://user:password@host:port/database")
    sys.exit(1)
else:
    # Mask password in output
    safe_url = DATABASE_URL
    if '@' in DATABASE_URL and ':' in DATABASE_URL:
        parts = DATABASE_URL.split('@')
        creds = parts[0].split(':')
        if len(creds) >= 3:
            safe_url = f"{creds[0]}:{creds[1]}:***@{parts[1]}"
    print(f"✓ DATABASE_URL loaded: {safe_url}")

if not SECRET_KEY:
    print("⚠ WARNING: SECRET_KEY not set (using default - not secure for production)")
else:
    print(f"✓ SECRET_KEY loaded: {SECRET_KEY[:10]}...")

# Test database connection
print("\n[2/4] Testing database connection...")
try:
    from app.database import test_db_connection
    if test_db_connection():
        print("✓ Database connection successful")
    else:
        print("✗ FAILED: Cannot connect to database")
        print("\nPlease verify:")
        print("1. PostgreSQL server is running")
        print("2. Database credentials are correct")
        print("3. Database exists")
        print("4. Network connectivity to database server")
        sys.exit(1)
except Exception as e:
    print(f"✗ FAILED: Database connection error: {e}")
    sys.exit(1)

# Check if routers can be imported
print("\n[3/4] Checking router imports...")
failed_routers = []
core_routers = ['auth', 'users', 'employees', 'attendance', 'leave']

for router_name in core_routers:
    try:
        __import__(f'app.routers.{router_name}')
        print(f"  ✓ {router_name}")
    except Exception as e:
        print(f"  ✗ {router_name}: {str(e)[:50]}")
        failed_routers.append(router_name)

if failed_routers:
    print(f"\n⚠ WARNING: {len(failed_routers)} core routers failed to import")
    print("The server will start but some endpoints may not be available")
else:
    print("\n✓ All core routers imported successfully")

# Check port availability
print("\n[4/4] Checking port availability...")
import socket
port = 8000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('0.0.0.0', port))
sock.close()

if result == 0:
    print(f"⚠ WARNING: Port {port} is already in use")
    print("You may need to stop the existing process or use a different port")
else:
    print(f"✓ Port {port} is available")

print("\n" + "=" * 70)
print("✅ Startup verification complete!")
print("=" * 70)
print("\nYou can now start the server with:")
print("  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
print("\nOr use the startup script:")
print("  start-backend-network.cmd")
print("=" * 70)
