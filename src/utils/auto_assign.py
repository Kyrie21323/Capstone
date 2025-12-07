"""
Automatic Meeting Assignment Utility
Assigns meeting times and locations when users match.
"""
from models import db, ParticipantAvailability, EventSession, MeetingPoint, Meeting, Match
from datetime import datetime, timedelta, time as datetime_time
from sqlalchemy import and_

def find_overlapping_sessions(user1_id, user2_id, event_id):
    """
    Find sessions where both users are available.
    
    Returns:
        list: List of EventSession objects where both users are available
    """
    # Get user1's available sessions
    user1_sessions = db.session.query(ParticipantAvailability.session_id).filter(
        ParticipantAvailability.user_id == user1_id,
        ParticipantAvailability.event_id == event_id,
        ParticipantAvailability.is_available == True
    ).all()
    user1_session_ids = {s[0] for s in user1_sessions}
    
    # Get user2's available sessions
    user2_sessions = db.session.query(ParticipantAvailability.session_id).filter(
        ParticipantAvailability.user_id == user2_id,
        ParticipantAvailability.event_id == event_id,
        ParticipantAvailability.is_available == True
    ).all()
    user2_session_ids = {s[0] for s in user2_sessions}
    
    # Find overlapping session IDs
    overlapping_ids = user1_session_ids.intersection(user2_session_ids)
    
    if not overlapping_ids:
        return []
    
    # Get the actual session objects, ordered by day and time
    overlapping_sessions = EventSession.query.filter(
        EventSession.id.in_(overlapping_ids)
    ).order_by(EventSession.day_number, EventSession.start_time).all()
    
    return overlapping_sessions


def find_available_meeting_point(session_location, session_id, start_time, end_time):
    """
    Find an available meeting point for the given time slot.
    
    Args:
        session_location: SessionLocation object
        session_id: ID of the session
        start_time: Start time of the meeting (datetime)
        end_time: End time of the meeting (datetime)
    
    Returns:
        MeetingPoint or None if no available point found
    """
    # Get all meeting points associated with this session location via many-to-many
    meeting_points = session_location.meeting_points.all() if hasattr(session_location.meeting_points, 'all') else session_location.meeting_points
    
    if not meeting_points:
        return None
    
    # Check each meeting point for availability
    for point in meeting_points:
        # Count overlapping meetings
        overlapping_count = Meeting.query.filter(
            Meeting.location_id == point.id,
            Meeting.session_id == session_id,
            Meeting.status != 'cancelled',
            # Check for time overlap
            and_(
                Meeting.start_time < end_time,
                Meeting.end_time > start_time
            )
        ).count()
        
        if overlapping_count < point.capacity:
            # This point is available!
            return point
    
    return None


def auto_assign_meeting(match_id, user1_id, user2_id, event_id, event):
    """
    Automatically assign a meeting time and location for a match.
    
    Args:
        match_id: ID of the Match record
        user1_id: ID of first user
        user2_id: ID of second user
        event_id: ID of the event
        event: Event object (to get dates)
    
    Returns:
        tuple: (success: bool, message: str, meeting: Meeting or None)
    """
    try:
        # Find overlapping sessions
        overlapping_sessions = find_overlapping_sessions(user1_id, user2_id, event_id)
        
        if not overlapping_sessions:
            return (False, "No overlapping session availability", None)
        
        # Try to assign to the first available session
        for session in overlapping_sessions:
            if not session.session_location:
                continue  # Skip sessions without locations
            
            # Calculate actual datetime for this session
            # Assumes event has start_date set
            if not event.start_date:
                return (False, "Event dates not set", None)
            
            # Calculate the actual date for this session day
            session_date = event.start_date.date() + timedelta(days=session.day_number - 1)
            
            # Combine date with session start time
            session_start_datetime = datetime.combine(session_date, session.start_time)
            session_end_datetime = datetime.combine(session_date, session.end_time)
            
            # Try to find a 15-minute slot within the session
            # Start from session start time
            current_time = session_start_datetime
            meeting_duration = timedelta(minutes=15)
            
            while current_time + meeting_duration <= session_end_datetime:
                meeting_start = current_time
                meeting_end = current_time + meeting_duration
                
                # Find available meeting point
                meeting_point = find_available_meeting_point(
                    session.session_location,
                    session.id,
                    meeting_start,
                    meeting_end
                )
                
                if meeting_point:
                    # Found an available slot! Create the meeting
                    meeting = Meeting(
                        match_id=match_id,
                        session_id=session.id,
                        location_id=meeting_point.id,
                        start_time=meeting_start,
                        end_time=meeting_end,
                        status='scheduled'
                    )
                    db.session.add(meeting)
                    
                    # Update the match with assignment info
                    match = Match.query.get(match_id)
                    if match:
                        match.assigned_meeting_id = meeting.id
                        match.assignment_attempted = True
                        match.assigned_at = datetime.utcnow()
                    
                    db.session.commit()
                    
                    return (True, "Meeting assigned successfully", meeting)
                
                # Move to next 15-minute slot
                current_time += meeting_duration
        
        # No available slots found
        return (False, "No available meeting points in overlapping sessions", None)
        
    except Exception as e:
        db.session.rollback()
        return (False, f"Error during assignment: {str(e)}", None)
