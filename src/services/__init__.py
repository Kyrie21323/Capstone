"""
Prophere services package.
Business logic and external integrations (email, etc.).
"""
from .email_service import (
    send_match_notification,
    send_match_notifications_to_both,
    handle_match_created,
)

__all__ = [
    'send_match_notification',
    'send_match_notifications_to_both',
    'handle_match_created',
]
