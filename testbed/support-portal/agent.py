"""
agent.py — Customer Support AI Agent

This module implements a LangGraph-based stateful AI agent for the support portal.
The agent orchestrates multi-step reasoning over a customer query before generating
a final response via the LLM.

Architecture:
  Query → Classify → [Retrieve KB | Search Tickets] → Synthesize → Respond

Using LangGraph here because the support flow requires conditional branching
(e.g., billing queries go to Ticketing, technical queries go to KB) and stateful
history tracking across turns. A simple LLM call chain is insufficient for this
level of control flow.

Purpose for the scanner:
  This file imports `langgraph` which is mapped in known_signals.py to:
    provider="LangChain", asset_type="AI Agent"
  The scanner should discover this as a standalone "AI Agent" evidence record,
  separate from the existing openai import in llm_service.py.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
import openai
import os


# ---------------------------------------------------------------------------
# Agent state schema
# ---------------------------------------------------------------------------

class SupportAgentState(TypedDict):
    query: str
    category: Literal["billing", "technical", "general", "unknown"]
    kb_context: str
    ticket_context: str
    final_response: str


# ---------------------------------------------------------------------------
# Agent nodes
# ---------------------------------------------------------------------------

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"


def classify_query(state: SupportAgentState) -> SupportAgentState:
    """Classify the customer query into a support category."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the customer support query into one of: "
                    "billing, technical, general, unknown. "
                    "Respond with only the category word."
                ),
            },
            {"role": "user", "content": state["query"]},
        ],
        max_tokens=10,
    )
    category = response.choices[0].message.content.strip().lower()
    if category not in ("billing", "technical", "general"):
        category = "unknown"
    return {**state, "category": category}


def retrieve_kb_context(state: SupportAgentState) -> SupportAgentState:
    """Simulate retrieving relevant knowledge base articles."""
    # In production this would call a vector search service (e.g., the
    # doc-search app in this testbed). For the testbed it returns a stub.
    kb_context = (
        f"[KB] Found 2 articles relevant to technical query: '{state['query'][:40]}...'"
    )
    return {**state, "kb_context": kb_context}


def retrieve_ticket_context(state: SupportAgentState) -> SupportAgentState:
    """Simulate retrieving open billing tickets for the customer."""
    ticket_context = (
        f"[Tickets] No open billing tickets found for query: '{state['query'][:40]}...'"
    )
    return {**state, "ticket_context": ticket_context}


def synthesize_response(state: SupportAgentState) -> SupportAgentState:
    """Generate the final customer-facing response using all gathered context."""
    context_parts = []
    if state.get("kb_context"):
        context_parts.append(state["kb_context"])
    if state.get("ticket_context"):
        context_parts.append(state["ticket_context"])
    context = "\n".join(context_parts) or "No additional context available."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful customer support agent. "
                    "Use the provided context to give a clear, empathetic response."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nCustomer query: {state['query']}",
            },
        ],
        max_tokens=300,
    )
    final_response = response.choices[0].message.content.strip()
    return {**state, "final_response": final_response}


# ---------------------------------------------------------------------------
# Route logic — determines which retrieval node to use
# ---------------------------------------------------------------------------

def route_query(state: SupportAgentState) -> Literal["retrieve_kb", "retrieve_tickets", "synthesize"]:
    if state["category"] == "technical":
        return "retrieve_kb"
    elif state["category"] == "billing":
        return "retrieve_tickets"
    else:
        return "synthesize"


# ---------------------------------------------------------------------------
# Build the LangGraph state machine
# ---------------------------------------------------------------------------

def build_support_agent() -> StateGraph:
    """
    Construct and compile the support agent graph.

    Graph structure:
      classify → [conditional route] → retrieve_kb / retrieve_tickets → synthesize → END
    """
    graph = StateGraph(SupportAgentState)

    graph.add_node("classify", classify_query)
    graph.add_node("retrieve_kb", retrieve_kb_context)
    graph.add_node("retrieve_tickets", retrieve_ticket_context)
    graph.add_node("synthesize", synthesize_response)

    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", route_query, {
        "retrieve_kb": "retrieve_kb",
        "retrieve_tickets": "retrieve_tickets",
        "synthesize": "synthesize",
    })
    graph.add_edge("retrieve_kb", "synthesize")
    graph.add_edge("retrieve_tickets", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


# Compiled agent — import this in your route handlers
support_agent = build_support_agent()


def run_agent(query: str) -> str:
    """
    Entry point: run the support agent for a given customer query.
    Returns the final generated response string.
    """
    initial_state: SupportAgentState = {
        "query": query,
        "category": "unknown",
        "kb_context": "",
        "ticket_context": "",
        "final_response": "",
    }
    result = support_agent.invoke(initial_state)
    return result["final_response"]
