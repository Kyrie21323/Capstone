# Developer Guide

Technical documentation for developers working on Prophere.

## Project Structure

```
Capstone/
├── src/                       # Main application code
│   ├── app.py                # Application factory (160 lines)
│   ├── config.py             # Environment configuration
│   ├── models.py             # SQLAlchemy database models
│   ├── matching_engine.py    # NLP matching system
│   ├── allocation_engine.py  # Meeting allocation algorithm
│   ├── routes/               # Blueprint modules (NEW)
│   │   ├── __init__.py      # Blueprint registration
│   │   ├── auth.py          # Authentication routes
│   │   ├── user.py          # User feature routes
│   │   ├── admin.py         # Admin panel routes
│   │   ├── matching.py      # Matching routes
│   │   ├── scheduling.py    # Scheduling routes
│   │   ├── api.py           # JSON API endpoints
│   │   └── utils.py         # Shared route utilities
│   ├── utils/               # Utility modules (ENHANCED)
│   │   ├── validators.py    # Input validation
│   │   ├── helpers.py       # Common functions
│   │   ├── decorators.py    # Custom decorators
│   │   ├── graph_utils.py   # Network graph generation
│   │   └── sample_graph_data.py
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── admin/          # Admin panel templates
│   │   ├── base.html       # Base template with modular JS
│   │   └── *.html          # Feature-specific templates
│   └── static/             # Static assets
│       ├── css/
│       │   └── style.css   # Design system with tokens
│       └── js/             # JavaScript modules (NEW)
│           ├── notifications.js
│           ├── modals.js
│           └── keywords.js
├── scripts/                  # Management scripts
│   ├── script_helpers.py    # Shared utilities
│   ├── manage_users.py      # User management CLI
│   ├── setup_database.py    # Database setup
│   └── import_database.py   # Export/import operations
├── migrations/              # Flask-Migrate migrations
├── uploads/                 # User uploaded files
├── exports/                 # Database exports
├── instance/                # Runtime database
│   └── nfc_networking.db
├── main.py                  # Application entry point
└── requirements.txt         # Python dependencies
```

---

## Technical Architecture

### Application Entry Point

**`main.py`**
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app

if __name__ == '__main__':
    app.run(debug=True)
```

Configures Python path and starts Flask application.

### Core Application

**`src/app.py`** (160 lines)
- Application factory pattern using `create_app()`
- Environment-based configuration loading
- Blueprint registration
- Extension initialization (SQLAlchemy, Flask-Login, Flask-Migrate)
- Error handlers

**Key Configurations**:
```python
# Load environment-specific config
from config import get_config
config_class = get_config()  # dev/test/prod
app.config.from_object(config_class)
```

### Blueprint Architecture

**`src/routes/__init__.py`**
Defines and registers all blueprints:
- `auth_bp` - Authentication (register, login, logout)
- `user_bp` - User features (dashboard, events, resumes)
- `admin_bp` - Admin panel (URL prefix: `/admin`)
- `matching_bp` - Matching system (URL prefix: `/event`)
- `scheduling_bp` - Scheduling (URL prefix: `/event`)
- `api_bp` - JSON endpoints (URL prefix: `/api`)

**Blueprint Files**:
- `routes/auth.py` - 111 lines
- `routes/user.py` - 380 lines
- `routes/admin.py` - 305 lines
- `routes/matching.py` - 355 lines
- `routes/scheduling.py` - 165 lines
- `routes/api.py` - 55 lines

### Configuration Management

**`src/config.py`**

Environment-specific configurations:
```python
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///...'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://...'
```

### Environment Configuration

**Using Different Environments:**

```bash
# Development (default)
python main.py

# Production
FLASK_ENV=production python main.py

# Testing
FLASK_ENV=testing pytest
```

**Environment Variables:**

Create a `.env` file for production:
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-very-secure-random-key-here-min-32-chars

# Database
DATABASE_URL=postgresql://user:password@localhost/prophere

# File Upload
UPLOAD_FOLDER=/var/www/prophere/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

**Configuration Class Selection:**

The app automatically selects the right config based on `FLASK_ENV`:
- `development` → `DevelopmentConfig` (default)
- `testing` → `TestingConfig`
- `production` → `ProductionConfig`

**Programmatic Config Selection:**
```python
from src.app import create_app

