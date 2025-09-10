from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
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
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
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
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique user-event pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event'),)
    
    def __repr__(self):
        return f'<Membership User {self.user_id} -> Event {self.event_id}>'

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
