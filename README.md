# Prophere

A Flask-based networking platform for events with intelligent matching, meeting scheduling, and location management capabilities.

![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-Academic-orange.svg)

---

## Overview

Prophere revolutionizes professional networking at events by providing:
- **Smart Event Management** - Create events with unique access codes
- **Intelligent Matching** - NLP-based matching using keywords and documents  
- **Automated Scheduling** - Meeting time and location allocation
- **Network Visualization** - Interactive professional network graphs

### Vision

At large events, attendees struggle to track connections and coordinate meetings. This platform provides intelligent matching, automated scheduling, and seamless contact management to maximize networking effectiveness.

### Target Audience
- **Event Organizers**: Conference planners, career fair coordinators, networking event hosts
- **Professional Attendees**: Job seekers, entrepreneurs, industry professionals
- **Educational Institutions**: Universities hosting career fairs and networking events
- **Corporate Events**: Company networking sessions, industry meetups, trade shows

## Key Features

### For Attendees
✅ Join events with unique codes  
✅ Upload resumes for intelligent matching  
✅ Select which sessions to attend  
✅ Tinder-style matching interface with session filtering  
✅ Instant Meeting Assignment: Matches are automatically scheduled in real-time
✅ Smart Availability Management: Automatic meeting validation and reassignment
✅ Real-time web and browser notifications for matches
✅ Automatic email calendar invites  

### For Event Managers
✅ Create and manage events with publishing workflow 
✅ Define event locations and sessions 
✅ Enable matching per session and configure meeting points 
✅ Analytics dashboard 
✅ Export/import database 
✅ Dual Notification System (Email + Web Push)

📖 **Full feature documentation**: [FEATURES.md](FEATURES.md)

---

## Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, Flask-Login
- **Database**: SQLite (development), PostgreSQL-ready
- **NLP**: Sentence Transformers for semantic matching
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2
- **Graph Visualization**: Cytoscape.js for interactive network graphs
- **File Processing**: PyPDF2, python-docx
- **Migrations**: Flask-Migrate for schema management

## Project Structure

```
Capstone/
├── src/                # Application code
│   ├── routes/         # Modular blueprints
│   ├── utils/          # Utilities and helpers
│   ├── templates/      # HTML templates
│   └── static/         # CSS and JavaScript
├── scripts/            # Management scripts
├── uploads/            # User files
├── migrations/         # Database migrations
└── main.py            # Entry point
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed architecture.

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

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd Capstone
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate
pip install -r requirements.txt

# Setup database
python scripts/setup_database.py

# Run application
python main.py
```

Access at http://127.0.0.1:5000

**Login**: `admin@nfcnetworking.com` / `admin123`

📖 **Full installation guide**: [SETUP.md](SETUP.md)

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

## Development & Deployment

For local development, production deployment, database migrations, and advanced configuration, see [DEVELOPMENT.md](DEVELOPMENT.md).

---

## Support

For issues or questions:
1. Check documentation in relevant `.md` files
2. Review [DATABASE.md](DATABASE.md) for troubleshooting
3. See [SETUP.md](SETUP.md) for installation issues
4. Create GitHub issue with detailed information

---

**Built with ❤️ at NYU Abu Dhabi**
