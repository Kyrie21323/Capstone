# Features

Detailed guide to all features available in the NFC Networking Platform.

## User Authentication System

### Registration & Login
- **Email-based Authentication**: Secure registration and login using email addresses
- **Password Security**: Passwords hashed using Werkzeug's PBKDF2-SHA256 with salt
- **Session Management**: Persistent sessions using Flask-Login
- **Remember Me**: Optional persistent login across browser sessions

### Role-Based Access Control
- **Event Attendee**: Standard user role for event participants
- **Event Manager**: Administrative role with full event management capabilities
- **Role Promotion**: Admins can promote attendees to managers
- **Role Demotion**: Admins can demote managers to attendees
- **Self-Protection**: Users cannot modify their own admin status

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

---

## Meeting Scheduling

### For Event Participants

#### Availability Management
- **Session Selection**: Indicate which event sessions you can attend
- **Time Preferences**: Select preferred time slots within sessions
- **Availability Updates**: Modify availability at any time before allocation
- **Visual Calendar**: Clear interface showing all available time slots

### For Event Managers

#### Session Management
- **Create Sessions**: Define event sessions with:
  - Session name (e.g., "Morning Networking")
  - Start time and end time
  - Location description (e.g., "Grand Hall")
- **Edit Sessions**: Modify session details
- **Delete Sessions**: Remove sessions (with cascade cleanup)
- **Session Overview**: View all sessions in chronological order

#### Location Management
- **Create Locations**: Define meeting locations with:
  - Location name (e.g., "Hall 1 Table 11")
  - Capacity (default: 2 people)
- **Organize Locations**: Group by event
- **Delete Locations**: Remove unused locations
- **Capacity Planning**: Set appropriate capacity for each location

#### Automated Allocation
- **One-Click Allocation**: Run algorithm to assign meetings
- **Intelligent Matching**:
  - Matches participants based on mutual availability
  - Assigns appropriate meeting locations
  - Respects location capacity constraints
- **Conflict Resolution**: Handles scheduling conflicts automatically
- **Results Preview**: View allocation results before confirming

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

### File Security

#### Validation
- **Type Checking**: Only PDF, DOC, DOCX files accepted
- **Size Verification**: Files must be under 16MB
- **Virus Scanning**: (Planned) Malware detection
- **Secure Filenames**: System generates secure unique filenames

#### Storage
- **User Isolation**: Each user has separate upload directory
- **Event Isolation**: One resume per user per event
- **Access Control**: Only file owner can view/download/delete
- **Metadata Tracking**: Original filename, MIME type, size, upload timestamp

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
- **Search**: Filter users by name or email (coming soon)
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
- **Network Graphs**: Visualize connection networks (coming soon)
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

### Network Visualization (Coming Soon)
- Interactive graphs showing connection networks
- Visual representation of matching patterns
- Community detection algorithms
- Export network data for analysis

### Messaging System (Planned)
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
