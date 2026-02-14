"""
Fix Models Script
Ensures all database models are properly defined
"""

from app.database import Base, engine
from sqlalchemy import inspect

def fix_models():
    print("=" * 60)
    print("🔧 Fixing Database Models")
    print("=" * 60)
    
    try:
        # Import all models
        from app import models_orm
        
        print("\n✅ All models imported successfully")
        
        # Create all tables
        print("\n📝 Creating/updating tables...")
        Base.metadata.create_all(bind=engine)
        
        # List all tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ Database has {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   • {table}")
        
        print("\n" + "=" * 60)
        print("✅ Models fixed successfully!")
        print("=" * 60)
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = fix_models()
    exit(0 if success else 1)
