from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_login import current_user
import os
from models import Resume

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            flash('Admin access required!', 'error')
            # Redirect to user dashboard if logged in, else login
            if current_user.is_authenticated:
                return redirect(url_for('user.dashboard'))
            else:
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def cleanup_orphaned_files():
    """Clean up files that exist in filesystem but not in database"""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        orphaned_files = []
        
        # Walk through all files in uploads directory
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip .DS_Store and other system files
                if file.startswith('.'):
                    continue
                    
                relative_path = os.path.relpath(file_path, upload_folder)
                
                # Extract event_id/user_id/whatever directory part and filename from path
                # Note: Original code assumed first part is event_id, but upload path uses user_id.
                # Logic: We check if the file exists in Resume table.
                path_parts = relative_path.split(os.sep)
                if len(path_parts) >= 2:
                    folder_id = path_parts[0] # Could be event_id or user_id depending on code version
                    filename = path_parts[1]
                    
                    # Check if this file exists in database 
                    # We try to find it by filename. 
                    # If paths are inconsistent, filename uniqueness is our best bet.
                    # Filenames are: {user_id}_{event_id}_{timestamp}_{original}
                    
                    resume = Resume.query.filter_by(filename=filename).first()
                    
                    if not resume:
                        orphaned_files.append(file_path)
                elif len(path_parts) == 1:
                     # Files in root of uploads? likely orphaned
                     orphaned_files.append(file_path)
                     
        # Delete orphaned files
        for file_path in orphaned_files:
            try:
                os.remove(file_path)
            except Exception as e:
                pass  # Log error but don't fail the operation
        
        return len(orphaned_files)
        
    except Exception as e:
        # print(f"Cleanup error: {e}")
        return 0
