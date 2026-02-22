"""
Hardcoded demo profiles for the Interactive Media Showcase installation.
These are pure in-memory objects — no database, no ORM.
"""
import random

DEMO_PROFILES = [
    {
        "id": 1,
        "name": "Speculative Designer",
        "emoji": "🔮",
        "interests": ["Future Cities", "Critical Design", "AI Ethics"],
        "bio": "Explores speculative futures through immersive installations that question the relationship between technology and society.",
        "color": "#7C3AED",
    },
    {
        "id": 2,
        "name": "Sound Artist",
        "emoji": "🎧",
        "interests": ["Generative Audio", "Spatial Sound", "Live Coding"],
        "bio": "Crafts sonic landscapes that blur the boundary between noise and music, often collaborating with visual systems in real time.",
        "color": "#0EA5E9",
    },
    {
        "id": 3,
        "name": "Creative Technologist",
        "emoji": "⚡",
        "interests": ["Physical Computing", "Tangible Interfaces", "Rapid Prototyping"],
        "bio": "Bridges hardware and software to build interactive objects that respond to human presence and environmental data.",
        "color": "#10B981",
    },
    {
        "id": 4,
        "name": "AI Researcher",
        "emoji": "🧠",
        "interests": ["Generative AI", "AI Ethics", "Human-AI Interaction"],
        "bio": "Studies the social implications of machine learning systems with a focus on creative applications and algorithmic bias.",
        "color": "#F59E0B",
    },
    {
        "id": 5,
        "name": "Data Visualizer",
        "emoji": "📊",
        "interests": ["Information Design", "Future Cities", "Live Data"],
        "bio": "Transforms raw datasets into visual narratives, making complex systems legible and emotionally resonant.",
        "color": "#EF4444",
    },
    {
        "id": 6,
        "name": "XR Developer",
        "emoji": "🥽",
        "interests": ["Mixed Reality", "Spatial Computing", "Generative AI"],
        "bio": "Builds extended-reality experiences that collapse the distance between the digital and physical world.",
        "color": "#8B5CF6",
    },
    {
        "id": 7,
        "name": "Interaction Designer",
        "emoji": "🖐️",
        "interests": ["Tangible Interfaces", "Human-AI Interaction", "Critical Design"],
        "bio": "Designs systems where the body itself becomes the interface, exploring embodied cognition through interactive artifacts.",
        "color": "#06B6D4",
    },
    {
        "id": 8,
        "name": "Computational Artist",
        "emoji": "🎨",
        "interests": ["Generative Art", "Live Coding", "Spatial Sound"],
        "bio": "Uses code as a paintbrush, generating visual and sonic compositions that evolve in real time through algorithmic processes.",
        "color": "#EC4899",
    },
    {
        "id": 9,
        "name": "Urban Futurist",
        "emoji": "🏙️",
        "interests": ["Future Cities", "Live Data", "Physical Computing"],
        "bio": "Imagines and prototypes the cities of tomorrow, focusing on participatory urban systems and civic technology.",
        "color": "#84CC16",
    },
    {
        "id": 10,
        "name": "Bio Artist",
        "emoji": "🧬",
        "interests": ["Biofeedback", "AI Ethics", "Critical Design"],
        "bio": "Works at the intersection of biology and art, creating living installations that respond to physiological and environmental signals.",
        "color": "#F97316",
    },
]


def get_profile_by_id(profile_id: int) -> dict | None:
    """Return a single profile dict by numeric ID, or None if not found."""
    return next((p for p in DEMO_PROFILES if p["id"] == profile_id), None)


# ---------------------------------------------------------------------------
# Per-interest question pools used by generate_question()
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
    "I see you work with {to_interest} — what's the most surprising thing you've discovered about it?",
    "If someone fundamentally misunderstood {to_interest}, what would you correct first?",
    "What does {to_interest} let you say that nothing else can?",
    "Where does {to_interest} hit its limit for you?",
    "What drew you into {to_interest} in the first place?",
    "What's the hardest thing to explain about {to_interest} to someone outside the field?",
    "If {to_interest} disappeared tomorrow, what would you miss most about it?",
]

_FROM_TO_TEMPLATES: list[str] = [
    "As someone focused on {from_interest}, I'm genuinely curious — how do you approach {to_interest}?",
    "From where I work in {from_interest}, {to_interest} looks like a different language. What's its grammar?",
    "I wonder if {from_interest} and {to_interest} are secretly solving the same problem. Do you think so?",
    "What would {to_interest} look like if it borrowed a core idea from {from_interest}?",
    "If you had to explain {to_interest} using only concepts from {from_interest}, where would you start?",
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


def generate_question(
    from_profile: dict,
    to_profile: dict,
    exclude: list[str] | None = None,
) -> str:
    """
    Generate a directional conversation-starter question.

    Args:
        from_profile: The profile asking the question.
        to_profile:   The profile being asked.
        exclude:      List of recently shown question strings to avoid.

    Returns:
        A question string not present in `exclude` (if possible).
    """
    if exclude is None:
        exclude = []

    shared = [i for i in from_profile["interests"] if i in to_profile["interests"]]
    candidates: list[str] = []

    # Pool 1 — shared-interest templates (highest relevance)
    for topic in shared:
        candidates.extend(_SHARED_TEMPLATES.get(topic, [
            f"Since we both explore {topic}, where do you see it going from here?",
            f"What drew you into {topic} in the first place?",
            f"What does {topic} let you do that nothing else can?",
        ]))

    # Pool 2 — questions about what to_profile does
    for interest in to_profile["interests"]:
        for tmpl in _TO_TEMPLATES:
            candidates.append(tmpl.format(to_interest=interest))

    # Pool 3 — from_profile's perspective on to_profile's interests
    for f_int in from_profile["interests"]:
        for t_int in to_profile["interests"]:
            if f_int != t_int:
                for tmpl in _FROM_TO_TEMPLATES:
                    candidates.append(tmpl.format(
                        from_interest=f_int,
                        to_interest=t_int,
                    ))

    # Pool 4 — meta IM questions (always available as fallback)
    candidates.extend(_META_QUESTIONS)

    # Remove duplicates while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for q in candidates:
        if q not in seen:
            seen.add(q)
            unique.append(q)

    # Filter out recently shown questions
    available = [q for q in unique if q not in exclude]

    # If everything has been exhausted, reset the pool
    if not available:
        available = unique

    return random.choice(available)
