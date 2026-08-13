"""
Formatter utility — non-AI text processing utilities.
These functions exist to make the codebase look realistic (not stripped to a single AI call).
The scanner should NOT flag these as AI signals.
"""

import re
from typing import Optional


def format_ticket_body(raw_text: str) -> str:
    """
    Sanitise and normalise customer ticket text before sending to the LLM.
    Removes excessive whitespace, strips HTML tags, truncates to 2000 chars.
    """
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", raw_text)
    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Truncate to safe length for LLM context window
    return text[:2000]


def format_reply_for_email(reply: str, customer_name: str, agent_name: Optional[str] = "Support Team") -> str:
    """
    Wrap an LLM-generated reply in a professional email format.
    """
    greeting = f"Dear {customer_name},"
    sign_off = f"\nBest regards,\n{agent_name}"
    return f"{greeting}\n\n{reply}\n{sign_off}"


def truncate_snippet(text: str, max_length: int = 200) -> str:
    """Return a truncated preview of a text block."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."


def sanitize_customer_name(name: str) -> str:
    """Remove potentially dangerous characters from a customer name field."""
    return re.sub(r"[^a-zA-Z0-9 .\-']", "", name).strip()
