"""
Support route — handles incoming support ticket submissions and generates AI replies.
"""

import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.llm_service import generate_support_reply
from utils.formatter import format_ticket_body

router = APIRouter()


class TicketRequest(BaseModel):
    ticket_id: str
    customer_name: str
    subject: str
    body: str
    priority: Optional[str] = "normal"


class TicketReply(BaseModel):
    ticket_id: str
    reply: str
    model_used: str
    tokens_used: Optional[int] = None


@router.post("/reply", response_model=TicketReply)
async def create_support_reply(request: TicketRequest):
    """
    Generate an AI-powered reply to a customer support ticket.
    Uses OpenAI GPT to craft a helpful, professional response.
    """
    formatted_body = format_ticket_body(request.body)

    try:
        reply_text, model_name, tokens = await generate_support_reply(
            customer_name=request.customer_name,
            subject=request.subject,
            ticket_body=formatted_body,
            priority=request.priority,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

    return TicketReply(
        ticket_id=request.ticket_id,
        reply=reply_text,
        model_used=model_name,
        tokens_used=tokens,
    )


@router.get("/tickets/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """Stub endpoint for ticket status lookup (not AI-related)."""
    return {"ticket_id": ticket_id, "status": "open", "created_at": "2024-01-15T10:00:00Z"}
