"""
Admin routes for Prophere.
Handles event creation, user management, and system administration.
"""
from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import db, User, Event, Membership, Resume
from datetime import datetime
import os
from . import admin_bp
from .utils import admin_required, cleanup_orphaned_files

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    # Get statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_events = Event.query.count()
    total_memberships = Membership.query.count()
    total_resumes = Resume.query.count()
    
    # Get recent events
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    # Get recent users (excluding admins)
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_events=total_events,
                         total_memberships=total_memberships,
                         total_resumes=total_resumes,
                         recent_events=recent_events,
                         recent_users=recent_users)

@admin_bp.route('/events')
@login_required
@admin_required
def admin_events():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin/events.html', events=events)

@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_event():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        description = request.form.get('description', '').strip()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Validate description word count
        if description:
            word_count = len(description.split())
            if word_count > 300:
                flash('Description cannot exceed 300 words. Please shorten your description.', 'error')
                return render_template('admin/create_event.html')
        
        # Check if event code already exists
        if Event.query.filter_by(code=code).first():
            flash(f'Event code "{code}" already exists!', 'error')
            return render_template('admin/create_event.html')
        
        # Create new event
        event = Event(
            name=name,
            code=code,
            description=description if description else None,
            start_date=datetime.strptime(start_date, '%Y-%m-%d') if start_date else None,
            end_date=datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        )
        db.session.add(event)
        db.session.commit()
        
        flash(f'Event "{name}" created successfully!', 'success')
        return redirect(url_for('admin.admin_events'))
    
    return render_template('admin/create_event.html')

@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.name = request.form['name']
        event.code = request.form['code']
        description = request.form.get('description', '').strip()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Validate description word count
        if description:
            word_count = len(description.split())
            if word_count > 300:
                flash('Description cannot exceed 300 words. Please shorten your description.', 'error')
                return render_template('admin/edit_event.html', event=event)
        
        # Check if event code already exists (excluding current event)
        existing_event = Event.query.filter_by(code=event.code).first()
        if existing_event and existing_event.id != event.id:
            flash(f'Event code "{event.code}" already exists!', 'error')
            return render_template('admin/edit_event.html', event=event)
        
        event.description = description if description else None
        event.start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        event.end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        db.session.commit()
        flash(f'Event "{event.name}" updated successfully!', 'success')
        return redirect(url_for('admin.admin_events'))
    
    return render_template('admin/edit_event.html', event=event)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Delete associated files
    resumes = Resume.query.filter_by(event_id=event_id).all()
    for resume in resumes:
        # Note: Checking file path consistency. 
        # App.py upload uses user_id folder. 
        # Original delete logic used event_id folder?
        # Trying to be safe: check both or stick to one logic?
        # If I want to be 100% safe I should try both paths.
        
        # Try user_id path first (as in upload)
        file_path_user = os.path.join(current_app.config['UPLOAD_FOLDER'], str(resume.user_id), resume.filename)
        # Try event_id path (as in original delete logic which might be buggy or legacy)
        file_path_event = os.path.join(current_app.config['UPLOAD_FOLDER'], str(event_id), resume.filename)
        
        if os.path.exists(file_path_user):
            os.remove(file_path_user)
        elif os.path.exists(file_path_event):
            os.remove(file_path_event)
            
    # Delete associated records
    Membership.query.filter_by(event_id=event_id).delete()
    Resume.query.filter_by(event_id=event_id).delete()
    
    # Delete event
    db.session.delete(event)
    db.session.commit()
    
    flash(f'Event "{event.name}" deleted successfully!', 'success')
    return redirect(url_for('admin.admin_events'))

@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin status from yourself
    if user.id == current_user.id:
        flash('You cannot remove admin status from yourself!', 'error')
        return redirect(url_for('admin.admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'removed'
    flash(f'Admin status {status} for {user.name}!', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin.admin_users'))
    
    # Store user name for flash message
    user_name = user.name
    
    try:
        # Delete associated data first
        # Delete memberships
        Membership.query.filter_by(user_id=user_id).delete()
        
        # Delete resumes and associated files
        resumes = Resume.query.filter_by(user_id=user_id).all()
        deleted_files = []
        failed_files = []
        
        for resume in resumes:
            # Check user_id path (standard per upload)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(resume.user_id), resume.filename)
            
            # Check if file exists and delete it
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files.append(resume.filename)
                except Exception as e:
                    failed_files.append(f"{resume.filename}: {str(e)}")
            else:
                # Try event_id path fallback just in case
                file_path_alt = os.path.join(current_app.config['UPLOAD_FOLDER'], str(resume.event_id), resume.filename)
                if os.path.exists(file_path_alt):
                    try:
                        os.remove(file_path_alt)
                        deleted_files.append(resume.filename)
                    except Exception as e:
                        failed_files.append(f"{resume.filename}: {str(e)}")
                else:
                    failed_files.append(f"{resume.filename}: File not found")
        
        # Delete resume records from database
        Resume.query.filter_by(user_id=user_id).delete()
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        
        # Create success message with file deletion details
        success_msg = f'User {user_name} has been deleted successfully!'
        if deleted_files:
            success_msg += f' Deleted {len(deleted_files)} resume file(s).'
        if failed_files:
            success_msg += f' Warning: {len(failed_files)} file(s) could not be deleted.'
        
        flash(success_msg, 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user {user_name}: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/cleanup-files', methods=['POST'])
@login_required
@admin_required
def admin_cleanup_files():
    """Admin route to clean up orphaned files"""
    try:
        orphaned_count = cleanup_orphaned_files()
        if orphaned_count > 0:
            flash(f'Cleaned up {orphaned_count} orphaned file(s)!', 'success')
        else:
            flash('No orphaned files found.', 'info')
    except Exception as e:
        flash(f'Error during cleanup: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/graph/dev/<size>', methods=['GET'])
@login_required
def dev_graph_page(size):
    """
    Admin-only page for visualizing synthetic graph datasets.
    """
    # Note: Using explicit check instead of admin_required decorator for variety/legacy match,
    # but could use decorator. Sticking to original logic structure but with redirect fix.
    if not current_user.is_admin:
        flash('Admin access required to view the dev graph visualizer.', 'error')
        return redirect(url_for('user.dashboard'))
    
    if size not in ['small', 'medium', 'large']:
        flash('Invalid dataset size. Use: small, medium, or large.', 'error')
        return redirect(url_for('admin.admin_events'))
    
    return render_template('dev_graph.html', size=size)
