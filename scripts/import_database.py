#!/usr/bin/env python3
"""
Database Import/Export Tool

This script handles database import and export operations:
- Export database to JSON with files
- Import database from JSON exports
- Auto-detect latest export
- Progress tracking and validation

Replaces: sync_with_files.py (deprecated)
"""

import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from script_helpers import (
    setup_python_path, get_project_root, 
    print_section, print_success, print_error, print_warning, print_info,
    confirm_action
)

# Setup Python path
PROJECT_ROOT = setup_python_path()

from app import app, db
from models import User, Event, Membership, Resume, Match, UserInteraction


def export_database(exports_dir: Path = None, include_files: bool = True) -> bool:
    """
    Export database to JSON with optional file backup.
    
    Args:
        exports_dir: Directory to save exports (default: PROJECT_ROOT/exports)
        include_files: Whether to include uploaded files
        
    Returns:
        bool: True if successful, False otherwise
    """
    if exports_dir is None:
        exports_dir = get_project_root() / 'exports'
    
    exports_dir.mkdir(exist_ok=True)
    
    print_section("Exporting Database", "📤")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with app.app_context():
            # Export data from all tables
            export_data = {}
            
            # Users
            users = User.query.all()
            export_data['user'] = [
                {
                    'id': u.id,
                    'name': u.name,
                    'email': u.email,
                    'password_hash': u.password_hash,
                    'is_admin': int(u.is_admin),
                    'created_at': u.created_at.isoformat() if u.created_at else None
                }
                for u in users
            ]
            print_success(f"Exported {len(users)} users")
            
            # Events
            events = Event.query.all()
            export_data['event'] = [
                {
                    'id': e.id,
                    'name': e.name,
                    'code': e.code,
                    'description': e.description,
                    'start_date': e.start_date.isoformat() if e.start_date else None,
                    'end_date': e.end_date.isoformat() if e.end_date else None,
                    'created_at': e.created_at.isoformat() if e.created_at else None
                }
                for e in events
            ]
            print_success(f"Exported {len(events)} events")
            
            # Memberships
            memberships = Membership.query.all()
            export_data['membership'] = [
                {
                    'id': m.id,
                    'user_id': m.user_id,
                    'event_id': m.event_id,
                    'keywords': m.keywords,
                    'joined_at': m.joined_at.isoformat() if m.joined_at else None
                }
                for m in memberships
            ]
            print_success(f"Exported {len(memberships)} memberships")
            
            # Resumes
            resumes = Resume.query.all()
            export_data['resume'] = [
                {
                    'id': r.id,
                    'user_id': r.user_id,
                    'event_id': r.event_id,
                    'filename': r.filename,
                    'original_name': r.original_name,
                    'mime_type': r.mime_type,
                    'file_size': r.file_size,
                    'uploaded_at': r.uploaded_at.isoformat() if r.uploaded_at else None
                }
                for r in resumes
            ]
            print_success(f"Exported {len(resumes)} resumes")
            
            # Matches
            matches = Match.query.all()
            export_data['match'] = [
                {
                    'id': m.id,
                    'user1_id': m.user1_id,
                    'user2_id': m.user2_id,
                    'event_id': m.event_id,
                    'matched_at': m.matched_at.isoformat() if m.matched_at else None,
                    'is_active': int(m.is_active)
                }
                for m in matches
            ]
            print_success(f"Exported {len(matches)} matches")
            
            # User Interactions
            interactions = UserInteraction.query.all()
            export_data['user_interaction'] = [
                {
                    'id': i.id,
                    'user_id': i.user_id,
                    'target_user_id': i.target_user_id,
                    'event_id': i.event_id,
                    'action': i.action,
                    'created_at': i.created_at.isoformat() if i.created_at else None
                }
                for i in interactions
            ]
            print_success(f"Exported {len(interactions)} interactions")
        
        # Save JSON export
        export_file = exports_dir / f"database_export_{timestamp}.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        print_success(f"Saved to: {export_file.name}")
        
        # Export files if requested
        if include_files:
            uploads_dir = get_project_root() / 'uploads'
            if uploads_dir.exists():
                files_export_dir = exports_dir / f"files_export_{timestamp}"
                shutil.copytree(uploads_dir, files_export_dir)
                print_success(f"Files saved to: {files_export_dir.name}")
            else:
                print_warning("No uploads directory found")
        
        print_info(f"Export completed: {export_file.name}")
        return True
        
    except Exception as e:
        print_error(f"Export failed: {e}")
        return False


