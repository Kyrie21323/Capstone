# NFC Networking Assistant

A Flask-based web application for NFC-powered networking at events.

## About This Project

The NFC Networking Assistant is designed to revolutionize professional networking at events by leveraging NFC (Near Field Communication) technology. This application serves as the foundation for a comprehensive networking platform that helps attendees connect meaningfully and track their professional interactions.

### Vision
At large events, attendees often struggle to:
- Remember who they met and what they discussed
- Identify who they should meet based on shared interests
- Track meaningful connections beyond business card exchanges
- Follow up effectively after the event

### Solution
This platform provides:
- **Smart Event Management**: Organizers can create events with unique access codes
- **Professional Profile Management**: Users can upload resumes and manage their professional information
- **Intelligent Networking**: Future NFC integration will enable automatic contact exchange and interaction tracking
- **Relationship Mapping**: Visual representation of professional networks and connections
- **Follow-up Assistance**: Automated reminders and suggested next steps

### Current Features (MVP)
- User authentication and profile management
- Event-based networking with unique access codes
- Resume upload and management
- Admin panel for event and user management
- UI with custom notification system

### Future Roadmap
- **NFC Integration**: Tap-to-connect functionality for seamless contact exchange
- **AI-Powered Matching**: Machine learning algorithms to suggest relevant connections
- **Network Visualization**: Interactive graphs showing professional relationships
- **Smart Recommendations**: Personalized suggestions for who to meet next
- **Post-Event Analytics**: Insights on networking effectiveness and follow-up opportunities

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite with Flask-SQLAlchemy ORM
- **Authentication**: Flask-Login with secure password hashing
- **Frontend**: HTML5, CSS3, JavaScript
- **File Management**: Secure file uploads with validation
- **Database Migrations**: Flask-Migrate for schema management

### Target Audience
- **Event Organizers**: Conference planners, career fair coordinators, networking event hosts
- **Professional Attendees**: Job seekers, entrepreneurs, industry professionals
- **Educational Institutions**: Universities hosting career fairs and networking events
- **Corporate Events**: Company networking sessions, industry meetups, trade shows


## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Access the Application

- **Main Site**: http://127.0.0.1:5000
- **Admin Panel**: http://127.0.0.1:5000/admin

## Default Login Credentials

- **🚀 Super Admin**: admin@nfcnetworking.com / admin123
- **👥 Regular Users**: [email] / password123

## Sample Events

- **NYUAD2025** - NYUAD Career Fair 2025
- **TECH2025** - Tech Conference Dubai  
- **STARTUP2025** - Startup Networking Event

## Documentation

- **[TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)** - Complete technical reference, architecture, implementation details, and project structure