# NFC Networking Assistant - Technical Documentation

This document provides comprehensive technical details about the NFC Networking Assistant implementation, architecture, and features.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Models](#database-models)
3. [Security Implementation](#security-implementation)
4. [Feature Implementation Details](#feature-implementation-details)
5. [User Interface Architecture](#user-interface-architecture)
6. [API Routes and Endpoints](#api-routes-and-endpoints)

## Architecture Overview

### Technology Stack

- **Backend Framework**: Flask 2.3.3 (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Frontend**: HTML5, CSS3, JavaScript with Jinja2 templating
- **File Management**: Secure uploads with validation
- **Database Migrations**: Flask-Migrate with Alembic

### Project Structure

```
Capstone/
├── main.py                 # Application entry point
├── init_db.py             # Database initialization script
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── TECHNICAL_DOCUMENTATION.md # This file
├── src/                   # Source code directory
│   ├── app.py            # Flask application and routes
│   ├── models.py         # Database models
│   ├── templates/        # Jinja2 HTML templates
│   │   ├── admin/        # Admin-specific templates
│   │   └── *.html        # User-facing templates
│   ├── static/           # Static assets (CSS, JS, images)
│   └── instance/         # Instance-specific files
│       └── nfc_networking.db # SQLite database
├── uploads/              # User uploaded files
│   ├── 1/                # Event-specific uploads
│   └── 2/
└── migrations/           # Database migrations (Flask-Migrate)
    ├── versions/         # Migration files
    └── alembic.ini       # Alembic configuration
```

### Key Files

#### `main.py`
- **Purpose**: Main entry point for the application
- **Usage**: Run with `python main.py`
- **Features**: Sets up Python path and imports the Flask app

#### `src/app.py`
- **Purpose**: Core Flask application
- **Features**: 
  - Routes and view functions
  - Authentication logic
  - File upload handling
  - Admin panel functionality

#### `src/models.py`
- **Purpose**: Database models
- **Models**:
  - `User`: User accounts and authentication
  - `Event`: Networking events
  - `Membership`: User-event relationships
  - `Resume`: File uploads and metadata

#### `src/templates/`
- **Purpose**: HTML templates using Jinja2
- **Structure**:
  - `base.html`: Base template with common layout
  - `admin/`: Admin-specific pages
  - User-facing pages: `index.html`, `login.html`, `dashboard.html`, etc.

## Database Models

### User Model

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='user', lazy=True)
    resumes = db.relationship('Resume', backref='user', lazy=True)
```

**Key Features:**
- Flask-Login integration with `UserMixin`
- Secure password storage with Werkzeug hashing
- Admin role management
- One-to-many relationships with memberships and resumes

### Event Model

```python
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='event', lazy=True)
    resumes = db.relationship('Resume', backref='event', lazy=True)
```

**Key Features:**
- Unique event codes for easy joining
- Rich text descriptions (300-word limit enforced)
- Optional date range configuration
- One-to-many relationships with memberships and resumes

### Membership Model

```python
class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique user-event pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event'),)
```

**Key Features:**
- Prevents duplicate event memberships
- Automatic timestamp tracking
- Foreign key relationships to User and Event models

### Resume Model

```python
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique user-event resume pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_resume'),)
```

**Key Features:**
- One resume per user per event constraint
- Complete file metadata tracking
- Secure filename storage
- File size and MIME type validation

## Security Implementation

### Password Security

- **Hashing Algorithm**: Werkzeug's `generate_password_hash()` with salt
- **Verification**: `check_password_hash()` for secure comparison
- **Storage**: Passwords never stored in plain text

### File Security

- **Type Validation**: Only PDF, DOC, DOCX files allowed
- **Size Limits**: 16MB maximum file size
- **Secure Naming**: `secure_filename()` prevents path traversal
- **Unique Filenames**: Timestamp-based naming prevents conflicts

### Access Control

- **Admin Routes**: `@admin_required` decorator protection
- **User Authorization**: File access restricted to file owners
- **Session Management**: Flask-Login handles secure sessions
- **CSRF Protection**: Flask-WTF integration ready

### File Access Security

```python
# Example: Secure file serving
@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    # Extract event_id and validate user access
    resume = Resume.query.filter_by(filename=actual_filename, event_id=event_id).first()
    
    if resume.user_id != current_user.id:
        flash('You are not authorized to access this file!', 'error')
        return redirect(url_for('dashboard'))
```

## Feature Implementation Details

### User Authentication System

#### Registration Process

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Validate email uniqueness
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        # Create user with hashed password
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
```

**Features:**
- Email uniqueness validation
- Secure password hashing
- Automatic user creation
- Flash message feedback

#### Login System

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
```

**Features:**
- Email/password authentication
- Session management with Flask-Login
- Automatic redirect based on user role
- Secure logout with session cleanup

### Event Management System

#### Event Creation (Admin Only)

```python
@app.route('/admin/events/create', methods=['GET', 'POST'])
@admin_required
def admin_create_event():
    # Validate event code uniqueness
    if Event.query.filter_by(code=code).first():
        flash(f'Event code "{code}" already exists!', 'error')
        return render_template('admin/create_event.html')
    
    # Create event with validation
    event = Event(
        name=name,
        code=code,
        description=description if description else None,
        start_date=datetime.strptime(start_date, '%Y-%m-%d') if start_date else None,
        end_date=datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    )
```

**Features:**
- Unique event code validation
- Rich text descriptions with word count limits
- Optional date configuration
- Admin-only access control

#### Event Participation

```python
@app.route('/join_event', methods=['POST'])
@login_required
def join_event():
    event_code = request.form['event_code'].strip()
    event = Event.query.filter_by(code=event_code).first()
    
    # Check for existing membership
    existing_membership = Membership.query.filter_by(
        user_id=current_user.id, 
        event_id=event.id
    ).first()
    
    if existing_membership:
        flash(f'You are already a member of "{event.name}"!', 'info')
        return redirect(url_for('dashboard'))
```

**Features:**
- Event code-based joining
- Duplicate membership prevention
- User feedback and validation
- Dashboard integration

### Resume Management System

#### Upload Process

```python
@app.route('/upload_resume/<int:event_id>', methods=['GET', 'POST'])
@login_required
def upload_resume(event_id):
    # Validate file type and size
    allowed_extensions = {'pdf', 'doc', 'docx'}
    if not ('.' in file.filename and 
            file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        flash('Only PDF, DOC, and DOCX files are allowed!', 'error')
        return redirect(url_for('upload_resume', event_id=event_id))
    
    # Generate secure filename
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{current_user.id}_{event_id}_{timestamp}_{filename}"
```

**Features:**
- Event-specific upload requirements
- File type and size validation
- Secure filename generation
- Database metadata tracking
- File organization by event

### Admin Panel Features

#### Dashboard Analytics

```python
@app.route('/admin')
@admin_required
def admin_dashboard():
    # Get statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_events = Event.query.count()
    total_memberships = Membership.query.count()
    total_resumes = Resume.query.count()
    
    # Get recent data
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
```

**Features:**
- Real-time platform statistics
- Recent activity tracking
- User and event analytics
- Performance metrics

#### User Management

```python
@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin_users'))
    
    # Cascade delete associated data
    Membership.query.filter_by(user_id=user_id).delete()
    Resume.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
```

**Features:**
- User listing and management
- Admin role promotion/demotion
- User deletion with data cleanup
- Self-protection mechanisms

## API Routes and Endpoints

### Public Routes
- `GET /` - Landing page
- `GET /register` - User registration form
- `POST /register` - Process registration
- `GET /login` - Login form
- `POST /login` - Process login

### User Routes (Login Required)
- `GET /dashboard` - User dashboard
- `POST /join_event` - Join event with code
- `GET /upload_resume/<event_id>` - Resume upload form
- `POST /upload_resume/<event_id>` - Process resume upload
- `GET /view_resume/<resume_id>` - View uploaded resume
- `GET /uploads/<path:filename>` - Serve uploaded files
- `GET /logout` - User logout

### Admin Routes (Admin Required)
- `GET /admin` - Admin dashboard
- `GET /admin/events` - Event management
- `GET /admin/events/create` - Create event form
- `POST /admin/events/create` - Process event creation
- `GET /admin/events/<id>/edit` - Edit event form
- `POST /admin/events/<id>/edit` - Process event update
- `POST /admin/events/<id>/delete` - Delete event
- `GET /admin/users` - User management
- `POST /admin/users/<id>/toggle_admin` - Toggle admin status
- `POST /admin/users/<id>/delete` - Delete user
- `POST /admin/cleanup-files` - Cleanup orphaned files


This technical documentation provides a comprehensive overview of the NFC Networking Assistant's implementation, covering all major aspects of the system architecture, security, and functionality.
