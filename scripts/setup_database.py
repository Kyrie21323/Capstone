#!/usr/bin/env python3
"""
Database Setup Script for NFC Networking App

Run this script to initialize/reset the database on any device.
Can also fix missing tables without resetting data.

Replaces: fix_database.py (use --fix flag instead)
"""

import os
import shutil
import argparse
from pathlib import Path
from script_helpers import setup_python_path, print_section, print_success, print_info, confirm_action

def setup_database(reset: bool = True):
    """
    Initialize or reset the database.
    
    Args:
        reset: If True, remove existing database and migrations
    """
    # Get project root
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    migrations_dir = project_root / "migrations"
    instance_dir = project_root / "instance"
    
    print_section("Database Setup", "🗃️")
    
    if reset:
        # Remove existing database
        db_file = instance_dir / "nfc_networking.db"
        if db_file.exists():
            print_info(f"Removing existing database: {db_file.name}")
            db_file.unlink()
        
        # Remove existing migrations completely
        if migrations_dir.exists():
            print_info(f"Removing existing migrations")
            shutil.rmtree(migrations_dir)
    
    # Create directories
    instance_dir.mkdir(exist_ok=True)
    migrations_dir.mkdir(exist_ok=True)
    
    # Change to src directory for flask commands
    os.chdir(src_dir)
    
    if reset:
        print_info("Initializing Flask-Migrate...")
        os.system("flask db init")
        
        print_info("Creating initial migration...")
        os.system('flask db migrate -m "Initial migration with all models"')
    
    print_info("Applying migrations...")
    os.system("flask db upgrade")
    
    print_success("Database setup complete!")
    print()
    print_info("Database Summary:")
    print("   - All tables created")
    print("   - Sample data will be created on first run")
    print("   - Ready for development")

def fix_database():
    """Create missing tables without resetting the database."""
    print_section("Fixing Database Tables", "🔧")
    
    # Setup path
    setup_python_path()
    
    from app import app, db
    from sqlalchemy import inspect
    
    with app.app_context():
        try:
            # Create all tables (this will only create missing ones)
            db.create_all()
            print_success("All database tables created successfully!")
            
            # Check which tables exist
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print()
            print_info(f"Database now has {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   ✅ {table}")
            
            return True
                
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Setup or fix the database',
        epilog='Examples:\n'
               '  %(prog)s                Setup fresh database (resets everything)\n'
               '  %(prog)s --fix          Create missing tables without reset\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--fix', action='store_true',
                       help='Fix missing tables without resetting database')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    if args.fix:
        # Fix missing tables
        success = fix_database()
        if success:
            print()
            print_success("Database is now ready!")
            print_info("You can now use all features")
        else:
            print()
            print("❌ Database fix failed. Please check the error above.")
    else:
        # Full reset
        if not args.yes:
            print()
            if not confirm_action("⚠️  This will RESET the database. Continue?", default=False):
                print("❌ Setup cancelled")
                return
        
        setup_database(reset=True)

if __name__ == "__main__":
    main()
