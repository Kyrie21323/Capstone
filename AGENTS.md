# PROPHERE KNOWLEDGE BASE

**Generated:** 2026-02-05  
**Commit:** 6e22c26  
**Branch:** main  
**Version:** 1.4.0

---

## OVERVIEW

Flask-based networking platform for events with intelligent NLP matching (Sentence Transformers), automated meeting scheduling, and location management.

**Stack:** Flask 3.1.2 · SQLAlchemy · Sentence Transformers · Jinja2 · Cytoscape.js

**Strategic Positioning:** "Tinder for Events" - See [STRATEGY.md](STRATEGY.md)

---

## NAVIGATION GUIDE

**New to the project?** Follow this reading order:
1. **AGENTS.md** (this file) - Project structure and quick reference
2. **[STRATEGY.md](STRATEGY.md)** - Competitive positioning, market analysis
3. **[ROADMAP.md](ROADMAP.md)** - 12-week development plan
4. **[DATABASE.md](DATABASE.md)** - Model schemas and operations
5. **[API.md](API.md)** - Route reference

**Sub-navigation:**
- **[src/AGENTS.md](src/AGENTS.md)** - Core application structure
- **[src/routes/AGENTS.md](src/routes/AGENTS.md)** - Blueprint organization
- **[src/utils/AGENTS.md](src/utils/AGENTS.md)** - Shared helpers
- **[src/templates/AGENTS.md](src/templates/AGENTS.md)** - Jinja2 patterns

## STRUCTURE

```
Capstone/
├── main.py              # Entry point (Python path setup + app.run)
├── src/                 # Application core → see src/AGENTS.md
│   ├── app.py          # Factory pattern (create_app), blueprint registration
│   ├── models.py       # SQLAlchemy models (User, Event, Match, etc.)
│   ├── config.py       # Env-based config (Dev/Prod/Test)
│   ├── matching_engine.py    # NLP similarity (60% keywords, 40% docs)
│   ├── allocation_engine.py  # Meeting scheduler (constraint satisfaction)
│   ├── routes/         # Modular blueprints → see src/routes/AGENTS.md
│   ├── utils/          # Shared helpers → see src/utils/AGENTS.md
│   ├── templates/      # Jinja2 HTML → see src/templates/AGENTS.md
│   └── static/         # CSS + JS modules
├── scripts/            # CLI tools (manage_users.py, import_database.py, setup_database.py)
├── migrations/         # Flask-Migrate schema versions
├── uploads/            # User resume storage
├── exports/            # Database export archives
└── instance/           # SQLite database runtime
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add/modify route | `src/routes/{auth,user,admin,matching}.py` | Blueprint pattern |
| Database schema | `src/models.py` | SQLAlchemy ORM only (no raw SQL) |
| NLP matching logic | `src/matching_engine.py` | Sentence Transformers (all-MiniLM-L6-v2) |
| Meeting allocation | `src/allocation_engine.py` | Constraint satisfaction |
| Session validation | `src/utils/session_validation.py` | Availability reassignment |
| Email/calendar | `src/utils/email_notifications.py` | .ics invite generation |
| Authentication | `src/routes/auth.py` + `utils/decorators.py` | Flask-Login + @admin_required |
| Frontend templates | `src/templates/` | Base inheritance (base.html) |
| JavaScript modules | `src/static/js/` | notifications.js, modals.js, keywords.js |
| User management | `scripts/manage_users.py` | Create admin/manager/attendee |
| Database ops | `scripts/import_database.py` | Export/import with files |
| DB setup/fix | `scripts/setup_database.py` | Fresh setup or --fix missing tables |

## CONVENTIONS

### Python Code
- **PEP 8** with 4-space indent, 100-char line limit
- **Type hints** where applicable
- **SQLAlchemy ORM only** - NEVER raw SQL
- **Factory pattern**: `create_app()` for testing flexibility
- **Blueprint organization**: Feature-based (auth, user, admin, matching, scheduling)

### Database
- **Migrations**: ALL schema changes via `flask db migrate` (see DATABASE.md)
- **Cascade deletes**: Defined in model relationships
- **Constraints**: Unique constraints + check constraints enforced at DB level

### Templates
- **Inheritance**: All extend `base.html`
- **Logic minimal**: Use route functions for business logic
- **Modular JS**: Extract to `static/js/` if >20 lines or reused

### Routes
- **POST-redirect-GET pattern** for all state-changing operations
- **Flash messages**: `success`, `error`, `warning`, `info`
- **Decorators**: `@login_required`, `@admin_required`

## ANTI-PATTERNS (THIS PROJECT)

**NEVER:**
- Use raw SQL (use SQLAlchemy ORM)
- Suppress type errors (`as any`, `@ts-ignore` in JS)
- Commit changes without explicit user request
- Delete tests to make builds pass
- Skip migrations for schema changes
- Store passwords in plaintext (use Werkzeug hashing)
- Allow file uploads without type/size validation
- Create admin routes without `@admin_required`

**ALWAYS:**
- Run `lsp_diagnostics` after code changes
- Use `secure_filename()` for user uploads
- Validate input with `src/utils/validators.py`
- Use `flash()` for user feedback
- Test export/import after database migrations

## UNIQUE STYLES

### Hierarchical Location System
- **3 tiers**: Event Location (venue) → Event Session (time slot) → Meeting Point (specific spot)
- **Day-based sessions**: Sessions use relative days (Day 1, Day 2), NOT absolute dates
- **Multi-location meetings**: Meeting points can link to multiple Event Locations

### Auto-Assignment System
- **On-match trigger**: Meetings assigned immediately when mutual like occurs
- **Real-time feedback**: Status shown in modal (`assigned`, `pending`, `failed`)
- **Smart reassignment**: Automatic rescheduling when availability changes (see `session_validation.py`)

### Dual Notification System
- **Web Push**: Browser notifications for matches/assignments
- **Email**: .ics calendar invites sent via `email_notifications.py`

### NLP Matching
- **Embedding model**: `all-MiniLM-L6-v2` (loaded once at startup)
- **Multi-factor scoring**: 60% keyword similarity + 40% document similarity
- **Text extraction**: PyPDF2 for PDF, python-docx for DOCX

## COMMANDS

```bash
# Development
python main.py                                    # Run dev server (debug=True)