def find_latest_export(exports_dir: Path = None):
    """
    Find the most recent export in the exports directory.
    
    Args:
        exports_dir: Directory to search (default: PROJECT_ROOT/exports)
        
    Returns:
        tuple: (json_path, files_dir) or (None, None) if not found
    """
    if exports_dir is None:
        exports_dir = get_project_root() / 'exports'
    
    if not exports_dir.exists():
        print_error("exports directory not found!")
        return None, None
    
    # Find all JSON export files
    json_files = list(exports_dir.glob('database_export_*.json'))
    if not json_files:
        print_error("No export files found!")
        return None, None
    
    # Sort by name (which includes timestamp) and get the latest
    latest_json = sorted(json_files)[-1]
    
    # Find corresponding files export directory
    export_name = latest_json.stem  # e.g., 'database_export_20251007_004333'
    files_dir = exports_dir / f"files_{export_name.replace('database_', '')}"
    
    print_info(f"Found export: {latest_json.name}")
    if files_dir.exists():
        print_info(f"Found files: {files_dir.name}")
    else:
        print_warning("No files directory found for this export")
        files_dir = None
    
    return latest_json, files_dir


def clear_database():
    """Clear all data from the database."""
    print_section("Clearing Database", "🗑️")
    
    with app.app_context():
        # Delete in reverse order of dependencies
        UserInteraction.query.delete()
        Match.query.delete()
        Resume.query.delete()
        Membership.query.delete()
        Event.query.delete()
        User.query.delete()
        db.session.commit()
    
    print_success("Database cleared")


