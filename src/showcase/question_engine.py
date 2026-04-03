"""
Showcase question generation engine.

Accepts showcase user dicts (from showcase_users.py) with schema:
  { "keywords": [...], "profile_text": "...", ... }

generate_question(from_user, to_user, exclude=None) is the public API.
The function signature is unchanged; all callers continue to work as-is.

─────────────────────────────────────────────────────────────────────────────
IMPLEMENTATION METHOD: deterministic rule-based extraction — no LLM, no API.
─────────────────────────────────────────────────────────────────────────────

Generation uses two tiers, tried in order:

  Tier 1 — Profile-text derived  (most personalized, tried first)
    Three regex extractors read each user's profile_text:
      • Embedded questions  — sentences ending in '?' inside the bio
      • Stated interests    — phrases after "I'm drawn to / interested in" etc.
      • Tension phrases     — "X and Y" extracted from intersection/boundary language
    These signals are assembled into directional question strings.
    The direction from_user → to_user is structurally different from the reverse.
    If ALL profile-derived candidates are in the exclude list, Tier 2 is used.

  Tier 2 — Keyword template fallback  (used when Tier 1 is exhausted)
    Four sub-pools built from keywords, in priority order:
      1. Shared-keyword templates
      2. Questions about to_user's keywords
      3. Cross-keyword questions (from_user framing meets to_user keywords)
      4. Meta questions (generic, always available)

Both profile_text AND keywords are now actively used.
The session-based exclude/history mechanism applies to both tiers equally.
"""
import random
import re


# ---------------------------------------------------------------------------
# Tier 1 — Profile-text extraction helpers
# ---------------------------------------------------------------------------

# "I'm drawn to X", "I'm interested in X", "I've been focused on X",
# "My current obsession is X", etc.
_INTEREST_RE = re.compile(
    r"""
    (?:
        (?:I'?m | I'?ve \s+ been) \s+ (?:particularly \s+)?
        (?:drawn\ to | interested\ in | fascinated\ by |
           obsessed\ with | focused\ on)
      |
        [Mm]y \s+ (?:current \s+)? obsession \s+ is
    )
    \s+
    ([^.,!?;:—\n]{10,120})
    """,
    re.VERBOSE | re.IGNORECASE,
)

# "at the intersection of X and Y", "boundary between X and Y",
# "gap between X and Y", "distance between X and Y", etc.
_TENSION_RE = re.compile(
    r"""
    (?:
        at \s+ the \s+ (?:intersection | edge | boundary) \s+ of
      | (?:boundary | gap | space | edge | tension | distance) \s+ between
      | intersection \s+ of
    )
    \s+
    ([^.,!?;:—\n]{4,60}?)
    \s+ and \s+
    ([^.,!?;:—\n]{4,60})
    """,
    re.VERBOSE | re.IGNORECASE,
)


def _extract_interests(text: str) -> list[str]:
    """
    Return short phrases expressing what this user says they are drawn toward.
    Sources: "I'm drawn to X", "I'm interested in X", "My obsession is X", etc.
    """
    # Short function words that look bad when a phrase ends on them
    _TRAILING_JUNK = re.compile(
        r"\s+(?:the|a|an|of|in|to|for|and|or|but|at|by|with|from)\s*$",
        re.IGNORECASE,
    )
    results: list[str] = []
    for m in _INTEREST_RE.finditer(text):
        phrase = m.group(1).strip().rstrip(".,;—")
        # Trim to word boundary if the capture ran long
        if len(phrase) > 85:
            phrase = phrase[:85].rsplit(" ", 1)[0].rstrip(".,;—")
        # Strip any dangling function word left at the end after trimming
        phrase = _TRAILING_JUNK.sub("", phrase).rstrip(".,;—")
        if len(phrase) >= 8:
            results.append(phrase)
    return results


def _extract_tensions(text: str) -> list[str]:
    """
    Return "X and Y" strings from intersection / boundary language.
    Sources: "at the intersection of X and Y", "boundary between X and Y", etc.
    """
    results: list[str] = []
    for m in _TENSION_RE.finditer(text):
        a = m.group(1).strip()
        b = m.group(2).strip().rstrip(".,;—")
        tension = f"{a} and {b}"
        if 8 <= len(tension) <= 100:
            results.append(tension)
    return results


