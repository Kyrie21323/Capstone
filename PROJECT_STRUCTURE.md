# NFC Networking Assistant - Project Structure

## Overview
This project follows a clean, organized structure with source code separated from configuration and documentation.

## Directory Structure

```
Capstone/
├── main.py                 # Main entry point for the application
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
├── PROJECT_STRUCTURE.md   # This file
│
├── src/                   # Source code directory
│   ├── app.py            # Flask application and routes
│   ├── models.py         # Database models
│   ├── templates/        # Jinja2 templates
│   │   ├── admin/        # Admin-specific templates
│   │   └── *.html        # User-facing templates
│   ├── static/           # Static assets (CSS, JS, images)
│   └── uploads/          # User uploaded files
│       ├── 1/            # Event-specific uploads
│       └── 2/
│
├── instance/              # Instance-specific files
│   └── nfc_networking.db # SQLite database
│
└── migrations/            # Database migrations (Flask-Migrate)
    ├── versions/         # Migration files
    └── alembic.ini       # Alembic configuration
```

## Key Files

### `main.py`
- **Purpose**: Main entry point for the application
- **Usage**: Run with `python main.py`
- **Features**: Sets up Python path and imports the Flask app

### `src/app.py`
- **Purpose**: Core Flask application
- **Features**: 
  - Routes and view functions
  - Authentication logic
  - File upload handling
  - Admin panel functionality

### `src/models.py`
- **Purpose**: Database models
- **Models**:
  - `User`: User accounts and authentication
  - `Event`: Networking events
  - `Membership`: User-event relationships
  - `Resume`: File uploads and metadata

### `src/templates/`
- **Purpose**: HTML templates using Jinja2
- **Structure**:
  - `base.html`: Base template with common layout
  - `admin/`: Admin-specific pages
  - User-facing pages: `index.html`, `login.html`, `dashboard.html`, etc.

## Running the Application

1. **Activate virtual environment**:
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the application**:
   - Main site: http://127.0.0.1:5000
   - Admin panel: http://127.0.0.1:5000/admin

## Database Management

- **Database**: SQLite (stored in `instance/nfc_networking.db`)
- **Migrations**: Managed by Flask-Migrate
- **Commands**:
  ```bash
  flask db init      # Initialize migrations
  flask db migrate   # Create migration
  flask db upgrade   # Apply migrations
  ```

## Development Notes

- **Template System**: All templates extend `base.html` for consistency
- **File Uploads**: Stored in `src/uploads/` with event-based organization
- **Admin Access**: Requires `is_admin=True` flag in user account
- **Security**: Passwords hashed with Werkzeug, file type validation
- **Notifications**: Custom popup system replaces Flask flash messages
