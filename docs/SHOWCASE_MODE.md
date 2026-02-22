# Showcase Mode — Technical Documentation

**Version:** 1.0  
**Last updated:** 2026-02-22  
**Relevant files:** `src/showcase/`, `src/routes/showcase.py`, `src/templates/showcase/`, `src/static/css/showcase.css`

---

## Table of Contents

1. [What This Is](#1-what-this-is)
2. [Architecture Overview](#2-architecture-overview)
3. [File Map](#3-file-map)
4. [Complete User Flow](#4-complete-user-flow)
5. [How Each Component Works](#5-how-each-component-works)
   - [5.1 Profiles (`demo_profiles.py`)](#51-profiles-demo_profilespy)
   - [5.2 Routes (`routes/showcase.py`)](#52-routes-routesshowcasepy)
   - [5.3 Session Memory](#53-session-memory)
   - [5.4 Templates](#54-templates)
   - [5.5 JavaScript Engine](#55-javascript-engine)
   - [5.6 Question Generator](#56-question-generator)
6. [Maintenance Guide](#6-maintenance-guide)
   - [6.1 Adding or Editing Profiles](#61-adding-or-editing-profiles)
   - [6.2 Adding Questions](#62-adding-questions)
   - [6.3 Changing the Match Memory Depth](#63-changing-the-match-memory-depth)
   - [6.4 Changing the Reveal Timing](#64-changing-the-reveal-timing)
   - [6.5 Changing Colors or Typography](#65-changing-colors-or-typography)
7. [NFC Migration Guide](#7-nfc-migration-guide)
   - [7.1 What Must Change (and What Must Not)](#71-what-must-change-and-what-must-not)
   - [7.2 How the Tap Endpoint Works Today](#72-how-the-tap-endpoint-works-today)
   - [7.3 Option A — Web NFC API (iPad / Chrome Android)](#73-option-a--web-nfc-api-ipad--chrome-android)
   - [7.4 Option B — Physical NFC Reader via Serial/USB](#74-option-b--physical-nfc-reader-via-serialusb)
   - [7.5 Option C — NFC Tags with Encoded Profile IDs](#75-option-c--nfc-tags-with-encoded-profile-ids)
   - [7.6 Recommended Approach for IM Showcase](#76-recommended-approach-for-im-showcase)
   - [7.7 NFC Tag Encoding Reference](#77-nfc-tag-encoding-reference)
8. [API Reference](#8-api-reference)
9. [Isolation Guarantee](#9-isolation-guarantee)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What This Is

Showcase Mode is a **completely isolated, installation-only feature** of Prophere built for the Interactive Media Showcase. It lives under the `/showcase` URL prefix and has zero dependencies on:

- User authentication (no login required)
- The SQLAlchemy database (no models touched)
- The NLP matching engine (Sentence Transformers not loaded)
- Email / Celery / any other production service

All state lives in the **Flask session cookie** and resets when the browser session clears. The entire experience is designed to run on a single iPad in kiosk mode.

---

## 2. Architecture Overview

```
Browser (iPad)
     │
     │  GET /showcase           → Landing page
     │  POST /showcase/tap      → Simulates NFC tap (picks random profile)
     │  GET  /showcase/match    → Match reveal screen
     │  POST /showcase/generate_question  → Returns new question as JSON
     │  POST /showcase/reset    → Clears session, returns to landing
     │
     ▼
Flask Blueprint (showcase_bp)
     │
     ├── Session (cookie)
     │     showcase_scanned    → [profile_id, ...]  (tapped so far)
     │     showcase_matched    → True / False
     │     showcase_questions  → {"1_to_4": ["q1","q2"], ...}
     │
     └── In-memory data only
           DEMO_PROFILES       → list of 10 dicts
           generate_question() → directional question pool
```

There is no database call anywhere in this flow. The session cookie is the only persistent state, and it clears on browser close or when the operator presses "Reset Showcase".

---

## 3. File Map

```
Capstone/
├── src/
│   ├── showcase/
│   │   ├── __init__.py           — Package marker
│   │   └── demo_profiles.py      — 10 hardcoded profiles + generate_question()
│   │
│   ├── routes/
│   │   └── showcase.py           — Blueprint: 5 routes + session helpers
│   │
│   ├── templates/
│   │   └── showcase/
│   │       ├── index.html        — Landing page (tap flow, 3 states)
│   │       └── match.html        — Match reveal + conversation engine
│   │
│   ├── static/
│   │   └── css/
│   │       └── showcase.css      — All showcase styles (no shared CSS)
│   │
│   └── app.py                    — Blueprint registered here (1 line change)
│
└── docs/
    └── SHOWCASE_MODE.md          — This file
```

---

## 4. Complete User Flow

```
┌─────────────────────────────────────────────────────┐
│  LANDING PAGE  /showcase                            │
│                                                     │
│  State A — No taps yet                              │
│    Pulsing NFC hex icon                             │
│    "Tap to Connect"                                 │
│    [Simulate NFC Tap] button                        │
│                                                     │
│  POST /showcase/tap → random profile selected       │
│  → redirect back to /showcase                       │
│                                                     │
│  State B — One tap done                             │
│    Profile card visible                             │
│    "Waiting for a second tap…"                      │
│    [Simulate Second NFC Tap] button                 │
│                                                     │
│  POST /showcase/tap → second profile selected       │
│  → session_matched = True                           │
│  → redirect to /showcase/match                     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  MATCH PAGE  /showcase/match                        │
│                                                     │
│  Phase 1 — Searching (0–800ms)                      │
│    Both cards dimmed with purple pulse              │
│    "SEARCHING…" with progress bar in connector      │
│                                                     │
│  Phase 1 — Reveal (~800ms–1100ms)                   │
│    SVG line draws between cards                     │
│    Cards un-dim                                     │
│    "🎉 You've Been Matched!" fades in               │
│    Shared interests badge (if any)                  │
│    "Who asks first?" prompt                         │
│    [Ask as Profile A] [Ask as Profile B]            │
│                                                     │
│  User presses directional button                    │
│  → POST /showcase/generate_question (fetch)         │
│  → Phase 1 fades out                               │
│                                                     │
│  Phase 2 — Conversation engine                      │
│    Speaker bar: [🔮 A · asking] → [🧠 B]           │
│    "Profile A asks:" header                         │
│    Large question in blockquote                     │
│    [Ask Another] [⇄ Switch Roles]                  │
│                                                     │
│  Ask Another → POST /showcase/generate_question     │
│              → question fades out/in               │
│                                                     │
│  Switch Roles → swaps from/to IDs locally           │
│               → POST /showcase/generate_question    │
│               → speaker bar updates                 │
│                                                     │
│  [↺ Reset Showcase] → POST /showcase/reset          │
│                     → clears all session keys       │
│                     → redirect to /showcase         │
└─────────────────────────────────────────────────────┘
```

---

## 5. How Each Component Works

### 5.1 Profiles (`demo_profiles.py`)

The 10 profiles are plain Python dicts in a module-level list `DEMO_PROFILES`. They are never stored in a database. Each profile has:

```python
{
    "id":        int,    # 1–10, used as the stable identifier everywhere
    "name":      str,    # Display name shown in UI
    "emoji":     str,    # Single emoji, shown on cards and chips
    "interests": list,   # Exactly 3 strings from a shared vocabulary
    "bio":       str,    # One sentence shown on the profile card
    "color":     str,    # Hex color (#RRGGBB), drives card accent + chip border
}
```

The `id` field is the **only thing stored in the session**. All other profile data is looked up at render time via `get_profile_by_id(id)`.

---

### 5.2 Routes (`routes/showcase.py`)

| Route | Method | Description |
|-------|--------|-------------|
| `/showcase/` | GET | Landing page. Reads session to determine which of 3 states to show. |
| `/showcase/tap` | POST | Picks a random unused profile, adds its ID to session. If 2 tapped → redirect to match. |
| `/showcase/match` | GET | Renders match page. Reads 2 profile IDs from session. |
| `/showcase/generate_question` | POST | Accepts `{from_id, to_id}` JSON, returns question + profile display data. |
| `/showcase/reset` | POST | Pops all 3 session keys, redirects to landing. |
| `/showcase/status` | GET | Debug-only JSON dump of current session state. |

The blueprint is registered in `src/app.py`:

```python
from routes.showcase import showcase_bp
app.register_blueprint(showcase_bp)  # url_prefix='/showcase' set in Blueprint()
```

---

### 5.3 Session Memory

Three keys are written to the Flask session cookie:

| Key | Type | Contents | Cleared by |
|-----|------|----------|------------|
| `showcase_scanned` | `list[int]` | Profile IDs tapped so far (max 2) | `reset` |
| `showcase_matched` | `bool` | True once 2 profiles are tapped | `reset` |
| `showcase_questions` | `dict` | `{"1_to_4": ["q…","q…"], …}` | `reset` |

The `showcase_questions` dict is keyed by **direction strings** (`"{from_id}_to_{to_id}"`). Each direction independently stores its last `_MEMORY_DEPTH` (default: 3) questions. This means:

- Profile 1 → Profile 4 has its own 3-question memory
- Profile 4 → Profile 1 has a completely separate 3-question memory
- Asking the same question from both directions is possible (and often intentional)

The cookie stays under Flask's 4 KB limit: 3 directions × 3 questions × ~150 chars = ~1350 bytes.

---

### 5.4 Templates

**`index.html`** — Three Jinja2 states controlled by `scanned | length`:

| Condition | State shown |
|-----------|-------------|
| `scanned | length == 0` | Full landing: hex icon, "Tap to Connect", big button |
| `scanned | length == 1` | One-tap: profile card, waiting dots, "Second tap" button |
| `matched == True` | JS redirect to `/showcase/match` (avoids re-rendering) |

Both tap buttons are `<form method="POST" action="/showcase/tap">` — a plain HTML form POST. This is the **exact hook for NFC replacement** (see Section 7).

**`match.html`** — Two phases managed entirely in HTML/JS:

- **Phase 1** (`#phase-match`): Server-rendered profile cards + animated connector. Hidden elements fade in after the 800ms algorithmic delay via JS.
- **Phase 2** (`#phase-question`): Starts as `display:none`. All content is populated dynamically by JS after fetching from `/showcase/generate_question`. Never requires a page reload.

Profile data is embedded at page load as a JS object:

```html
<script>
  window.SHOWCASE = {
    profile1: {{ profile1 | tojson }},
    profile2: {{ profile2 | tojson }},
    generateUrl: "{{ url_for('showcase.generate_question_route') }}"
  };
</script>
```

This means the match page has everything it needs without additional server calls until a question is requested.

---

### 5.5 JavaScript Engine

All JS is inline in `match.html`. There are no external libraries. Key functions:

```
revealMatch()
  └── Called after 800ms DOMContentLoaded delay
  └── Fades searching → draws SVG line → un-dims cards → shows reveal group

startConversation(fromId, toId)
  └── Called by the directional "Ask as X" buttons
  └── Fetches question → populates Phase 2 → transitions Phase 1 out

askAnother()
  └── Refetches with same currentFromId / currentToId
  └── Calls cycleQuestion() for fade-out/in transition

switchRoles()
  └── Swaps currentFromId ↔ currentToId
  └── Refetches → cycleQuestion()

fetchQuestion(fromId, toId, callback)
  └── fetch() POST to window.SHOWCASE.generateUrl
  └── Returns JSON: question, from_name, from_emoji, from_color, to_name, to_emoji, to_color

populateQuestion(data)
  └── Updates chip emojis, names, CSS custom properties, label, blockquote text

cycleQuestion(data)
  └── Adds sc-q-exit to question screen (250ms fade out)
  └── Calls populateQuestion() mid-fade
  └── Adds sc-q-enter (450ms fade in)
  └── Removes sc-q-enter after animation completes
```

---

### 5.6 Question Generator

`generate_question(from_profile, to_profile, exclude=None)` builds a candidate pool from four sources, in order of contextual relevance:

```
Pool 1 — Shared interest templates (highest specificity)
  For each interest both profiles share:
    5 hand-written questions specific to that topic

Pool 2 — To-profile interest templates
  For each of to_profile's 3 interests:
    7 directional question templates → 21 candidates

Pool 3 — Cross-perspective templates
  For each unique (from_interest, to_interest) pair:
    5 templates → up to 45 candidates

Pool 4 — Meta IM questions (always available fallback)
  14 fixed installation-themed questions

Total pool per pair: 80–120+ unique questions before filtering
```

The function:
1. Deduplicates all candidates while preserving pool order
2. Removes any question in the `exclude` list (last 3 for this direction)
3. Returns `random.choice(available)`
4. If the entire pool is exhausted (rare), it resets and draws from the full pool again

---

## 6. Maintenance Guide

### 6.1 Adding or Editing Profiles

Open `src/showcase/demo_profiles.py`. Profiles are in the `DEMO_PROFILES` list.

**To add a profile:**

```python
{
    "id": 11,                         # Must be unique across all profiles
    "name": "Game Designer",
    "emoji": "🎮",
    "interests": ["Game Mechanics", "Narrative Design", "Player Psychology"],
    "bio": "One sentence. Subject does X through Y.",
    "color": "#D97706",               # Hex color. Pick from https://tailwindcss.com/docs/customizing-colors
},
```

Rules:
- `id` must be a unique integer. Don't reuse IDs from deleted profiles.
- `interests` must be exactly 3 strings. Use the existing vocabulary where possible (shared interests only appear when both profiles use the identical string).
- `color` is used for the card top border, profile name, and conversation chip border.

**To edit a profile**, just modify its dict in place. Since nothing is stored in the database, there is no migration required.

**To remove a profile**, delete the dict. If there are 9 or fewer profiles left, the showcase still works — the pool just shrinks.

---

### 6.2 Adding Questions

There are three places to add questions:

**New topic-specific pool** (for a new shared interest):

In `demo_profiles.py`, add a key to `_SHARED_TEMPLATES`:

```python
_SHARED_TEMPLATES: dict[str, list[str]] = {
    # ... existing entries ...
    "Game Mechanics": [
        "Since we both think about game mechanics — what's the difference between a rule and a constraint?",
        "What's the most meaningful choice you've designed into a system?",
        # Add as many as you want — 4–6 is ideal
    ],
}
```

**New generic to-profile templates** (apply to any interest):

Add to `_TO_TEMPLATES`. Use `{to_interest}` as the placeholder:

```python
_TO_TEMPLATES: list[str] = [
    # ... existing entries ...
    "What does success look like in {to_interest} that most practitioners overlook?",
]
```

**New meta questions** (universal fallbacks):

Add to `_META_QUESTIONS`:

```python
_META_QUESTIONS: list[str] = [
    # ... existing entries ...
    "If your work had a warning label, what would it say?",
]
```

---

### 6.3 Changing the Match Memory Depth

The number of recent questions remembered per direction before repeating is controlled by:

```python
# src/routes/showcase.py, line 22
_MEMORY_DEPTH = 3
```

Change this to `5` for longer memory or `1` to allow repeats after just one question.

---

### 6.4 Changing the Reveal Timing

All timing is in the `<script>` block of `src/templates/showcase/match.html`:

```js
// Delay before the "searching" animation ends and match reveals
setTimeout(revealMatch, 800);        // ← Change 800 to adjust algorithmic delay (ms)

// Inside revealMatch():
searching.classList.add('sc-fade-out');
setTimeout(function () { ... }, 300); // ← Searching text fade duration
setTimeout(function () { ... }, 500); // ← Connection node dot delay after line
setTimeout(function () { ... }, 350); // ← Announce + CTA fade-in delay after line

// Phase transition when pressing "Ask as X"
setTimeout(function () { ... }, 380); // ← Phase 1 → Phase 2 slide duration
```

Total delay from page load to "Who asks first?" buttons: approximately `800 + 300 + 350 = 1450ms`.

---

### 6.5 Changing Colors or Typography

All showcase styles are isolated in `src/static/css/showcase.css`. The design tokens are CSS custom properties at the top of the file:

```css
:root {
  --bg:          #0a0a0f;   /* Page background */
  --surface:     #13131a;   /* Card background */
  --surface-2:   #1c1c28;   /* Tag / chip background */
  --border:      rgba(255,255,255,0.08);
  --text:        #f0f0f5;
  --text-muted:  #6b7080;
  --accent:      #7C3AED;   /* Primary purple */
  --accent-glow: rgba(124,58,237,0.35);
  --success:     #10B981;   /* Green — used for connection line + shared interests */
}
```

Changing `--accent` will update the button color, hex node, pulse ring, and search bar in one edit.

---

## 7. NFC Migration Guide

> This section documents exactly what to change to replace the simulated button-click taps with real NFC hardware.

### 7.1 What Must Change (and What Must Not)

| Component | Status | Action needed |
|-----------|--------|---------------|
| `POST /showcase/tap` | ✅ Keep as-is | This endpoint is the integration point |
| `tap()` route logic | ✅ Keep as-is | Profile selection, session write, redirect |
| Button in `index.html` | ❌ Replace | This is the only frontend change required |
| `match.html` | ✅ Keep as-is | No NFC interaction happens here |
| `demo_profiles.py` | ✅ Keep as-is | May need `nfc_uid` field added (see below) |
| Session / question engine | ✅ Keep as-is | Fully unaffected |

**The entire NFC migration is a frontend-only change on `index.html`.** The backend tap logic stays identical.

---

### 7.2 How the Tap Endpoint Works Today

Currently, pressing the button submits this HTML form:

```html
<!-- src/templates/showcase/index.html -->
<form action="/showcase/tap" method="POST">
  <button type="submit">Simulate NFC Tap</button>
</form>
```

The `tap()` route does:
1. Pick a random profile from the unused pool
2. Append its `id` to `session["showcase_scanned"]`
3. If 2 profiles are now scanned → set `session["showcase_matched"] = True` → redirect to `/showcase/match`
4. Otherwise → redirect back to `/showcase/`

The route currently has **no concept of which specific profile was tapped** — it picks randomly. For real NFC tags, each physical tag encodes a specific profile ID, and the route needs to know which one was read.

---

### 7.3 Option A — Web NFC API (iPad / Chrome Android)

> **Best for: Chrome on Android.** As of 2026, Web NFC is supported in Chrome for Android but **not in Safari on iPad**. If the showcase runs on an Android tablet, this is the cleanest option.

**Step 1 — Add `nfc_uid` to each profile** in `demo_profiles.py`:

```python
{
    "id": 1,
    "name": "Speculative Designer",
    "nfc_uid": "04:A1:B2:C3:D4:E5:F6",  # ← UID printed on your NFC tag
    # ... rest unchanged
}
```

Add a helper to look up by NFC UID:

```python
def get_profile_by_nfc_uid(uid: str) -> dict | None:
    return next((p for p in DEMO_PROFILES if p.get("nfc_uid") == uid), None)
```

**Step 2 — Add a new route** in `routes/showcase.py` that accepts a specific profile ID:

```python
@showcase_bp.route("/tap/<int:profile_id>", methods=["POST"])
def tap_specific(profile_id):
    """Tap a specific profile by ID (used by NFC readers)."""
    if session.get(_MATCHED_KEY):
        return redirect(url_for("showcase.match"))

    profile = get_profile_by_id(profile_id)
    if not profile:
        return redirect(url_for("showcase.index"))

    scanned_ids = session.get(_SCANNED_KEY, [])
    if profile_id in scanned_ids:
        return redirect(url_for("showcase.index"))  # already scanned

    scanned_ids.append(profile_id)
    session[_SCANNED_KEY] = scanned_ids

    if len(scanned_ids) >= 2:
        session[_MATCHED_KEY] = True
        return redirect(url_for("showcase.match"))

    return redirect(url_for("showcase.index"))
```

**Step 3 — Replace the button in `index.html`** with a Web NFC listener:

```html
<!-- Replace the <form> button with this -->
<button id="nfc-btn" class="sc-btn sc-btn-primary sc-btn-xl" onclick="startNFCScan()">
  <span class="sc-btn-icon">📲</span>
  Hold Badge to Reader
</button>

<script>
async function startNFCScan() {
  if (!('NDEFReader' in window)) {
    alert('NFC not supported in this browser. Use Chrome on Android.');
    return;
  }
  const reader = new NDEFReader();
  try {
    await reader.scan();
    reader.onreading = ({ serialNumber }) => {
      // POST the UID to the server to look up the profile
      fetch('/showcase/tap_by_uid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid: serialNumber })
      }).then(r => {
        if (r.redirected) window.location.href = r.url;
      });
    };
  } catch (err) {
    console.error('NFC scan failed:', err);
  }
}
</script>
```

Add a corresponding route:

```python
@showcase_bp.route("/tap_by_uid", methods=["POST"])
def tap_by_uid():
    data = request.get_json(silent=True) or {}
    uid = data.get("uid", "").upper()
    profile = get_profile_by_nfc_uid(uid)
    if not profile:
        return jsonify(error="Unknown NFC tag"), 404
    # Reuse tap_specific logic
    return tap_specific(profile["id"])
```

---

### 7.4 Option B — Physical NFC Reader via Serial/USB

> **Best for: iPad with a USB-C NFC reader (e.g., ACR122U).** The reader sends the tag UID to a small companion script, which POSTs to the Flask server.

**Architecture:**

```
NFC Reader (USB-C to iPad)
       │
       │ (tag UID via serial/USB HID)
       ▼
  Companion script (Python on same machine, or Shortcuts on iPad)
       │
       │ POST /showcase/tap_by_uid  {"uid": "04:A1:B2:..."}
       ▼
  Flask server (unchanged)
```

The Flask backend change is the same as Option A (`tap_by_uid` route + `nfc_uid` field on profiles).

**For a Mac/PC running the Flask server + ACR122U reader:**

```python
# companion_nfc.py (run alongside main.py)
import nfc
import requests

def on_connect(tag):
    uid = ':'.join(f'{b:02X}' for b in tag.identifier)
    requests.post('http://localhost:5000/showcase/tap_by_uid',
                  json={'uid': uid})
    return True

with nfc.ContactlessFrontend('usb') as clf:
    while True:
        clf.connect(rdwr={'on-connect': on_connect})
```

Requires: `pip install nfcpy requests`

---

### 7.5 Option C — NFC Tags with Encoded Profile IDs

> **Simplest option for iPad Safari.** Each NFC tag has a URL encoded on it that points directly to `/showcase/tap/<id>`. When the iPad scans the tag, iOS opens the URL automatically — no Web NFC API needed.

**Step 1 — Write a URL to each NFC tag:**

Use any NFC writer app (e.g., NFC Tools on iOS) to write an NDEF Text/URL record:

```
Tag for Profile 1:  https://your-domain.com/showcase/tap/1
Tag for Profile 2:  https://your-domain.com/showcase/tap/2
...
Tag for Profile 10: https://your-domain.com/showcase/tap/10
```

For local network use:

```
http://192.168.1.100:5000/showcase/tap/1
```

**Step 2 — Change the tap route to accept GET** (iOS opens URLs via GET, not POST):

```python
# In routes/showcase.py
@showcase_bp.route("/tap/<int:profile_id>", methods=["GET", "POST"])
def tap_specific(profile_id):
    """Direct tap for a specific profile. Accepts GET (NFC tag URL open) and POST."""
    if session.get(_MATCHED_KEY):
        return redirect(url_for("showcase.match"))

    profile = get_profile_by_id(profile_id)
    if not profile:
        return redirect(url_for("showcase.index"))

    scanned_ids = session.get(_SCANNED_KEY, [])
    if profile_id not in scanned_ids:
        scanned_ids.append(profile_id)
        session[_SCANNED_KEY] = scanned_ids

    if len(scanned_ids) >= 2:
        session[_MATCHED_KEY] = True
        return redirect(url_for("showcase.match"))

    return redirect(url_for("showcase.index"))
```

**Step 3 — No frontend change needed.** When a visitor holds their NFC badge over the reader, iOS reads the URL and navigates to it. The server handles the rest and redirects to the appropriate screen.

This is the **recommended approach for iPad at the IM Showcase** (see Section 7.6).

---

### 7.6 Recommended Approach for IM Showcase

Given the constraints (iPad, Safari, event venue, no permanent infrastructure):

**Use Option C — NFC tags with encoded URLs.**

Reasons:
- Works natively on iPad Safari without any Web NFC polyfill
- No companion script, no USB hardware required
- Each physical badge can be a sticker tag with a pre-written URL
- Failure mode is graceful: if NFC fails, the operator can still use the on-screen button
- Zero code change on the backend for the current random-tap behavior — just add the `tap/<id>` route

**Physical setup:**

1. Buy 10 NFC sticker tags (NTAG213 or NTAG215, ~$0.50 each)
2. Use NFC Tools (iOS) to write a URL to each: `http://<server-ip>:5000/showcase/tap/<id>`
3. Attach each sticker to a printed badge card representing that profile
4. Place badges near the iPad on the installation table
5. Visitor picks up a badge, holds it to the iPad's NFC reader (top-left corner on most iPads)
6. iOS reads the URL and navigates — server handles the match logic

**Keep the simulation buttons as a fallback** by leaving the existing `<form>` buttons in the template. They can be hidden via CSS at the event if needed:

```css
/* In showcase.css — hide simulation buttons during live NFC mode */
.sc-simulate-only { display: none; }
```

Add `class="sc-simulate-only"` to the form wrappers in `index.html`.

---

### 7.7 NFC Tag Encoding Reference

| Badge | Profile | URL to encode on tag |
|-------|---------|---------------------|
| Badge 1 | Speculative Designer | `http://<ip>:5000/showcase/tap/1` |
| Badge 2 | Sound Artist | `http://<ip>:5000/showcase/tap/2` |
| Badge 3 | Creative Technologist | `http://<ip>:5000/showcase/tap/3` |
| Badge 4 | AI Researcher | `http://<ip>:5000/showcase/tap/4` |
| Badge 5 | Data Visualizer | `http://<ip>:5000/showcase/tap/5` |
| Badge 6 | XR Developer | `http://<ip>:5000/showcase/tap/6` |
| Badge 7 | Interaction Designer | `http://<ip>:5000/showcase/tap/7` |
| Badge 8 | Computational Artist | `http://<ip>:5000/showcase/tap/8` |
| Badge 9 | Urban Futurist | `http://<ip>:5000/showcase/tap/9` |
| Badge 10 | Bio Artist | `http://<ip>:5000/showcase/tap/10` |

Replace `<ip>` with your server's local network IP address (find with `ipconfig` on Windows, `ifconfig` on Mac/Linux).

---

## 8. API Reference

### `POST /showcase/tap`
Randomly selects an unused profile and adds it to the session.

**No request body required.**

**Response:** HTTP redirect  
- → `/showcase/` (if 0 or 1 profiles scanned)  
- → `/showcase/match` (if 2 profiles now scanned)

---

### `GET /showcase/match`
Renders the match page. Reads `showcase_scanned` from session.

**Response:** HTML page  
- → Redirect to `/showcase/` if fewer than 2 profiles in session

---

### `POST /showcase/generate_question`
Generates a directional conversation question, avoiding the last 3 shown for this direction.

**Request body (JSON):**
```json
{
  "from_id": 1,
  "to_id":   4
}
```

**Response (JSON):**
```json
{
  "question":   "Since we both think about AI Ethics — where do you draw the line?",
  "from_name":  "Speculative Designer",
  "from_emoji": "🔮",
  "from_color": "#7C3AED",
  "to_name":    "AI Researcher",
  "to_emoji":   "🧠",
  "to_color":   "#F59E0B"
}
```

**Error response (400):**
```json
{ "error": "Invalid profile IDs" }
```

---

### `POST /showcase/reset`
Clears all three showcase session keys.

**Response:** HTTP redirect → `/showcase/`

---

### `GET /showcase/status`
Debug helper. Returns current session state as JSON.

**Response:**
```json
{
  "scanned":   [{"id": 1, "name": "Speculative Designer"}],
  "matched":   false,
  "remaining": 9
}
```

---

## 9. Isolation Guarantee

The following production systems are **never touched** by any showcase code:

| System | Guarantee |
|--------|-----------|
| User authentication | No `@login_required`, no `current_user` |
| SQLAlchemy / database | No `db.session`, no model imports |
| NLP matching engine | No `MatchingEngine` or `sentence_transformers` |
| Email / Flask-Mail | No `mail.send()` |
| Celery task queue | No task imports |
| Admin routes | No `@admin_required` |
| Production session keys | Keys prefixed `showcase_*`, isolated from user sessions |

If you add any import from `models.py` or `matching_engine.py` to the showcase files, the isolation is broken. Do not do this.

---

## 10. Troubleshooting

**"Same question keeps appearing"**

The memory depth is 3. If you're seeing repeats after fewer questions, the pool for that particular pair may be small (no shared interests, limited cross-interest combinations). Add more questions to `_META_QUESTIONS` or `_TO_TEMPLATES`.

**"Profiles run out before a match is made"**

With 10 profiles, the random picker should never exhaust the pool in a single session. If this happens, press "↺ Reset Showcase" and it clears the used-profile list.

**"The reveal animation plays but cards stay dim"**

The `sc-card-searching` class is removed by JS after the 800ms delay. If it's stuck, open browser DevTools and check for a JS error in the console. The most likely cause is a failed `setTimeout` chain — check if `revealMatch()` is being called.

**"Generate question returns 400"**

Means `from_id` or `to_id` sent in the fetch body doesn't match any profile. Check that `window.SHOWCASE.profile1.id` and `window.SHOWCASE.profile2.id` are being passed correctly. Open DevTools → Network → find the `generate_question` POST → inspect the request body.

**"NFC tags open a browser but don't change the showcase state"**

Most likely the URL on the tag uses a different IP or port than the server is running on. Check:
1. Server is running: `python main.py` is active
2. iPad and server are on the same Wi-Fi network
3. The IP in the tag URL matches `ipconfig` output on the server machine
4. Port 5000 is not blocked by the firewall

**"Session doesn't reset between visitors"**

Press "↺ Reset Showcase" before each new pair. Alternatively, clear Safari's website data: Settings → Safari → Advanced → Website Data → Delete for localhost.
