# Database Guide

Complete guide to database management, models, and operations.

## Database Models

### User
**Purpose**: Store user account information and authentication data

**Fields**:
- `id` - Primary key
- `name` - User's display name
- `email` - Unique email address (used for login)
- `password_hash` - Hashed password (Werkzeug PBKDF2-SHA256)
- `is_admin` - Boolean flag for admin/manager status
- `created_at` - Registration timestamp

**Relationships**:
- `memberships` → Many Membership records
- `resumes` → Many Resume records
- `matches` → Many Match records (as user1 or user2)
- `interactions` → Many UserInter action records

---

### Event
**Purpose**: Store event information

**Fields**:
- `id` - Primary key
- `name` - Event name
- `code` - Unique event code (3-20 alphanumeric characters)
- `description` - Event description
- `start_date` - Event start date
- `end_date` - Event end date
- `created_at` - Event creation timestamp

**Relationships**:
- `memberships` → Many Membership records
- `resumes` → Many Resume records
- `sessions` → Many EventSession records
- `locations` → Many MeetingLocation records

---

### Membership
**Purpose**: Link users to events with their interest keywords

**Fields**:
- `id` - Primary key
- `user_id` - Foreign key to User
- `event_id` - Foreign key to Event
- `keywords` - Comma-separated interest keywords
- `joined_at` - Join timestamp

**Constraints**:
- Unique constraint on (user_id, event_id) - one membership per user per event

---

### Resume
**Purpose**: Store document metadata

**Fields**:
- `id` - Primary key
- `user_id` - Foreign key to User
- `event_id` - Foreign key to Event
- `filename` - Secure generated filename
- `original_name` - User's original filename
- `mime_type` - File MIME type
- `file_size` - File size in bytes
- `uploaded_at` - Upload timestamp

**Constraints**:
- Unique constraint on (user_id, event_id) - one resume per user per event

---

### Match
**Purpose**: Store confirmed mutual matches

**Fields**:
- `id` - Primary key
- `user1_id` - Foreign key to User
- `user2_id` - Foreign key to User
- `event_id` - Foreign key to Event
- `matched_at` - Match creation timestamp
- `is_active` - Boolean status flag

**Constraints**:
- Unique constraint on (user1_id, user2_id, event_id)
- Check constraint: user1_id != user2_id (no self-matching)

---

### UserInteraction
**Purpose**: Track like/pass actions in matching flow

**Fields**:
- `id` - Primary key
- `user_id` - Foreign key to User (who performed action)
- `target_user_id` - Foreign key to User (who received action)
- `event_id` - Foreign key to Event
- `action` - Either 'like' or  'pass'
- `created_at` - Action timestamp

**Constraints**:
- Unique constraint on (user_id, target_user_id, event_id)
- Check constraint: action IN ('like', 'pass')

---

### EventSession
**Purpose**: Define time slots for event sessions

**Fields**:
- `id` - Primary key
- `event_id` - Foreign key to Event
- `name` - Session name
- `start_time` - Session start timestamp
- `end_time` - Session end timestamp
- `location_description` - General location description

---

### MeetingPoint (Table: `meeting_location`)
**Purpose**: Define specific meeting spots (e.g., tables)

**Fields**:
- `id` - Primary key
- `event_id` - Foreign key to Event
- `name` - Location name (e.g., "Hall 1 Table 11")
- `capacity` - Number of concurrent pairs (default: 1)

**Relationships**:
- `session_locations` → Many-to-Many with `SessionLocation`

---

### meeting_point_locations (Association Table)
**Purpose**: Link Meeting Points to multiple Event Locations

**Fields**:
- `meeting_point_id` - Foreign key to MeetingPoint
- `session_location_id` - Foreign key to SessionLocation

---

### ParticipantAvailability
**Purpose**: Store user availability for sessions

**Fields**:
- `id` - Primary key
- `user_id` - Foreign key to User
- `event_session_id` - Foreign key to EventSession
- `event_id` - Foreign key to Event
- `is_available` - Boolean availability flag

**Constraints**:
- Unique constraint on (user_id, event_session_id)

---

## Database Operations

### Setup & Initialization

#### Fresh Database Setup
```bash
python scripts/setup_database.py
```

Creates:
- New database with all tables
- Flask-Migrate migrations
- Sample users (5 attendees, 1 admin)
- Sample events (3 events)
- Sample memberships

