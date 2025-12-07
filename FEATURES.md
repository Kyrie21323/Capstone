# Features

Detailed guide to all features available in Prophere.

---

## Feature Overview

Prophere provides a comprehensive suite of features for professional networking at events:

### Core Capabilities
- ✅ **Role-based Authentication**: Secure login system with Event Attendee and Event Manager roles
- ✅ **Smart Event Management**: Create, join, and manage events with unique access codes
- ✅ **AI-Powered Matching**: Machine learning algorithms (Sentence Transformers) using semantic similarity to suggest relevant connections based on keywords and document content
- ✅ **Smart Recommendations**: Personalized suggestions for who to meet next, filtering out already-interacted users and ranking by compatibility scores
- ✅ **Document Upload**: Resume/portfolio upload and management (PDF, DOCX)
- ✅ **Tinder-style Matching**: Interactive matching interface with like/pass functionality
- ✅ **Post-match Features**: View confirmed matches and exchange contact information
- ✅ **Meeting Scheduling**: Session and time slot management with automated allocation
- ✅ **Location Management**: Define and allocate meeting locations for matched participants

### Advanced Features
- ✅ **Network Visualization**: Interactive graph visualizer showing event attendee connections and mutual matches
  - **Event Network Graph**: Admin-only visualization of attendee networks using Cytoscape.js
  - **Interactive Elements**: Zoom, pan, and click nodes to see details
  - **Statistics**: Real-time stats on connected components and density
- ✅ **Admin Panel**: Complete event and user management system with analytics
- ✅ **Mobile Responsive Interface**: Optimized for usage on smartphones and tablets
- ✅ **Cross-device Sync**: Database and file synchronization between devices via export/import

---

## Event Management

### For All Users

#### Joining Events
- **Unique Event Codes**: Join events using alphanumeric codes (3-20 characters)
- **Interest Keywords**: Define at least 2 keywords representing your interests/skills
- **Keyword Updates**: Modify keywords after joining an event
- **Event Dashboard**: View all joined events in one place

#### Leaving Events
- **Clean Departure**: Leave events with automatic data cleanup
- **Data Removal**: Removes memberships, resumes, and interactions upon leaving
- **Match Preservation**: Existing matches are maintained until both users leave

### For Event Managers

#### Event Creation
- **Event Details**: Set name, description, start date, and end date
- **Unique Codes**: System generates unique event codes
- **Code Customization**: Option to set custom event codes
- **Event Visibility**: Events visible to all users with the code

#### Event Modification
- **Edit Events**: Update event details at any time
- **Delete Events**: Remove events with cascade deletion of related data
- **Event Statistics**: View member count, match count, resume count

#### Graph Visualizer

- **Event Network Graph**: `/event/<event_id>/graph` - Visualize attendee connections for a specific event
- **Dev Graph Visualizer**: `/admin/graph/dev/<dataset_size>`
  - `/admin/graph/dev/small` - Small synthetic dataset
  - `/admin/graph/dev/medium` - Medium synthetic dataset
  - `/admin/graph/dev/large` - Large synthetic dataset

---

## Intelligent Matching System

### How It Works

The platform uses advanced NLP (Natural Language Processing) to match users based on their interests and professional backgrounds.

#### Matching Algorithm
1. **Text Extraction**: Extracts text from uploaded resumes (PDF, DOCX)
2. **Embedding Generation**: Uses Sentence Transformers to create semantic embeddings
3. **Similarity Calculation**: Computes similarity scores between users
4. **Multi-factor Scoring**:
   - Keyword similarity: **60% weight**
   - Document content similarity: **40% weight**
5. **Ranking**: Sorts potential matches by similarity score

### Interactive Matching Interface

#### Tinder-Style UI
- **Card Interface**: Browse potential matches one at a time
- **Visual Design**: See user names, keywords, and similarity scores
- **Swipe Actions**: Like or pass on each potential match
- **Progress Tracking**: See how many matches you've reviewed

#### Actions
- **Like**: Express interest in connecting with a user
- **Pass**: Skip a potential match
- **View Resume**: Preview uploaded documents (if available)
- **Similarity Score**: See percentage match based on interests/documents

### Match Creation

#### Mutual Matching
- **Automatic Detection**: Match created when both users like each other
- **Notifications**: Flash messages notify users of new matches
- **Match History**: View all confirmed matches in one place
- **Match Status**: Active/inactive status tracking

#### Interaction Tracking
- **History**: System remembers your like/pass decisions
- **No Duplicates**: Each user appears only once in your matching queue
- **Privacy**: Your interactions are private (not visible to other users)

