"""
Session Validation and Meeting Reassignment Utilities
Handles validation of meetings after session availability updates and automatic reassignment.
"""
from models import db, Match, Meeting, EventSession, ParticipantAvailability
from datetime import datetime
from sqlalchemy import and_, or_
from utils.auto_assign import auto_assign_meeting


def check_user_has_matches(user_id, event_id):
    """
    Check if a user has any active matches for the event.
    
    Args:
        user_id: ID of the user
        event_id: ID of the event
    
    Returns:
        bool: True if user has active matches, False otherwise
    """
    match_count = Match.query.filter(
        Match.event_id == event_id,
        Match.is_active == True,
        or_(Match.user1_id == user_id, Match.user2_id == user_id)
    ).count()
    
    return match_count > 0


def validate_meetings_after_update(user_id, event_id):
    """
    Find meetings that are no longer valid after a user updates their session availability.
    
    A meeting is invalid if it's scheduled during a session that the user is no longer attending.
    
    Args:
        user_id: ID of the user who updated availability
        event_id: ID of the event
    
    Returns:
        list: List of Meeting objects that are now invalid
    """
    # Get user's current available sessions
    available_sessions = db.session.query(ParticipantAvailability.session_id).filter(
        ParticipantAvailability.user_id == user_id,
        ParticipantAvailability.event_id == event_id,
        ParticipantAvailability.is_available == True
    ).all()
    available_session_ids = {s[0] for s in available_sessions}
    
    # Find all meetings involving this user
    user_meetings = db.session.query(Meeting).join(
        Match, Meeting.match_id == Match.id
    ).filter(
        Match.event_id == event_id,
        or_(Match.user1_id == user_id, Match.user2_id == user_id),
        Meeting.status == 'scheduled'
    ).all()
    
    # Check which meetings are in sessions the user is no longer attending
    invalid_meetings = []
    for meeting in user_meetings:
        if meeting.session_id not in available_session_ids:
            invalid_meetings.append(meeting)
    
    return invalid_meetings


def validate_partner_availability(meeting):
    """
    Check if both users in a meeting are still available for the meeting's session.
    
    Args:
        meeting: Meeting object
    
    Returns:
        tuple: (is_valid: bool, missing_user_id: int or None)
    """
    match = meeting.match
    session_id = meeting.session_id
    
    # Check user1 availability
    user1_available = ParticipantAvailability.query.filter_by(
        user_id=match.user1_id,
        session_id=session_id,
        is_available=True
    ).first() is not None
    
    # Check user2 availability
    user2_available = ParticipantAvailability.query.filter_by(
        user_id=match.user2_id,
        session_id=session_id,
        is_available=True
    ).first() is not None
    
    if not user1_available and not user2_available:
        return (False, "both users")
    elif not user1_available:
        return (False, match.user1_id)
    elif not user2_available:
        return (False, match.user2_id)
    else:
        return (True, None)


def reassign_invalid_meetings(user_id, event_id, event):
    """
    Cancel invalid meetings and attempt to reassign them to new time slots.
    
    Args:
        user_id: ID of the user who updated availability
        event_id: ID of the event
        event: Event object (for date calculations)
    
    Returns:
        dict: Results with counts and details
            {
                'cancelled': int,
                'reassigned': int,
                'failed': int,
                'details': list of dicts with meeting info
            }
    """
    results = {
        'cancelled': 0,
        'reassigned': 0,
        'failed': 0,
        'details': []
    }
    
    # Find invalid meetings
    invalid_meetings = validate_meetings_after_update(user_id, event_id)
    
    for meeting in invalid_meetings:
        match = meeting.match
        old_session = meeting.session.name if meeting.session else "Unknown"
        old_location = meeting.location.name if meeting.location else "Unknown"
        old_time = meeting.start_time.strftime('%I:%M %p') if meeting.start_time else "Unknown"
        
        # Check if partner is also unavailable
        is_valid, missing_user = validate_partner_availability(meeting)
        
        # Cancel the meeting
        meeting.status = 'cancelled'
        results['cancelled'] += 1
        
        # Update match assignment info
        match.assigned_meeting_id = None
        match.assignment_attempted = True
        
        try:
            # Try to reassign
            success, message, new_meeting = auto_assign_meeting(
                match.id,
                match.user1_id,
                match.user2_id,
                event_id,
                event
            )
            
            if success and new_meeting:
                results['reassigned'] += 1
                match.assignment_failed_reason = None
                results['details'].append({
                    'match_id': match.id,
                    'status': 'reassigned',
                    'old_session': old_session,
                    'old_location': old_location,
                    'old_time': old_time,
                    'new_session': new_meeting.session.name,
                    'new_location': new_meeting.location.name,
                    'new_time': new_meeting.start_time.strftime('%I:%M %p')
                })
            else:
                results['failed'] += 1
                match.assignment_failed_reason = message
                results['details'].append({
                    'match_id': match.id,
                    'status': 'failed',
                    'old_session': old_session,
                    'old_location': old_location,
                    'old_time': old_time,
                    'reason': message
                })
        except Exception as e:
            results['failed'] += 1
            match.assignment_failed_reason = f"Error during reassignment: {str(e)}"
            results['details'].append({
                'match_id': match.id,
                'status': 'error',
                'old_session': old_session,
                'reason': str(e)
            })
    
    db.session.commit()
    return results


def assign_new_meetings(user_id, event_id, event):
    """
    Try to assign meetings to previously unassigned matches that now have overlapping availability.
    
    Args:
        user_id: ID of the user who updated availability
        event_id: ID of the event
        event: Event object (for date calculations)
    
    Returns:
        dict: Results with counts and details
            {
                'newly_assigned': int,
                'assignment_failed': int,
                'details': list of dicts with assignment info
            }
    """
    results = {
        'newly_assigned': 0,
        'assignment_failed': 0,
        'details': []
    }
    
    # Find all active matches involving this user without meetings
    matches = Match.query.filter(
        Match.event_id == event_id,
        Match.is_active == True,
        or_(Match.user1_id == user_id, Match.user2_id == user_id)
    ).all()
    
    # Filter to only those without assigned meetings
    unassigned_matches = []
    for match in matches:
        existing_meeting = Meeting.query.filter_by(
            match_id=match.id,
            status='scheduled'
        ).first()
        if not existing_meeting:
            unassigned_matches.append(match)
    
    # Try to assign each unassigned match
    for match in unassigned_matches:
        try:
            success, message, new_meeting = auto_assign_meeting(
                match.id,
                match.user1_id,
                match.user2_id,
                event_id,
                event
            )
            
            if success and new_meeting:
                results['newly_assigned'] += 1
                match.assignment_failed_reason = None
                results['details'].append({
                    'match_id': match.id,
                    'status': 'assigned',
                    'session': new_meeting.session.name,
                    'location': new_meeting.location.name,
                    'time': new_meeting.start_time.strftime('%I:%M %p')
                })
            else:
                results['assignment_failed'] += 1
                match.assignment_failed_reason = message
                results['details'].append({
                    'match_id': match.id,
                    'status': 'failed',
                    'reason': message
                })
        except Exception as e:
            results['assignment_failed'] += 1
            match.assignment_failed_reason = f"Error during assignment: {str(e)}"
            results['details'].append({
                'match_id': match.id,
                'status': 'error',
                'reason': str(e)
            })
    
    db.session.commit()
    return results