**Options**:
- `--yes` - Skip confirmation prompt
- `--fix` - Only create missing tables (doesn't reset data)

#### Fix Missing Tables
```bash
python scripts/setup_database.py --fix
```

Use when:
- Adding new models
- Tables accidentally deleted
- Migration issues

---

### User Management

#### Create Super Admin
```bash
python scripts/manage_users.py --admin
```

Creates/updates:
- Email: `admin@nfcnetworking.com`
- Password: `admin123`
- Role: Event Manager

#### Create Event Manager
```bash
python scripts/manage_users.py --manager user@example.com --password secret --name "Manager Name"
```

#### Create Attendee
```bash
python scripts/manage_users.py --attendee user@example.com --password secret --name "User Name"
```

#### List All Users
```bash
python scripts/manage_users.py --list
```

**Filtering**:
- `--admins-only` - Show only Event Managers
- `--attendees-only` - Show only Attendees

#### Reset Password
```bash
python scripts/manage_users.py --manager user@example.com --reset-password
```

---

### Export & Import

#### Export Database
```bash
python scripts/import_database.py --export
```

**What's exported**:
- All tables (users, events, memberships, resumes, matches, interactions)
- All uploaded files (resumes)
- Format: JSON + original file formats
- Location: `./exports/database_export_TIMESTAMP.json`

**Options**:
- `--no-files` - Export database only, skip files

#### Import Database
```bash
python scripts/import_database.py --import
```

**What's imported**:
- All data from latest export
- All files with proper structure
- Replaces existing database completely

**Options**:
- `--yes` - Skip confirmation prompt
- `--no-files` - Import database only, skip files

> **⚠️ WARNING**: Import command replaces ALL existing data!

---

## Database Structure Summary

| Table | Records | Purpose | Key Relationships |
|-------|---------|---------|------------------|
| `user` | Users | Authentication & profiles | → memberships, resumes, matches |
| `event` | Events | Event information | → memberships, resumes, sessions |
| `membership` | Memberships | User-event links | user ← → event |
| `resume` | Resumes | Document metadata | user ← → event |
| `match` | Matches | Confirmed connections | user ← → user ← → event |
| `user_interaction` | Interactions | Like/pass tracking | user → user → event |
| `event_session` | Sessions | Time slots | → event, → availability |
| `meeting_location` | MeetingPoint | Specific meeting spots | → event, ←→ session_location |
| `participant_availability` | Availability | User time preferences | user → session → event |

---

## Migrations

### Flask-Migrate Commands

#### Initialize Migrations
```bash
cd src
flask db init
```

Creates `migrations/` directory with Alembic configuration.

#### Create Migration
```bash
cd src
flask db migrate -m "Description of changes"
```

Generates migration script based on model changes.

#### Apply Migrations
```bash
cd src
flask db upgrade
```

Applies pending migrations to database.

#### Rollback Migration
```bash
cd src
flask db downgrade
```

Reverts last migration.

---

## Troubleshooting

### Migration Conflicts

**Problem**: Alembic revision conflicts

**Solution**:
```bash
# Remove migrations and database
rm -rf migrations instance/nfc_networking.db

# Reset with setup script
python scripts/setup_database.py
```

### Database Locked

**Problem**: `database is locked` error

**Causes**:
- Flask app still running
- Multiple connections
- Incomplete transaction

**Solution**:
1. Stop Flask application
2. Wait 5 seconds
3. Restart application

### Missing Tables

**Problem**: Table doesn't exist error

**Solution**:
```bash
# Option 1: Fix missing tables
python scripts/setup_database.py --fix

# Option 2: Apply pending migrations
cd src
flask db upgrade
```

### Corrupted Database

**Problem**: Database file corrupted

**Solution**:
```bash
# If you have export
python scripts/import_database.py --import

# If no export, reset database
python scripts/setup_database.py
```

### Orphaned Files

**Problem**: Files in uploads/ but no database records

**Solution**:
- Login as admin
- Navigate to Admin Panel
- Click "Cleanup Orphaned Files"
- Review list and confirm deletion

---

## Best Practices

### Regular Backups
```bash
# Weekly export
python scripts/import_database.py --export
```

Keep multiple timestamped exports for safety.

### Migration Workflow
1. Modify models in `src/models.py`
2. Create migration: `flask db migrate -m "Description"`
3. Review generated migration in `migrations/versions/`
4. Apply migration: `flask db upgrade`
5. Test thoroughly
6. Commit migration files to Git

### Data Cleanup
- Use `manage_users.py --list` to audit users regularly
- Remove test accounts before production
- Export before major changes
- Clean orphaned files periodically

---

For more information:
- [SETUP.md](SETUP.md) - Installation guide
- [README.md](../README.md) - Platform features
- [AGENTS.md](../AGENTS.md) - Technical details
