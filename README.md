# NFC Networking Platform

A Flask-based networking platform for events with intelligent matching, meeting scheduling, and location management capabilities.

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-Academic-orange.svg)

---

## Overview

The NFC Networking Platform revolutionizes professional networking at events by providing:
- **Smart Event Management** - Create events with unique access codes
- **Intelligent Matching** - NLP-based matching using keywords and documents  
- **Automated Scheduling** - Meeting time and location allocation
- **Network Visualization** - Interactive professional network graphs

### Vision

At large events, attendees struggle to track connections and coordinate meetings. This platform provides intelligent matching, automated scheduling, and seamless contact management to maximize networking effectiveness.

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

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd Capstone
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate
pip install -r requirements.txt

# Setup database
python scripts/setup_database.py
```

### Run the Application

```bash
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

- **Admin**: `admin@nfcnetworking.com` / `admin123`
- **Sample Events**: NYUAD2025, TECH2025, STARTUP2025

📖 **Full installation guide**: [SETUP.md](SETUP.md)

---

## Key Features

### For Attendees
✅ Join events with unique codes  
✅ Upload resumes for intelligent matching  
✅ Tinder-style matching interface  
✅ View confirmed matches  
✅ Indicate meeting availability  

### For Event Managers
✅ Create and manage events  
✅ Define sessions and locations  
✅ Run automated meeting allocation  
✅ Analytics dashboard  
✅ Export/import database  

📖 **Full feature documentation**: [FEATURES.md](FEATURES.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| **[SETUP.md](SETUP.md)** | Installation, configuration, and troubleshooting |
| **[FEATURES.md](FEATURES.md)** | Detailed feature descriptions and usage |
| **[DATABASE.md](DATABASE.md)** | Database models, operations, and management |
| **[API.md](API.md)** | Complete API routes reference |
| **[DEVELOPMENT.md](DEVELOPMENT.md)** | Technical architecture and developer guide |

---

## Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, Flask-Login
- **Database**: SQLite (development), PostgreSQL-ready
- **NLP**: Sentence Transformers for semantic matching
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2
- **File Processing**: PyPDF2, python-docx

---

## Project Structure

```
Capstone/
├── src/                    # Application code
│   ├── app.py             # Main Flask app
│   ├── models.py          # Database models
│   ├── matching_engine.py # NLP matching
│   └── templates/         # HTML templates
├── scripts/               # Management scripts
│   ├── manage_users.py    # User management
│   ├── setup_database.py  # Database setup
│   └── import_database.py # Export/import
├── uploads/               # User files
├── migrations/            # Database migrations
└── main.py               # Entry point
```

---

## Common Tasks

### Create Users
```bash
# Create admin
python scripts/manage_users.py --admin

# Create event manager
python scripts/manage_users.py --manager user@example.com

# List all users
python scripts/manage_users.py --list
```

### Database Operations
```bash
# Export database
python scripts/import_database.py --export

# Import database
python scripts/import_database.py --import

# Fix missing tables
python scripts/setup_database.py --fix
```

---

## Recent Updates

### Version 1.1.0 (December 2025)

**New Features**:
- Meeting scheduling system with sessions and locations
- Automated meeting allocation algorithm
- Participant availability management
- Database import/export tools
- Consolidated management scripts

**Bug Fixes**:
- Fixed sessions and locations pages (missing imports)
- Improved error handling
- Enhanced validation

**Improvements**:
- Restructured documentation (6 focused files)
- Better CLI interfaces
- Comprehensive setup guide

---

## Development

### Prerequisites
- Python 3.8+
- pip

### Setup Development Environment
```bash
source .venv/bin/activate
python main.py
```

**Debug mode** enabled by default at http://127.0.0.1:5000

📖 **Developer guide**: [DEVELOPMENT.md](DEVELOPMENT.md)

---

## Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 'src.app:app'
```

**Important**:
- Change `SECRET_KEY` in production
- Use PostgreSQL instead of SQLite
- Enable HTTPS/SSL
- Configure proper file storage

📖 **Deployment guide**: [DEVELOPMENT.md#production-deployment](DEVELOPMENT.md#production-deployment)

---

## Future Roadmap

- 🔜 **NFC Integration** - Tap-to-connect functionality
- 🔜 **Mobile Apps** - iOS and Android applications
- 🔜 **Messaging System** - Direct messages between matches
- 🔜 **Calendar Integration** - Export to Google/iCal
- 🔜 **Advanced Analytics** - Network effectiveness insights

---

## License and Contributors

This project is a part of *NYU Abu Dhabi Interactive Media Capstone 2026*.

The ownership lies to the repository owners and contributors.

## Support

For issues or questions:
1. Check documentation in relevant `.md` files
2. Review [DATABASE.md](DATABASE.md) for troubleshooting
3. See [SETUP.md](SETUP.md) for installation issues
4. Create GitHub issue with detailed information

---

**Built with ❤️ at NYU Abu Dhabi**