# NFC Networking Platform

A Flask-based networking platform for events with intelligent matching capabilities.

## Project Structure

```
Capstone/
├── src/                    # Main application code
│   ├── app.py             # Flask application
│   ├── models.py          # Database models
│   ├── matching_engine.py # NLP matching system
│   └── templates/         # HTML templates
│       ├── admin/         # Admin interface
│       ├── base.html      # Base template
│       ├── dashboard.html # User dashboard
│       ├── login.html     # Login page
│       └── ...
├── scripts/               # Utility scripts
│   ├── sync_with_files.py # Database + file sync
│   ├── fix_database.py    # Database repair
│   ├── setup_database.py  # Database setup
│   └── ...
├── docs/                  # Documentation
│   ├── DATABASE_SETUP.md
│   └── TECHNICAL_DOCUMENTATION.md
├── exports/               # Database exports
├── migrations/            # Database migrations
├── uploads/               # User uploaded files
├── instance/              # Database files
├── main.py               # Application entry point
├── requirements.txt       # Python dependencies
└── README.md            # This file
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Access the application:**
   - Open http://localhost:5000
   - Login as Event Attendee or Event Manager

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

## Features

- **Role-based Authentication**: Event Attendee vs Event Manager
- **Event Management**: Create, join, and manage events
- **Intelligent Matching**: NLP-based user matching using keywords and documents
- **Document Upload**: Resume/portfolio upload and management
- **Real-time Matching**: Tinder-style matching interface
- **Cross-device Sync**: Database and file synchronization

## Development

The application uses:
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Flask-Migrate**: Database migrations
- **Sentence Transformers**: NLP matching
- **Bootstrap**: UI framework
