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

📖 **Technical documentation**: [AGENTS.md](AGENTS.md) | [DATABASE.md](DATABASE.md) | [API.md](API.md)

---

## Technology Stack

- **Backend**: Flask 3.1.2, SQLAlchemy, Flask-Login
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

See [AGENTS.md](AGENTS.md) for detailed structure and navigation guide.

---

## Documentation

| Document | Description |
|----------|-------------|
| **[AGENTS.md](AGENTS.md)** | AI navigation guide - project structure and quick reference |
| **[SETUP.md](SETUP.md)** | Installation, configuration, and troubleshooting |
| **[DATABASE.md](DATABASE.md)** | Database models, operations, and management |
| **[API.md](API.md)** | Complete API routes reference |
| **[STRATEGY.md](STRATEGY.md)** | Competitive positioning and market strategy |
| **[ROADMAP.md](ROADMAP.md)** | 12-week development roadmap and feature priorities |

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

**Default Login** (after running setup script): `admin@nfcnetworking.com` / `admin123`

> **Note**: The app can also auto-create an admin user on startup if `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables are set. See [Deployment & Production Setup](#-deployment--production-setup) for details.

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

## 🚀 Deployment & Production Setup

Prophere includes automatic initialization features that make deployment to platforms like Render seamless, even without shell access. The app automatically handles database setup and admin user creation on first startup.

### 1. Deploying to Render

Deploy Prophere as a **Python 3 Web Service** on Render:

1. **Connect your GitHub repository** to Render
2. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt` (default)
   - **Start Command**: `python main.py`
3. **Set environment variables** (see Environment Variables section below)
4. **Deploy**: On first deployment, the service will automatically:
   - Create the SQLite database and all tables
   - Create the default admin user (if `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set)

> **Note**: This automation is especially important because Render's Free tier doesn't provide shell access, so all initialization must happen from within the app code.

### 2. Automatic Database Initialization

On startup, `main.py` automatically initializes the database if needed:

- The app inspects `SQLALCHEMY_DATABASE_URI` from the configuration
- If it points to a SQLite database file that **does not exist** (e.g., `instance/nfc_networking.db`), the app:
  - Enters a Flask application context
  - Calls `db.create_all()` to create all tables from SQLAlchemy models
  - Logs success and continues startup

**What this means**:
- ✅ No manual `flask db upgrade` needed in production
- ✅ No need to run `python scripts/setup_database.py` on Render
- ✅ New environments are self-bootstrapping
- ✅ Existing databases are never modified or reset

### 3. Automatic Admin Creation

After database initialization, the app automatically creates a default admin user if needed:

- **Checks for existing admin**: Queries for any `User` with `is_admin=True`
- **If admin exists**: Logs a message and skips creation (safe for subsequent deploys)
- **If NO admin exists**: Reads environment variables:
  - `ADMIN_EMAIL` - Email for the admin account
  - `ADMIN_PASSWORD` - Password for the admin account
- **If both env vars are set**: 
  - Creates a new `User` with `is_admin=True`
  - Securely hashes the password using Werkzeug
  - Commits the user to the database
  - Logs success message
- **If env vars are missing**: Logs a warning and continues (app starts normally)

This allows provisioning a default admin on Render without shell access. Once the first admin is created, subsequent deploys will **not** overwrite or recreate it.

### 4. Environment Variables (Local vs Production)

#### Local Development

For local development, you have flexibility:

- **Database**: Typically uses a local SQLite file (e.g., `instance/nfc_networking.db`)
- **Manual setup** (optional): Run `python scripts/setup_database.py --yes` and `python scripts/manage_users.py --admin` for manual control
- **Auto-admin** (optional): Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in a `.env` file to use the same auto-admin behavior locally

#### Render / Production

For production deployment on Render:

- **Database URI**: Configure `SQLALCHEMY_DATABASE_URI` via Render's Environment tab (typically a SQLite file in `instance/` for now; can be swapped to PostgreSQL later)
- **Admin credentials**: Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in Render's Environment tab to auto-create the first admin
- **Security**: Use different admin credentials than local dev for security
- **One-time creation**: Once the first admin is created, subsequent deploys will NOT overwrite or recreate it

#### Key Environment Variables

| Variable | Purpose | Required | Notes |
|----------|---------|----------|-------|
| `SQLALCHEMY_DATABASE_URI` | Database location | Yes | SQLite for now; PostgreSQL-ready |
| `ADMIN_EMAIL` | Initial admin login email | Production only | Set in Render Environment tab |
| `ADMIN_PASSWORD` | Initial admin password | Production only | Set in Render Environment tab |
| `SECRET_KEY` | Flask session secret | Recommended | Use a strong random key in production |
| `FLASK_ENV` | Environment mode | Optional | `production` for production |

---

## Strategic Planning

**New to the project?** Start with:
1. [AGENTS.md](AGENTS.md) - Project structure and code navigation
2. [STRATEGY.md](STRATEGY.md) - Competitive positioning and market analysis
3. [ROADMAP.md](ROADMAP.md) - 12-week development plan and priorities

**Technical references:** [DATABASE.md](DATABASE.md) | [API.md](API.md)

---

## Support

For issues or questions:
1. Check documentation in relevant `.md` files
2. Review [DATABASE.md](DATABASE.md) for troubleshooting
3. See [SETUP.md](SETUP.md) for installation issues
4. Create GitHub issue with detailed information

---

**Built with ❤️ at NYU Abu Dhabi**
