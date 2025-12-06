# API Reference

Complete reference for all API routes in the NFC Networking Platform.

## Public Routes

### Landing Page
```
GET /
```
**Description**: Application landing page  
**Authentication**: None  
**Returns**: HTML landing page

### Hello World
```
GET /hello
```
**Description**: Test endpoint  
**Authentication**: None  
**Returns**: "Hellofrom NFC Networking!"

---

## Authentication Routes

### Registration
```
POST /register
```
**Description**: Register new user account  
**Authentication**: None  
**Parameters**:
- `name` (string) - User's display name
- `email` (string) - Unique email address
- `password` (string) - Password (min 6 characters)

**Returns**: Redirect to login page

### Login
```
POST /login
```
**Description**: Authenticate user  
**Authentication**: None  
**Parameters**:
- `email` (string) - User email
- `password` (string) - User password

**Returns**: Redirect to dashboard or login page with error

### Logout
```
GET /logout
```
**Description**: End user session  
**Authentication**: Required  
**Returns**: Redirect to landing page

---

## User Routes

All routes require authentication (`@login_required`).

### Dashboard
```
GET /dashboard
```
**Description**: User dashboard showing joined events  
**Returns**: HTML dashboard with user's events

### Join Event
```
POST /join_event
```
**Description**: Join event with code and keywords  
**Parameters**:
- `event_code` (string) - Event code
- `keywords` (string) - Comma-separated keywords (min 2)

**Returns**: Redirect to dashboard with success/error message

### Leave Event
```
POST /leave_event
```
**Description**: Leave an event  
**Parameters**:
- `event_id` (int) - Event ID

**Returns**: Redirect to dashboard

### Update Keywords
```
POST /update_keywords
```
**Description**: Update interest keywords for an event  
**Parameters (JSON)**:
- `event_id` (int) - Event ID
- `keywords` (string) - New comma-separated keywords

**Returns**: JSON success/error response

### Resume Upload
```
GET /upload_resume/<event_id>
POST /upload_resume/<event_id>
```
**Description**: Upload resume for event  
**Parameters**:
- `file` (file) - Resume file (PDF, DOC, DOCX, max 16MB)

**Returns**: Redirect to dashboard with upload result

### View Resume
```
GET /view_resume/<resume_id>
```
**Description**: View uploaded resume  
**Access**: Owner only  
**Returns**: Resume file download

### Delete Resume
```
POST /delete_resume/<resume_id>
```
**Description**: Delete uploaded resume  
**Access**: Owner only  
**Returns**: Redirect with success/error message

### Event Matching
```
GET /event/<event_id>/matching
```
**Description**: Get matching interface for event  
**Returns**: HTML matching interface with next potential match

### Like User
```
POST /event/<event_id>/like/<user_id>
```
**Description**: Express interest in connecting  
**Returns**: Redirect to matching page

### Pass User
```
POST /event/<event_id>/pass/<user_id>
```
**Description**: Skip a potential match  
**Returns**: Redirect to matching page

### View Matches
```
GET /event/<event_id>/matches
```
**Description**: View confirmed matches  
**Returns**: HTML page with all matches for event

### Manage Availability
```
GET /event/<event_id>/availability
POST /event/<event_id>/availability
```
**Description**: View/update availability for sessions  
**Parameters (POST)**:
- Session IDs with boolean availability flags

**Returns**: HTML availability page or redirect

### Uploaded Files
```
GET /uploads/<filename>
```
**Description**: Serve uploaded files  
**Access**: Owner only  
**Returns**: File download

---

## Admin Routes

All routes require admin authentication (`@login_required` + `@admin_required`).

### Admin Dashboard
```
GET /admin
```
**Description**: Admin analytics dashboard  
**Returns**: HTML dashboard with platform statistics

### List Events
```
GET /admin/events
```
**Description**: List all events  
**Returns**: HTML page with all events

### Create Event
```
GET /admin/events/create
POST /admin/events/create
```
**Description**: Create new event  
**Parameters**:
- `name` (string) - Event name
- `code` (string) - Unique event code (3-20 alphanumeric)
- `description` (string) - Event description
- `start_date` (datetime) - Start date
- `end_date` (datetime) - End date

**Returns**: Redirect to events list

### Edit Event
```
GET /admin/events/<id>/edit
POST /admin/events/<id>/edit
```
**Description**: Edit existing event  
**Parameters**: Same as create event  
**Returns**: Redirect to events list

### Delete Event
```
POST /admin/events/<id>/delete
```
**Description**: Delete event and related data  
**Returns**: Redirect to events list

### List Users
```
GET /admin/users
```
**Description**: List all users  
**Returns**: HTML page with all users

### Toggle Admin Status
```
POST /admin/users/<id>/toggle_admin
```
**Description**: Promote/demote user  
**Returns**: Redirect to users list

### Delete User
```
POST /admin/users/<id>/delete
```
**Description**: Delete user and related data  
**Protection**: Cannot delete self  
**Returns**: Redirect to users list

### Manage Sessions
```
GET /event/<event_id>/sessions
POST /event/<event_id>/sessions
```
**Description**: Create/delete event sessions  
**Parameters (POST)**:
- `action` (string) - 'add' or 'delete'
- For add: `name`, `start_time`, `end_time`, `location_description`
- For delete: `session_id`

**Returns**: HTML sessions management page

### Manage Locations
```
GET /event/<event_id>/locations
POST /event/<event_id>/locations
```
**Description**: Create/delete meeting locations  
**Parameters (POST)**:
- `action` (string) - 'add' or 'delete'
- For add: `name`, `capacity`
- For delete: `location_id`

**Returns**: HTML locations management page

### Allocate Meetings
```
POST /event/<event_id>/allocate
```
**Description**: Run meeting allocation algorithm  
**Returns**: Redirect with allocation results

### Cleanup Files
```
POST /admin/cleanup-files
```
**Description**: Remove orphaned files  
**Returns**: Redirect with cleanup results

### Event Network Graph
```
GET /event/<event_id>/graph
GET /api/event/<event_id>/graph
```
**Description**: View/get network graph data  
**Returns**: HTML visualization or JSON graph data

---

## Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message description"
}
```

### Flash Messages
The application uses Flask flash messages for user notifications:
- `success` - Green success messages
- `error` - Red error messages
- `warning` - Yellow warning messages
- `info` - Blue info messages

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET request |
| 302 | Found | Redirect after POST |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server error |

---

## Authentication

### Required Headers
```
Cookie: session=<session_token>
```

Flask-Login manages session cookies automatically.

### Admin Protection
Routes with `@admin_required` check `current_user.is_admin`.

---

For implementation details, see [DEVELOPMENT.md](DEVELOPMENT.md).  
For feature descriptions, see [FEATURES.md](FEATURES.md).
