"""
Intent classification: determine what the user wants (e.g. resume Q&A, contact, general).
"""


def classify_intent(user_message: str) -> str:
    """Return intent label for the given user message."""
    if not user_message or not user_message.strip():
        return "general"
    lower = user_message.lower().strip()
    # Contact / lead: email, contact, get in touch, etc.
    if any(
        w in lower
        for w in (
            "email",
            "contact",
            "reach",
            "touch",
            "hire",
            "reach out",
            "get in touch",
            "connect",
        )
    ):
        return "contact"
    # Resume / career Q&A
    if any(
        w in lower
        for w in (
            "experience",
            "skill",
            "job",
            "resume",
            "career",
            "work",
            "education",
            "project",
            "role",
            "company",
            "linkedin",
        )
    ):
        return "resume_qa"
    return "general"
