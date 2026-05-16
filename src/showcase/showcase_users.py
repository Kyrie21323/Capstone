"""
Showcase User data access layer — single source of truth for NFC showcase users.

Schema per user:
  id           int   — internal numeric ID
  nfc_id       str   — string read from NFC badge (e.g. "1", "2", "A3F2...")
  name         str   — person's display name
  tag          str   — short archetype / role label (1–2 words), shown under name
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
        "name": "Kyrie Park",
        "tag": "Interactive Developer",
        "emoji": "💻",
        "color": "#2563EB",
        "keywords": ["Backend Developer", "Computer Vision", "Interactive Media"],
        "profile_text": (
            "I build the systems behind experiences people can see and touch — the servers, "
            "services, and data paths that let an installation actually stay alive in a room. "
            "Most of my work is backend engineering: APIs, streaming pipelines, and the glue that "
            "keeps interactive pieces from stuttering when the crowd shows up. I'm drawn to "
            "computer vision — how models parse images and video, and how that understanding "
            "feeds interactive media in real time rather than as a canned demo. "
            "I'm interested in the tension between expressive front-ends and honest infrastructure: "
            "if the CV pipeline is fragile, the whole interaction becomes a performance you can't "
            "trust. Lately I've been focused on closing that gap — so creative work feels immediate "
            "because the engineering underneath is deliberate, not improvised."
        ),
    },
    {
        "id": 2,
        "nfc_id": "2",
        "name": "Eunbom Jo",
        "tag": "Filmmaker & Performer",
        "emoji": "🎬",
        "color": "#B91C1C",
        "keywords": ["Film Media", "Acting", "Band Leader", "Base Guitar Player"],
        "profile_text": (
            "I live in the overlap between film media and live performance — directing and acting "
            "with the same stubborn curiosity about what makes a moment believable on camera "
            "and in front of a crowd. On set I'm drawn to rhythm and blocking: how a scene breathes, "
            "how a cut lands, how silence reads as loudly as a line. Off camera I lead a band and "
            "play bass guitar — holding down the low end while everyone else stretches the arrangement. "
            "I'm fascinated by how performance disciplines bleed into each other — screen grammar, "
            "stage presence, and the physical honesty musicians bring when the take is live. "
            "My current obsession is work where those worlds actually talk: film that respects "
            "musical time, and live music that borrows tension from cinema."
        ),
    },
    {
        "id": 3,
        "nfc_id": "3",
        "name": "Yiyang",
        "tag": "Video Creator",
        "emoji": "🎥",
        "color": "#DB2777",
        "keywords": ["Video Maker", "Movie Design", "Scripter"],
        "profile_text": (
            "I'm a video maker who cares as much about movie design as about what happens in the edit. "
            "I build pieces from the script outward — structure first, then image, then motion — "
            "because I'm convinced bad writing hides behind good colour grading more often than people admit. "
            "As a scripter I'm obsessed with economy: lines that do two jobs at once, scenes that "
            "earn their length, dialogue that sounds like constraint rather than improvisation. "
            "I'm drawn to movie design as a language — lens choice, production design, and pacing "
            "communicating tone before the audience can name it. Lately I've been focused on short-form "
            "and narrative work where every cut has to justify itself, and where the script and the "
            "edit stay in honest argument until something coherent wins."
        ),
    },
    {
        "id": 4,
        "nfc_id": "4",
        "name": "Junyong Moon",
        "tag": "Software Engineer",
        "emoji": "⚙️",
        "color": "#0D9488",
        "keywords": ["Computer Science", "Machine Learning", "Optimization", "DevOps", "Software Engineer"],
        "profile_text": (
            "I'm a software engineer who treats computer science as a habit, not a credential — "
            "systems thinking, clear interfaces between components, and an allergy to magic. "
            "A lot of my work sits at the intersection of machine learning and everything that "
            "has to happen after the notebook: data contracts, training jobs, evaluation, "
            "and the long boring path to something you can ship. I'm drawn to optimization — "
            "faster training, tighter inference, but also smarter trade-offs when perfect is "
            "the enemy of deployed. DevOps is part of how I think: reproducible builds, "
            "observability, and never pretending reliability is someone else's problem. "
            "Lately I've been focused on teams that move fast without lying to themselves about "
            "what breaks when traffic spikes or the pipeline drifts."
        ),
    },
    {
        "id": 5,
        "nfc_id": "5",
        "name": "Minseok Kim",
        "tag": "AI Developer",
        "emoji": "🤖",
        "color": "#6B21A8",
        "keywords": ["Machine Learning", "AI", "Developer", "Backend"],
        "profile_text": (
            "I build the backend half of AI products — the services, storage, and orchestration "
            "users never see but always depend on. My focus is machine learning in production: "
            "feature pipelines, model deployment, monitoring, and the APIs that let a team iterate "
            "without treating every release like a fire drill. I'm drawn to the gap between "
            "benchmark scores and real traffic — latency, skewed inputs, and the ways models fail "
            "when reality refuses to match the training set. As a developer I care about code that "
            "future-me won't silently resent: clear boundaries, tests where they matter, and systems "
            "that degrade honestly instead of lying with a 200 OK. Lately I've been obsessed with "
            "making AI backends predictable enough that product experiments feel safe again."
        ),
    },
    {
        "id": 6,
        "nfc_id": "6",
        "name": "Ren Okada",
        "tag": "XR Developer",
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
        "name": "Camille Fournier",
        "tag": "Interaction Designer",
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
        "name": "Jonah Mercer",
        "tag": "Computational Artist",
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
        "name": "Inés Valero",
        "tag": "Urban Futurist",
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
        "name": "Malik Osei",
        "tag": "Bio Artist",
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