# Explicit environment
app = create_app('production')

# Or use environment variable
import os
app = create_app(os.getenv('FLASK_ENV'))
```

### Database Models

**`src/models.py`**

All models inherit from `db.Model` (SQLAlchemy):
- `User` - Authentication and profiles
- `Event` - Event information
- `Membership` - User-event relationships
- `Resume` - Document metadata
- `Match` - Confirmed connections
- `UserInteraction` - Like/pass tracking
- `EventSession` - Time slots
- `MeetingLocation` - Meeting places
- `ParticipantAvailability` - User availability

### Matching Engine

**`src/matching_engine.py`**

```python
class MatchingEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def extract_text(self, file_path):
        # Extracts text from PDF/DOCX
        
    def compute_similarity(self, user1, user2, event_id):
        # Multi-factor scoring:
        # - Keyword similarity (60%)
        # - Document similarity (40%)
```

Uses **Sentence Transformers** for semantic embeddings.

### Allocation Engine

**`src/allocation_engine.py`**

Constraint satisfaction algorithm for meeting scheduling:
1. Collect participant availability
2. Match users with overlapping time slots
3. Assign meeting locations respecting capacity
4. Optimize for maximum meetings

---

## Security Implementation

### Password Security
- **Algorithm**: Werkzeug's PBKDF2-SHA256
- **Salt**: Automatic random salt per password
- **Hashing**: `generate_password_hash(password)`
- **Verification**: `check_password_hash(hash, password)`
- **Storage**: Only hashes stored, never plaintext

### File Security
- **Type Validation**: Only PDF, DOC, DOCX allowed
- **Size Limit**: 16MB maximum
- **Secure Naming**: `secure_filename()` prevents path traversal
- **Unique Filenames**: Timestamp-based to prevent conflicts
- **User Isolation**: Files in user-specific directories
- **Access Control**: Only file owner can access

### Authentication

**Flask-Login Integration**:
```python
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**Decorators**:
- `@login_required` - Must be authenticated
- `@admin_required` - Must be admin/manager

### Input Validation

**`src/utils/validators.py`**
- `validate_email()` - Email format validation
- `validate_password()` - Password strength (6+ chars)
- `validate_keywords()` - Keyword count and format
- `validate_file_extension()` - File type checking
- `sanitize_keywords()` - Clean and deduplicate keywords

### Custom Decorators

**`src/utils/decorators.py`**
- `@admin_required` - Must be authenticated admin
- `@prevent_admin_action` - Block admins from user actions
- `@requires_membership` - Check event membership
- `@anonymous_required` - Redirect authenticated users
- `@log_action()` - Action logging decorator factory

### Helper Functions

**`src/utils/helpers.py`**
- `format_datetime()`, `format_date()` - Date formatting
- `truncate_text()` - Text truncation with suffix  
- `get_file_size_str()` - Human-readable file sizes
- `clean_filename()` - Safe filesystem names
- `parse_keywords()` - Parse comma-separated keywords

### JavaScript Modules

**`src/static/js/`**

Reusable JavaScript modules extracted from templates:
- `notifications.js` - Toast notification system
- `modals.js` - Confirmation dialog system
- `keywords.js` - Tag-based keyword input

---

## Dependencies

### Core Framework
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Flask-Migrate==4.0.4
```

### NLP & ML
```
sentence-transformers==2.2.2
torch>=1.6.0
```

### Document Processing
```
PyPDF2==3.0.1
python-docx==0.8.11
```

### Database
```
SQLAlchemy==2.0.19
alembic==1.11.1
```

See `requirements.txt` for complete list.

---

## Development Workflow

### Local Development

1. **Activate Environment**:
   ```bash
   source .venv/bin/activate
   ```

2. **Run Application**:
   ```bash
   python main.py
   ```

3. **Access**:
   - Application: http://127.0.0.1:5000
   - Admin Panel: http://127.0.0.1:5000/admin

### Debug Mode

Enabled by default in `main.py`:
```python
app.run(debug=True)
```

**Features**:
- Auto-reload on code changes
- Detailed error pages
- Interactive Python debugger

### Database Migrations

**Workflow**:
```bash
# 1. Modify models in src/models.py

