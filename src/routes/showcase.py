"""
Showcase Mode blueprint — isolated installation experience.
No authentication, no database. Uses Flask session only.
All state resets when the session is cleared or reset is called manually.

Session keys
------------
showcase_active_users  : {"user_1_id": int|None, "user_2_id": int|None}
showcase_locked        : bool — True once a pair is formed; ignores further taps
showcase_interactions  : list of {source_id, target_id, timestamp} — visualization only
showcase_questions     : dict — recent question strings per direction (memory de-dup)
"""
from datetime import datetime, timezone

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from showcase.question_engine import generate_question
from showcase.showcase_users import (
    get_all_showcase_users,
    get_showcase_user_by_id,
    get_showcase_user_by_nfc_id,
)

showcase_bp = Blueprint("showcase", __name__, url_prefix="/showcase")

# ---------------------------------------------------------------------------
# Session key constants
# ---------------------------------------------------------------------------
_ACTIVE_USERS_KEY  = "showcase_active_users"   # {"user_1_id": int|None, "user_2_id": int|None}
_LOCKED_KEY        = "showcase_locked"          # bool
_INTERACTIONS_KEY  = "showcase_interactions"    # list[dict] — visualization only
_QUESTIONS_KEY     = "showcase_questions"       # dict[direction_key, list[str]]

_MEMORY_DEPTH = 3  # max questions remembered per direction before repeats allowed


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def _get_active_users() -> dict:
    return session.get(_ACTIVE_USERS_KEY, {"user_1_id": None, "user_2_id": None})


def _set_active_users(state: dict) -> None:
    session[_ACTIVE_USERS_KEY] = state


def _is_locked() -> bool:
    return session.get(_LOCKED_KEY, False)


def _direction_key(from_id: int, to_id: int) -> str:
    return f"{from_id}_to_{to_id}"


def _get_recent_questions(from_id: int, to_id: int) -> list[str]:
    memory = session.get(_QUESTIONS_KEY, {})
    return memory.get(_direction_key(from_id, to_id), [])


def _record_question(from_id: int, to_id: int, question: str) -> None:
    memory = session.get(_QUESTIONS_KEY, {})
    key = _direction_key(from_id, to_id)
    recent = memory.get(key, [])
    recent.append(question)
    if len(recent) > _MEMORY_DEPTH:
        recent = recent[-_MEMORY_DEPTH:]
    memory[key] = recent
    session[_QUESTIONS_KEY] = memory


def get_current_showcase_pair() -> tuple[dict | None, dict | None]:
    """
    Return the two active showcase user dicts as (user_1, user_2).
    Returns (None, None) if either slot is empty.

    This is the canonical source for the current interface pair.
    Do NOT use showcase_interactions for this purpose.
    """
    state = _get_active_users()
    user1 = get_showcase_user_by_id(state["user_1_id"]) if state["user_1_id"] else None
    user2 = get_showcase_user_by_id(state["user_2_id"]) if state["user_2_id"] else None
    return user1, user2


