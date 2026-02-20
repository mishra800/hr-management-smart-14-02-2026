#!/usr/bin/env python3
"""
Script to create default users in the database with properly hashed passwords
"""
import sys
sys.path.insert(0, '.')

from app.auth_utils import get_password_hash
from app.database import engine
from sqlalchemy import text

# Default users to create
DEFAULT_USERS = [
    {
        "email": "admin@company.com",
        "username": "admin",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin"
    },
    {
        "email": "hr@company.com",
        "username": "hr",
        "password": "hr123",
        "full_name": "HR Manager",
        "role": "hr"
    },
    {
        "email": "employee@company.com",
        "username": "employee",
        "password": "emp123",
        "full_name": "John Doe",
        "role": "employee"
    },
    {
        "email": "superadmin@company.com",
        "username": "superadmin",
        "password": "super123",
        "full_name": "Super Admin",
        "role": "super_admin"
    }
]

def create_users():
    """Create default users in the database"""
    print("=" * 60)
    print("Creating Default Users in Database")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Check if users already exist
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        
        if count > 0:
            print(f"\n⚠️  Database already has {count} user(s)")
            response = input("Do you want to delete existing users and recreate? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Aborted. No changes made.")
                return
            
            # Delete existing users
            conn.execute(text("DELETE FROM users"))
            conn.commit()
            print("✓ Existing users deleted")
        
        # Insert default users
        created_count = 0
        for user_data in DEFAULT_USERS:
            try:
                # Hash the password
                hashed_password = get_password_hash(user_data["password"])
                
                # Insert user
                query = text("""
                    INSERT INTO users (email, username, hashed_password, full_name, role, is_active, created_at, updated_at)
                    VALUES (:email, :username, :hashed_password, :full_name, :role, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """)
                
                conn.execute(query, {
                    "email": user_data["email"],
                    "username": user_data["username"],
                    "hashed_password": hashed_password,
                    "full_name": user_data["full_name"],
                    "role": user_data["role"]
                })
                
                print(f"✓ Created user: {user_data['email']} (password: {user_data['password']})")
                created_count += 1
                
            except Exception as e:
                print(f"✗ Failed to create {user_data['email']}: {e}")
        
        # Commit all changes
        conn.commit()
        
        # Verify users were created
        result = conn.execute(text("SELECT id, email, username, role FROM users ORDER BY id"))
        users = result.fetchall()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully created {created_count} users!")
        print("=" * 60)
        print("\nUsers in database:")
        print("-" * 60)
        for user in users:
            print(f"ID: {user[0]}, Email: {user[1]}, Username: {user[2]}, Role: {user[3]}")
        
        print("\n" + "=" * 60)
        print("Login Credentials:")
        print("=" * 60)
        for user_data in DEFAULT_USERS:
            print(f"\n{user_data['role'].upper()}:")
            print(f"  Email: {user_data['email']}")
            print(f"  Password: {user_data['password']}")
        
        print("\n" + "=" * 60)
        print("🎉 You can now login with any of these accounts!")
        print("=" * 60)

if __name__ == "__main__":
    try:
        create_users()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Database is running")
        print("2. Connection details in root .env file are correct")
        print("3. Users table exists in the database")
        sys.exit(1)
