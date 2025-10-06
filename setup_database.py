#!/usr/bin/env python3
"""
Database Setup Script for NFC Networking App
Run this script to initialize/reset the database on any device
"""

import os
import sys
import shutil
from pathlib import Path

def setup_database():
    """Initialize or reset the database"""
    
    # Get project root
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    migrations_dir = project_root / "migrations"
    instance_dir = src_dir / "instance"
    
    print("🗃️  Setting up database...")
    
    # Remove existing database
    db_file = instance_dir / "nfc_networking.db"
    if db_file.exists():
        print(f"   Removing existing database: {db_file}")
        db_file.unlink()
    
    # Remove existing migrations
    versions_dir = migrations_dir / "versions"
    if versions_dir.exists():
        print(f"   Removing existing migrations: {versions_dir}")
        shutil.rmtree(versions_dir)
    
    # Create directories
    instance_dir.mkdir(exist_ok=True)
    versions_dir.mkdir(exist_ok=True)
    
    # Change to src directory for flask commands
    os.chdir(src_dir)
    
    print("   Initializing Flask-Migrate...")
    os.system("flask db init")
    
    print("   Creating initial migration...")
    os.system("flask db migrate -m 'Initial migration with all models'")
    
    print("   Applying migration...")
    os.system("flask db upgrade")
    
    print("✅ Database setup complete!")
    print("\n📊 Database Summary:")
    print("   - All tables created")
    print("   - Sample data will be created on first run")
    print("   - Ready for development")

if __name__ == "__main__":
    setup_database()
