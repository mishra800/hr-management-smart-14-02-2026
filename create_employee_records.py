#!/usr/bin/env python3
"""
Script to create employee records for existing users
"""
import sys
sys.path.insert(0, '.')

from app.database import engine
from sqlalchemy import text

def create_employee_records():
    """Create employee records for users who don't have them"""
    print("=" * 60)
    print("Creating Employee Records for Existing Users")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Get all users who don't have employee records
        query = text("""
            SELECT u.id, u.email, u.full_name, u.role
            FROM users u
            LEFT JOIN employees e ON u.id = e.user_id
            WHERE e.id IS NULL
            ORDER BY u.id
        """)
        
        users_without_employees = conn.execute(query).fetchall()
        
        if not users_without_employees:
            print("\n✅ All users already have employee records!")
            return
        
        print(f"\nFound {len(users_without_employees)} users without employee records")
        print("-" * 60)
        
        created_count = 0
        for user in users_without_employees:
            user_id, email, full_name, role = user
            
            # Split full name
            name_parts = (full_name or "User").split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Generate employee ID
            emp_count_query = text("SELECT COUNT(*) FROM employees")
            emp_count = conn.execute(emp_count_query).scalar()
            employee_id = f"EMP{str(emp_count + 1).zfill(3)}"
            
            # Determine department and position based on role
            role_mapping = {
                'admin': ('Administration', 'System Administrator'),
                'super_admin': ('Administration', 'Super Administrator'),
                'hr': ('Human Resources', 'HR Manager'),
                'manager': ('Management', 'Department Manager'),
                'employee': ('General', 'Employee'),
                'assets_team': ('IT & Assets', 'Assets Manager')
            }
            
            department, position = role_mapping.get(role, ('General', 'Employee'))
            
            try:
                # Insert employee record
                insert_query = text("""
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
                        50,
                        'office',
                        'completed',
                        'completed',
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    RETURNING id
                """)
                
                result = conn.execute(insert_query, {
                    "user_id": user_id,
                    "employee_id": employee_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "department": department,
                    "position": position
                })
                
                emp_id = result.fetchone()[0]
                print(f"✓ Created employee record for: {email}")
                print(f"  Employee ID: {employee_id}, Department: {department}, Position: {position}")
                created_count += 1
                
            except Exception as e:
                print(f"✗ Failed to create employee record for {email}: {e}")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully created {created_count} employee records!")
        print("=" * 60)
        
        # Verify all users now have employee records
        verify_query = text("""
            SELECT 
                u.id as user_id,
                u.email,
                u.role,
                e.id as employee_id,
                e.employee_id as emp_code,
                e.department,
                e.position
            FROM users u
            LEFT JOIN employees e ON u.id = e.user_id
            ORDER BY u.id
        """)
        
        all_users = conn.execute(verify_query).fetchall()
        
        print("\nAll Users and Their Employee Records:")
        print("-" * 60)
        for user in all_users:
            status = "✓" if user[3] else "✗"
            print(f"{status} {user[1]} ({user[2]})")
            if user[3]:
                print(f"   Employee: {user[4]} | {user[5]} | {user[6]}")
        
        print("\n" + "=" * 60)
        print("🎉 All users now have employee records!")
        print("=" * 60)

if __name__ == "__main__":
    try:
        create_employee_records()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