def _extract_questions(text: str) -> list[str]:
    """
    Extract question sentences embedded in profile_text.
    Handles both standalone '?' sentences and colon-introduced sub-clauses
    (e.g. "I'm interested in X: what does X actually mean?").
    """
    results: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        for part in sentence.split(":"):
            part = part.strip()
            if part.endswith("?") and 15 <= len(part) <= 200:
                results.append(part)
    return results


def _compose_profile_questions(from_user: dict, to_user: dict) -> list[str]:
    """
    Build profile-text-derived questions for the direction from_user → to_user.

    Extracts structured signals from both profiles and composes questions that:
    - Reflect to_user's own embedded questions back as conversation prompts
    - Ask about to_user's stated interests and tensions
    - Bridge from_user's concerns into to_user's domain

    Returns a list of strings; may be empty if extraction yields nothing.
    Swapping from_user and to_user produces a structurally different list.
    """
    from_interests = _extract_interests(from_user.get("profile_text", ""))
    to_interests   = _extract_interests(to_user.get("profile_text", ""))
    from_tensions  = _extract_tensions(from_user.get("profile_text", ""))
    to_tensions    = _extract_tensions(to_user.get("profile_text", ""))
    from_questions = _extract_questions(from_user.get("profile_text", ""))
    to_questions   = _extract_questions(to_user.get("profile_text", ""))

    questions: list[str] = []

    # ── Reflect to_user's own embedded question back at them ───────────────
    for q in to_questions[:2]:
        questions.append(
            f"Your profile poses a question I'd love your current answer to: {q}"
        )

    # ── Ask about to_user's stated interests ───────────────────────────────
    for phrase in to_interests[:2]:
        questions.append(
            f"You described a pull toward {phrase} — "
            f"how has that shaped what you actually make?"
        )
        questions.append(
            f"That focus on {phrase} — "
            f"where has it taken your work that you didn't expect?"
        )

    # ── Ask about to_user's tension / intersection phrases ─────────────────
    for tension in to_tensions[:2]:
        questions.append(
            f"You work in the space between {tension} — "
            f"how do you keep that tension alive rather than resolving it?"
        )

    # ── Bridge from_user's embedded question into to_user's context ────────
    for q in from_questions[:1]:
        questions.append(
            f"Something I keep returning to in my own work: {q} "
            f"How do you encounter that from where you work?"
        )

    # ── Bridge from_user's interest to meet to_user's interest ────────────
    if from_interests and to_interests:
        questions.append(
            f"Your pull toward {to_interests[0]} and my work around "
            f"{from_interests[0]} — where do those two concerns actually touch?"
        )

    # ── Contrast from_user's tension with to_user's tension ───────────────
    if from_tensions and to_tensions and from_tensions[0] != to_tensions[0]:
        questions.append(
            f"We both seem to work in a productive tension — "
            f"mine around {from_tensions[0]}, yours around {to_tensions[0]}. "
            f"How do you navigate yours without collapsing it?"
        )

    return questions


# ---------------------------------------------------------------------------
# Tier 2 — Keyword-based template pools (fallback)
# ---------------------------------------------------------------------------

