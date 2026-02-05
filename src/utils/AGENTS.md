# UTILS - SHARED HELPERS

**Parent:** src/AGENTS.md  
**Purpose:** Reusable utilities, decorators, and cross-cutting concerns

## OVERVIEW

10 Python files providing shared functionality across the application.

## STRUCTURE

```
utils/
├── __init__.py
├── decorators.py           # @admin_required, @prevent_admin_action
├── validators.py           # Input validation (email, keywords, files)
├── helpers.py              # Date formatting, text truncation
├── auto_assign.py          # Meeting auto-assignment logic (v1.3.0)
├── session_validation.py   # Availability reassignment (v1.4.0)
├── email_notifications.py  # .ics calendar invites
├── graph_utils.py          # Network graph generation (Cytoscape.js)
├── sample_graph_data.py    # Dev/test synthetic data
└── db_migrations.py        # Migration utilities
```

## WHERE TO LOOK

| Task | File | Function |
|------|------|----------|
| Add custom decorator | `decorators.py` | New decorator function |
| Validate user input | `validators.py` | `validate_email()`, `validate_keywords()` |
| Format dates | `helpers.py` | `format_datetime()`, `format_date()` |
| Meeting assignment | `auto_assign.py` | `auto_assign_meeting()` |
| Session changes | `session_validation.py` | `validate_and_reassign()` |
| Send email invite | `email_notifications.py` | `send_meeting_notification()` |
| Generate graph | `graph_utils.py` | `generate_event_graph_data()` |

## CONVENTIONS

### Decorators
```python
from functools import wraps
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
```

### Validators
```python
def validate_email(email):
    """Returns (is_valid: bool, error_message: str)"""
    if not email or '@' not in email:
        return False, "Invalid email address"
    return True, ""
```

### Helpers
- Always pure functions (no side effects)
- Type hints where applicable
- Docstrings for complex logic

## ANTI-PATTERNS

- Validators that modify input (validate only, don't transform)
- Decorators without `@wraps(f)` (breaks introspection)
- Helpers that access global state (pass dependencies)
- Circular imports (use late imports if needed)

## NOTES

### Auto-Assignment System (v1.3.0)
`auto_assign.py` implements instant meeting scheduling:
1. Called when Match created
2. Queries both users' `ParticipantAvailability`
3. Finds overlapping `EventSession` times
4. Allocates 15-minute slot
5. Assigns `MeetingPoint` based on session location
6. Updates `Match.meeting_time` and `Match.meeting_location_id`
7. Returns `(success: bool, meeting: dict, reason: str)`

### Session Validation (v1.4.0)
`session_validation.py` handles availability changes:
- **validate_and_reassign()**: Main entry point
- **get_affected_meetings()**: Find conflicts
- **try_reassign_meeting()**: Attempt rescheduling
- **Logic**: If user deselects session with meeting, try moving to another mutual slot
- **Fallback**: Mark meeting `pending` with reason if reassignment fails

### Email Notifications
`email_notifications.py` generates .ics files:
- Creates `VEVENT` with `SUMMARY`, `DTSTART`, `DTEND`
- Adds `LOCATION` (meeting point name)
- Includes `DESCRIPTION` with both users' names
- Sends via SMTP (configured in `config.py`)

### Graph Utilities
`graph_utils.py` generates Cytoscape.js-compatible JSON:
- **Nodes**: Users with metadata (name, email, keywords)
- **Edges**: Matches between users
- **Layout**: Force-directed (cose algorithm)
- **Styling**: Color-coded by match count

### Validation Functions
- `validate_email(email)` - Format check
- `validate_password(password)` - Min 6 chars
- `validate_keywords(keywords)` - Min 2 keywords
- `validate_file_extension(filename)` - PDF, DOC, DOCX only
- `sanitize_keywords(keywords)` - Clean, deduplicate, lowercase

### Decorator Collection
- `@admin_required` - Check `current_user.is_admin`
- `@prevent_admin_action` - Block admins from user actions
- `@requires_membership` - Verify event membership
- `@anonymous_required` - Redirect authenticated users

### Helper Functions
- `format_datetime(dt)` - "Jan 15, 2025 at 3:30 PM"
- `format_date(dt)` - "Jan 15, 2025"
- `truncate_text(text, length)` - Add "..." if too long
- `get_file_size_str(bytes)` - "1.5 MB"
- `clean_filename(filename)` - Remove special chars
- `parse_keywords(keywords_str)` - Split, clean, deduplicate
