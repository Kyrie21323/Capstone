# ROUTES - BLUEPRINT MODULES

**Parent:** src/AGENTS.md  
**Purpose:** Modular route handlers (feature-based blueprints)

## OVERVIEW

8 Python files organizing all routes. Blueprint pattern with URL prefixes.

## STRUCTURE

```
routes/
├── __init__.py       # Blueprint registration
├── auth.py           # Register, login, logout
├── user.py           # Dashboard, events, resumes (19KB - large file)
├── admin.py          # Admin panel, analytics
├── matching.py       # Tinder UI, like/pass (30KB - largest file)
├── scheduling.py     # Sessions, availability, allocation
├── api.py            # JSON endpoints
└── utils.py          # Shared route helpers
```

## WHERE TO LOOK

| Blueprint | URL Prefix | Purpose | Key Routes |
|-----------|------------|---------|------------|
| `auth_bp` | `/` | Authentication | `/register`, `/login`, `/logout` |
| `user_bp` | `/` | User features | `/dashboard`, `/join_event`, `/upload_resume` |
| `admin_bp` | `/admin` | Admin panel | `/admin`, `/admin/users`, `/admin/events` |
| `matching_bp` | `/event/<id>` | Matching | `/matching`, `/like`, `/pass`, `/matches` |
| `scheduling_bp` | `/event/<id>` | Scheduling | `/sessions`, `/availability`, `/allocate` |
| `api_bp` | `/api` | JSON API | `/api/event/<id>/graph` |

## CONVENTIONS

### Blueprint Definition
```python
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    # ...
```

### POST-Redirect-GET
```python
@user_bp.route('/join_event', methods=['POST'])
@login_required
def join_event():
    # Process form
    flash('Success!', 'success')
    return redirect(url_for('user.dashboard'))
```

### Decorators
- `@login_required` - Must be authenticated
- `@admin_required` - Must be admin
- `@anonymous_required` - Redirect if logged in

### Flash Messages
```python
flash('Operation successful', 'success')   # Green
flash('Error occurred', 'error')           # Red
flash('Warning message', 'warning')        # Yellow
flash('Info message', 'info')              # Blue
```

## ANTI-PATTERNS

- Direct database access in templates (use route functions)
- Missing `@login_required` on protected routes
- Returning JSON from HTML routes (use `api_bp`)
- File uploads without `secure_filename()`

## NOTES

### Large Files
**`matching.py` (30KB)** - Tinder-style UI
- Complex session filtering logic
- Real-time similarity calculation
- Match modal with assignment status

**`user.py` (19KB)** - Resume management
- Multi-format upload (PDF, DOCX)
- File validation and storage
- Event membership management

### Blueprint Registration
In `__init__.py`:
```python
def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(matching_bp, url_prefix='/event')
    app.register_blueprint(scheduling_bp, url_prefix='/event')
    app.register_blueprint(api_bp, url_prefix='/api')
```

### Session Filtering (v1.3.0+)
Matching interface can filter users by:
- Selected sessions (default: ON)
- All event attendees (toggle OFF)

### Auto-Assignment Flow (v1.3.0+)
1. Users mutually like each other → Match created
2. `auto_assign.py` triggers immediately
3. Finds overlapping session availability
4. Assigns time slot + meeting point
5. Returns status: `assigned`, `pending`, or `failed`
6. Browser notification + email .ics sent if assigned

### Route Patterns
- HTML routes: Return `render_template()`
- JSON routes: Return `jsonify()`
- State changes: Always POST, never GET
- Error handling: `try/except` with flash + redirect