### Match Outcomes & Meeting Assignment

#### Real-Time Assignment
- **Immediate Feedback**: When a match occurs, the system instantly attempts to schedule a meeting
- **Status Display**:
  - **✅ Scheduled**: Meeting successfully assigned with time and location
  - **⚠️ Pending**: Meeting could not be auto-assigned (e.g., no overlapping availability)
  - **⏳ Processing**: Assignment calculation in progress

#### Match Modal
- **Smart Notifications**: Shows meeting details immediately upon matching
- **Next Steps Guidelines**: Provides actionable advice if meeting assignment fails
- **Browser Notifications**: Desktop alerts for successful assignments (even if tab is backgrounded)

#### Matches Page
- **Comprehensive View**: See all matches with their assignment status
- **Status Badges**: Color-coded indicators for quick status checks
- **Failure Reasons**: Explicit explanation why a meeting wasn't assigned (e.g., "No common free slots")
- **Manual Resolution**: Guidance on how to resolve scheduling conflicts manually

---

## Meeting Scheduling

### Hierarchical Location System

#### Three-Tier Architecture
1. **Event Locations**: Physical venues (e.g., "Main Hall", "Conference Room A")
2. **Event Sessions**: Time-based activities within locations (e.g., "Morning Networking")
3. **Meeting Points**: Specific spots for pairs to meet (e.g., "Table 1", "Booth 5")

This hierarchy provides clear organization and flexible meeting allocation.

### For Event Participants

#### Session Selection
- **Availability Management**: Select which event sessions you plan to attend
- **Matching-Enabled Sessions**: Only sessions with matching enabled are shown
- **Visual Feedback**: Clickable cards with day badges and times
- **Session Filtering**: See only attendees from your selected sessions (toggle available)

#### Smart Availability Management
- **Impact Analysis**: System warns you if deselecting a session will affect existing meetings
- **Automatic Reassignment**: If you become unavailable for a scheduled meeting, the system tries to reschedule it to another mutual free slot
- **Transparent Status**: Immediate feedback on whether meetings were successfully moved or if they require manual rescheduling

### For Event Managers

#### Event Location Management
- **Create Locations**: Define physical venues where sessions take place
- **Assign Purpose**: Link sessions and meeting points to locations
- **Guided Workflow**: Step-by-step interface for setup

#### Session Management (Day-Based)
- **Create Sessions**: Define event sessions with:
  - Session name (e.g., "Morning Networking")
  - Day number (Day 1, Day 2, Day 3, etc.)
  - Start time and end time (time-only, no dates!)
  - Assigned event location
  - Enable/disable matching per session
- **Day-Based System**: Sessions use relative days instead of specific dates
- **Flexible Dating**: Event dates set separately, sessions calculated at runtime
- **Edit Sessions**: Modify session details and toggle matching
- **Delete Sessions**: Remove sessions (with cascade cleanup)
- **Session Overview**: View all sessions ordered by day and time

#### Meeting Point Management
- **Create Meeting Points**: Define specific meeting spots with:
  - Location name (e.g., "Hall 1 Table 11")
  - Capacity (Number of *concurrent pairs* that can meet here)
  - **Multi-Location Assignment**: A single meeting point can be associated with *multiple* Event Locations (e.g., a central "Networking Hub" used by sessions in strictly different rooms)
- **Auto-Assignment Ready**: Meeting points are automatically selected based on session location
- **Delete Points**: Remove unused meeting points

#### Automatic Meeting Assignment
- **On-Match Trigger**: Automatically assigns meetings when users match
- **Intelligence**:
  - Finds overlapping session availability
  - Allocates 15-minute time slots
  - Assigns available meeting points
  - Avoids scheduling conflicts
- **Error Handling**: Gracefully handles edge cases
- **Logging**: Detailed logs for debugging and monitoring

#### Event Publishing Workflow
- **Draft Mode**: Create events without dates (not publicly visible)
- **Publish**: Requires start/end dates, enables attendee registration
- **Flexible Setup**: Set up sessions and locations before publishing

### Notifications
- **Dual System**: Real-time Web Push notifications + Email notifications
- **Calendar Integration**: Automated .ics calendar invites sent via email on match
- **Web Alerts**: Interactive toast notifications for instant feedback
- **Smart Triggers**: Browser notifications specific to successful meeting assignments

---

## Document Management

### Resume Upload

#### Supported Formats
- **PDF**: Portable Document Format (.pdf)
- **Microsoft Word**: Document files (.doc, .docx)
- **File Size Limit**: Maximum 16MB per file

