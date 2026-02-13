"""
Tool implementations: Pushover notifications, record user details, record unknown questions.
"""

import os
import requests


def push(text: str) -> None:
    """Send a notification via Pushover."""
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        },
    )


def record_user_details(
    email: str,
    name: str = "Name not provided",
    notes: str = "not provided",
) -> dict:
    """Record that a user is interested and provided contact details."""
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question: str) -> dict:
    """Record a question that couldn't be answered."""
    push(f"Recording {question}")
    return {"recorded": "ok"}


# Registry for controller to dispatch tool calls by name
TOOL_REGISTRY = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
}
