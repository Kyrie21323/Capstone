# Email notification system (match notifications)

Production-ready email flow: when a match is created and committed, both users receive an email. Sending is non-blocking (background thread) and never crashes the app.

## 1. Folder structure

```
Capstone/
├── main.py                    # Loads .env via python-dotenv
├── .env.example               # Template for MAIL_* and other env vars (copy to .env)
├── src/
│   ├── app.py                 # Flask-Mail initialized with app
│   ├── config.py              # MAIL_*, APPLICATION_ROOT_URL from env
│   ├── services/
│   │   ├── __init__.py        # Exposes send_match_notification, send_match_notifications_to_both
│   │   └── email_service.py   # SMTP send, templates, logging, no raises
│   ├── templates/
│   │   └── email/
│   │       ├── match_notification.html
│   │       └── match_notification.txt
│   └── routes/
│       └── matching.py        # Triggers email after db.session.commit() in a thread
└── docs/
    └── EMAIL_SETUP.md        # This file
```

## 2. Environment configuration

Copy `.env.example` to `.env` and set:

| Variable | Purpose | Example |
|----------|---------|--------|
| `MAIL_SERVER` | SMTP host | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port (TLS often 587) | `587` |
| `MAIL_USE_TLS` | Use TLS | `true` |
| `MAIL_USERNAME` | SMTP login | your email |
| `MAIL_PASSWORD` | SMTP password or app password | app password |
| `MAIL_DEFAULT_SENDER` | From address | `noreply@prophere.com` |
| `MAIL_SUPPRESS_SEND` | If `true`, skip sending (e.g. dev) | `false` |
| `APPLICATION_ROOT_URL` | Base URL for “View matches” link | `https://yourapp.com` |

- **Do not** hardcode credentials; use `.env` (and ensure `.env` is in `.gitignore`).
- For Gmail: use an [App Password](https://support.google.com/accounts/answer/185833), not your normal password.

## 3. Trigger after match creation (idempotent, no duplicate emails)

- Match is created and, if possible, a meeting is auto-assigned.
- **Then** `db.session.commit()` is called.
- **Only after a successful commit** we start a background thread that:
  - Pushes an app context and loads `Match`, `Event`, and optional `Meeting` by ID.
  - Calls `send_match_notifications_to_both(match, event, meeting)`.

So:

- Emails are sent only after the match is persisted.
- If the request is retried, the match already exists (`existing_match`), so we do not create a second match and do not send emails again (idempotent).

## 4. Asynchronous sending (non-blocking)

- A **daemon thread** runs the email send so the HTTP response is not blocked.
- The thread uses `app.app_context()` so Flask-Mail and DB access work correctly.
- Failures in the thread are logged; they do not affect the response or crash the app.

## 5. Email content

- **Subject:** `You've been matched at {{ event_name }}!`
- **HTML:** `templates/email/match_notification.html` (clean, responsive).
- **Plain text:** `templates/email/match_notification.txt` (fallback).
- Content includes: matched person’s name, event name, optional profile summary (e.g. keywords), and if a meeting was assigned: time, location, session and an attached `.ics` calendar invite.

## 6. Error handling

- **Service layer (`email_service.py`):**
  - All sending is in `try/except`; exceptions are logged and converted to `(False, message)` or `(0, total, messages)`.
  - No exception is re-raised to the caller, so the main app never crashes because of email.
- **Configuration:**
  - If `MAIL_SUPPRESS_SEND` is true or `MAIL_SERVER`/`MAIL_USERNAME` are missing, the service skips sending and logs a warning.
- **Background thread:**
  - Any exception in the thread is caught and logged; the request has already returned success.

## 7. Security considerations

- **Credentials:** Only from environment (e.g. `.env`), never in code or repo.
- **.env:** Add `.env` to `.gitignore`; commit only `.env.example` with placeholders.
- **TLS:** Use `MAIL_USE_TLS=true` for production.
- **Sender/recipients:** Use `MAIL_DEFAULT_SENDER`; recipients come from the `User` model (no user input for addresses).
- **Content:** Email body uses Jinja templates with escaped variables; no raw user HTML in the message body.
- **Logging:** Avoid logging full credentials; log only “email sent to …” or “send failed for match_id …”.

## 8. Example integration (match creation)

In `src/routes/matching.py`, after a mutual like and creating the `Match` and optional `Meeting`:

1. `db.session.commit()` so the match (and meeting) are persisted.
2. Capture `match_id`, `event_id`, and `meeting_id` (or `None`).
3. Start a daemon thread that runs in `app.app_context()`, loads `Match`, `Event`, and optional `Meeting` by ID, and calls `send_match_notifications_to_both(match, event, meeting)`.

See the `like_user` handler in `src/routes/matching.py` for the exact implementation.

## 9. Testing without sending

- Set `MAIL_SUPPRESS_SEND=true` in `.env`; the service will skip sending and log instead.
- Or leave `MAIL_SERVER`/`MAIL_USERNAME` unset; the service will log a warning and skip sending.
