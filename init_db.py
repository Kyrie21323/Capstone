#!/usr/bin/env python3
"""
Database Initialization Script
Creates tables and populates with sample data
"""

import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db
from models import User, Event, Membership, Resume
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with tables and sample data"""
    with app.app_context():
        print("🗃️  Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if data already exists
        if User.query.count() > 0:
            print("ℹ️  Database already has data. Skipping sample data creation.")
            return
        
        print("👤 Creating super admin account...")
        super_admin = User(
            name='Super Admin',
            email='admin@nfcnetworking.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.session.add(super_admin)
        
        print("📅 Creating sample events...")
        sample_events = [
            {
                'name': 'NYUAD Career Fair 2025',
                'code': 'NYUAD2025',
                'description': 'Join us for the largest career fair at NYU Abu Dhabi! Connect with top employers from various industries including technology, finance, consulting, and more. This event brings together students, recent graduates, and industry professionals for meaningful networking opportunities and career exploration.',
                'start_date': datetime(2025, 3, 15),
                'end_date': datetime(2025, 3, 15)
            },
            {
                'name': 'Tech Conference Dubai',
                'code': 'TECH2025',
                'description': 'The premier technology conference in the Middle East featuring cutting-edge innovations, AI developments, and digital transformation strategies. Network with tech leaders, entrepreneurs, and developers while exploring the latest trends in software development, cybersecurity, and emerging technologies.',
                'start_date': datetime(2025, 4, 20),
                'end_date': datetime(2025, 4, 22)
            },
            {
                'name': 'Startup Networking Event',
                'code': 'STARTUP2025',
                'description': 'A dynamic networking event designed for entrepreneurs, investors, and startup enthusiasts. Share ideas, find co-founders, connect with potential investors, and learn from successful startup founders. Perfect for anyone looking to launch their next venture or join the startup ecosystem.',
                'start_date': datetime(2025, 5, 10),
                'end_date': datetime(2025, 5, 10)
            }
        ]
        
        for event_data in sample_events:
            event = Event(
                name=event_data['name'],
                code=event_data['code'],
                description=event_data['description'],
                start_date=event_data['start_date'],
                end_date=event_data['end_date'],
                created_at=datetime.utcnow()
            )
            db.session.add(event)
        
        print("👥 Creating sample regular users...")
        sample_users = [
            {
                'name': 'John Smith',
                'email': 'john.smith@email.com',
                'password': 'password123'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@email.com',
                'password': 'password123'
            },
            {
                'name': 'Ahmed Al-Rashid',
                'email': 'ahmed.rashid@email.com',
                'password': 'password123'
            }
        ]
        
        for user_data in sample_users:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                is_admin=False,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Sample data created successfully!")
        print("\n📊 Database Summary:")
        print(f"   👤 Users: {User.query.count()} (1 super admin, {User.query.filter_by(is_admin=False).count()} regular)")
        print(f"   📅 Events: {Event.query.count()}")
        print(f"   📄 Resumes: {Resume.query.count()}")
        print(f"   🔗 Memberships: {Membership.query.count()}")
        
        print("\n🔑 Login Credentials:")
        print("   🚀 SUPER ADMIN: admin@nfcnetworking.com / admin123")
        print("   👥 Regular users: [email] / password123")
        
        print("\n🎉 Database initialization complete!")

if __name__ == '__main__':
    init_database()
