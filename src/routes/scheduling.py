"""
Scheduling routes for Prophere.
Handles session management, locations, availability, and allocation.
"""
from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import db, Event, EventSession, MeetingLocation, ParticipantAvailability, Membership
from datetime import datetime
from . import scheduling_bp
from .utils import admin_required

@scheduling_bp.route('/<int:event_id>/sessions', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_sessions(event_id):
    # Admin check handled by decorator
    
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')
            location_desc = request.form.get('location_description')
            
            try:
                start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
                end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
                
                if end_time <= start_time:
                    flash('End time must be after start time.', 'error')
                else:
                    session = EventSession(
                        event_id=event_id,
                        name=name,
                        start_time=start_time,
                        end_time=end_time,
                        location_description=location_desc
                    )
                    db.session.add(session)
                    db.session.commit()
                    flash('Session added successfully!', 'success')
            except ValueError:
                flash('Invalid date/time format.', 'error')
                
        elif action == 'delete':
            session_id = request.form.get('session_id')
            session = EventSession.query.get(session_id)
            if session and session.event_id == event_id:
                db.session.delete(session)
                db.session.commit()
                flash('Session deleted successfully!', 'success')
                
    sessions = EventSession.query.filter_by(event_id=event_id).order_by(EventSession.start_time).all()
    return render_template('manage_sessions.html', event=event, sessions=sessions)

@scheduling_bp.route('/<int:event_id>/locations', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_locations(event_id):
    # Admin check handled by decorator
    
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            capacity = request.form.get('capacity', 2)
            
            try:
                capacity = int(capacity)
                location = MeetingLocation(
                    event_id=event_id,
                    name=name,
                    capacity=capacity
                )
                db.session.add(location)
                db.session.commit()
                flash('Location added successfully!', 'success')
            except ValueError:
                flash('Invalid capacity.', 'error')
                
        elif action == 'delete':
            location_id = request.form.get('location_id')
            location = MeetingLocation.query.get(location_id)
            if location and location.event_id == event_id:
                db.session.delete(location)
                db.session.commit()
                flash('Location deleted successfully!', 'success')
                
    locations = MeetingLocation.query.filter_by(event_id=event_id).all()
    return render_template('manage_locations.html', event=event, locations=locations)

@scheduling_bp.route('/<int:event_id>/availability', methods=['GET', 'POST'])
@login_required
def manage_availability(event_id):
    # Prevent super admin from managing availability (this is for participants)
    if current_user.is_admin:
        flash('Super admin accounts cannot manage availability!', 'error')
        return redirect(url_for('user.dashboard'))
        
    event = Event.query.get_or_404(event_id)
    
    # Check if user is a member
    membership = Membership.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not membership:
        flash('You are not a member of this event!', 'error')
        return redirect(url_for('user.dashboard'))
        
    sessions = EventSession.query.filter_by(event_id=event_id).order_by(EventSession.start_time).all()
    
    if request.method == 'POST':
        # Get all session IDs from the form
        # The form will send 'session_X' = 'on' if checked
        
        # First, clear existing availability for this event
        ParticipantAvailability.query.filter_by(
            user_id=current_user.id,
            event_id=event_id
        ).delete()
        
        # Add new availability
        for session in sessions:
            is_available = request.form.get(f'session_{session.id}') == 'on'
            if is_available:
                availability = ParticipantAvailability(
                    user_id=current_user.id,
                    event_id=event_id,
                    session_id=session.id,
                    is_available=True
                )
                db.session.add(availability)
        
        db.session.commit()
        flash('Availability updated successfully!', 'success')
        return redirect(url_for('user.dashboard'))
        
    # Get current availability
    current_availability = ParticipantAvailability.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).all()
    available_session_ids = {a.session_id for a in current_availability}
    
    return render_template('manage_availability.html', 
                         event=event, 
                         sessions=sessions, 
                         available_session_ids=available_session_ids)

@scheduling_bp.route('/<int:event_id>/allocate', methods=['POST'])
@login_required
@admin_required
def allocate_meetings(event_id):
    # Admin check handled by decorator
    
    try:
        from allocation_engine import AllocationEngine
        engine = AllocationEngine(event_id)
        result = engine.allocate_meetings()
        
        if result['status'] == 'success':
            flash(f"Allocation complete! Scheduled {result['scheduled']} meetings.", 'success')
        else:
            flash(f"Allocation failed: {result['message']}", 'error')
            
    except Exception as e:
        flash(f"An error occurred during allocation: {str(e)}", 'error')
        
    return redirect(url_for('scheduling.manage_sessions', event_id=event_id))
