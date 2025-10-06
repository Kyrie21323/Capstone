#!/usr/bin/env python3
"""
Simple Database Sync Script
Syncs the database file directly via Git
"""

import os
import subprocess
import shutil
from pathlib import Path

def sync_database():
    """Sync database file via Git"""
    
    project_root = Path(__file__).parent
    
    # Try multiple possible database locations
    possible_paths = [
        project_root / "instance" / "nfc_networking.db",  # Main location (from app.py)
        project_root / "src" / "instance" / "nfc_networking.db",
        project_root / "nfc_networking.db"
    ]
    
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = path
            break
    
    print("🔄 Syncing database...")
    
    if not db_path:
        print("❌ Database not found! Tried these locations:")
        for path in possible_paths:
            print(f"   - {path}")
        print("💡 Run the app first to create the database.")
        return False
    
    try:
        # Add database to git
        subprocess.run(['git', 'add', str(db_path)], check=True)
        
        # Commit
        subprocess.run(['git', 'commit', '-m', 'Sync database data'], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Database synced to GitHub!")
        print("💡 On other devices, run: git pull")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False

def pull_database():
    """Pull database from Git"""
    
    print("📥 Pulling database from Git...")
    
    try:
        subprocess.run(['git', 'pull'], check=True)
        print("✅ Database pulled from GitHub!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git pull failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Database Sync")
    print("=" * 15)
    print("1. Push database to GitHub")
    print("2. Pull database from GitHub")
    
    choice = input("Select option (1-2): ").strip()
    
    if choice == '1':
        sync_database()
    elif choice == '2':
        pull_database()
    else:
        print("❌ Invalid option")
