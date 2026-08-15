"""
LLM Service — wraps Google Gemini API calls for the support portal.
This is where the AI integration lives; the scanner should detect:
  - `import google.generativeai` (LIBRARY_IMPORT signal)
  - model name string "gemini-1.5-flash" (MODEL_NAME_STRING signal)
  - GEMINI_API_KEY env var reference (ENV_VAR_KEY signal)
"""

import os
from typing import Tuple, Optional

import google.generativeai as genai

# Configure Gemini with key from environment
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Model pinned explicitly — makes the scanner's job deterministic
MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-3.7-flash")

SYSTEM_PROMPT = """You are a professional customer support agent. Your role is to:
- Respond empathetically and helpfully to customer issues
- Be concise and clear (2-4 sentences maximum)
- Always end with a next step or resolution path
- Never make promises you cannot keep
"""


async def generate_support_reply(
    customer_name: str,
    subject: str,
    ticket_body: str,
    priority: Optional[str] = "normal",
) -> Tuple[str, str, int]:
    """
    Call Google Gemini API to generate a support reply.

    Returns:
        Tuple of (reply_text, model_name, total_tokens_used)
    """
    user_message = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Customer: {customer_name}\n"
        f"Subject: {subject}\n"
        f"Priority: {priority}\n\n"
        f"Ticket:\n{ticket_body}"
    )

    model = genai.GenerativeModel(MODEL_NAME)
    response = await model.generate_content_async(
        user_message,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=int(os.environ.get("MAX_TOKENS", "512")),
            temperature=float(os.environ.get("TEMPERATURE", "0.7")),
        ),
    )

    reply_text = response.text
    # Gemini returns token counts via usage_metadata
    tokens_used = (
        response.usage_metadata.total_token_count
        if hasattr(response, "usage_metadata") and response.usage_metadata
        else None
    )

    return reply_text, MODEL_NAME, tokens_used


async def generate_ticket_summary(ticket_body: str) -> str:
    """
    Generate a one-sentence summary of a long support ticket.
    Uses gemini-1.5-flash for consistency.
    """
    model = genai.GenerativeModel("gemini-3.7-flash")
    response = await model.generate_content_async(
        f"Summarise this support ticket in one sentence:\n\n{ticket_body}"
    )
    return response.text
