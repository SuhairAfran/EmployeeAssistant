from typing import List
from langchain_core.tools import BaseTool
from app.models import UserRole

# Import all domain tools
from app.tools.hr_rag_tools import build_hr_policy_tool
from app.tools.it_rag_tools import build_it_policy_tool
from app.tools.hr_tools import (
    get_leave_balance, apply_for_leave, cancel_leave,
    view_leave_history, view_team_leaves, view_department_on_leave_today,
)
from app.tools.it_tools import (
    create_it_ticket, get_ticket_status, request_it_asset,
    view_it_tickets, search_known_issues,
)


# ── Tool-name → intent mapping ───────────────────────────────────────────────
# After the LLM picks a tool, we reverse-map the tool name back to the legacy
# intent string so the API response and frontend still receive a meaningful
# intent field.
TOOL_INTENT_MAP: dict[str, str] = {
    "get_leave_balance":              "hr.leave_check_balance",
    "apply_for_leave":                "hr.leave_apply",
    "cancel_leave":                   "hr.leave_cancel",
    "view_leave_history":             "hr.leave_view_history",
    "view_team_leaves":               "hr.leave_view_team",
    "view_department_on_leave_today": "hr.department_on_leave",
    "search_hr_policies":             "hr.policy_query",
    "create_it_ticket":               "it.ticket_create",
    "get_ticket_status":              "it.ticket_status",
    "view_it_tickets":                "it.ticket_view",
    "request_it_asset":               "it.asset_request",
    "search_known_issues":            "it.knowledge_search",
    "search_it_policies":             "it.policy_query",
}

# RAG tool names — used by the workflow to decide whether to run the evaluator.
RAG_TOOL_NAMES: set[str] = {"search_hr_policies", "search_it_policies"}


def get_tools_for_role(user_role: UserRole) -> List[BaseTool]:
    """Return all tools this role is permitted to use.

    The LLM's tool-calling capability acts as the intent classifier — it
    picks the right tool based on the rich descriptions in each tool's
    docstring. No separate intent LLM call is needed.

    Finance tools are intentionally excluded — finance features are not
    yet available.
    """
    tools: list[BaseTool] = []

    # ── HR ──────────────────────────────────────────────────────────────
    # Leave self-service (all authenticated users)
    tools.extend([
        get_leave_balance, apply_for_leave, cancel_leave, view_leave_history,
    ])

    # Colleague status (all users)
    tools.append(view_department_on_leave_today)

    # HR policy RAG — bound to trusted user_role, HR department only.
    tools.append(build_hr_policy_tool(user_role))

    # HR management tools (managers / admin / HR only)
    if user_role in (UserRole.manager, UserRole.admin, UserRole.hr_team):
        tools.append(view_team_leaves)

    # ── IT ──────────────────────────────────────────────────────────────
    tools.extend([
        create_it_ticket, get_ticket_status, request_it_asset,
        view_it_tickets, search_known_issues,
    ])

    # IT policy RAG — bound to trusted user_role, IT department.
    tools.append(build_it_policy_tool(user_role))

    # ── Finance ─────────────────────────────────────────────────────────
    # Disabled: finance features are not yet available.

    return tools


def infer_intent_from_tool_calls(tool_calls: list[dict]) -> str:
    """Derive the legacy intent string from the tools the LLM called.

    Returns the intent of the first recognised tool, or 'general.unknown'
    if no tools were called (pure conversational response).
    """
    for tc in tool_calls:
        name = tc.get("name", "")
        if name in TOOL_INTENT_MAP:
            return TOOL_INTENT_MAP[name]
    return "general.unknown"
