# Database Setup Guide

## Quick Setup (Recommended)

Run the setup script to initialize the database:

```bash
python scripts/setup_database.py
```

## Manual Setup

If you prefer to set up manually or encounter issues:

### 1. Clean Reset
```bash
# Remove existing database and migrations
Remove-Item -Path "instance\nfc_networking.db" -Force
Remove-Item -Path "migrations\versions\*" -Force

# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial migration with all models"

# Apply migration
flask db upgrade
```

### 2. Run the Application
```bash
python main.py
```

The app will automatically create sample data on first run.

## Database Structure

The application uses the following tables:
- `user` - User accounts (attendees and admins)
- `event` - Events created by admins
- `membership` - User-event relationships with keywords
- `resume` - Uploaded documents/resumes
- `match` - Mutual matches between users
- `user_interaction` - Like/pass interactions

## Troubleshooting

### Migration Conflicts
If you encounter migration conflicts:
1. Run the clean reset steps above
2. Use the setup script: `python scripts/setup_database.py`

### Database Locked
If you get "database is locked" errors:
1. Stop the Flask application
2. Wait a few seconds
3. Restart the application

### Missing Tables
If tables are missing:
1. Check that migrations were applied: `flask db upgrade`
2. Verify all models are imported in `models.py`
3. Run the setup script

## Cross-Device Synchronization

For development across multiple devices:
1. **Don't commit the database file** (it's in `.gitignore`)
2. **Do commit migration files** (they're version controlled)
3. **Run setup script on each device** for clean initialization
4. **Use the same Python environment** (same `requirements.txt`)

## Production Deployment

For production:
1. Use PostgreSQL or MySQL instead of SQLite
2. Set `DATABASE_URL` environment variable
3. Run migrations: `flask db upgrade`
4. Create admin user manually or through admin interface
