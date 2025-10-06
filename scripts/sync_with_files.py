#!/usr/bin/env python3
"""
File Sync Script
Syncs uploaded documents along with database data
"""

import os
import shutil
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def export_with_files():
    """Export database data AND upload files"""
    
    project_root = Path(__file__).parent.parent
    
    # Find database
    possible_paths = [
        project_root / "instance" / "nfc_networking.db",
        project_root / "src" / "instance" / "nfc_networking.db",
        project_root / "nfc_networking.db"
    ]
    
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("❌ Database not found!")
        return False
    
    print("📤 Exporting database data and files...")
    
    try:
        # Export database data
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        tables = ['user', 'event', 'membership', 'resume', 'match', 'user_interaction']
        export_data = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                export_data[table] = [dict(row) for row in rows]
                print(f"   ✅ {table}: {len(rows)} records")
            except sqlalchemy.OperationalError:
                export_data[table] = []
        
        # Save database export to exports directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exports_dir = project_root / "exports"
        exports_dir.mkdir(exist_ok=True)  # Create exports directory if it doesn't exist
        export_file = exports_dir / f"database_export_{timestamp}.json"
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Database exported to: {export_file}")
        
        # Export uploaded files to exports directory
        uploads_dir = project_root / "uploads"
        if uploads_dir.exists():
            files_export_dir = exports_dir / f"files_export_{timestamp}"
            shutil.copytree(uploads_dir, files_export_dir)
            print(f"✅ Files exported to: {files_export_dir}")
        else:
            print("⚠️  No uploads directory found")
            files_export_dir = None
        
        conn.close()
        
        print(f"\n💡 To sync on another device:")
        print(f"   1. Copy '{export_file.name}' to the other device")
        if files_export_dir:
            print(f"   2. Copy '{files_export_dir.name}' folder to the other device")
        print(f"   3. Run: python sync_with_files.py")
        
        return str(export_file)
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

def import_with_files():
    """Import database data AND upload files"""
    
    project_root = Path(__file__).parent.parent
    
    # List available exports (check both root and exports directory)
    export_files = list(project_root.glob("database_export_*.json"))
    exports_dir = project_root / "exports"
    if exports_dir.exists():
        export_files.extend(list(exports_dir.glob("database_export_*.json")))
    
    if not export_files:
        print("❌ No export files found!")
        print("💡 Make sure you have copied the export files to this device")
        return False
    
    print("📁 Available exports:")
    for i, file in enumerate(sorted(export_files, reverse=True), 1):
        size = file.stat().st_size
        modified = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"   {i}. {file.name} ({size} bytes, {modified.strftime('%Y-%m-%d %H:%M')})")
    
    try:
        file_num = int(input("Select export file number: ")) - 1
        if not (0 <= file_num < len(export_files)):
            print("❌ Invalid file number")
            return False
        
        export_file = export_files[file_num]
        
        # Find corresponding files export (check both root and exports directory)
        timestamp = export_file.stem.split('_')[-2] + '_' + export_file.stem.split('_')[-1]
        files_export_dir = project_root / f"files_export_{timestamp}"
        exports_files_dir = project_root / "exports" / f"files_export_{timestamp}"
        
        # Use exports directory if it exists, otherwise root
        if exports_files_dir.exists():
            files_export_dir = exports_files_dir
        
        print(f"📥 Importing from: {export_file.name}")
        
        # Import database data
        with open(export_file, 'r') as f:
            import_data = json.load(f)
        
        # Find database
        possible_paths = [
            project_root / "instance" / "nfc_networking.db",
            project_root / "src" / "instance" / "nfc_networking.db",
            project_root / "nfc_networking.db"
        ]
        
        db_path = None
        for path in possible_paths:
            if path.exists():
                db_path = path
                break
        
        if not db_path:
            print("❌ Database not found!")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        clear_order = ['user_interaction', 'match', 'resume', 'membership', 'event', 'user']
        for table in clear_order:
            try:
                cursor.execute(f"DELETE FROM {table}")
            except sqlalchemy.OperationalError:
                pass
        
        # Import data
        import_order = ['user', 'event', 'membership', 'resume', 'match', 'user_interaction']
        
        for table in import_order:
            if table in import_data and import_data[table]:
                records = import_data[table]
                if records:
                    columns = list(records[0].keys())
                    placeholders = ', '.join(['?' for _ in columns])
                    columns_str = ', '.join(columns)
                    
                    for record in records:
                        values = [record.get(col) for col in columns]
                        cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})", values)
                    
                    print(f"   ✅ {table}: {len(records)} records imported")
        
        conn.commit()
        conn.close()
        
        # Import files
        if files_export_dir.exists():
            uploads_dir = project_root / "uploads"
            if uploads_dir.exists():
                shutil.rmtree(uploads_dir)
            shutil.copytree(files_export_dir, uploads_dir)
            print(f"✅ Files imported to: {uploads_dir}")
        else:
            print("⚠️  No files export found - documents may not be available")
        
        print("✅ Import completed!")
        return True
        
    except ValueError:
        print("❌ Please enter a valid number")
        return False
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    """Main function with interactive menu"""
    
    print("🔄 Database + Files Synchronization")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Export database + files")
        print("2. Import database + files")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            export_with_files()
        
        elif choice == '2':
            import_with_files()
        
        elif choice == '3':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
