# Setup Guide

Complete installation and configuration guide for the NFC Networking Platform.

## Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package installer
- **Git**: For cloning the repository

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Capstone
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\Activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Flask-Login 0.6.2
- Flask-Migrate 4.0.4
- Sentence Transformers 2.2.2
- And more (see `requirements.txt`)

---

## Database Setup

Choose one of the following setup options:

### Option 1: Automated Setup (Recommended)

The easiest way to get started:

```bash
python scripts/setup_database.py
```

This will:
- Remove any existing database
- Initialize Flask-Migrate
- Create all database tables
- Generate sample data (users, events, memberships)

### Option 2: Import from Existing Export

If you have a database export (e.g., from another device):

```bash
python scripts/import_database.py --import
```

This will:
- Find the latest export in `./exports`
- Prompt for confirmation
- Clear existing database
- Import all data (users, events, memberships, resumes, matches)
- Restore uploaded files

> **⚠️ WARNING**: Import will replace ALL data in the current database!

### Option 3: Manual Setup

For advanced users who want full control:

```bash
# Change to src directory
cd src

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade

# Return to project root
cd ..

# Run the application
python main.py
```

---

## User Management Setup

### Create Admin Account

Create the default super admin:

```bash
python scripts/manage_users.py --admin
```

**Credentials:**
- Email: `admin@nfcnetworking.com`
- Password: `admin123`

### Create Additional Event Managers

```bash
python scripts/manage_users.py --manager user@example.com --password yourpassword
```

### Create Regular Users

```bash
python scripts/manage_users.py --attendee user@example.com --password yourpassword
```

### List All Users

```bash
python scripts/manage_users.py --list
```

---

## Running the Application

### Development Mode

```bash
python main.py
```

The application will start on:
- **Main Site**: http://127.0.0.1:5000
- **Admin Panel**: http://127.0.0.1:5000/admin

### Production Mode

For production deployment, use a production server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 'src.app:app'
```

---

## Default Login Credentials

After running the automated setup, you can log in with:

### Super Admin
- **Email**: `admin@nfcnetworking.com`
- **Password**: `admin123`

### Sample Users
- **Email**: Various (check database or run `python scripts/manage_users.py --list`)
- **Password**: `password123`

---

## Sample Events

The automated setup creates sample events:

| Event Code | Name | Description |
|------------|------|-------------|
| **NYUAD2025** | NYUAD Career Fair 2025 | Annual career fair |
| **TECH2025** | Tech Conference Dubai | Technology conference |
| **STARTUP2025** | Startup Networking Event | Startup networking |

---

## Environment Configuration

### Development Settings

The application uses debug mode by default in `main.py`:

```python
app.run(debug=True)
```

### Production Settings

For production, create a `.env` file or set environment variables:

```bash
export FLASK_ENV=production
export SECRET_KEY='your-secure-random-key-here'
export DATABASE_URL='your-database-connection-string'
```

Then modify `src/app.py` configuration:

```python
import os

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/nfc_networking.db')
app.config['DEBUG'] = os.environ.get('FLASK_ENV') != 'production'
```

---

## Troubleshooting

### Virtual Environment Issues

**Problem**: `pip: command not found` after activation

**Solution**: Ensure you're using Python 3.8+:
```bash
python3 --version
python3 -m venv .venv
```

### Module Not Found Errors

**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Make sure virtual environment is activated:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\Activate     # Windows
```

### Database Migration Conflicts

**Problem**: Migration errors or conflicts

**Solution**: Reset the database:
```bash
# Remove existing database and migrations
rm -rf migrations instance/nfc_networking.db

# Run automated setup
python scripts/setup_database.py
```

### Port Already in Use

**Problem**: `Address already in use` error

**Solution**: Change the port in `main.py`:
```python
app.run(debug=True, port=5001)
```

Or kill the process using port 5000:
```bash
# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Import Script Issues

**Problem**: Import script can't find exports

**Solution**: Ensure exports exist:
```bash
ls -la exports/
```

If no exports exist, you need to either:
- Run setup to create fresh database: `python scripts/setup_database.py`
- Copy export files from another device

---

## Next Steps

After successful setup:

1. **Access the Application**: Open http://127.0.0.1:5000
2. **Login as Admin**: Use `admin@nfcnetworking.com` / `admin123`
3. **Explore Features**: See [FEATURES.md](FEATURES.md) for detailed feature documentation
4. **Join an Event**: Use one of the sample event codes (e.g., NYUAD2025)
5. **Upload Resume**: Test the matching system by uploading a resume

For more information:
- **Features**: See [FEATURES.md](FEATURES.md)
- **Database Operations**: See [DATABASE.md](DATABASE.md)
- **API Reference**: See [API.md](API.md)
- **Development**: See [DEVELOPMENT.md](DEVELOPMENT.md)

---

**Ready to start!** 🚀
