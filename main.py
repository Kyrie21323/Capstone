#!/usr/bin/env python3
"""
NFC Networking Assistant - Main Entry Point
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the Flask app
from app import app, db
from models import User

def check_and_init_db():
    """Check if database needs initialization"""
    with app.app_context():
        try:
            # Try to query the database
            User.query.count()
            print("✅ Database is ready!")
        except Exception:
            print("⚠️  Database not initialized. Running initialization...")
            # Import and run the init script
            from init_db import init_database
            init_database()

if __name__ == '__main__':
    check_and_init_db()
    app.run(debug=True)
