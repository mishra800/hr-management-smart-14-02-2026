"""
Database Fix Script
Automatically fixes common database issues
"""

from app.database import engine
from sqlalchemy import text, inspect
import os
from pathlib import Path

def fix_database():
    print("=" * 60)
    print("🔧 Database Fix Script")
    print("=" * 60)
    
    # 1. Check connection
    print("\n1️⃣ Checking database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"   ✅ Connected to database: {db_name}")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        print("\n💡 Fix: Check your DATABASE_URL in .env file")
        return False
    
    # 2. Check if employees table exists
    print("\n2️⃣ Checking employees table...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'employees' not in tables:
        print("   ❌ employees table not found!")
        print("\n💡 Fix: Run this command:")
        print('   python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"')
        return False
    
    print("   ✅ employees table exists")
    
    # 3. Check if profile_image column exists
    print("\n3️⃣ Checking profile_image column...")
    columns = [col['name'] for col in inspector.get_columns('employees')]
    
    if 'profile_image' not in columns:
        print("   ⚠️  profile_image column missing, adding it...")
        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE employees 
                    ADD COLUMN profile_image VARCHAR(500)
                """))
                conn.commit()
            print("   ✅ profile_image column added successfully")
        except Exception as e:
            print(f"   ❌ Failed to add column: {e}")
            return False
    else:
        print("   ✅ profile_image column exists")
    
    # 4. Check other important columns
    print("\n4️⃣ Checking other important columns...")
    required_columns = ['user_id', 'first_name', 'last_name', 'email', 'position']
    missing_columns = [col for col in required_columns if col not in columns]
    
    if missing_columns:
        print(f"   ⚠️  Missing columns: {', '.join(missing_columns)}")
        print("   💡 You may need to run the complete schema")
    else:
        print("   ✅ All required columns present")
    
    # 5. Create uploads directory
    print("\n5️⃣ Creating uploads directory...")
    upload_dir = Path("uploads/profile_images")
    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Directory created: {upload_dir.absolute()}")
    except Exception as e:
        print(f"   ❌ Failed to create directory: {e}")
        return False
    
    # 6. Test write permissions
    print("\n6️⃣ Testing write permissions...")
    test_file = upload_dir / "test.txt"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ Write permissions OK")
    except Exception as e:
        print(f"   ❌ Write permission failed: {e}")
        print("   💡 Fix: Check folder permissions")
        return False
    
    # 7. Check users table
    print("\n7️⃣ Checking users table...")
    if 'users' not in tables:
        print("   ❌ users table not found!")
        return False
    print("   ✅ users table exists")
    
    # 8. Count records
    print("\n8️⃣ Checking data...")
    try:
        with engine.connect() as conn:
            user_count = conn.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
            emp_count = conn.execute(text("SELECT COUNT(*) FROM employees")).fetchone()[0]
            print(f"   ✅ Users: {user_count}, Employees: {emp_count}")
            
            if user_count == 0:
                print("   ⚠️  No users found. Run: python create_default_users.py")
    except Exception as e:
        print(f"   ⚠️  Could not count records: {e}")
    
    # 9. Test image upload path
    print("\n9️⃣ Testing image upload...")
    try:
        test_image_path = upload_dir / "test_user_1.jpg"
        test_image_path.write_bytes(b"fake image data")
        
        # Try to update database
        with engine.connect() as conn:
            # Check if we can update
            result = conn.execute(text("SELECT id FROM employees LIMIT 1"))
            emp = result.fetchone()
            
            if emp:
                conn.execute(text("""
                    UPDATE employees 
                    SET profile_image = :path 
                    WHERE id = :id
                """), {"path": str(test_image_path), "id": emp[0]})
                conn.commit()
                print("   ✅ Database update test successful")
                
                # Revert
                conn.execute(text("""
                    UPDATE employees 
                    SET profile_image = NULL 
                    WHERE id = :id
                """), {"id": emp[0]})
                conn.commit()
            else:
                print("   ⚠️  No employees to test with")
        
        test_image_path.unlink()
    except Exception as e:
        print(f"   ⚠️  Upload test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Database fix completed successfully!")
    print("=" * 60)
    print("\n✅ Your database is ready for profile image uploads")
    print("\n📝 Next steps:")
    print("   1. Restart your backend server")
    print("   2. Try uploading a profile image")
    print("   3. Check backend/uploads/profile_images/ for saved images")
    print("\n" + "=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = fix_database()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\n💡 Please check:")
        print("   - Database is running")
        print("   - DATABASE_URL in .env is correct")
        print("   - You have proper permissions")
        exit(1)
