#!/usr/bin/env python3
"""
Database Finder Script
Helps locate the database file
"""

import os
from pathlib import Path

def find_database():
    """Find the database file"""
    
    project_root = Path(__file__).parent
    
    # Search for database files
    possible_names = ["nfc_networking.db", "*.db", "*.sqlite", "*.sqlite3"]
    found_files = []
    
    print("🔍 Searching for database files...")
    
    # Search in common locations
    search_paths = [
        project_root,
        project_root / "src",
        project_root / "src" / "instance",
        project_root / "instance"
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            for name_pattern in possible_names:
                if "*" in name_pattern:
                    # Use glob for wildcard patterns
                    files = list(search_path.glob(name_pattern))
                else:
                    # Check specific file
                    file_path = search_path / name_pattern
                    files = [file_path] if file_path.exists() else []
                
                for file_path in files:
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        # Avoid duplicates by checking if path already exists
                        if not any(existing_path == file_path for existing_path, _ in found_files):
                            found_files.append((file_path, size))
    
    if found_files:
        print(f"✅ Found {len(found_files)} database file(s):")
        for file_path, size in found_files:
            print(f"   📁 {file_path} ({size} bytes)")
        
        # Find the most likely candidate (largest file with nfc_networking in name)
        best_candidate = None
        for file_path, size in found_files:
            if "nfc_networking" in file_path.name:
                best_candidate = file_path
                break
        
        if not best_candidate and found_files:
            # If no nfc_networking file, pick the largest
            best_candidate = max(found_files, key=lambda x: x[1])[0]
        
        print(f"\n🎯 Recommended database: {best_candidate}")
        return str(best_candidate)
    else:
        print("❌ No database files found!")
        print("\n💡 Make sure to run the app first to create the database.")
        return None

if __name__ == "__main__":
    find_database()
