# Recent Updates

## Version 1.4.0 (2025/12/07)

### Session Validation & Reassignment

#### New Features
- **Smart Session Updates**: Validation system that prevents silent meeting cancellations when attendees change their availability.
- **Automatic Reassignment**: When a user leaves a session where they had a meeting, the system automatically tries to reschedule the meeting to another overlapping slot.
- **Confirmation Dialogs**: Interactive modals warn users before they make changes that would affect existing meetings.
- **Loading States**: Visual feedback during complex reassignment calculations.
- **Meeting Status Visibility**: Matches page now clearly differentiates between Scheduled, Pending (failed reassignment), and Cancelled meetings.

#### Updates
- **API**: New endpoint `/event/<id>/availability/check-matches` for frontend state checking.
- **Frontend**: manage_availability.html enhanced with AJAX support and modal workflows.
- **Backend Refactoring**: Centralized validation logic in `src/utils/session_validation.py`.

## Version 1.3.0 (2025/12/07)

### Enhanced UI & Notifications

#### New Features
- **Modern UI**: Replaced all emojis with Lucide Icons for a professional look.
- **Dual Notification System**:
  - Real-time Web Push notifications for matches.
  - Automatic email notifications with .ics calendar invites.
- **Auto-Assignment**: Meetings are automatically scheduled (time & location) instantly upon matching.
- **Network Graph**: Fixed visualization issues and syntax errors.
- **Admin Workflows**: New guided setup flows for Event Sessions and Matching.

#### Improvements
- **Session Filtering**: Match filter now defaults to showing only attendees in your sessions.
- **Location Hierarchy**: Logic for Session Location -> Event Session -> Meeting Point fully implemented.
- **Performance**: Optimized graph data fetching.

### Version 1.2.0 (2025/12/06)

### New Features
- Meeting scheduling system with sessions and locations
- Automated meeting allocation algorithm
- Participant availability management
- Database import/export tools
- Consolidated management scripts

### Bug Fixes
- Fixed sessions and locations pages (missing imports)
- Improved error handling
- Enhanced validation

### Improvements
- Restructured documentation (6 focused files)
- Better CLI interfaces
- Comprehensive setup guide
