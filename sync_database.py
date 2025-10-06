#!/usr/bin/env python3
"""
Database Data Synchronization Script
Export/Import database data across devices
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def export_database_data():
    """Export all data from the database to JSON files"""
    
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
    
    if not db_path:
        print("❌ Database not found! Tried these locations:")
        for path in possible_paths:
            print(f"   - {path}")
        return False
    
    print("📤 Exporting database data...")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Export each table
        tables = ['user', 'event', 'membership', 'resume', 'match', 'user_interaction']
        export_data = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                export_data[table] = [dict(row) for row in rows]
                print(f"   ✅ {table}: {len(rows)} records")
            except sqlite3.OperationalError as e:
                print(f"   ⚠️  {table}: Table doesn't exist ({e})")
                export_data[table] = []
        
        # Save to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = project_root / f"database_export_{timestamp}.json"
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Data exported to: {export_file}")
        return str(export_file)
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False
    finally:
        conn.close()

def import_database_data(export_file):
    """Import data from JSON file to database"""
    
    if not os.path.exists(export_file):
        print(f"❌ Export file not found: {export_file}")
        return False
    
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
    
    if not db_path:
        print("❌ Database not found! Tried these locations:")
        for path in possible_paths:
            print(f"   - {path}")
        return False
    
    print(f"📥 Importing data from: {export_file}")
    
    try:
        # Load export data
        with open(export_file, 'r') as f:
            import_data = json.load(f)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing data (in correct order due to foreign keys)
        clear_order = ['user_interaction', 'match', 'resume', 'membership', 'event', 'user']
        for table in clear_order:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f"   🗑️  Cleared {table}")
            except sqlite3.OperationalError:
                pass  # Table doesn't exist
        
        # Import data (in correct order)
        import_order = ['user', 'event', 'membership', 'resume', 'match', 'user_interaction']
        
        for table in import_order:
            if table in import_data and import_data[table]:
                records = import_data[table]
                if records:
                    # Get column names
                    columns = list(records[0].keys())
                    placeholders = ', '.join(['?' for _ in columns])
                    columns_str = ', '.join(columns)
                    
                    # Insert records
                    for record in records:
                        values = [record.get(col) for col in columns]
                        cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})", values)
                    
                    print(f"   ✅ {table}: {len(records)} records imported")
        
        conn.commit()
        print("✅ Data import completed!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    finally:
        conn.close()

def list_export_files():
    """List available export files"""
    project_root = Path(__file__).parent
    export_files = list(project_root.glob("database_export_*.json"))
    
    if not export_files:
        print("📁 No export files found")
        return []
    
    print("📁 Available export files:")
    for i, file in enumerate(sorted(export_files, reverse=True), 1):
        size = file.stat().st_size
        modified = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"   {i}. {file.name} ({size} bytes, {modified.strftime('%Y-%m-%d %H:%M')})")
    
    return export_files

def main():
    """Main function with interactive menu"""
    
    print("🔄 Database Data Synchronization")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Export database data")
        print("2. Import database data")
        print("3. List export files")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            export_file = export_database_data()
            if export_file:
                print(f"\n💡 To sync on another device:")
                print(f"   1. Copy '{export_file}' to the other device")
                print(f"   2. Run: python sync_database.py")
                print(f"   3. Choose option 2 and select the file")
        
        elif choice == '2':
            export_files = list_export_files()
            if export_files:
                try:
                    file_num = int(input("Select file number: ")) - 1
                    if 0 <= file_num < len(export_files):
                        import_database_data(str(export_files[file_num]))
                    else:
                        print("❌ Invalid file number")
                except ValueError:
                    print("❌ Please enter a valid number")
        
        elif choice == '3':
            list_export_files()
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