# User management
python scripts/manage_users.py --admin            # Create default admin
python scripts/manage_users.py --manager EMAIL    # Create event manager
python scripts/manage_users.py --list             # List all users

# Database
python scripts/setup_database.py                  # Fresh setup (confirms first)
python scripts/setup_database.py --fix            # Fix missing tables only
python scripts/import_database.py --export        # Export DB + files
python scripts/import_database.py --import        # Import latest export

# Migrations (from src/)
cd src && flask db migrate -m "Description"       # Create migration
cd src && flask db upgrade                        # Apply migrations
cd src && flask db downgrade                      # Rollback last
```

## NOTES

### Deployment
- **Auto DB init**: If SQLite missing, creates all tables on startup (`main.py`)
- **Auto admin**: Creates admin from `ADMIN_EMAIL`/`ADMIN_PASSWORD` env vars if none exist
- **Render-ready**: Designed for Render free tier (no shell access needed)

### Export/Import
- **ALWAYS export** before major migrations or schema changes
- **Exports include**: All tables + uploaded files
- **Location**: `./exports/database_export_TIMESTAMP.json`
- **Use `--no-files`** for faster DB-only exports (see [DATABASE.md](DATABASE.md))

### Testing
- Single test file: `tests/test_scheduling.py`
- **TODO**: Expand test coverage (see [ROADMAP.md](ROADMAP.md) Week 3)

### Large Files
- `src/routes/matching.py` (30KB) - Tinder-style UI + session filtering
- `src/routes/user.py` (19KB) - Resume upload + event management

---

## STRATEGIC CONTEXT

**Current State:** v1.4.0 academic prototype  
**Target State:** v2.0.0 production-ready (12 weeks)

**Read next:** [STRATEGY.md](STRATEGY.md) for competitive analysis  
**Implementation plan:** [ROADMAP.md](ROADMAP.md) for 12-week sprint breakdown
