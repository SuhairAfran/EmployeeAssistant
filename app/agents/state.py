"""
Agent State
===========
The single TypedDict that flows through every LangGraph node.
Every node reads from this state and returns a partial update.

Rule: never pass data between nodes via side channels (globals,
      module-level vars, etc.) — everything goes through AgentState.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal, TypedDict, Dict, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.models import UserRole


# ── Intent categories ─────────────────────────────────────────────────────────

Intent = Literal[
    # HR
    "hr.policy_query",
    "hr.leave_apply",
    "hr.leave_check_balance",
    "hr.leave_view_history",
    "hr.leave_cancel",
    "hr.leave_check_status",
    "hr.leave_view_team",
    "hr.leave_approve",
    "hr.department_on_leave",
    # IT
    "it.ticket_create",
    "it.ticket_status",
    "it.asset_request",
    "it.ticket_view",
    "it.knowledge_search",
    "it.policy_query",
    # Finance
    "finance.payslip_fetch",
    "finance.reimbursement_submit",
    "finance.reimbursement_status",
    "finance.tax_query",
    # Meta
    "general.greeting",
    "general.unknown",
]

RouteTo = Literal["hr_agent", "it_agent", "finance_agent", "rag_agent", "unknown"]


# ── GEPA: planning and evaluation ─────────────────────────────────────────────

class ActionPlan(TypedDict):
    """Written by the Plan node before tool execution."""
    steps: list[str]           # ["1. Check leave balance", "2. Validate dates", ...]
    tools_needed: list[str]    # ["get_leave_balance", "check_overlaps"]
    reasoning: str             # why these steps


class EvalScore(TypedDict):
    """Written by the Evaluate node after response generation."""
    score: float               # 0.0 – 1.0
    relevance: float
    completeness: float
    rbac_compliant: bool
    critique: str              # natural language feedback for retry


# ── Main state ────────────────────────────────────────────────────────────────

class AgentState(TypedDict, total=False):
    """
    Flows through the entire LangGraph workflow.
    Nodes return a dict with only the keys they modify.
    """

    # ── Identity & auth ────────────────────────────────────────
    user_id:       str
    user_email:    str
    user_name:     str
    user_role:     UserRole
    department_id: str | None
    manager_id:    str | None
    gender:        str
    is_married:    bool
    preferred_lang: str

    # ── Conversation ────────────────────────────────────────────
    session_id:    str
    messages:      Annotated[list[BaseMessage], add_messages]  # full LangChain message history
    raw_query:     str                 # original user text (unchanged)

    # ── Routing ─────────────────────────────────────────────────
    intent:        Intent
    intent_confidence: float           # 0.0–1.0
    route_to:      RouteTo

    # ── GEPA: Plan → Execute → Evaluate ────────────────────────
    plan:          ActionPlan
    eval_score:    EvalScore
    retry_count:   int                 # incremented on each GEPA retry
    retry_critique: str                # critique passed back to Plan node

    # ── Tool execution ──────────────────────────────────────────
    tool_calls:    list[dict]          # [{name, args, result}]
    tool_error:    str | None

    # ── RAG ─────────────────────────────────────────────────────
    rag_docs:      list[dict]          # [{content, source, score}]
    rag_confidence: float              # avg cosine similarity of retrieved chunks
    web_search_triggered: bool

    # ── Human-in-loop (approval) ────────────────────────────────
    approval_required: bool
    approval_entity_type: str | None   # 'leave' | 'asset_request' | 'reimbursement'
    approval_entity_id:  str | None
    approval_decision:   str | None    # 'approved' | 'rejected'
    approval_note:       str | None

    # ── Email ────────────────────────────────────────────────────
    email_triggered:  bool
    email_recipients: list[str]
    email_subject:    str | None
    email_body:       str | None

    # ── Final response ──────────────────────────────────────────
    response:      str                 # final message shown to user
    response_type: Literal["text", "form", "table", "error"]
    metadata:      dict[str, Any]      # additional data for frontend (e.g., leave_id)

    # ── Observability ────────────────────────────────────────────
    agent_used:    str | None
    llm_model:     str | None
    latency_ms:    int | None
    error:         str | None


def initial_state(user_ctx: dict, query: str, session_id: str | None = None) -> AgentState:
    """
    Create a fresh AgentState from the enriched user context dict
    (returned by app.middleware.rbac.enrich_request).
    """
    return AgentState(
        user_id=user_ctx["user_id"],
        user_email=user_ctx["user_email"],
        user_name=user_ctx["user_name"],
        user_role=user_ctx["user_role"],
        department_id=user_ctx.get("department_id"),
        manager_id=user_ctx.get("manager_id"),
        gender=user_ctx.get("gender", "unknown"),
        is_married=user_ctx.get("is_married", False),
        preferred_lang=user_ctx.get("preferred_lang", "en"),
        session_id=session_id or str(uuid.uuid4()),
        messages=[],
        raw_query=query,
        intent="general.unknown",
        intent_confidence=0.0,
        route_to="unknown",
        retry_count=0,
        tool_calls=[],
        rag_docs=[],
        rag_confidence=0.0,
        web_search_triggered=False,
        approval_required=False,
        email_triggered=False,
        email_recipients=[],
        response="",
        response_type="text",
        metadata={},
    )