#### Upload Process
1. Navigate to event dashboard
2. Click "Upload Resume" for specific event
3. Select file from your device
4. System validates file type and size
5. File uploaded and processed for matching

### File Security & Privacy
- **Validation**: strict type checking (PDF/DOCX) and size limits (16MB)
- **Isolation**: Files are securely stored with unique filenames
- **Access Control**: Strict ownership checks ensure only you can view your files

### File Operations
- **View**: Preview uploaded resumes
- **Download**: Retrieve original files
- **Delete**: Remove resumes (clears from matching)
- **Replace**: Upload new version (auto-deletes old)

---

## Admin Panel

### Dashboard Analytics

#### Key Metrics
- **Total Users**: Count of registered attendees (excludes admins)
- **Total Events**: Number of events in the system
- **Total Memberships**: Event participation count
- **Total Resumes**: Uploaded documents count
- **Total Matches**: Confirmed connections count

#### Recent Activity
- **Recent Events**: Last 5 created events
- **Recent Users**: Last 5 registered users
- **Activity Tracking**: Monitor platform usage trends

### User Management

#### User Operations
- **List Users**: View all registered users with details
- **Search**: Filter users by name or email
- **Toggle Admin Status**: Promote/demote users
- **Delete Users**: Remove users with cascade cleanup
  - Removes all memberships
  - Removes all resumes
  - Removes all matches
  - Removes all interactions

#### Safety Features
- **Self-Protection**: Admins cannot delete their own account
- **Confirmation**: Deletion requires explicit confirmation
- **Cascade Notices**: Warns about related data deletion

### Event Management

#### Event Operations
- **Create Events**: Add new events via admin panel
- **Edit Events**: Modify event details
- **Delete Events**: Remove events with full cleanup
- **View Statistics**: See member count, matches, resumes per event

#### Advanced Features
- **Session Management**: Access session configuration for any event
- **Location Management**: Configure meeting locations
- **Network Graphs**: Visualize connection networks
- **Allocation Control**: Run/reset meeting allocations

### File Management

#### Orphaned File Cleanup
- **Detection**: Finds files without database records
- **Preview**: Lists files to be removed
- **Cleanup**: Removes orphaned files from storage
- **Safety**: Only removes files not referenced in database

---

## Cross-Device Synchronization

### Export Functionality

#### What Gets Exported
- **Database**: All data (users, events, memberships, resumes, matches, interactions)
- **Files**: All uploaded documents
- **Format**: JSON for data, original format for files
- **Timestamp**: Export named with date/time for easy identification

#### Export Command
```bash
python scripts/import_database.py --export
```

#### Export Options
- `--no-files`: Export database without files (faster)
- Default: Exports both database and files

### Import Functionality

#### What Gets Imported
- **All Tables**: Users, events, memberships, resumes, matches, interactions
- **All Files**: Restores uploaded documents to correct locations
- **Validation**: Checks data integrity before import

#### Import Command
```bash
python scripts/import_database.py --import
```

#### Import Options
- `--no-files`: Import database without files
- `--yes`: Skip confirmation prompt (use with caution)
- Default: Imports latest export with confirmation

#### Safety Features
- **Confirmation**: Warns before replacing existing data
- **Latest Detection**: Automatically finds most recent export
- **Progress Tracking**: Shows import progress with emoji indicators
- **Error Handling**: Reports missing files or data issues

### Use Cases

#### Device Migration
1. Export on old device: `python scripts/import_database.py --export`
2. Copy `exports/` folder to new device
3. Import on new device: `python scripts/import_database.py --import`

#### Backup & Restore
- **Regular Backups**: Export periodically for data safety
- **Quick Restore**: Import from backups if data is lost
- **Version Control**: Keep multiple exports with timestamps

#### Multi-Device Development
- **Sync Development Data**: Share database across team
- **Consistent Environment**: Ensure all devs have same data
- **Fast Setup**: New team members import existing data

---

## Additional Features

### Network Visualization
- Interactive graphs showing connection networks
- Visual representation of matching patterns
- Community detection algorithms
- Export network data for analysis

### Messaging System (Future)
- Direct messaging between matched users
- Event-specific message boards
- Notification system for new messages

### Calendar Integration (Planned)
- Export meeting schedules to calendar apps
- iCal/Google Calendar support
- Meeting reminders and notifications

### Mobile App (Future)
- Native iOS and Android applications
- Real-time notifications
- QR code scanning for quick event join
- NFC integration for tap-to-connect

---

For implementation details, see [DEVELOPMENT.md](DEVELOPMENT.md).  
For API endpoints, see [API.md](API.md).  
For setup instructions, see [SETUP.md](SETUP.md).
