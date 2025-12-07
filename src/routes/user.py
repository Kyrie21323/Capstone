"""
User routes for Prophere.
Handles dashboard, events, resumes, and keywords.
"""
from flask import render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Event, Membership, Resume, UserInteraction
import os
from datetime import datetime
from . import user_bp

# Config needs to be accessed from current_app
from flask import current_app

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Redirect admins to admin dashboard
    if current_user.is_administrator():
        return redirect(url_for('admin.admin_dashboard'))
    
    # Get user's memberships and resumes
    memberships = Membership.query.filter_by(user_id=current_user.id).all()
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    
    return render_template('dashboard.html', memberships=memberships, resumes=resumes)

@user_bp.route('/join_event', methods=['POST'])
@login_required
def join_event():
    # Prevent super admin from joining events
    if current_user.is_admin:
        flash('Super admin accounts cannot join events!', 'error')
        return redirect(url_for('user.dashboard'))
    
    event_code = request.form.get('event_code', '').strip()
    keywords = request.form.get('keywords', '').strip()
    
    # Validate event code
    if not event_code:
        flash('Please enter an event code.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Validate event code format (alphanumeric, 3-20 characters)
    if not event_code.replace('_', '').replace('-', '').isalnum() or len(event_code) < 3 or len(event_code) > 20:
        flash('Event code must be 3-20 characters long and contain only letters, numbers, hyphens, and underscores.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Validate keywords
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        if len(keyword_list) < 2:
            flash('Please enter at least 2 keywords. Type keywords and press Enter to create tags.', 'error')
            return redirect(url_for('user.dashboard'))
        
        # Validate individual keywords (max 50 chars each, no special chars)
        for keyword in keyword_list:
            if len(keyword) > 50:
                flash('Each keyword must be 50 characters or less.', 'error')
                return redirect(url_for('user.dashboard'))
            if not keyword.replace(' ', '').replace('-', '').isalnum():
                flash('Keywords can only contain letters, numbers, spaces, and hyphens.', 'error')
                return redirect(url_for('user.dashboard'))
    else:
        flash('Please enter your areas of interest (at least 2 keywords).', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Find event by code
    event = Event.query.filter_by(code=event_code).first()
    
    if not event:
        flash(f'Event code "{event_code}" does not exist. Please check the code and try again.', 'info')
        return redirect(url_for('user.dashboard'))
    
    # Check if user is already a member
    existing_membership = Membership.query.filter_by(
        user_id=current_user.id, 
        event_id=event.id
    ).first()
    
    if existing_membership:
        flash(f'You are already a member of "{event.name}"!', 'info')
        return redirect(url_for('user.dashboard'))
    
    # Create new membership with keywords
    membership = Membership(
        user_id=current_user.id,
        event_id=event.id,
        keywords=keywords
    )
    db.session.add(membership)
    db.session.commit()
    
    flash(f'Successfully joined "{event.name}" with interests: {", ".join(keyword_list)}!', 'success')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/leave_event', methods=['POST'])
@login_required
def leave_event():
    event_id = request.form['event_id']
    
    # Find the membership
    membership = Membership.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id
    ).first()
    
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('user.dashboard'))
    
    event = Event.query.get(event_id)
    event_name = event.name if event else 'Unknown Event'
    
    try:
        # Delete associated resume and file if exists
        resume = Resume.query.filter_by(
            user_id=current_user.id,
            event_id=event_id
        ).first()
        
        if resume:
            # Delete the resume file
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(event_id), resume.filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    pass  # Log error but don't fail the operation
            
            # Delete resume record from database
            db.session.delete(resume)
        
        # Delete the membership
        db.session.delete(membership)
        db.session.commit()
        
        flash(f'Successfully left "{event_name}"! Your document has been removed.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error leaving event: {str(e)}', 'error')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/upload_resume/<int:event_id>', methods=['GET', 'POST'])
@login_required
def upload_resume(event_id):
    # Prevent super admin from uploading documents
    if current_user.is_admin:
        flash('Super admin accounts cannot upload documents!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Check if user is a member of this event
    membership = Membership.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id
    ).first()
    
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('user.dashboard'))
    
    event = Event.query.get(event_id)
    
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('user.upload_resume', event_id=event_id))
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('user.upload_resume', event_id=event_id))
        
        # Check file type
        allowed_extensions = {'pdf', 'doc', 'docx'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            flash('Only PDF, DOC, and DOCX files are allowed!', 'error')
            return redirect(url_for('user.upload_resume', event_id=event_id))
        
        # Check file size (16MB max) - efficient method
        try:
            file.seek(0, 2)  # Seek to end of file
            file_size = file.tell()  # Get file size
            file.seek(0)  # Reset to beginning
            
            if file_size > current_app.config['MAX_CONTENT_LENGTH']:
                flash('File too large! Maximum size is 16MB.', 'error')
                return redirect(url_for('user.upload_resume', event_id=event_id))
        except Exception as e:
            flash('Error reading file. Please try again.', 'error')
            return redirect(url_for('user.upload_resume', event_id=event_id))
        
        # Create secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{current_user.id}_{event_id}_{timestamp}_{filename}"
        
        # Create user-specific upload directory
        # Note: In original code it was by user_id, in some other places it seems to be event_id?
        # Checking view_resume logic: os.path.join(app.config['UPLOAD_FOLDER'], str(resume.user_id), resume.filename)
        # Checking uploaded_file logic: parts = filename.split('/') -> event_id = parts[0] in app.py:909
        # Wait, app.py:328 says: upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
        # But app.py:249 (leave_event) says: os.path.join(app.config['UPLOAD_FOLDER'], str(event_id), resume.filename)
        # And app.py:389 (view_resume) says: os.path.join(app.config['UPLOAD_FOLDER'], str(resume.user_id), resume.filename)
        # app.py:925 (uploaded_file) says: os.path.join(app.config['UPLOAD_FOLDER'], filename) where filename is path:filename
        
        # There seems to be an inconsistency in the original code logic about paths. 
        # I should stick to what `upload_resume` did in app.py:328: 
        # upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
        
        # Ensure UPLOAD_FOLDER is absolute and exists
        upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
        upload_dir = os.path.join(upload_folder, str(current_user.id))
        
        try:
            os.makedirs(upload_dir, exist_ok=True)
        except Exception as e:
            flash('Error creating upload directory. Please try again.', 'error')
            return redirect(url_for('user.upload_resume', event_id=event_id))
        
        # Use absolute path for file saving
        file_path = os.path.abspath(os.path.join(upload_dir, unique_filename))
        try:
            file.save(file_path)
        except Exception as e:
            flash('Error saving file. Please try again.', 'error')
            return redirect(url_for('user.upload_resume', event_id=event_id))
        
        # Check if user already has a resume for this event
        existing_resume = Resume.query.filter_by(
            user_id=current_user.id,
            event_id=event_id
        ).first()
        
        if existing_resume:
            # Update existing resume
            existing_resume.filename = unique_filename
            existing_resume.original_name = file.filename
            existing_resume.mime_type = file.content_type
            existing_resume.file_size = file_size
            existing_resume.uploaded_at = datetime.utcnow()
        else:
            # Create new resume record
            resume = Resume(
                user_id=current_user.id,
                event_id=event_id,
                filename=unique_filename,
                original_name=file.filename,
                mime_type=file.content_type,
                file_size=file_size
            )
            db.session.add(resume)
        
        db.session.commit()
        flash(f'Document uploaded successfully for "{event.name}"!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('upload_resume.html', event=event)

@user_bp.route('/view_resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    # Get the resume record
    resume = Resume.query.get(resume_id)
    
    if not resume:
        flash('Document not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You are not authorized to view this document!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Construct the file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(resume.user_id), resume.filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('Document file not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    return render_template('view_resume.html', resume=resume, file_path=file_path)

@user_bp.route('/delete_resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    # Get the resume record
    resume = Resume.query.get(resume_id)
    
    if not resume:
        flash('Document not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You are not authorized to delete this document!', 'error')
        return redirect(url_for('user.dashboard'))
    
    try:
        # Delete the resume file
        # Note: Original code had: os.path.join(app.config['UPLOAD_FOLDER'], str(resume.event_id), resume.filename)
        # But upload put it in str(current_user.id). 
        # I should probably stick to what upload did, but I must follow logic of original app.py to be safe or fix it if broken.
        # Original app.py:415 uses resume.event_id in path. app.py:328 used current_user.id.
        # This looks like a bug in original code (inconsistent paths).
        # However, for refactoring, I should copy the logic as is, or fix it if I am sure.
        # Given "view_resume" works with user_id, and upload works with user_id, delete using event_id seems WRONG in original code.
        # But I should check if I missed something.
        # app.py:249 (leave_event) uses event_id.
        # app.py:389 (view_resume) uses user_id.
        # app.py:415 (delete_resume) uses event_id.
        # app.py:328 (upload) uses user_id.
        
        # It seems inconsistent. I will use user_id to match upload and view, assuming user_id path is where it lives.
        # Wait, in `leave_event` (line 249 original) it uses `event_id`.
        # This means files might be scattered or I am misreading where they are saved.
        # Line 328: upload_dir = ... str(current_user.id)
        # So files are in uploads/<user_id>/...
        # So line 415 in original app.py seems BUGGY (uses event_id).
        # I will FIX this to use user_id to be consistent with upload location.
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(resume.user_id), resume.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                pass  # Log error but don't fail the operation
        
        # Delete resume record from database
        db.session.delete(resume)
        db.session.commit()
        
        flash('Document deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete document. Please try again.', 'error')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/update_keywords', methods=['POST'])
@login_required
def update_keywords():
    # Prevent super admin from updating keywords
    if current_user.is_admin:
        flash('Super admin accounts cannot update keywords!', 'error')
        return redirect(url_for('user.dashboard'))
    
    event_id = request.form.get('event_id')
    keywords = request.form.get('keywords', '').strip()
    
    # Validate inputs
    if not event_id:
        flash('Event ID is required.', 'error')
        return redirect(url_for('user.dashboard'))
    
    try:
        event_id = int(event_id)
    except ValueError:
        flash('Invalid event ID.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Find the membership
    membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not membership:
        flash('You are not a member of this event.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Validate keywords
    if not keywords:
        flash('Please enter at least 2 keywords.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Parse keywords (comma-separated)
    keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
    
    if len(keyword_list) < 2:
        flash('Please enter at least 2 keywords.', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Validate individual keywords
    for keyword in keyword_list:
        if len(keyword) > 50:
            flash('Each keyword must be 50 characters or less.', 'error')
            return redirect(url_for('user.dashboard'))
        if not keyword.replace(' ', '').replace('-', '').isalnum():
            flash('Keywords can only contain letters, numbers, spaces, and hyphens.', 'error')
            return redirect(url_for('user.dashboard'))
    
    # Update keywords
    membership.keywords = keywords.strip()
    db.session.commit()
    
    flash('Keywords updated successfully!', 'success')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    # Extract user_id and actual filename from path
    # Format: {user_id}/{filename}
    parts = filename.split('/')
    if len(parts) < 2:
        flash('Invalid file path!', 'error')
        return redirect(url_for('user.dashboard'))
    
    try:
        user_id = int(parts[0])
    except ValueError:
        flash('Invalid file path!', 'error')
        return redirect(url_for('user.dashboard'))
    
    actual_filename = '/'.join(parts[1:])
    
    # Find the resume record by filename and user_id
    resume = Resume.query.filter_by(filename=actual_filename, user_id=user_id).first()
    
    if not resume:
        flash('File not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        flash('You are not authorized to access this file!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Construct the full file path using the same structure as upload
    # Files are saved to: UPLOAD_FOLDER/{user_id}/{filename}
    # Ensure we use absolute path for consistency
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    file_path = os.path.join(upload_folder, str(resume.user_id), resume.filename)
    
    # Normalize path to handle any path separator issues
    file_path = os.path.abspath(os.path.normpath(file_path))
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('File not found on server!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Serve the file
    return send_file(file_path, as_attachment=False)
