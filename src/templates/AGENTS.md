# TEMPLATES - JINJA2 HTML

**Parent:** src/AGENTS.md  
**Purpose:** Frontend views with server-side rendering

## OVERVIEW

14 HTML files + 10 admin templates. Base template inheritance pattern.

## STRUCTURE

```
templates/
├── base.html               # Master template (navbar, flash, scripts)
├── landing.html            # Public homepage
├── login.html              # Login form
├── register.html           # Registration form
├── dashboard.html          # User event dashboard
├── upload_resume.html      # File upload
├── matching.html           # Tinder-style UI
├── matches.html            # Confirmed matches list
├── manage_availability.html # Session selection
├── admin/                  # Admin panel templates
│   ├── dashboard.html      # Analytics
│   ├── users.html          # User management
│   ├── events.html         # Event management
│   ├── sessions.html       # Session management
│   ├── locations.html      # Location management
│   ├── workflow_*.html     # Guided setup flows
│   └── graph.html          # Network visualization
└── ...
```

## WHERE TO LOOK

| Page | Template | Features |
|------|----------|----------|
| Landing | `landing.html` | Public homepage, hero section |
| Dashboard | `dashboard.html` | User events, quick actions |
| Matching | `matching.html` | Card UI, session filter toggle |
| Matches | `matches.html` | Status badges (assigned/pending/failed) |
| Availability | `manage_availability.html` | Session cards, confirmation modals |
| Admin Analytics | `admin/dashboard.html` | Stats, charts, recent activity |
| Network Graph | `admin/graph.html` | Cytoscape.js visualization |

## CONVENTIONS

### Template Inheritance
```jinja2
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
  <!-- Page content -->
{% endblock %}

{% block scripts %}
  {{ super() }}  <!-- Include parent scripts -->
  <script src="{{ url_for('static', filename='js/page.js') }}"></script>
{% endblock %}
```

### Flash Messages
```jinja2
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <div class="alert alert-{{ category }}">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
```

### Static Files
```jinja2
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- JS -->
<script src="{{ url_for('static', filename='js/notifications.js') }}"></script>

<!-- Images -->
<img src="{{ url_for('static', filename='img/logo.png') }}">
```

### Loops with Conditionals
```jinja2
{% for event in events %}
  <div class="event-card">
    <h3>{{ event.name }}</h3>
    {% if event.is_published %}
      <span class="badge">Published</span>
    {% endif %}
  </div>
{% else %}
  <p>No events found.</p>
{% endfor %}
```

## ANTI-PATTERNS

- Business logic in templates (use route functions)
- Direct database queries (pass data from routes)
- Inline JS >20 lines (extract to `static/js/`)
- Hardcoded URLs (use `url_for()`)
- Missing CSRF tokens on forms
- Forgetting `{% endblock %}` (breaks inheritance)

## NOTES

### Base Template Features
`base.html` provides:
- Navigation bar with login status
- Flash message container
- Lucide icons CDN (v0.263.1)
- Modular JS imports (notifications, modals, keywords)
- CSS custom properties design system

### JavaScript Modules
Extracted from templates (v1.3.0+):
- `static/js/notifications.js` - Toast notification system
- `static/js/modals.js` - Confirmation dialog system
- `static/js/keywords.js` - Tag-based keyword input

### Matching Interface
`matching.html` features:
- Card-style user profiles
- Similarity score display
- Like/pass buttons
- Session filter toggle (default: ON)
- Progress indicator ("X users reviewed")
- Match modal with assignment status

### Availability Management
`manage_availability.html` (v1.4.0):
- Session cards with day badges
- Click to toggle selection
- Confirmation modal if changes affect meetings
- Loading spinner during reassignment
- Real-time status updates via AJAX

### Match Status Display
`matches.html` shows:
- ✅ **Assigned**: Meeting time/location confirmed
- ⏳ **Pending**: Auto-assignment failed, needs manual scheduling
- 🚫 **Failed**: Explicit failure with reason (e.g., "No common free slots")

### Admin Workflows
Guided setup flows (v1.3.0):
- `workflow_event_sessions.html` - Session configuration dashboard
- `workflow_attendee_matching.html` - Matching setup dashboard
- Step-by-step instructions
- Direct action links

### Network Graph
`graph.html` uses Cytoscape.js:
- Force-directed layout (cose algorithm)
- Interactive zoom/pan
- Click nodes for details
- Real-time stats (connected components, density)
- Dev mode: `/admin/graph/dev/{small|medium|large}` for testing

### Form Patterns
All forms use:
- CSRF protection (Flask-WTF)
- `method="POST"` for state changes
- Flash messages for feedback
- Redirect after POST (PRG pattern)

### Icon Usage
Lucide icons via CDN:
```html
<i data-lucide="user"></i>
<i data-lucide="calendar"></i>
<i data-lucide="check-circle"></i>
```

### Conditional Rendering
```jinja2
{% if current_user.is_authenticated %}
  <a href="{{ url_for('user.dashboard') }}">Dashboard</a>
{% else %}
  <a href="{{ url_for('auth.login') }}">Login</a>
{% endif %}
```
