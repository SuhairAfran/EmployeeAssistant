"""
app/tools/__init__.py
=====================
Public API for the tools package.

`workflow.py` (execute_node) calls:
    from app.tools import get_tools_for_intent

`get_tools_for_intent` returns the LangChain-compatible tool list for a given
intent + role combination.  Tools are lazy-wrapped so RBAC can be enforced
inside the MCP server rather than duplicated here.

Adding new tools:
  1. Implement the tool function in the relevant sub-module (or mcp/server.py).
  2. Register it below in TOOL_REGISTRY with its required permission.
  3. Map the intent to the new tool key in INTENT_TOOL_MAP.
"""
from __future__ import annotations

from app.models import UserRole
from app.middleware.rbac import _has_permission


# ── Tool registry ─────────────────────────────────────────────────────────────
# Maps a short tool key → (callable, required_permission).
# We use lazy imports so this module doesn't import the DB at module-load time.

def _get_tool_registry() -> dict:
    """Build the tool registry lazily to avoid circular imports at startup."""
    from app.mcp.server import (
        apply_leave,
        get_leave_balance,
        create_ticket,
        request_asset,
        fetch_payslip,
        submit_reimbursement,
        record_approval,
        inventory_status,
    )

    return {
        # HR
        "apply_leave":           (apply_leave,          "hr:leave:apply"),
        "get_leave_balance":     (get_leave_balance,    "hr:leave:view_own"),
        # IT
        "create_ticket":         (create_ticket,        "it:ticket:create"),
        "request_asset":         (request_asset,        "it:asset:request"),
        "inventory_status":      (inventory_status,     "it:inventory:view"),
        # Finance
        "fetch_payslip":         (fetch_payslip,        "finance:payslip:view_own"),
        "submit_reimbursement":  (submit_reimbursement, "finance:claim:submit"),
        # Cross-department
        "record_approval":       (record_approval,      "hr:leave:approve"),
        # RAG – permission checked, but the actual tool is role-bound at call time
        "search_knowledge":      (None,                 "hr:policy:read"),
    }


# ── Intent → tool keys mapping ────────────────────────────────────────────────

INTENT_TOOL_MAP: dict[str, list[str]] = {
    "hr.leave_apply":            ["apply_leave", "get_leave_balance"],
    "hr.leave_check_balance":    ["get_leave_balance"],
    "hr.leave_view_history":     ["get_leave_balance"],
    "hr.leave_cancel":           ["apply_leave"],
    "hr.leave_check_status":     ["get_leave_balance"],
    "hr.policy_query":           ["search_knowledge"],   # RAG retrieval
    "it.ticket_create":          ["create_ticket"],
    "it.ticket_status":          ["create_ticket"],
    "it.ticket_view":            ["create_ticket"],
    "it.asset_request":          ["request_asset"],
    "finance.payslip_fetch":     ["fetch_payslip"],
    "finance.reimbursement_submit": ["submit_reimbursement"],
    "finance.reimbursement_status": ["submit_reimbursement"],
    "finance.tax_query":         [],   # RAG only
    "general.greeting":          [],
    "general.unknown":           [],
}


def get_tools_for_intent(intent: str, user_role: UserRole) -> list:
    """
    Return the list of LangChain-compatible tools available for a given
    intent, filtered by the user's RBAC permissions.

    Called by execute_node in workflow.py.

    Args:
        intent:    The classified intent string (e.g. "hr.leave_apply").
        user_role: The authenticated user's role enum value.

    Returns:
        List of callable tool objects that the LLM can bind to.
    """
    from app.tools.rag_tools import create_rag_tool_with_role

    registry = _get_tool_registry()
    tool_keys = INTENT_TOOL_MAP.get(intent, [])

    allowed_tools = []
    for key in tool_keys:
        if key not in registry:
            continue
        tool_fn, required_perm = registry[key]
        if _has_permission(user_role, required_perm):
            # For the RAG tool, create a role-bound instance dynamically
            if key == "search_knowledge":
                allowed_tools.append(create_rag_tool_with_role(user_role))
            else:
                allowed_tools.append(tool_fn)

    return allowed_tools
