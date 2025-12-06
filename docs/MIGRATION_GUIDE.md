# Script Migration Guide

## Overview

The scripts directory has been optimized to reduce redundancy and improve maintainability. This guide helps you migrate from old scripts to the new consolidated versions.

## What Changed

### Removed Scripts

The following scripts have been removed and replaced:

| Old Script | Status | New Command |
|------------|--------|-------------|
| `create_admin.py` | ❌ Removed | `manage_users.py --admin` |
| `create_manager.py` | ❌ Removed | `manage_users.py --manager EMAIL` |
| `fix_database.py` | ❌ Removed | `setup_database.py --fix` |
| `sync_with_files.py` | ❌ Removed | `import_database.py --export/--import` |
| `src/init_db.py` | ❌ Removed | (Unused wrapper, called `app.init_db()` directly) |

### New/Enhanced Scripts

| Script | Description |
|--------|-------------|
| `script_helpers.py` | Shared utilities for all scripts |
| `manage_users.py` | Unified user management tool |
| `import_database.py` | Complete import/export tool with better CLI |
| `setup_database.py` | Enhanced with `--fix` flag |

---

## Migration Examples

### Creating Admin Users

**Old:**
```bash
python scripts/create_admin.py
```

**New:**
```bash
python scripts/manage_users.py --admin
```

**Benefits:**
- Same functionality
- More options (--password, --name, --reset-password)
- Better error handling

---

### Creating Event Managers

**Old:**
```bash
python scripts/create_manager.py user@example.com --password mypass --name "John Doe"
```

**New:**
```bash
python scripts/manage_users.py --manager user@example.com --password mypass --name "John Doe"
```

**Benefits:**
- Consolidated with admin creation
- Can also create/promote attendees
- List all users with `--list`

---

### Fixing Database Tables

**Old:**
```bash
python scripts/fix_database.py
```

**New:**
```bash
python scripts/setup_database.py --fix
```

**Benefits:**
- Single tool for setup and fixing
- Consistent interface
- Better progress reporting

---

### Database Export

**Old:**
```bash
python scripts/sync_with_files.py
# Select option 1: Export
```

**New:**
```bash
python scripts/import_database.py --export
```

**Benefits:**
- Direct command (no menu)
- Uses SQLAlchemy (type-safe)
- Includes matches and interactions
- `--no-files` option to skip file backup

---

### Database Import

**Old:**
```bash
python scripts/sync_with_files.py
# Select option 2: Import
# Select export file from list
```

**New:**
```bash
python scripts/import_database.py --import
```

**Benefits:**
- Auto-detects latest export
- Better progress tracking
- Handles matches and interactions
- `--yes` flag for automation

---

## New Features

### User Management

**List all users:**
```bash
python scripts/manage_users.py --list
```

**List only managers:**
```bash
python scripts/manage_users.py --list --admins-only
```

**Create attendee:**
```bash
python scripts/manage_users.py --attendee user@example.com
```

**Reset password:**
```bash
python scripts/manage_users.py --manager user@example.com --reset-password
```

### Database Operations

**Export without files:**
```bash
python scripts/import_database.py --export --no-files
```

**Import without confirmation:**
```bash
python scripts/import_database.py --import --yes
```

**Setup database without confirmation:**
```bash
python scripts/setup_database.py --yes
```

---

## Quick Reference

### manage_users.py

```bash
# Create default admin
python scripts/manage_users.py --admin

# Create/update manager
python scripts/manage_users.py --manager EMAIL [--password PASS] [--name NAME]

# Create/update attendee  
python scripts/manage_users.py --attendee EMAIL [--password PASS] [--name NAME]

# List users
python scripts/manage_users.py --list [--admins-only] [--attendees-only]

# Reset password
python scripts/manage_users.py --manager EMAIL --reset-password
```

### import_database.py

```bash
# Export database
python scripts/import_database.py --export [--no-files]

# Import database
python scripts/import_database.py --import [--no-files] [--yes]
```

### setup_database.py

```bash
# Full reset (requires confirmation)
python scripts/setup_database.py

# Full reset without confirmation
python scripts/setup_database.py --yes

# Fix missing tables only
python scripts/setup_database.py --fix
```

---

## Troubleshooting

### "Module 'script_helpers' not found"

Make sure you're running scripts from the project root:
```bash
cd /path/to/Capstone
python scripts/manage_users.py --admin
```

### "No such file: create_admin.py"

The old scripts have been removed. See the migration examples above for the new commands.

### ImportError with old code

If you have code that imports from the old scripts, update imports:

**Old:**
```python
from scripts.create_admin import create_admin
```

**New:**
```python
from scripts.manage_users import create_or_update_user
```

---

##Benefits Summary

✅ **Reduced Code**: ~300 lines removed through consolidation  
✅ **Fewer Scripts**: From 7 to 4 scripts  
✅ **Consistent Interface**: All scripts use shared utilities  
✅ **Better CLI**: Argparse with help messages and examples  
✅ **Type Safety**: SQLAlchemy-based (no raw SQL)  
✅ **More Features**: List users, export/import in one tool  
✅ **Better UX**: Progress indicators, colored output, confirmations  

---

## Need Help?

Run any script with `--help` to see all options:

```bash
python scripts/manage_users.py --help
python scripts/import_database.py --help
python scripts/setup_database.py --help
```
