
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import app, db
from models import User, Event, EventSession, MeetingLocation, ParticipantAvailability, Match, Meeting
from allocation_engine import AllocationEngine
from datetime import datetime, timedelta

def test_scheduling():
    with app.app_context():
        print("Setting up test data...")
        
        # 1. Create Event
        event = Event(name="Test Event", code="TEST001")
        db.session.add(event)
        db.session.commit()
        
        # 2. Create Sessions
        start_time = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        session1 = EventSession(
            event_id=event.id,
            name="Morning Session",
            start_time=start_time,
            end_time=start_time + timedelta(hours=3),
            location_description="Main Hall"
        )
        db.session.add(session1)
        
        # 3. Create Locations
        loc1 = MeetingLocation(event_id=event.id, name="Table 1", capacity=2)
        loc2 = MeetingLocation(event_id=event.id, name="Table 2", capacity=2)
        db.session.add(loc1)
        db.session.add(loc2)
        
        # 4. Create Users
        u1 = User(name="User A", email="a@test.com", password_hash="hash")
        u2 = User(name="User B", email="b@test.com", password_hash="hash")
        u3 = User(name="User C", email="c@test.com", password_hash="hash")
        u4 = User(name="User D", email="d@test.com", password_hash="hash")
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()
        
        # 5. Create Matches
        m1 = Match(user1_id=u1.id, user2_id=u2.id, event_id=event.id)
        m2 = Match(user1_id=u3.id, user2_id=u4.id, event_id=event.id)
        db.session.add_all([m1, m2])
        db.session.commit()
        
        # 6. Set Availability
        # All users available for session 1
        for u in [u1, u2, u3, u4]:
            avail = ParticipantAvailability(
                user_id=u.id,
                event_id=event.id,
                session_id=session1.id,
                is_available=True
            )
            db.session.add(avail)
        db.session.commit()
        
        print("Running allocation...")
        engine = AllocationEngine(event.id)
        result = engine.allocate_meetings()
        print(f"Result: {result}")
        
        # 7. Verify
        meetings = Meeting.query.join(Match).filter(Match.event_id == event.id).all()
        print(f"Scheduled meetings: {len(meetings)}")
        
        for m in meetings:
            print(f"Meeting: {m.match.user1.name} & {m.match.user2.name} at {m.start_time} in {m.location.name}")
            
        if len(meetings) == 2:
            print("SUCCESS: Both matches scheduled!")
        else:
            print("FAILURE: Not all matches scheduled.")
            
        # Cleanup
        # (Optional, but good for repeated runs if using a persistent DB)
        # For now, we assume a fresh DB or we don't care about cleanup in dev
        
if __name__ == "__main__":
    test_scheduling()
