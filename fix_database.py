#!/usr/bin/env python3
"""
Database Table Fix Script
Creates missing tables for the matching system
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import models
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from app import app, db
from models import User, Event, Membership, Resume, Match, UserInteraction

def fix_database_tables():
    """Create missing database tables"""
    
    print("🔧 Fixing database tables...")
    
    with app.app_context():
        try:
            # Create all tables (this will only create missing ones)
            db.create_all()
            print("✅ All database tables created successfully!")
            
            # Check which tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 Database now has {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   ✅ {table}")
            
            # Check if the problematic tables exist
            required_tables = ['user_interaction', 'match']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ Still missing: {missing_tables}")
                return False
            else:
                print("✅ All required tables are present!")
                return True
                
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

if __name__ == "__main__":
    success = fix_database_tables()
    if success:
        print("\n🎉 Database is now ready!")
        print("💡 You can now use all features including:")
        print("   - Smart Matching")
        print("   - View Matches")
        print("   - View Documents")
    else:
        print("\n❌ Database fix failed. Please check the error above.")