_SHARED_TEMPLATES: dict[str, list[str]] = {
    "Future Cities": [
        "Since we both think about future cities — what's the one urban system you'd redesign first?",
        "What does a city that actually listens to its inhabitants look like to you?",
        "If future cities are inevitable, what should they refuse to automate?",
        "What drew you into thinking about cities as a medium in the first place?",
        "Where does speculation end and planning begin, in your practice?",
    ],
    "Critical Design": [
        "Since we both work with critical design — what assumption are you trying to break right now?",
        "What everyday object would you redesign to make people uncomfortable in a productive way?",
        "Is critical design more about asking questions or providing answers, for you?",
        "What's the most misunderstood thing about critical design in your experience?",
        "How do you know when a provocation has landed?",
    ],
    "AI Ethics": [
        "Since we're both thinking about AI ethics — where do you draw the line between tool and agent?",
        "What ethical constraint on AI would you make non-negotiable?",
        "If an AI made a creative mistake, who would own it?",
        "What's the question about AI you think nobody is asking loudly enough?",
        "Do you think ethics can be encoded, or does it have to be practised?",
    ],
    "Generative Audio": [
        "Since we both work with generative audio — what's the difference between generated sound and composed sound to you?",
        "What's the most interesting thing that's emerged from a generative system that you didn't intend?",
        "Where does the algorithm end and the ear begin?",
        "If your generative system could make only one sound for the rest of its life, what would you want it to be?",
    ],
    "Spatial Sound": [
        "Since we both think about spatial sound — what's the smallest space you've made feel enormous?",
        "How do you use sound to make an invisible boundary feel real?",
        "What does silence mean inside a spatial audio piece?",
        "If you could redesign the acoustics of this room right now, what would you change?",
    ],
    "Live Coding": [
        "Since we both live-code — what's the most interesting bug you've ever performed?",
        "If your code could make a deliberate mistake, what would it create?",
        "How do you think about the audience watching you write?",
        "What's the relationship between legibility and performance in live coding for you?",
    ],
    "Physical Computing": [
        "Since we both work with physical computing — what's the most human-feeling sensor you've used?",
        "What physical material best captures the feeling of a data stream, in your experience?",
        "Where does the hardware become expressive rather than functional?",
        "What's an interaction you've designed that surprised the person using it?",
    ],
    "Tangible Interfaces": [
        "Since we both design tangible interfaces — what does a good affordance feel like in your hand?",
        "What's a digital concept you think only becomes real when it's physical?",
        "Design a gesture that means 'I agree' without using words — what is it?",
        "What gets lost when something moves from tangible to screen?",
    ],
    "Generative AI": [
        "Since we both work with generative AI — what's the difference between a tool that assists and one that replaces?",
        "If an AI co-created your next piece, what credit would it deserve?",
        "Where does prompt end and authorship begin?",
        "What's a generative result that made you genuinely question your own taste?",
    ],
    "Human-AI Interaction": [
        "Since we both think about human-AI interaction — where does the human end and the system begin in interactive work?",
        "What does trust look like in a human-AI interface?",
        "What's the most important thing an AI should know when to not do?",
        "What interaction pattern do you think we're getting completely wrong right now?",
    ],
    "Mixed Reality": [
        "Since we both work in mixed reality — what should never be augmented, and why?",
        "What's the seam you're most trying to hide in your XR work?",
        "When does mixed reality enhance presence and when does it break it?",
        "What physical thing becomes more itself when digitally layered?",
    ],
    "Spatial Computing": [
        "Since we both think in spatial computing — if space were programmable, what would you change about this room?",
        "What's the right amount of latency in a spatial experience?",
        "Where does environment end and interface begin?",
        "What's a spatial interaction that made you rethink how you move through the world?",
    ],
    "Information Design": [
        "Since we both think about information design — what's the most important dataset nobody is visualising?",
        "What's the difference between data that informs and data that transforms?",
        "When does a visualisation become a piece of art rather than a chart?",
        "What's a visual encoding choice you've made that you later regretted?",
    ],
    "Live Data": [
        "Since we both work with live data — if this moment were a dataset, what would its most interesting outlier be?",
        "What's the most surprising thing a live data feed has ever shown you?",
        "When does real-time data become noise rather than signal?",
        "What live data stream do you wish existed?",
    ],
    "Generative Art": [
        "Since we both make generative art — if randomness had a signature style, what would yours look like?",
        "What's the difference between a generative system that surprises you and one that bores you?",
        "When does variation become expression?",
        "What's a parameter you've adjusted that changed the entire mood of a piece?",
    ],
    "Biofeedback": [
        "Since we both work with biofeedback — what emotion would you most want a room to detect and respond to?",
        "What's the most intimate biometric to use in a public installation?",
        "Where does the body become data and where does it resist?",
        "What physiological signal do you think is underexplored as a creative input?",
    ],
}


_TO_TEMPLATES: list[str] = [
    "I see you work with {keyword} — what's the most surprising thing you've discovered about it?",
    "If someone fundamentally misunderstood {keyword}, what would you correct first?",
    "What does {keyword} let you say that nothing else can?",
    "Where does {keyword} hit its limit for you?",
    "What drew you into {keyword} in the first place?",
    "What's the hardest thing to explain about {keyword} to someone outside the field?",
    "If {keyword} disappeared tomorrow, what would you miss most about it?",
]


