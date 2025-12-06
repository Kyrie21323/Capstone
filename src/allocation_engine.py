from models import db, Match, Meeting, EventSession, MeetingLocation, ParticipantAvailability
from datetime import timedelta

class AllocationEngine:
    def __init__(self, event_id):
        self.event_id = event_id
        
    def allocate_meetings(self):
        # 1. Get all active matches for the event that don't have meetings yet
        matches = Match.query.filter_by(event_id=self.event_id, is_active=True).all()
        matches_to_schedule = [m for m in matches if not m.meetings]
        
        # 2. Get all sessions and locations
        sessions = EventSession.query.filter_by(event_id=self.event_id).order_by(EventSession.start_time).all()
        locations = MeetingLocation.query.filter_by(event_id=self.event_id).all()
        
        if not sessions or not locations:
            return {"status": "error", "message": "No sessions or locations defined"}
            
        # 3. Get availability map: (user_id, session_id) -> bool
        availabilities = ParticipantAvailability.query.filter_by(event_id=self.event_id).all()
        availability_map = {(a.user_id, a.session_id): a.is_available for a in availabilities}
        
        scheduled_count = 0
        
        # 4. Iterate through matches and try to schedule
        for match in matches_to_schedule:
            scheduled = False
            
            for session in sessions:
                # Check if both users are available for this session
                user1_avail = availability_map.get((match.user1_id, session.id), False)
                user2_avail = availability_map.get((match.user2_id, session.id), False)
                
                if user1_avail and user2_avail:
                    # Find a time slot and location in this session
                    slot = self.find_slot_in_session(session, locations, match)
                    if slot:
                        # Create meeting
                        meeting = Meeting(
                            match_id=match.id,
                            session_id=session.id,
                            location_id=slot['location'].id,
                            start_time=slot['start_time'],
                            end_time=slot['end_time'],
                            status='scheduled'
                        )
                        db.session.add(meeting)
                        scheduled = True
                        scheduled_count += 1
                        break # Move to next match
            
            if not scheduled:
                print(f"Could not schedule match {match.id}")
                
        db.session.commit()
        return {"status": "success", "scheduled": scheduled_count, "total": len(matches_to_schedule)}
        
    def find_slot_in_session(self, session, locations, match):
        # Simple greedy strategy: 15 min slots
        slot_duration = timedelta(minutes=15)
        current_time = session.start_time
        
        while current_time + slot_duration <= session.end_time:
            end_time = current_time + slot_duration
            
            # Check if users are free at this time (not already booked in another meeting)
            if not self.is_user_free(match.user1_id, current_time, end_time) or \
               not self.is_user_free(match.user2_id, current_time, end_time):
                current_time += slot_duration
                continue
                
            # Check for available location
            for location in locations:
                if self.is_location_free(location.id, current_time, end_time):
                    return {
                        'start_time': current_time,
                        'end_time': end_time,
                        'location': location
                    }
            
            current_time += slot_duration
            
        return None
        
    def is_user_free(self, user_id, start_time, end_time):
        # Check if user has any meeting overlapping with this time
        # We need to join Match and Meeting
        existing_meeting = db.session.query(Meeting).join(Match).filter(
            (Match.user1_id == user_id) | (Match.user2_id == user_id),
            Meeting.start_time < end_time,
            Meeting.end_time > start_time,
            Meeting.status != 'cancelled'
        ).first()
        
        return existing_meeting is None
        
    def is_location_free(self, location_id, start_time, end_time):
        existing_meeting = Meeting.query.filter(
            Meeting.location_id == location_id,
            Meeting.start_time < end_time,
            Meeting.end_time > start_time,
            Meeting.status != 'cancelled'
        ).first()
        
        return existing_meeting is None