def import_data(json_path: Path, files_dir: Path = None):
    """
    Import data from JSON export.
    
    Args:
        json_path: Path to JSON export file
        files_dir: Path to files export directory
    """
    print_section("Importing Data", "📥")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    with app.app_context():
        # Import users
        if 'user' in data and data['user']:
            print(f"👥 Importing {len(data['user'])} users...")
            for user_data in data['user']:
                user = User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    is_admin=bool(user_data['is_admin'])
                )
                db.session.add(user)
            db.session.commit()
            print_success(f"Imported {len(data['user'])} users")
        
        # Import events
        if 'event' in data and data['event']:
            print(f"📅 Importing {len(data['event'])} events...")
            for event_data in data['event']:
                event = Event(
                    id=event_data['id'],
                    name=event_data['name'],
                    code=event_data['code'],
                    description=event_data.get('description'),
                    start_date=datetime.fromisoformat(event_data['start_date']) if event_data.get('start_date') else None,
                    end_date=datetime.fromisoformat(event_data['end_date']) if event_data.get('end_date') else None
                )
                db.session.add(event)
            db.session.commit()
            print_success(f"Imported {len(data['event'])} events")
        
        # Import memberships
        if 'membership' in data and data['membership']:
            print(f"🎫 Importing {len(data['membership'])} memberships...")
            for membership_data in data['membership']:
                membership = Membership(
                    id=membership_data['id'],
                    user_id=membership_data['user_id'],
                    event_id=membership_data['event_id'],
                    keywords=membership_data.get('keywords'),
                    joined_at=datetime.fromisoformat(membership_data['joined_at']) if membership_data.get('joined_at') else None
                )
                db.session.add(membership)
            db.session.commit()
            print_success(f"Imported {len(data['membership'])} memberships")
        
        # Import resumes
        if 'resume' in data and data['resume']:
            print(f"📄 Importing {len(data['resume'])} resume records...")
            for resume_data in data['resume']:
                resume = Resume(
                    id=resume_data['id'],
                    user_id=resume_data['user_id'],
                    event_id=resume_data['event_id'],
                    filename=resume_data['filename'],
                    original_name=resume_data['original_name'],
                    mime_type=resume_data['mime_type'],
                    file_size=resume_data['file_size'],
                    uploaded_at=datetime.fromisoformat(resume_data['uploaded_at']) if resume_data.get('uploaded_at') else None
                )
                db.session.add(resume)
            db.session.commit()
            print_success(f"Imported {len(data['resume'])} resume records")
        
        # Import matches
        if 'match' in data and data['match']:
            print(f"💑 Importing {len(data['match'])} matches...")
            for match_data in data['match']:
                match = Match(
                    id=match_data['id'],
                    user1_id=match_data['user1_id'],
                    user2_id=match_data['user2_id'],
                    event_id=match_data['event_id'],
                    matched_at=datetime.fromisoformat(match_data['matched_at']) if match_data.get('matched_at') else None,
                    is_active=bool(match_data['is_active'])
                )
                db.session.add(match)
            db.session.commit()
            print_success(f"Imported {len(data['match'])} matches")
        
        # Import user interactions
        if 'user_interaction' in data and data['user_interaction']:
            print(f"👆 Importing {len(data['user_interaction'])} interactions...")
            for interaction_data in data['user_interaction']:
                interaction = UserInteraction(
                    id=interaction_data['id'],
                    user_id=interaction_data['user_id'],
                    target_user_id=interaction_data['target_user_id'],
                    event_id=interaction_data['event_id'],
                    action=interaction_data['action'],
                    created_at=datetime.fromisoformat(interaction_data['created_at']) if interaction_data.get('created_at') else None
                )
                db.session.add(interaction)
            db.session.commit()
            print_success(f"Imported {len(data['user_interaction'])} interactions")
        
        # Import resume files
        if files_dir and files_dir.exists() and 'resume' in data and data['resume']:
            uploads_dir = get_project_root() / 'uploads'
            uploads_dir.mkdir(exist_ok=True)
            
            print(f"📁 Copying resume files...")
            copied_count = 0
            
            for resume_data in data['resume']:
                user_id = resume_data['user_id']
                filename = resume_data['filename']
                
                # Source file in export
                source_file = files_dir / str(user_id) / filename
                
                # Destination in uploads
                dest_dir = uploads_dir / str(user_id)
                dest_dir.mkdir(exist_ok=True)
                dest_file = dest_dir / filename
                
                if source_file.exists():
                    shutil.copy2(source_file, dest_file)
                    copied_count += 1
                else:
                    print_warning(f"File not found: {source_file}")
            
            print_success(f"Copied {copied_count} resume files")


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Import/Export database with files',
        epilog='Examples:\n'
               '  %(prog)s --export                Export current database\n'
               '  %(prog)s --import                Import latest export\n'
               '  %(prog)s --export --no-files     Export without files\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--export', action='store_true',
                       help='Export database to JSON')
    parser.add_argument('--import', dest='import_db', action='store_true',
                       help='Import database from latest export')
    parser.add_argument('--no-files', action='store_true',
                       help='Skip file backup/restore')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    if args.export:
        # Export database
        export_database(include_files=not args.no_files)
    
    elif args.import_db:
        # Import database
        print_section("Database Import Tool", "🔄")
        
        # Find latest export
        json_path, files_dir = find_latest_export()
        if not json_path:
            return
        
        # Confirm with user
        if not args.yes:
            print()
            print_warning("This will replace ALL data in the current database!")
            if not confirm_action("Continue?", default=False):
                print_error("Import cancelled")
                return
        
        # Clear and import
        clear_database()
        import_data(json_path, files_dir if not args.no_files else None)
        
        print()
        print_section("Import Completed Successfully!", "✅")
    
    else:
        # No action specified
        parser.print_help()


if __name__ == '__main__':
    main()