# 2. Create migration
cd src
flask db migrate -m "Add new field to User model"

# 3. Review migration in migrations/versions/

# 4. Apply migration
flask db upgrade

# 5. Test changes
```

**Rollback**:
```bash
cd src
flask db downgrade
```

---

## Testing

### Manual Testing

1. **Create Test Users**:
   ```bash
   python scripts/manage_users.py --admin
   python scripts/manage_users.py --attendee test@example.com -p password123
   ```

2. **Test Event Flow**:
   - Register/login
   - Join event with code
   - Upload resume
   - Test matching

3. **Test Admin Features**:
   - Login as admin
   - Create events
   - Manage sessions/locations
   - Run allocation

### Unit Testing (Coming Soon)

Planned test structure:
```
tests/
├── test_models.py
├── test_auth.py
├── test_matching.py
├── test_routes.py
└── conftest.py
```

---

## Production Deployment

### Environment Setup

**1. Set Environment Variables:**
```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export DATABASE_URL=postgresql://user:pass@localhost/prophere
```

**2. Install Production Dependencies:**
```bash
pip install gunicorn psycopg2-binary
```

### Database Migration

**Switch from SQLite to PostgreSQL:**
```bash
# Export data from development
python scripts/import_database.py --export

# Update DATABASE_URL environment variable
export DATABASE_URL=postgresql://user:pass@localhost/prophere

# Import data to production
python scripts/import_database.py --import
```

### Production Server

**Run with Gunicorn:**
```bash
# Basic
gunicorn -w 4 -b 0.0.0.0:8000 'src.app:create_app()'

# With timeout for ML operations
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 'src.app:create_app()'

# With environment
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:8000 'src.app:create_app("production")'
```

**Gunicorn Options**:
- `-w 4` - 4 worker processes
- `-b 0.0.0.0:8000` - Bind to all interfaces on port 8000
- `--timeout 120` - Increase timeout for ML operations

### Nginx Configuration

Example reverse proxy:
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /uploads/ {
        alias /var/www/uploads/;
    }
}
```

### SSL/HTTPS

Use Let's Encrypt:
```bash
sudo certbot --nginx -d example.com
```

### File Storage

For production, consider:
- **AWS S3** for uploaded files
- **PostgreSQL** instead of SQLite
- **Redis** for session storage

---

## Performance Optimization

### Caching Recommendations
- Cache NLP model embeddings
- Cache user similarity scores
- Use Redis for session storage
- CDN for static files

### Database Optimization
- Add indexes on frequently queried fields
- Use database connection pooling
- Implement query result caching
- Regular VACUUM on PostgreSQL

### ML Model Optimization
- Load model once at startup
- Batch process similarity calculations
- Consider smaller model variants
- Use GPU if available

---

## Code Style & Conventions

### Python
- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints where applicable

### Templates
- Jinja2 for HTML templating
- Keep logic minimal in templates
- Use template inheritance (`{% extends "base.html" %}`)

### Database
- Use SQLAlchemy ORM (no raw SQL)
- Explicit foreign keys and indexes
- Cascade deletes where appropriate
- Migrations for all schema changes

###Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**: Ensure Python path includes `src`:
```python
import sys
sys.path.insert(0, 'src')
```

### ML Model Issues

**Problem**: Slow similarity calculations

**Solution**:
- Use smaller model (current: `all-MiniLM-L6-v2`)
- Cache embeddings
- Batch process users

### File Upload Errors

**Problem**: Large files rejected

**Solution**: Increase `MAX_CONTENT_LENGTH`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

---

For more information:
- [SETUP.md](SETUP.md) - Installation guide
- [FEATURES.md](FEATURES.md) - Feature documentation
- [DATABASE.md](DATABASE.md) - Database operations
- [API.md](API.md) - API reference
