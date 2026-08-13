"""
LLM Service — wraps OpenAI API calls for the support portal.
This is where the AI integration lives; the scanner should detect:
  - `import openai` (LIBRARY_IMPORT signal)
  - model name string "gpt-4o-mini" (MODEL_NAME_STRING signal)
  - OPENAI_API_KEY env var reference (ENV_VAR_KEY signal)
"""

import os
from typing import Tuple, Optional

import openai

# OpenAI client initialised with key from environment
client = openai.AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Model pinned explicitly — makes the scanner's job deterministic
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")

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
    Call OpenAI Chat Completions API to generate a support reply.

    Returns:
        Tuple of (reply_text, model_name, total_tokens_used)
    """
    user_message = (
        f"Customer: {customer_name}\n"
        f"Subject: {subject}\n"
        f"Priority: {priority}\n\n"
        f"Ticket:\n{ticket_body}"
    )

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=int(os.environ.get("MAX_TOKENS", "512")),
        temperature=float(os.environ.get("TEMPERATURE", "0.7")),
    )

    reply_text = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if response.usage else None

    return reply_text, MODEL_NAME, tokens_used


async def generate_ticket_summary(ticket_body: str) -> str:
    """
    Generate a one-sentence summary of a long support ticket.
    Uses the same OpenAI gpt-4o-mini model for consistency.
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Summarise this support ticket in one sentence:\n\n{ticket_body}",
            }
        ],
        max_tokens=100,
    )
    return response.choices[0].message.content
