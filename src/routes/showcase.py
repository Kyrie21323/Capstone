"""
Showcase Mode blueprint — isolated installation experience.
No authentication, no database. Uses Flask session only.
All state resets when the session is cleared.
"""
import random
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request

showcase_bp = Blueprint("showcase", __name__, url_prefix="/showcase")

# Import profiles at module level (pure in-memory, no DB)
from showcase.demo_profiles import DEMO_PROFILES, get_profile_by_id, generate_question

# ---------------------------------------------------------------------------
# Session key constants
# ---------------------------------------------------------------------------
_SCANNED_KEY   = "showcase_scanned"    # list of profile IDs tapped so far
_MATCHED_KEY   = "showcase_matched"    # bool — True once a pair is formed
_QUESTIONS_KEY = "showcase_questions"  # dict — recent questions per direction

# How many recent questions to remember per direction before allowing repeats
_MEMORY_DEPTH = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_scanned_profiles() -> list[dict]:
    """Return full profile dicts for IDs stored in session."""
    ids = session.get(_SCANNED_KEY, [])
    return [get_profile_by_id(pid) for pid in ids if get_profile_by_id(pid)]


def _available_profiles() -> list[dict]:
    """Return profiles not yet scanned this session."""
    used_ids = set(session.get(_SCANNED_KEY, []))
    return [p for p in DEMO_PROFILES if p["id"] not in used_ids]


def _direction_key(from_id: int, to_id: int) -> str:
    return f"{from_id}_to_{to_id}"


def _get_recent_questions(from_id: int, to_id: int) -> list[str]:
    """Return the list of recently shown questions for this direction."""
    memory = session.get(_QUESTIONS_KEY, {})
    return memory.get(_direction_key(from_id, to_id), [])


def _record_question(from_id: int, to_id: int, question: str) -> None:
    """Append question to session memory for this direction, capped at _MEMORY_DEPTH."""
    memory = session.get(_QUESTIONS_KEY, {})
    key = _direction_key(from_id, to_id)
    recent = memory.get(key, [])
    recent.append(question)
    if len(recent) > _MEMORY_DEPTH:
        recent = recent[-_MEMORY_DEPTH:]
    memory[key] = recent
    session[_QUESTIONS_KEY] = memory


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@showcase_bp.route("/", methods=["GET"])
def index():
    """Landing page — shows the NFC tap button and any already-scanned profiles."""
    scanned = _get_scanned_profiles()
    matched = session.get(_MATCHED_KEY, False)
    remaining = len(_available_profiles())
    return render_template(
        "showcase/index.html",
        scanned=scanned,
        matched=matched,
        remaining=remaining,
    )


@showcase_bp.route("/tap", methods=["POST"])
def tap():
    """
    Simulate an NFC tap: pick a random unused profile and add it to the session.
    - If this is the 2nd tap → set matched flag and redirect to match screen.
    - If already matched → ignore and redirect back.
    - If no profiles remain → redirect back (all used up).
    """
    if session.get(_MATCHED_KEY):
        return redirect(url_for("showcase.match"))

    available = _available_profiles()
    if not available:
        return redirect(url_for("showcase.index"))

    chosen = random.choice(available)

    scanned_ids = session.get(_SCANNED_KEY, [])
    scanned_ids.append(chosen["id"])
    session[_SCANNED_KEY] = scanned_ids

    if len(scanned_ids) >= 2:
        session[_MATCHED_KEY] = True
        return redirect(url_for("showcase.match"))

    return redirect(url_for("showcase.index"))


@showcase_bp.route("/match", methods=["GET"])
def match():
    """Match screen — shown after two profiles have been scanned."""
    scanned = _get_scanned_profiles()
    if len(scanned) < 2:
        return redirect(url_for("showcase.index"))

    profile1, profile2 = scanned[0], scanned[1]
    shared_interests = [i for i in profile1["interests"] if i in profile2["interests"]]

    return render_template(
        "showcase/match.html",
        profile1=profile1,
        profile2=profile2,
        shared_interests=shared_interests,
    )


@showcase_bp.route("/generate_question", methods=["POST"])
def generate_question_route():
    """
    Generate a directional conversation question, avoiding recent repeats.

    Request body (JSON):
        { "from_id": <int>, "to_id": <int> }

    Response (JSON):
        {
            "question":   str,
            "from_name":  str,
            "from_emoji": str,
            "from_color": str,
            "to_name":    str,
            "to_emoji":   str,
            "to_color":   str,
        }
    """
    data = request.get_json(silent=True) or {}
    from_id = data.get("from_id")
    to_id   = data.get("to_id")

    from_profile = get_profile_by_id(from_id)
    to_profile   = get_profile_by_id(to_id)

    if not from_profile or not to_profile:
        return jsonify(error="Invalid profile IDs"), 400

    recent   = _get_recent_questions(from_id, to_id)
    question = generate_question(from_profile, to_profile, exclude=recent)
    _record_question(from_id, to_id, question)

    return jsonify(
        question   = question,
        from_name  = from_profile["name"],
        from_emoji = from_profile["emoji"],
        from_color = from_profile["color"],
        to_name    = to_profile["name"],
        to_emoji   = to_profile["emoji"],
        to_color   = to_profile["color"],
    )


@showcase_bp.route("/reset", methods=["POST"])
def reset():
    """Clear all showcase session state and return to landing."""
    session.pop(_SCANNED_KEY,   None)
    session.pop(_MATCHED_KEY,   None)
    session.pop(_QUESTIONS_KEY, None)
    return redirect(url_for("showcase.index"))


@showcase_bp.route("/status", methods=["GET"])
def status():
    """Return current showcase state as JSON (debug helper)."""
    scanned = _get_scanned_profiles()
    return jsonify(
        scanned=[{"id": p["id"], "name": p["name"]} for p in scanned],
        matched=session.get(_MATCHED_KEY, False),
        remaining=len(_available_profiles()),
    )
