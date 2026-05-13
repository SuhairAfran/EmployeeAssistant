"""
app/graph/audit.py
==================
Async helper to write tool-call events to the audit_logs table.

Called from _run_specialist in workflow.py after each tool invocation
(success, failure, and RBAC violations).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import structlog

from app.database import AsyncSessionLocal

logger = structlog.get_logger("audit")

# ── Entity type extraction ─────────────────────────────────────────────────────
# Maps keys returned by tool results to (entity_type, entity_id) for the schema.
_ENTITY_KEY_MAP: list[tuple[str, str]] = [
    ("leave_id",   "leave"),
    ("ticket_id",  "ticket"),
    ("request_id", "asset_request"),
    ("claim_id",   "reimbursement"),
]


def _extract_entity(tool_result: Any) -> tuple[str | None, str | None]:
    """Pull entity_type / entity_id out of a tool result dict, if present."""
    if not isinstance(tool_result, dict):
        return None, None
    for key, entity_type in _ENTITY_KEY_MAP:
        if key in tool_result:
            return entity_type, str(tool_result[key])
    return None, None


# ── Public API ────────────────────────────────────────────────────────────────

async def save_audit_log(
    *,
    user_id: str,
    session_id: str | None,
    action: str,
    tool_used: str,
    agent_used: str | None = None,
    llm_model: str | None = None,
    status: str = "success",
    error_message: str | None = None,
    latency_ms: int | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    ip_address: str | None = None,
    metadata: dict | None = None,
) -> None:
    """
    Fire-and-forget write to audit_logs.

    Swallows all exceptions so a logging failure never crashes a user request.
    """
    try:
        # Resolve session_id UUID — audit_logs.session_id references conversation_sessions(id)
        # If the session_id passed is not a valid UUID or not found, we leave it NULL
        # to avoid a FK violation.
        session_uuid: str | None = None
        if session_id:
            try:
                # Validate it's a well-formed UUID before inserting
                uuid.UUID(session_id)
                session_uuid = session_id
            except ValueError:
                pass  # not a UUID — skip FK reference

        now = datetime.now(timezone.utc)

        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            await db.execute(
                text("""
                INSERT INTO audit_logs (
                    id, user_id, session_id,
                    action, entity_type, entity_id,
                    agent_used, tool_used, llm_model,
                    status, error_message, latency_ms,
                    ip_address, metadata, created_at
                ) VALUES (
                    gen_random_uuid(), :user_id, :session_id,
                    :action, :entity_type, :entity_id,
                    :agent_used, :tool_used, :llm_model,
                    :status, :error_message, :latency_ms,
                    :ip_address::inet, :metadata, :created_at
                )
                """),
                {
                    "user_id":       user_id,
                    "session_id":    session_uuid,
                    "action":        action,
                    "entity_type":   entity_type,
                    "entity_id":     entity_id,
                    "agent_used":    agent_used,
                    "tool_used":     tool_used,
                    "llm_model":     llm_model,
                    "status":        status,
                    "error_message": error_message,
                    "latency_ms":    latency_ms,
                    "ip_address":    ip_address,
                    "metadata":      metadata or {},
                    "created_at":    now,
                },
            )
            await db.commit()

        logger.debug(
            "audit_log_saved",
            action=action,
            tool=tool_used,
            status=status,
            user=user_id,
        )

    except Exception as exc:  # noqa: BLE001
        # Never crash the user request because of an audit failure
        logger.warning("audit_log_failed", error=str(exc), action=action, tool=tool_used)
