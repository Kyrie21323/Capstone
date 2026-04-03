"""
Showcase User data access layer — single source of truth for NFC showcase users.

Schema per user:
  id           int   — internal numeric ID
  nfc_id       str   — string read from NFC badge (e.g. "1", "2", "A3F2...")
  name         str   — display name shown on screen
  emoji        str   — single emoji used as avatar
  color        str   — hex accent colour for UI theming
  keywords     list  — interests/skills used for question matching
  profile_text str   — longer text used for future NLP-based question generation

Replace contents when real attendee dataset is ready.
Do NOT connect this to the production database or matching engine.
"""

SHOWCASE_USERS: list[dict] = [
    {
        "id": 1,
        "nfc_id": "1",
        "name": "Speculative Designer",
        "emoji": "🔮",
        "color": "#7C3AED",
        "keywords": ["Future Cities", "Critical Design", "AI Ethics"],
        "profile_text": (
            "I design futures that don't exist yet — and question whether they should. "
            "My practice sits at the intersection of critical design and speculative fiction, "
            "using immersive installations to surface the social and ethical tensions embedded "
            "in emerging technology. I'm particularly drawn to urban systems: how cities encode "
            "power, how infrastructure shapes behaviour, and what it would mean to design a city "
            "that genuinely listens. Lately I've been focused on AI governance — not as a policy "
            "problem but as a design problem, asking what values get baked in when nobody is watching."
        ),
    },
    {
        "id": 2,
        "nfc_id": "2",
        "name": "Sound Artist",
        "emoji": "🎧",
        "color": "#0EA5E9",
        "keywords": ["Generative Audio", "Spatial Sound", "Live Coding"],
        "profile_text": (
            "I work with sound as a material — something to be shaped, positioned in space, "
            "and set in motion algorithmically. My live sets are written in SuperCollider and "
            "performed in real time, which means every performance is genuinely unrepeatable. "
            "I'm interested in the boundary between noise and music: at what point does randomness "
            "become composition? I've been building multichannel speaker arrays for gallery "
            "installations where the listener's movement through space becomes the instrument. "
            "My current obsession is using machine listening to generate sound that responds to "
            "the acoustic signature of the room it's played in."
        ),
    },
    {
        "id": 3,
        "nfc_id": "3",
        "name": "Creative Technologist",
        "emoji": "⚡",
        "color": "#10B981",
        "keywords": ["Physical Computing", "Tangible Interfaces", "Rapid Prototyping"],
        "profile_text": (
            "I bridge the gap between an idea on a whiteboard and a thing you can touch. "
            "My work involves rapid prototyping with microcontrollers, custom PCBs, and whatever "
            "sensing technology fits the concept — capacitive touch, LIDAR, thermal cameras. "
            "I'm drawn to moments when hardware becomes expressive: when a circuit stops being "
            "a component and starts feeling like a behaviour. Most of my projects are "
            "collaborations — I tend to come in when someone has a vision that needs to "
            "physically exist in the world and isn't sure how to get there. "
            "I think the best interfaces are the ones people forget are there."
        ),
    },
    {
        "id": 4,
        "nfc_id": "4",
        "name": "AI Researcher",
        "emoji": "🧠",
        "color": "#F59E0B",
        "keywords": ["Generative AI", "AI Ethics", "Human-AI Interaction"],
        "profile_text": (
            "I study what happens when generative systems meet creative practice — and who "
            "gets to decide what counts as good output. My research sits between machine learning "
            "and the social sciences, looking at how bias propagates through large language models "
            "and image generators, and what it means to call something 'creative' when it comes "
            "from a statistical process. I'm particularly interested in consent and attribution: "
            "what do artists owe AI systems trained on their work, and vice versa? "
            "I try to bring rigour to conversations that often stay at the level of hype, "
            "and I think the most important AI questions right now are the ones framed as ethics "
            "problems but are actually political ones."
        ),
    },
    {
        "id": 5,
        "nfc_id": "5",
        "name": "Data Visualiser",
        "emoji": "📊",
        "color": "#EF4444",
        "keywords": ["Information Design", "Live Data", "Future Cities"],
        "profile_text": (
            "I make data legible — and sometimes uncomfortable. My practice is about finding "
            "the visual language that lets a dataset tell its own story without simplifying "
            "what's genuinely complex. I've worked on projects ranging from real-time air quality "
            "dashboards for public screens to long-form narrative pieces about housing displacement. "
            "I'm drawn to live data because it forces you to design for uncertainty: "
            "what does your visualisation look like when the feed goes down, or when the "
            "numbers are stranger than you expected? Right now I'm exploring what it means "
            "to visualise a city as a living organism — tracking flows of people, energy, "
            "and information simultaneously."
        ),
    },
    {
        "id": 6,
        "nfc_id": "6",
        "name": "XR Developer",
        "emoji": "🥽",
        "color": "#8B5CF6",
        "keywords": ["Mixed Reality", "Spatial Computing", "Generative AI"],
        "profile_text": (
            "I build experiences that collapse the distance between the physical and digital — "
            "not as a technical trick, but as a way of asking what presence actually means. "
            "Most of my work is in Unity and Unreal with custom shader pipelines, but the "
            "interesting problems are never technical: they're about when augmentation enhances "
            "a space and when it just clutters it. I've been using generative AI to populate "
            "virtual environments in real time, which creates genuinely uncanny results. "
            "My current project is a mixed reality piece set in a decommissioned factory "
            "where the building's industrial history surfaces as overlapping spatial layers — "
            "you walk through time as you walk through space."
        ),
    },
    {
        "id": 7,
        "nfc_id": "7",
        "name": "Interaction Designer",
        "emoji": "🖐️",
        "color": "#06B6D4",
        "keywords": ["Tangible Interfaces", "Human-AI Interaction", "Critical Design"],
        "profile_text": (
            "I design for the body — for hands, posture, gesture, and the way people move "
            "through space without thinking about it. My work challenges the assumption that "
            "the ideal interface is invisible: sometimes making the interface visible and "
            "deliberate is exactly the point. I'm interested in embodied cognition — how "
            "physical interaction shapes understanding — and what that means when we increasingly "
            "interact with systems that have no physical form at all. My critical design work "
            "tries to make the politics of interaction legible: who is this interface designed "
            "for, whose body does it assume, and what does it ask you to become to use it?"
        ),
    },
    {
        "id": 8,
        "nfc_id": "8",
        "name": "Computational Artist",
        "emoji": "🎨",
        "color": "#EC4899",
        "keywords": ["Generative Art", "Live Coding", "Spatial Sound"],
        "profile_text": (
            "Code is my medium — not a tool I use to produce work, but the material the work "
            "is made from. I write algorithms that generate visual and sonic compositions in "
            "real time, usually performed live in front of an audience who can see the code "
            "running on screen. I'm interested in the aesthetics of process: what a system "
            "looks like when it's deciding, failing, and recovering. My pieces tend to be "
            "durational — they evolve over hours, and the interesting events happen at the "
            "edge of the parameters I've set. I use p5.js, openFrameworks, and SuperCollider, "
            "sometimes all at once, and I believe the best generative work surprises "
            "its author."
        ),
    },
    {
        "id": 9,
        "nfc_id": "9",
        "name": "Urban Futurist",
        "emoji": "🏙️",
        "color": "#84CC16",
        "keywords": ["Future Cities", "Live Data", "Physical Computing"],
        "profile_text": (
            "I prototype the city of tomorrow using the materials of today. My practice "
            "combines urban research, sensor networks, and participatory design to imagine "
            "civic infrastructure that is responsive, accountable, and genuinely public. "
            "I've built environmental monitoring systems for community groups, designed "
            "data-driven public installations for city squares, and run co-design workshops "
            "with residents who are rarely asked what they want from technology. "
            "I'm sceptical of smart city rhetoric that frames urban problems as data "
            "problems — but I do think real-time data, used well and governed well, "
            "can make the invisible visible in ways that shift the political conversation."
        ),
    },
    {
        "id": 10,
        "nfc_id": "10",
        "name": "Bio Artist",
        "emoji": "🧬",
        "color": "#F97316",
        "keywords": ["Biofeedback", "AI Ethics", "Critical Design"],
        "profile_text": (
            "I work at the edge of biology and art — using living systems, physiological "
            "signals, and biodata as creative material. My installations respond to the "
            "nervous systems of the people inside them: galvanic skin response, heart rate "
            "variability, and breath all become inputs that shape light, sound, and structure "
            "in real time. I'm interested in what the body knows that the mind doesn't, "
            "and how making that visible in a public space changes the relationship between "
            "self and environment. Ethically, I think deeply about consent and intimacy: "
            "when you instrument a body, you take on a responsibility that most technology "
            "design ignores completely."
        ),
    },
]


def get_showcase_user_by_nfc_id(nfc_id: str) -> dict | None:
    """Return the showcase user whose nfc_id matches, or None if unknown."""
    return next((u for u in SHOWCASE_USERS if u["nfc_id"] == nfc_id), None)


def get_showcase_user_by_id(user_id: int) -> dict | None:
    """Return the showcase user with the given numeric ID, or None."""
    return next((u for u in SHOWCASE_USERS if u["id"] == user_id), None)


def get_all_showcase_users() -> list[dict]:
    """Return a copy of the full showcase user list."""
    return list(SHOWCASE_USERS)
