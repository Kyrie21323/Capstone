#!/usr/bin/env python3
"""
Simple Database Sync via Git
Syncs the actual database file across devices
"""

import os
import subprocess
import shutil
from pathlib import Path

def sync_database_via_git():
    """Sync database file via Git"""
    
    project_root = Path(__file__).parent
    db_path = project_root / "src" / "instance" / "nfc_networking.db"
    
    print("🔄 Syncing database via Git...")
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Not in a Git repository!")
            return False
        
        # Temporarily remove database from .gitignore
        gitignore_path = project_root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
            
            # Remove database ignore lines
            lines = content.split('\n')
            filtered_lines = [line for line in lines if 'nfc_networking.db' not in line]
            
            with open(gitignore_path, 'w') as f:
                f.write('\n'.join(filtered_lines))
        
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
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        return False
    finally:
        # Restore .gitignore
        if gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.write(content)

def pull_database_from_git():
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
    print("🔄 Git Database Sync")
    print("=" * 20)
    print("1. Push database to GitHub")
    print("2. Pull database from GitHub")
    
    choice = input("Select option (1-2): ").strip()
    
    if choice == '1':
        sync_database_via_git()
    elif choice == '2':
        pull_database_from_git()
    else:
        print("❌ Invalid option")
