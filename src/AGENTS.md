# SRC - APPLICATION CORE

**Parent:** Root AGENTS.md  
**Purpose:** Core application logic, models, and engines

## OVERVIEW

Application factory with blueprint-based architecture. Entry point: `app.py` (create_app pattern).

## STRUCTURE

```
src/
├── app.py                 # Factory: create_app() + blueprint registration (160 lines)
├── models.py              # SQLAlchemy ORM (User, Event, Match, Session, etc.)
├── config.py              # Dev/Prod/Test configs via FLASK_ENV
├── matching_engine.py     # NLP similarity engine (Sentence Transformers)
├── allocation_engine.py   # Meeting scheduler (constraint satisfaction)
├── routes/               # Blueprints → see routes/AGENTS.md
├── utils/                # Shared helpers → see utils/AGENTS.md
├── templates/            # Jinja2 HTML → see templates/AGENTS.md
└── static/
    ├── css/style.css     # Design system with CSS custom properties
    └── js/               # Modular JS (notifications, modals, keywords)
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| App initialization | `app.py` | Flask factory, extension init |
| Add model | `models.py` | Add class + migration |
| Config change | `config.py` | Environment-specific settings |
| Matching algorithm | `matching_engine.py` | Tune weights, model selection |
| Scheduling logic | `allocation_engine.py` | Meeting allocation constraints |

## CONVENTIONS

### Factory Pattern
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))
    
    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    return app
```

### Models
- Inherit from `db.Model`
- Use relationships with `backref` and `cascade`
- Unique constraints via `__table_args__`
- No raw SQL - ORM only

### Configuration
- `DevelopmentConfig` - SQLite, debug=True
- `ProductionConfig` - PostgreSQL-ready, debug=False  
- `TestingConfig` - Separate DB, testing=True

## ANTI-PATTERNS

- Circular imports (use blueprint late imports)
- Direct `app = Flask(__name__)` (use factory)
- Hardcoded secrets in code (use environment vars)
- Migrations without review

## NOTES

### Blueprint Loading
Blueprints registered in `routes/__init__.py` via `register_blueprints(app)`.

### Extension Initialization
All Flask extensions initialized in `app.py`:
- SQLAlchemy (`db`)
- Flask-Login (`login_manager`)
- Flask-Migrate (`migrate`)

### Model Highlights
- `User`: Authentication + profile
- `Event`: Event metadata + unique codes
- `Membership`: User↔Event link with keywords
- `Match`: Mutual connections
- `EventSession`: Time slots (day-based, not absolute dates)
- `MeetingPoint`: Specific meeting spots with capacity
- `ParticipantAvailability`: User session selection

### Matching Engine
- Model: `all-MiniLM-L6-v2` (384-dim embeddings)
- Scoring: 60% keyword + 40% document similarity
- Text extraction: PyPDF2 (PDF), python-docx (DOCX)

### Allocation Engine
- Input: User availabilities + existing matches
- Constraints: Time overlap, location capacity
- Output: Meeting assignments with time/location
- Fallback: Mark as `pending` if unassignable
