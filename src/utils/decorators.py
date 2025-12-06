"""
Custom decorators for Prophere
Reusable decorators for route protection and functionality enhancement
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Decorator to require admin authentication for a route
    
    Usage:
        @app.route('/admin')
        @login_required
        @admin_required
        def admin_page():
            return "Admin only"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('user.dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def prevent_admin_action(f):
    """
    Decorator to prevent super admin from performing user-level actions
    Useful for routes like join_event, upload_resume where admins shouldn't participate
    
    Usage:
        @app.route('/join-event')
        @login_required
        @prevent_admin_action
        def join_event():
            return "Join event"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_admin:
            flash('Super admin accounts cannot perform this action.', 'error')
            return redirect(url_for('admin.admin_dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def anonymous_required(f):
    """
    Decorator to require user NOT be authenticated
    Useful for login/register pages to redirect already-logged-in users
    
    Usage:
        @app.route('/login')
        @anonymous_required
        def login():
            return "Login page"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def requires_membership(f):
    """
    Decorator to require user be a member of the event specified in route params
    Expects event_id in kwargs
    
    Usage:
        @app.route('/event/<int:event_id>/matching')
        @login_required
        @requires_membership
        def event_matching(event_id):
            return "Matching page"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from models import Membership
        
        event_id = kwargs.get('event_id')
        
        if not event_id:
            flash('Invalid event.', 'error')
            return redirect(url_for('user.dashboard'))
        
        membership = Membership.query.filter_by(
            user_id=current_user.id,
            event_id=event_id
        ).first()
        
        if not membership:
            flash('You must be a member of this event to access this page.', 'error')
            return redirect(url_for('user.dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def log_action(action_name):
    """
    Decorator factory to log actions (can be extended to save to database)
    
    Usage:
        @app.route('/delete-event/<int:event_id>')
        @login_required
        @admin_required
        @log_action('delete_event')
        def delete_event(event_id):
            return "Delete event"
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For now, just print to console
            # Can be extended to save to audit log table
            print(f"[ACTION] {action_name} by user {current_user.id if current_user.is_authenticated else 'anonymous'}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
