"""
Scheduling routes for Prophere.
Handles session management, locations, availability, and allocation.
"""
from flask import render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from models import db, Event, EventSession, MeetingPoint, SessionLocation, ParticipantAvailability, Membership, Match
from datetime import datetime
from . import scheduling_bp
from .utils import admin_required

@scheduling_bp.route('/<int:event_id>/event-locations', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_event_locations(event_id):
    """Manage event locations (physical venues for sessions)"""
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            description = request.form.get('description', '')
            
            if name:
                session_location = SessionLocation(
                    event_id=event_id,
                    name=name,
                    description=description
                )
                db.session.add(session_location)
                db.session.commit()
                flash(f'Event location "{name}" added successfully!', 'success')
            else:
               flash('Location name is required.', 'error')
                
        elif action == 'delete':
            location_id = request.form.get('location_id')
            session_location = SessionLocation.query.get(location_id)
            if session_location and session_location.event_id == event_id:
                # Check if any sessions or meeting points are using this location
                sessions_using = len([s for s in session_location.sessions if s.event_id == event_id])
                # Count meeting points associated via many-to-many
                meeting_points_list = session_location.meeting_points.all() if hasattr(session_location.meeting_points, 'all') else session_location.meeting_points
                meeting_points_using = len(meeting_points_list)
                
                if sessions_using > 0 or meeting_points_using > 0:
                    flash(f'Cannot delete "{session_location.name}": {sessions_using} session(s) and {meeting_points_using} meeting point(s) are using it.', 'error')
                else:
                    db.session.delete(session_location)
                    db.session.commit()
                    flash(f'Event location "{session_location.name}" deleted successfully!', 'success')
                    
    session_locations = SessionLocation.query.filter_by(event_id=event_id).all()
    return render_template('admin/manage_event_locations.html', event=event, session_locations=session_locations)

@scheduling_bp.route('/<int:event_id>/event-sessions-workflow')
@login_required
@admin_required
def event_sessions_workflow(event_id):
    """Guided workflow for setting up event sessions"""
    event = Event.query.get_or_404(event_id)
    
    # Get counts for status indicators
    session_locations_count = SessionLocation.query.filter_by(event_id=event_id).count()
    sessions_count = EventSession.query.filter_by(event_id=event_id).count()
    meeting_points_count = MeetingPoint.query.filter_by(event_id=event_id).count()
    
    return render_template('admin/event_sessions_workflow.html', 
                         event=event,
                         session_locations_count=session_locations_count,
                         sessions_count=sessions_count,
                         meeting_points_count=meeting_points_count)

@scheduling_bp.route('/<int:event_id>/attendee-matching-workflow')
@login_required
@admin_required
def attendee_matching_workflow(event_id):
    """Guided workflow for attendee matching setup"""
    event = Event.query.get_or_404(event_id)
    
    # Get stats for display
    total_members = Membership.query.filter_by(event_id=event_id).count()
    matching_enabled_sessions = EventSession.query.filter_by(event_id=event_id, matching_enabled=True).count()
    total_matches = Match.query.filter_by(event_id=event_id, is_active=True).count()
    
    return render_template('admin/attendee_matching_workflow.html',
                         event=event,
                         total_members=total_members,
                         matching_enabled_sessions=matching_enabled_sessions,
                         total_matches=total_matches)

@scheduling_bp.route('/<int:event_id>/sessions', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_sessions(event_id):
    # Admin check handled by decorator
    
    event = Event.query.get_or_404(event_id)
    session_locations = SessionLocation.query.filter_by(event_id=event_id).all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            day_number = request.form.get('day_number')
            start_time_str = request.form.get('start_time')
            end_time_str = request.form.get('end_time')
            session_location_id = request.form.get('session_location_id')
            matching_enabled = request.form.get('matching_enabled') == 'on'
            
            try:
                from datetime import time
                # Parse time strings (format: HH:MM)
                start_hour, start_min = map(int, start_time_str.split(':'))
                end_hour, end_min = map(int, end_time_str.split(':'))
                
                start_time = time(start_hour, start_min)
                end_time = time(end_hour, end_min)
                
                if end_time <= start_time:
                    flash('End time must be after start time.', 'error')
                else:
                    session = EventSession(
                        event_id=event_id,
                        name=name,
                        day_number=int(day_number),
                        start_time=start_time,
                        end_time=end_time,
                        session_location_id=int(session_location_id) if session_location_id else None,
                        matching_enabled=matching_enabled
                    )
                    db.session.add(session)
                    db.session.commit()
                    flash('Session added successfully!', 'success')
            except ValueError as e:
                flash(f'Invalid input: {str(e)}', 'error')
                
        elif action == 'delete':
            session_id = request.form.get('session_id')
            session = EventSession.query.get(session_id)
            if session and session.event_id == event_id:
                db.session.delete(session)
                db.session.commit()
                flash('Session deleted successfully!', 'success')
        
        elif action == 'toggle_matching':
            session_id = request.form.get('session_id')
            session = EventSession.query.get(session_id)
            if session and session.event_id == event_id:
                session.matching_enabled = not session.matching_enabled
                db.session.commit()
                status = 'enabled' if session.matching_enabled else 'disabled'
                flash(f'Matching {status} for {session.name}!', 'success')
                
    sessions = EventSession.query.filter_by(event_id=event_id).order_by(EventSession.day_number, EventSession.start_time).all()
    return render_template('admin/manage_sessions.html', event=event, sessions=sessions, session_locations=session_locations)

@scheduling_bp.route('/<int:event_id>/meeting-points', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_meeting_points(event_id):
    # Admin check handled by decorator
    
    event = Event.query.get_or_404(event_id)
    session_locations = SessionLocation.query.filter_by(event_id=event_id).all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            capacity = request.form.get('capacity', 1)
            session_location_ids = request.form.getlist('session_location_ids')
            
            try:
                capacity = int(capacity)
                location = MeetingPoint(
                    event_id=event_id,
                    name=name,
                    capacity=capacity
                )
                
                # Associate with multiple event locations
                if session_location_ids:
                    # Also set the first one as primary for backward compatibility if needed
                    # location.session_location_id = int(session_location_ids[0])
                    for loc_id in session_location_ids:
                        session_loc = SessionLocation.query.get(int(loc_id))
                        if session_loc:
                            location.session_locations.append(session_loc)
                            
                db.session.add(location)
                db.session.commit()
                flash('Meeting point added successfully!', 'success')
            except ValueError:
                flash('Invalid capacity.', 'error')
                
        elif action == 'delete':
            location_id = request.form.get('location_id')
            location = MeetingPoint.query.get(location_id)
            if location and location.event_id == event_id:
                db.session.delete(location)
                db.session.commit()
                flash('Meeting point deleted successfully!', 'success')
                
    locations = MeetingPoint.query.filter_by(event_id=event_id).all()
    return render_template('admin/manage_meeting_points.html', event=event, locations=locations, session_locations=session_locations)

@scheduling_bp.route('/<int:event_id>/availability/check-matches', methods=['GET'])
@login_required
def check_availability_matches(event_id):
    """API endpoint to check if user has matches (for pre-submission confirmation)"""
    if current_user.is_admin:
        return jsonify({'has_matches': False})
    
    try:
        from utils.session_validation import check_user_has_matches
        has_matches = check_user_has_matches(current_user.id, event_id)
        return jsonify({'has_matches': has_matches})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    
    # Only show sessions with matching enabled
    sessions = EventSession.query.filter_by(
        event_id=event_id,
        matching_enabled=True
    ).order_by(EventSession.day_number, EventSession.start_time).all()
    
    if request.method == 'POST':
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
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
        
        # Validate and reassign meetings
        try:
            from utils.session_validation import reassign_invalid_meetings, assign_new_meetings
            
            print(f"🔍 Starting validation for user {current_user.id} in event {event_id}")
            
            # Reassign invalid meetings
            reassignment_results = reassign_invalid_meetings(current_user.id, event_id, event)
            print(f"📊 Reassignment results: {reassignment_results}")
            
            # Try to assign new meetings
            new_assignment_results = assign_new_meetings(current_user.id, event_id, event)
            print(f"📊 New assignment results: {new_assignment_results}")
            
            # Prepare response
            results = {
                'success': True,
                'cancelled': reassignment_results['cancelled'],
                'reassigned': reassignment_results['reassigned'],
                'failed_reassignment': reassignment_results['failed'],
                'newly_assigned': new_assignment_results['newly_assigned'],
                'failed_assignment': new_assignment_results['assignment_failed'],
                'redirect_url': url_for('matching.event_matches', event_id=event_id)
            }
            
            print(f"✅ Validation complete. Results: {results}")
            
            if is_ajax:
                return jsonify(results)
            else:
                flash('Availability updated successfully!', 'success')
                return redirect(url_for('matching.event_matches', event_id=event_id))
                
        except Exception as e:
            print(f"Error during validation/reassignment: {str(e)}")
            if is_ajax:
                return jsonify({
                    'success': True,  # Availability was saved
                    'validation_error': str(e),
                    'redirect_url': url_for('matching.event_matches', event_id=event_id)
                })
            else:
                flash('Availability updated, but there was an error validating meetings.', 'warning')
                return redirect(url_for('matching.event_matches', event_id=event_id))
        
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
