from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Using String(255) to accommodate Werkzeug's scrypt hashes which can exceed 128 chars
    # Older PBKDF2 hashes are ~88 chars, but scrypt can be 150+ chars
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='user', lazy=True)
    resumes = db.relationship('Resume', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def is_administrator(self):
        return self.is_admin

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)  # Optional initially, required to publish
    end_date = db.Column(db.DateTime, nullable=True)  # Optional initially, required to publish
    is_published = db.Column(db.Boolean, default=False, nullable=False)  # Controls public availability
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='event', lazy=True)
    resumes = db.relationship('Resume', backref='event', lazy=True)
    
    def __repr__(self):
        return f'<Event {self.name}>'

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    keywords = db.Column(db.Text, nullable=True)  # Store keywords as comma-separated string
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique user-event pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event'),)
    
    def __repr__(self):
        return f'<Membership User {self.user_id} -> Event {self.event_id}>'
    
    def get_keywords_list(self):
        """Return keywords as a list"""
        if self.keywords:
            return [keyword.strip() for keyword in self.keywords.split(',') if keyword.strip()]
        return []

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique user-event resume pairs (one resume per user per event)
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_resume'),)
    
    def __repr__(self):
        return f'<Resume {self.original_name} for User {self.user_id} in Event {self.event_id}>'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    matched_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Auto-assignment tracking
    assigned_meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=True)
    assignment_attempted = db.Column(db.Boolean, default=False)
    assignment_failed_reason = db.Column(db.String(200), nullable=True)
    assigned_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='matches_as_user1')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='matches_as_user2')
    event = db.relationship('Event', backref='matches')
    # Note: assigned_meeting accessed via Meeting.query.filter_by(match_id=self.id).first()
    
    # Ensure unique pairs and prevent self-matching
    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', 'event_id', name='unique_match_pair'),
        db.CheckConstraint('user1_id != user2_id', name='no_self_match'),
    )
    
    def __repr__(self):
        return f'<Match User {self.user1_id} <-> User {self.user2_id} in Event {self.event_id}>'
    
    def get_other_user(self, current_user_id):
        """Get the other user in this match"""
        if self.user1_id == current_user_id:
            return self.user2
        elif self.user2_id == current_user_id:
            return self.user1
        return None

class UserInteraction(db.Model):
    """Track individual likes/passes before they become matches"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # 'like' or 'pass'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='interactions_made')
    target_user = db.relationship('User', foreign_keys=[target_user_id], backref='interactions_received')
    event = db.relationship('Event', backref='user_interactions')
    
    # Ensure unique user-target-event combinations
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_user_id', 'event_id', name='unique_user_interaction'),
        db.CheckConstraint('user_id != target_user_id', name='no_self_interaction'),
        db.CheckConstraint("action IN ('like', 'pass')", name='valid_action'),
    )
    
    def __repr__(self):
        return f'<UserInteraction User {self.user_id} {self.action}s User {self.target_user_id} in Event {self.event_id}>'

class SessionLocation(db.Model):
    """Physical location where sessions take place (e.g., 'Main Hall', 'Conference Room A')"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    event = db.relationship('Event', backref='session_locations')
    
    def __repr__(self):
        return f'<SessionLocation {self.name} for Event {self.event_id}>'

class EventSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Morning Session"
    day_number = db.Column(db.Integer, nullable=False)  # e.g., 1 for Day 1, 2 for Day 2
    start_time = db.Column(db.Time, nullable=False)  # Time only (e.g., 09:00)
    end_time = db.Column(db.Time, nullable=False)  # Time only (e.g., 12:00)
    location_description = db.Column(db.String(200), nullable=True)  # General location info (deprecated, use session_location)
    session_location_id = db.Column(db.Integer, db.ForeignKey('session_location.id'), nullable=True)
    matching_enabled = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    event = db.relationship('Event', backref='sessions')
    session_location = db.relationship('SessionLocation', backref='sessions')
    
    def __repr__(self):
        return f'<EventSession {self.name} for Event {self.event_id}>'

# Association table for MeetingPoint <-> SessionLocation
meeting_point_locations = db.Table('meeting_point_locations',
    db.Column('meeting_point_id', db.Integer, db.ForeignKey('meeting_location.id'), primary_key=True),
    db.Column('session_location_id', db.Integer, db.ForeignKey('session_location.id'), primary_key=True)
)

class MeetingPoint(db.Model):
    """Specific meeting spot within a session location (e.g., 'Table 1', 'Booth 5')"""
    __tablename__ = 'meeting_location'  # Keep existing table name for backward compatibility
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    # session_location_id kept for backward compatibility during migration, but new code should use relationship
    session_location_id = db.Column(db.Integer, db.ForeignKey('session_location.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Hall 1 Table 11"
    capacity = db.Column(db.Integer, default=1)  # Number of concurrent meetings (pairs)
    
    # Relationships
    event = db.relationship('Event', backref='meeting_points')
    # Old single relationship - kept for backward compatibility only
    session_location = db.relationship('SessionLocation', foreign_keys=[session_location_id], backref='_old_meeting_points')
    # New many-to-many relationship - this is the primary one
    session_locations = db.relationship('SessionLocation',
                                       secondary=meeting_point_locations,
                                       backref='meeting_points')
    
    def __repr__(self):
        return f'<MeetingPoint {self.name} for Event {self.event_id}>'

class ParticipantAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('event_session.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='availabilities')
    event = db.relationship('Event', backref='participant_availabilities')
    session = db.relationship('EventSession', backref='availabilities')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'session_id', name='unique_user_session_availability'),
    )
    
    def __repr__(self):
        return f'<ParticipantAvailability User {self.user_id} Session {self.session_id}>'

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('event_session.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('meeting_location.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, cancelled, completed
    
    # Relationships
    match = db.relationship('Match', foreign_keys=[match_id], backref='meetings')
    session = db.relationship('EventSession', backref='meetings')
    location = db.relationship('MeetingPoint', backref='meetings')
    
    def __repr__(self):
        return f'<Meeting Match {self.match_id} at {self.start_time}>'
