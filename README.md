# NFC Networking Platform

A Flask-based networking platform for events with intelligent matching capabilities.

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
- **Role-based Authentication**: Event Attendee vs Event Manager login
- **Event Management**: Create, join, and manage events with unique codes
- **AI-Powered Matching**: Machine learning algorithms (Sentence Transformers) using semantic similarity to suggest relevant connections based on keywords and document content
- **Smart Recommendations**: Personalized suggestions for who to meet next, filtering out already-interacted users and ranking by compatibility scores
- **Document Upload**: Resume/portfolio upload and management
- **Tinder-style Matching**: Interactive matching interface with like/pass functionality
- **Post-match Features**: View matches, messaging, and contact exchange
- **Network Visualization**: Interactive graph visualizer showing event attendee connections and mutual matches
  - **Event Network Graph**: Admin-only visualization of attendee networks with force-directed layout
  - **Dev Graph Visualizer**: Synthetic dataset testing tool for stress testing graph visualizations
- **Admin Panel**: Complete event and user management system
- **Cross-device Sync**: Database and file synchronization between devices

### Future Roadmap
- **NFC Integration**: Tap-to-connect functionality for seamless contact exchange
- **Post-Event Analytics**: Insights on networking effectiveness and follow-up opportunities

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite with Flask-SQLAlchemy ORM
- **Authentication**: Flask-Login with secure password hashing
- **Frontend**: HTML5, CSS3, JavaScript with custom notification system
- **Graph Visualization**: Cytoscape.js for interactive network graphs
- **NLP Matching**: Sentence Transformers for intelligent user matching
- **File Management**: Secure file uploads with validation
- **Database Migrations**: Flask-Migrate for schema management
- **Cross-device Sync**: JSON-based data export/import system

### Target Audience
- **Event Organizers**: Conference planners, career fair coordinators, networking event hosts
- **Professional Attendees**: Job seekers, entrepreneurs, industry professionals
- **Educational Institutions**: Universities hosting career fairs and networking events
- **Corporate Events**: Company networking sessions, industry meetups, trade shows


## Quick Start
```bash
# Create and activate virtual environment
python -m venv .venv
# Windows: .venv\Scripts\Activate
# macOS/Linux: source .venv/bin/activate
```
### Option 1: Automated Setup (Recommended)
```bash
python scripts/setup_database.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Access the Application

- **Main Site**: http://127.0.0.1:5000
- **Admin Panel**: http://127.0.0.1:5000/admin

### Graph Visualizer (Admin Only)

- **Event Network Graph**: `/event/<event_id>/graph` - Visualize attendee connections for a specific event
- **Dev Graph Visualizer**: 
  - `/admin/graph/dev/small` - Small synthetic dataset
  - `/admin/graph/dev/medium` - Medium synthetic dataset
  - `/admin/graph/dev/large` - Large synthetic dataset

## Default Login Credentials

- **🚀 Super Admin**: admin@nfcnetworking.com / admin123
- **👥 Regular Users**: [email] / password123

## Sample Events

- **NYUAD2025** - NYUAD Career Fair 2025
- **TECH2025** - Tech Conference Dubai  
- **STARTUP2025** - Startup Networking Event

## Database Management

### Setup Database
```bash
python scripts/setup_database.py
```

### Sync Between Devices
```bash
# Export (on source device)
python scripts/sync_with_files.py

# Import (on target device)  
python scripts/sync_with_files.py
```

### Fix Database Issues
```bash
python scripts/fix_database.py
```

## Documentation

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Clean project organization and structure
- **[docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md)** - Complete technical reference
- **[docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md)** - Database setup and management guide