"""
Email Notification Utility
Sends email notifications with calendar invites when users match.
"""
from flask import current_app, render_template_string
from flask_mail import Mail, Message
from icalendar import Calendar, Event as CalEvent, vText
from datetime import datetime
from models import User, Event, Meeting

# Email template for match notification
MATCH_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #57068c 0%, #ab82c5 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .match-info { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #57068c; }
        .meeting-details { background: #e7f3ff; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .button { display: inline-block; padding: 12px 24px; background: #57068c; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 It's a Match!</h1>
        </div>
        <div class="content">
            <p>Great news! You've matched with <strong>{{ other_user_name }}</strong> at {{ event_name }}!</p>
            
            <div class="match-info">
                <h3>Your Match</h3>
                <p><strong>Name:</strong> {{ other_user_name }}</p>
                <p><strong>Email:</strong> {{ other_user_email }}</p>
                {% if other_user_keywords %}
                <p><strong>Interests:</strong> {{ other_user_keywords }}</p>
                {% endif %}
            </div>
            
            {% if meeting %}
            <div class="meeting-details">
                <h3>📅 Your Meeting Has Been Scheduled</h3>
                <p><strong>Date & Time:</strong> {{ meeting_time }}</p>
                <p><strong>Duration:</strong> 15 minutes</p>
                <p><strong>Location:</strong> {{ meeting_location }}</p>
                <p><strong>Session:</strong> {{ session_name }}</p>
            </div>
            
            <p>A calendar invite is attached to this email. Simply open the attachment to add this meeting to your calendar!</p>
            {% else %}
            <p>We couldn't automatically schedule your meeting, but you can coordinate directly with your match.</p>
            {% endif %}
            
            <p>Looking forward to you making valuable connections!</p>
            
            <div class="footer">
                <p>This is an automated message from {{ event_name }}</p>
                <p>Powered by Prophere</p>
            </div>
        </div>
    </div>
</body>
</html>
"""


def create_calendar_invite(meeting, match, event, user1, user2):
    """
    Create an iCalendar (.ics) file for a meeting.
    
    Args:
        meeting: Meeting object
        match: Match object
        event: Event object
        user1: User object (first user)
        user2: User object (second user)
    
    Returns:
        bytes: iCalendar file content
    """
    cal = Calendar()
    cal.add('prodid', '-//Prophere Networking Platform//EN')
    cal.add('version', '2.0')
    cal.add('method', 'REQUEST')
    
    # Create the event
    event_item = CalEvent()
    event_item.add('summary', f'Networking Meeting: {user1.name} & {user2.name}')
    event_item.add('dtstart', meeting.start_time)
    event_item.add('dtend', meeting.end_time)
    event_item.add('dtstamp', datetime.utcnow())
    
    # Add location
    location_text = f"{meeting.location.name}"
    if meeting.session and meeting.session.session_location:
        location_text = f"{meeting.session.session_location.name} - {meeting.location.name}"
    event_item.add('location', vText(location_text))
    
    # Add description
    description = f"""
Networking meeting from {event.name}

Attendees:
- {user1.name} ({user1.email})
- {user2.name} ({user2.email})

Session: {meeting.session.name if meeting.session else 'N/A'}
Location: {location_text}

This is a 15-minute networking meeting. Please be on time!
    """.strip()
    event_item.add('description', vText(description))
    
    # Add organizer and attendees
    event_item.add('organizer', vText(f'mailto:{current_app.config.get("MAIL_DEFAULT_SENDER", "noreply@prophere.com")}'))
    event_item.add('attendee', vText(f'mailto:{user1.email}'))
    event_item.add('attendee', vText(f'mailto:{user2.email}'))
    
    # Add to calendar
    cal.add_component(event_item)
    
    return cal.to_ical()


def send_match_notification_email(user, other_user, event, meeting=None, match=None):
    """
    Send email notification to a user about a new match.
    
    Args:
        user: User object (recipient)
        other_user: User object (the match)
        event: Event object
        meeting: Meeting object (optional, if auto-assigned)
        match: Match object (for additional context)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        mail = Mail(current_app)
        
        # Prepare email data
        other_user_keywords = ', '.join(match.get_other_user(user.id).keywords.split(',')[:5]) if match else 'N/A'
        
        # Format meeting details if available
        meeting_time = None
        meeting_location = None
        session_name = None
        
        if meeting:
            meeting_time = meeting.start_time.strftime('%A, %B %d, %Y at %I:%M %p')
            meeting_location = meeting.location.name
            if meeting.session and meeting.session.session_location:
                meeting_location = f"{meeting.session.session_location.name} - {meeting.location.name}"
            session_name = meeting.session.name if meeting.session else 'N/A'
        
        # Render email HTML
        html_content = render_template_string(
            MATCH_EMAIL_TEMPLATE,
            other_user_name=other_user.name,
            other_user_email=other_user.email,
            other_user_keywords=other_user_keywords,
            event_name=event.name,
            meeting=meeting,
            meeting_time=meeting_time,
            meeting_location=meeting_location,
            session_name=session_name
        )
        
        # Create email message
        msg = Message(
            subject=f"🎉 New Match at {event.name}!",
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@prophere.com'),
            recipients=[user.email]
        )
        msg.html = html_content
        
        # Attach calendar invite if meeting exists
        if meeting and match:
            # Get both users for the calendar invite
            user1 = User.query.get(match.user1_id)
            user2 = User.query.get(match.user2_id)
            
            ics_content = create_calendar_invite(meeting, match, event, user1, user2)
            msg.attach(
                "meeting.ics",
                "text/calendar",
                ics_content,
                headers=[('Content-Class', 'urn:content-classes:calendarmessage')]
            )
        
        # Send email
        mail.send(msg)
        
        print(f"✅ Email sent to {user.email} about match with {other_user.name}")
        return (True, "Email sent successfully")
        
    except Exception as e:
        print(f"❌ Failed to send email to {user.email}: {str(e)}")
        return (False, f"Failed to send email: {str(e)}")


def send_match_notifications_to_both(match, event, meeting=None):
    """
    Send match notification emails to both users in a match.
    
    Args:
        match: Match object
        event: Event object
        meeting: Meeting object (optional, if auto-assigned)
    
    Returns:
        tuple: (success_count: int, total: int, messages: list)
    """
    user1 = User.query.get(match.user1_id)
    user2 = User.query.get(match.user2_id)
    
    if not user1 or not user2:
        return (0, 2, ["User not found"])
    
    results = []
    success_count = 0
    
    # Send to user1
    success1, msg1 = send_match_notification_email(user1, user2, event, meeting, match)
    results.append(f"User1 ({user1.email}): {msg1}")
    if success1:
        success_count += 1
    
    # Send to user2
    success2, msg2 = send_match_notification_email(user2, user1, event, meeting, match)
    results.append(f"User2 ({user2.email}): {msg2}")
    if success2:
        success_count += 1
    
    return (success_count, 2, results)
