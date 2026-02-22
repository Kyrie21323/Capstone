"""
Production-ready email service for Prophere.
Sends match notifications via SMTP (configurable via environment).
Uses Flask-Mail; credentials from env (MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, etc.).
Never raises: logs failures and returns success/failure so the main app does not crash.
Structured logging: match_id, recipient (email only), success/failure, timestamp. No credentials logged.
"""
import logging
from datetime import datetime
from typing import Optional, Tuple, List

from flask import current_app, render_template
from flask_mail import Mail, Message
from icalendar import Calendar, Event as CalEvent, vText

logger = logging.getLogger(__name__)


def _log_email_result(match_id: Optional[int], recipient_email: str, success: bool, detail: str = ""):
    """Structured log for email send result. Never log credentials."""
    extra = {
        "match_id": match_id,
        "recipient_email": recipient_email,
        "success": success,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if detail:
        extra["detail"] = detail
    if success:
        logger.info("Match notification email sent", extra=extra)
    else:
        logger.warning("Match notification email failed", extra=extra)


def _get_mail() -> Optional[Mail]:
    """Get Flask-Mail instance. Returns None if mail not configured or disabled."""
    if current_app.config.get('MAIL_SUPPRESS_SEND'):
        print("⚠️ MAIL_SUPPRESS_SEND is enabled — email not sent.")
        logger.warning("MAIL_SUPPRESS_SEND is True; skipping send.")
        return None
    username = current_app.config.get('MAIL_USERNAME') or ""
    password = current_app.config.get('MAIL_PASSWORD') or ""
    if username.lower().endswith("@gmail.com") and len(password) < 16:
        print("⚠️ Gmail requires an App Password. Normal password will fail.")
        logger.warning("Gmail detected but MAIL_PASSWORD length < 16; use App Password from https://myaccount.google.com/apppasswords")
    if not current_app.config.get('MAIL_SERVER') or not username:
        print("⚠️ Email not configured: MAIL_SERVER or MAIL_USERNAME missing. Skipping send.")
        logger.warning("Email not configured: MAIL_SERVER or MAIL_USERNAME missing. Skipping send.")
        return None
    return Mail(current_app)


def _profile_summary_for_user_in_event(user_id: int, event_id: int) -> str:
    """Build a short profile summary (e.g. keywords) for a user in an event."""
    try:
        from models import Membership
        m = Membership.query.filter_by(user_id=user_id, event_id=event_id).first()
        if m and m.keywords:
            keywords = m.get_keywords_list()
            return ", ".join(keywords[:8]) if keywords else ""
    except Exception as e:
        logger.debug("Could not get profile summary: %s", e)
    return ""


def _create_calendar_invite(meeting, match, event, user1, user2) -> bytes:
    """Build .ics calendar invite for a meeting."""
    cal = Calendar()
    cal.add('prodid', '-//Prophere Networking Platform//EN')
    cal.add('version', '2.0')
    cal.add('method', 'REQUEST')
    event_item = CalEvent()
    event_item.add('summary', f'Networking Meeting: {user1.name} & {user2.name}')
    event_item.add('dtstart', meeting.start_time)
    event_item.add('dtend', meeting.end_time)
    event_item.add('dtstamp', datetime.utcnow())
    location_text = meeting.location.name if meeting.location else "TBA"
    if meeting.session and getattr(meeting.session, 'session_location', None) and meeting.session.session_location:
        location_text = f"{meeting.session.session_location.name} - {meeting.location.name}"
    event_item.add('location', vText(location_text))
    description = (
        f"Networking meeting from {event.name}\n"
        f"Attendees: {user1.name} ({user1.email}), {user2.name} ({user2.email})\n"
        f"Session: {meeting.session.name if meeting.session else 'N/A'}\n"
        f"Location: {location_text}\n"
        "15-minute networking meeting."
    )
    event_item.add('description', vText(description))
    sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@prophere.com')
    event_item.add('organizer', vText(f'mailto:{sender}'))
    event_item.add('attendee', vText(f'mailto:{user1.email}'))
    event_item.add('attendee', vText(f'mailto:{user2.email}'))
    cal.add_component(event_item)
    return cal.to_ical()


def send_match_notification(
    recipient_user,
    matched_user,
    event,
    meeting=None,
    profile_summary: Optional[str] = None,
    match_id: Optional[int] = None,
) -> Tuple[bool, str]:
    """
    Send a single match notification email to one user.

    Args:
        recipient_user: User model instance (recipient).
        matched_user: User model instance (the person they matched with).
        event: Event model instance.
        meeting: Optional Meeting model instance (if auto-assigned).
        profile_summary: Optional string (e.g. keywords). If None, will try to derive from Membership.
        match_id: Optional match id for structured logging.

    Returns:
        (success: bool, message: str)
    """
    if profile_summary is None:
        profile_summary = _profile_summary_for_user_in_event(matched_user.id, event.id)

    mail = _get_mail()
    if mail is None:
        return (False, "Email sending disabled or not configured")

    try:
        meeting_time = None
        meeting_location = None
        session_name = None
        if meeting:
            meeting_time = meeting.start_time.strftime('%A, %B %d, %Y at %I:%M %p')
            meeting_location = meeting.location.name if meeting.location else "TBA"
            if meeting.session and getattr(meeting.session, 'session_location', None) and meeting.session.session_location:
                meeting_location = f"{meeting.session.session_location.name} - {meeting.location.name}"
            session_name = meeting.session.name if meeting.session else "TBA"

        platform_url = current_app.config.get('APPLICATION_ROOT_URL', '')
        try:
            from flask import request
            if not platform_url and request:
                platform_url = request.url_root.rstrip('/')
        except Exception:
            pass

        html_body = render_template(
            'email/match_notification.html',
            recipient_name=recipient_user.name,
            matched_name=matched_user.name,
            matched_email=matched_user.email,
            event_name=event.name,
            profile_summary=profile_summary or "",
            meeting=meeting,
            meeting_time=meeting_time,
            meeting_location=meeting_location,
            session_name=session_name,
            platform_url=platform_url,
        )
        text_body = render_template(
            'email/match_notification.txt',
            recipient_name=recipient_user.name,
            matched_name=matched_user.name,
            matched_email=matched_user.email,
            event_name=event.name,
            profile_summary=profile_summary or "",
            meeting=meeting,
            meeting_time=meeting_time,
            meeting_location=meeting_location,
            session_name=session_name,
            platform_url=platform_url,
        )

        subject = f"You've been matched at {event.name}!"
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@prophere.com')
        msg = Message(
            subject=subject,
            sender=sender,
            recipients=[recipient_user.email],
        )
        msg.body = text_body
        msg.html = html_body

        if meeting and hasattr(meeting, 'match') and meeting.match:
            from models import User
            user1 = User.query.get(meeting.match.user1_id)
            user2 = User.query.get(meeting.match.user2_id)
            if user1 and user2:
                ics = _create_calendar_invite(meeting, meeting.match, event, user1, user2)
                msg.attach("meeting.ics", "text/calendar", ics, headers=[('Content-Class', 'urn:content-classes:calendarmessage')])

        recipient_email = getattr(recipient_user, "email", "")
        print(f"📤 Attempting to send email to {recipient_email}")
        mail.send(msg)
        print(f"✅ Email sent to {recipient_email}")
        _log_email_result(match_id, recipient_email, True)
        return (True, "Email sent successfully")
    except Exception as e:
        recipient_email = getattr(recipient_user, "email", "")
        print(f"❌ Email failed for {recipient_email}: {str(e)}")
        _log_email_result(match_id, recipient_email, False, detail=str(e))
        logger.exception("Match notification send failed for match_id=%s recipient=%s", match_id, recipient_email)
        return (False, str(e))


def send_match_notifications_to_both(match, event, meeting=None) -> Tuple[int, int, List[str]]:
    """
    Send match notification emails to both users in a match.
    Call this only after the match has been successfully committed to the database.

    Args:
        match: Match model instance (with user1_id, user2_id, event_id).
        event: Event model instance.
        meeting: Optional Meeting model instance (if auto-assigned).

    Returns:
        (success_count: int, total: int, messages: list of str)
    """
    from models import User
    mid = getattr(match, "id", None)
    user1 = User.query.get(match.user1_id)
    user2 = User.query.get(match.user2_id)
    if not user1 or not user2:
        _log_email_result(mid, "n/a", False, detail="User not found")
        logger.warning("Match %s: user1 or user2 not found, skipping email", mid)
        return (0, 2, ["User not found"])

    results = []
    success_count = 0

    s1, m1 = send_match_notification(user1, user2, event, meeting=meeting, match_id=mid)
    results.append(f"User1 ({user1.email}): {m1}")
    if s1:
        success_count += 1

    s2, m2 = send_match_notification(user2, user1, event, meeting=meeting, match_id=mid)
    results.append(f"User2 ({user2.email}): {m2}")
    if s2:
        success_count += 1

    return (success_count, 2, results)


def handle_match_created(match_id: int) -> None:
    """
    Idempotent handler for match creation: send notification emails at most once per match.
    Call this inside an active Flask app context (e.g. from a background thread with app.app_context()).

    - If email_sent_at is already set, skips sending (idempotent).
    - Sends to both users; only if BOTH succeed sets match.email_sent_at and commits.
    - On any failure, does not update email_sent_at and logs the failure.

    Args:
        match_id: ID of the Match record (must already be committed).
    """
    from models import db, Match, Event, Meeting

    print("📩 handle_match_created called for match_id=%s" % match_id)
    match = Match.query.get(match_id)
    if not match:
        print("❌ handle_match_created: match_id=%s not found" % match_id)
        logger.warning("handle_match_created: match_id=%s not found", match_id, extra={"match_id": match_id, "timestamp": datetime.utcnow().isoformat() + "Z"})
        return

    print("email_sent_at:", match.email_sent_at)
    if match.email_sent_at is not None:
        logger.info(
            "Match notification already sent, skipping (idempotent)",
            extra={"match_id": match_id, "email_sent_at": match.email_sent_at.isoformat(), "timestamp": datetime.utcnow().isoformat() + "Z"},
        )
        return

    event = Event.query.get(match.event_id)
    if not event:
        _log_email_result(match_id, "n/a", False, detail="Event not found")
        logger.warning("handle_match_created: event_id=%s not found for match_id=%s", match.event_id, match_id)
        return

    meeting = Meeting.query.filter_by(match_id=match_id, status="scheduled").first()

    success_count, total, messages = send_match_notifications_to_both(match, event, meeting)

    if success_count == total and total == 2:
        try:
            match.email_sent_at = datetime.utcnow()
            db.session.commit()
            logger.info(
                "Match notification emails sent and recorded",
                extra={"match_id": match_id, "success_count": success_count, "timestamp": datetime.utcnow().isoformat() + "Z"},
            )
        except Exception as e:
            logger.exception("Failed to update match.email_sent_at for match_id=%s: %s", match_id, e)
            db.session.rollback()
    else:
        logger.warning(
            "Match notification partial or failed, not updating email_sent_at",
            extra={"match_id": match_id, "success_count": success_count, "total": total, "messages": messages, "timestamp": datetime.utcnow().isoformat() + "Z"},
        )