_FROM_TO_TEMPLATES: list[str] = [
    "As someone focused on {from_kw}, I'm genuinely curious — how do you approach {to_kw}?",
    "From where I work in {from_kw}, {to_kw} looks like a different language. What's its grammar?",
    "I wonder if {from_kw} and {to_kw} are secretly solving the same problem. Do you think so?",
    "What would {to_kw} look like if it borrowed a core idea from {from_kw}?",
    "If you had to explain {to_kw} using only concepts from {from_kw}, where would you start?",
]


_META_QUESTIONS: list[str] = [
    "If this installation were a prototype of the future, what would you change about it?",
    "What's the one thing your practice does that no algorithm could replicate?",
    "What does your work want people to feel that they can't easily articulate?",
    "If you could give your discipline a completely different name, what would it be?",
    "What's a question your work asks that you still don't know how to answer?",
    "What failure in your practice taught you something that success couldn't?",
    "If a stranger spent five minutes with your work, what would you hope they walked away thinking?",
    "What's the last thing that genuinely surprised you about your own field?",
    "If you had to describe your creative process using weather, what would it be?",
    "What's something you believe about your field that most people in it would disagree with?",
    "If your two practices had to share a single body of work, what medium would it exist in?",
    "What's the gap between what you intend and what audiences experience in your work?",
    "What would it mean for your practice to be wrong?",
    "What does 'finished' feel like in your work — or does it ever?",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_question(
    from_user: dict,
    to_user: dict,
    exclude: list[str] | None = None,
) -> str:
    """
    Generate a directional conversation-starter question.

    Args:
        from_user:  Showcase user dict — the person asking.
                    Must contain 'keywords' (list) and 'profile_text' (str).
        to_user:    Showcase user dict — the person being asked.
                    Must contain 'keywords' (list) and 'profile_text' (str).
        exclude:    List of recently shown question strings to avoid repeating.

    Returns:
        A question string not present in `exclude` (if possible).

    Tier 1 (profile-text derived) is tried first. If every profile-derived
    question is already in the exclude list, Tier 2 (keyword templates) is
    used. The exclude mechanism works identically across both tiers.
    """
    if exclude is None:
        exclude = []

    # ── Tier 1: profile-text derived questions ─────────────────────────────
    # These are composed from signals extracted from each user's profile_text.
    # The direction from_user → to_user produces a structurally different set
    # than to_user → from_user, so "Switch Roles" remains meaningful.
    profile_qs = _compose_profile_questions(from_user, to_user)
    preferred  = [q for q in profile_qs if q not in exclude]
    if preferred:
        return random.choice(preferred)

    # ── Tier 2: keyword template fallback ──────────────────────────────────
    from_keywords = from_user.get("keywords", [])
    to_keywords   = to_user.get("keywords", [])
    shared        = [k for k in from_keywords if k in to_keywords]
    candidates: list[str] = []

    # Pool 1 — shared-keyword templates (highest relevance)
    for topic in shared:
        candidates.extend(_SHARED_TEMPLATES.get(topic, [
            f"Since we both explore {topic}, where do you see it going from here?",
            f"What drew you into {topic} in the first place?",
            f"What does {topic} let you do that nothing else can?",
        ]))

    # Pool 2 — questions about what to_user does
    for kw in to_keywords:
        for tmpl in _TO_TEMPLATES:
            candidates.append(tmpl.format(keyword=kw))

    # Pool 3 — from_user's perspective on to_user's keywords
    for f_kw in from_keywords:
        for t_kw in to_keywords:
            if f_kw != t_kw:
                for tmpl in _FROM_TO_TEMPLATES:
                    candidates.append(tmpl.format(from_kw=f_kw, to_kw=t_kw))

    # Pool 4 — meta questions (always available as final fallback)
    candidates.extend(_META_QUESTIONS)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for q in candidates:
        if q not in seen:
            seen.add(q)
            unique.append(q)

    # Filter out recently shown questions
    available = [q for q in unique if q not in exclude]

    # If every question has been exhausted, reset the pool
    if not available:
        available = unique

    return random.choice(available)