def _record_interaction(user1_id: int, user2_id: int) -> None:
    """
    Append a visualization-only interaction record.
    This is for graph/history display ONLY.
    Do NOT use this to determine the current active pair.
    """
    interactions = session.get(_INTERACTIONS_KEY, [])
    interactions.append({
        "source_id": user1_id,
        "target_id": user2_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    session[_INTERACTIONS_KEY] = interactions


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@showcase_bp.route("/", methods=["GET"])
def index():
    """Landing page — shows active users and NFC tap controls."""
    state  = _get_active_users()
    locked = _is_locked()
    user1  = get_showcase_user_by_id(state["user_1_id"]) if state["user_1_id"] else None
    user2  = get_showcase_user_by_id(state["user_2_id"]) if state["user_2_id"] else None

    return render_template(
        "showcase/index.html",
        user1=user1,
        user2=user2,
        locked=locked,
        all_users=get_all_showcase_users(),
    )


@showcase_bp.route("/tap", methods=["POST"])
def tap():
    """
    Handle an NFC tap — real hardware or simulated button.

    Expects form field 'nfc_id' (str).
    Also accepts JSON body {"nfc_id": "..."} for programmatic use.

    Tap logic
    ---------
    - Unknown nfc_id          → ignore, redirect to index (safe)
    - Interface is locked     → ignore, redirect to match (safe)
    - Same badge as user_1    → log out user_1, unlock interface
    - Same badge as user_2    → log out user_2, unlock interface (shouldn't
                                happen while locked, but handled defensively)
    - Slot 1 empty            → assign user to slot 1, wait for second tap
    - Slot 2 empty            → assign user to slot 2, lock interface,
                                record interaction, redirect to match
    """
    # Accept both form POST and JSON body
    data   = request.get_json(silent=True) or {}
    nfc_id = str(request.form.get("nfc_id") or data.get("nfc_id", "")).strip()

    # Unknown badge — ignore silently
    user = get_showcase_user_by_nfc_id(nfc_id)
    if not user:
        return redirect(url_for("showcase.index"))

    user_id = user["id"]
    state   = _get_active_users()

    # Interface locked → ignore further taps
    if _is_locked():
        return redirect(url_for("showcase.match"))

    # Same badge as slot 1 → log out user_1
    if state["user_1_id"] == user_id:
        state["user_1_id"] = None
        _set_active_users(state)
        return redirect(url_for("showcase.index"))

    # Same badge as slot 2 → log out user_2 (defensive; normally locked by now)
    if state["user_2_id"] == user_id:
        state["user_2_id"] = None
        _set_active_users(state)
        return redirect(url_for("showcase.index"))

    # Slot 1 is empty → assign and wait
    if state["user_1_id"] is None:
        state["user_1_id"] = user_id
        _set_active_users(state)
        return redirect(url_for("showcase.index"))

    # Slot 2 is empty → pair formed, lock, record visualization interaction
    if state["user_2_id"] is None:
        state["user_2_id"] = user_id
        _set_active_users(state)
        session[_LOCKED_KEY] = True
        _record_interaction(state["user_1_id"], user_id)
        return redirect(url_for("showcase.match"))

    # Fallback (should not be reached if lock check is correct)
    return redirect(url_for("showcase.index"))


@showcase_bp.route("/match", methods=["GET"])
def match():
    """Match screen — shown once both slots are filled."""
    user1, user2 = get_current_showcase_pair()
    if not user1 or not user2:
        return redirect(url_for("showcase.index"))

    shared_keywords = [k for k in user1["keywords"] if k in user2["keywords"]]

    return render_template(
        "showcase/match.html",
        profile1=user1,
        profile2=user2,
        shared_interests=shared_keywords,
    )


@showcase_bp.route("/generate_question", methods=["POST"])
def generate_question_route():
    """
    Generate a directional conversation question, avoiding recent repeats.

    Request body (JSON):
        { "from_id": <int>, "to_id": <int> }

    Response (JSON):
        {
            "question":    str,
            "from_name":   str,
            "from_emoji":  str,
            "from_color":  str,
            "to_name":     str,
            "to_emoji":    str,
            "to_color":    str,
        }
    """
    data    = request.get_json(silent=True) or {}
    from_id = data.get("from_id")
    to_id   = data.get("to_id")

    from_user = get_showcase_user_by_id(from_id)
    to_user   = get_showcase_user_by_id(to_id)

    if not from_user or not to_user:
        return jsonify(error="Invalid user IDs"), 400

    recent   = _get_recent_questions(from_id, to_id)
    question = generate_question(from_user, to_user, exclude=recent)
    _record_question(from_id, to_id, question)

    return jsonify(
        question   = question,
        from_name  = from_user["name"],
        from_emoji = from_user["emoji"],
        from_color = from_user["color"],
        to_name    = to_user["name"],
        to_emoji   = to_user["emoji"],
        to_color   = to_user["color"],
    )


@showcase_bp.route("/reset", methods=["POST"])
def reset():
    """
    Manual-only reset.
    Clears all showcase session state and returns to landing page.
    """
    session.pop(_ACTIVE_USERS_KEY, None)
    session.pop(_LOCKED_KEY,       None)
    session.pop(_INTERACTIONS_KEY, None)
    session.pop(_QUESTIONS_KEY,    None)
    return redirect(url_for("showcase.index"))


@showcase_bp.route("/status", methods=["GET"])
def status():
    """Return current showcase state as JSON (debug / NFC hardware helper)."""
    user1, user2 = get_current_showcase_pair()
    return jsonify(
        user_1        = {"id": user1["id"], "name": user1["name"]} if user1 else None,
        user_2        = {"id": user2["id"], "name": user2["name"]} if user2 else None,
        locked        = _is_locked(),
        interactions  = session.get(_INTERACTIONS_KEY, []),
    )
