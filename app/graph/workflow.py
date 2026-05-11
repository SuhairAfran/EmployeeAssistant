"""
LangGraph Workflow — Tool-first dispatch (no intent node)
=========================================================
The LLM's native tool-calling replaces the dedicated intent classifier.
Graph: scope_gate → execute_node → (eval_node) → save_memory → respond → END
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import date, timedelta
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, StateGraph
from psycopg_pool import AsyncConnectionPool
from sqlalchemy import func

from app.agents import AgentState, EvalScore, initial_state
from app.config import settings
from app.graph.prompts import (
    EVAL_SYSTEM,
    EXECUTE_CONTEXT_TEMPLATE,
    EXECUTE_SYSTEM_STATIC,
)
from app.middleware import RBACViolation
from app.models import UserRole
from app.tools import RAG_TOOL_NAMES, infer_intent_from_tool_calls


# ── LLM factory ──────────────────────────────────────────────────────────────

def get_llm(model_key: str, temperature: float = settings.LLM_TEMPERATURE) -> BaseChatModel:
    """Create an LLM client based on the requested model key."""
    model_name = getattr(settings, f"LLM_{model_key.upper()}", settings.LLM_HR)

    kwargs = {}
    verify_ssl = getattr(settings, "OPENAI_VERIFY_SSL", True)
    if not verify_ssl:
        import httpx
        kwargs["http_client"] = httpx.Client(verify=False)
        kwargs["http_async_client"] = httpx.AsyncClient(verify=False)

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,
        **kwargs
    )


# ── Node 1: Scope gate (pure Python, no LLM) ─────────────────────────────────

# Simple heuristic for greetings — no LLM needed.
_GREETING_TOKENS = {
    "hi", "hello", "hey", "morning", "afternoon", "evening",
    "good morning", "good afternoon", "good evening",
    "thanks", "thank you", "thankyou", "bye", "goodbye",
    "how are you", "howdy", "sup", "what's up", "yo",
}


def _is_greeting(text: str) -> bool:
    normalised = text.strip().lower().rstrip("!.,?")
    return normalised in _GREETING_TOKENS or (
        len(normalised.split()) <= 3 and any(
            normalised.startswith(g) for g in ("hi ", "hey ", "hello ", "thanks ", "thank ")
        )
    )


async def scope_gate_node(state: AgentState) -> AgentState:
    """Fast Python-only gate: handle greetings, set up tool list.

    No LLM call. Greetings get a canned response and skip to respond.
    All other queries proceed to execute_node with the full tool set.
    """
    raw = state["raw_query"]

    if _is_greeting(raw):
        return {
            "intent": "general.greeting",
            "response": (
                f"Hi {state.get('user_name', 'there')}! I can help with workplace "
                "HR and IT support — leave, HR policies, IT tickets, asset "
                "requests, known issues, approvals, and self-service info. "
                "What would you like to do?"
            ),
            "response_type": "text",
            "route_to": "respond",
        }

    return {"route_to": "execute_node"}


def route_after_scope_gate(state: AgentState) -> str:
    return state.get("route_to", "execute_node")


# ── Helpers: history management ───────────────────────────────────────────────

def _build_date_context() -> dict:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    next_week_start = week_start + timedelta(days=7)
    next_week_end = next_week_start + timedelta(days=6)
    days_to_monday = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_to_monday)
    return {
        "current_date": today.isoformat(),
        "current_weekday": today.strftime("%A"),
        "tomorrow_date": tomorrow.isoformat(),
        "tomorrow_weekday": tomorrow.strftime("%A"),
        "day_after_tomorrow_date": day_after.isoformat(),
        "day_after_tomorrow_weekday": day_after.strftime("%A"),
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "next_week_start": next_week_start.isoformat(),
        "next_week_end": next_week_end.isoformat(),
        "next_monday": next_monday.isoformat(),
    }


def _get_role_guidance(user_role: UserRole) -> str:
    if user_role == UserRole.employee:
        return "You are a helpful Service Assistant. Guide the user politely through policies and applications."
    elif user_role == UserRole.manager:
        return "You are an HR Administrative Copilot. This user is a manager. They can view team leaves and approve requests via the approvals dashboard. When they ask about pending leaves, direct them to the approvals tab."
    elif user_role == UserRole.admin:
        return "You are an HR Administrative Copilot. This user has full authorization. Guide them efficiently through all HR operations."
    elif user_role == UserRole.hr_team:
        return "You are an HR Administrative Copilot. This user is on the HR team. Guide them efficiently through all HR operations."
    else:
        return "You are a helpful workplace assistant."


def _sanitize_history(history: list) -> list:
    """Strip any tool-call sequences that are not fully closed.

    OpenAI requires that every assistant message containing ``tool_calls``
    is immediately followed by one ``ToolMessage`` per ``tool_call_id``
    before any other role can speak.
    """
    if not history:
        return []

    sanitized: list = []
    i = 0
    n = len(history)
    while i < n:
        message = history[i]
        tool_calls = getattr(message, "tool_calls", None)

        if isinstance(message, AIMessage) and tool_calls:
            expected_ids = {
                tc.get("id")
                for tc in tool_calls
                if isinstance(tc, dict) and tc.get("id")
            }
            j = i + 1
            following: list[ToolMessage] = []
            while j < n and isinstance(history[j], ToolMessage):
                following.append(history[j])
                j += 1
            found_ids = {
                getattr(tm, "tool_call_id", None) for tm in following
            }
            if expected_ids and expected_ids.issubset(found_ids):
                sanitized.append(message)
                sanitized.extend(following)
            i = j
            continue

        if isinstance(message, ToolMessage):
            i += 1
            continue

        sanitized.append(message)
        i += 1

    return sanitized


def _truncate_history(history: list, max_messages: int) -> list:
    """Sliding-window truncate prior messages, preserving tool_call pairing."""
    if not history:
        return []

    window = history[-max_messages:] if len(history) > max_messages else list(history)

    while window:
        head = window[0]
        if isinstance(head, ToolMessage):
            window = window[1:]
            continue
        if isinstance(head, AIMessage) and getattr(head, "tool_calls", None):
            window = window[1:]
            continue
        break

    return _sanitize_history(window)


# ── Node 2: Execute (tools + RAG) ────────────────────────────────────────────

async def execute_node(state: AgentState) -> AgentState:
    from app.tools import get_tools_for_role

    llm = get_llm("hr")  # default model for all queries
    tools = get_tools_for_role(state["user_role"])
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    history = _truncate_history(
        state.get("messages", []), settings.MAX_HISTORY_MESSAGES
    )

    messages = [
        SystemMessage(content=EXECUTE_SYSTEM_STATIC),
        SystemMessage(content=EXECUTE_CONTEXT_TEMPLATE.format(
            user_name=state["user_name"],
            user_role=state["user_role"].value,
            department_id=state.get("department_id", "N/A"),
            role_guidance=_get_role_guidance(state["user_role"]),
            **_build_date_context(),
        )),
        *history,
        HumanMessage(content=state["raw_query"]),
    ]

    start = time.time()
    initial_llm = llm_with_tools.with_config(
        {"tags": ["execute_llm", "initial_pass"], "run_name": "initial_pass"}
    )
    result = await initial_llm.ainvoke(messages)
    latency = int((time.time() - start) * 1000)

    tool_calls = []
    tool_messages: list[ToolMessage] = []

    approval_required = False
    approval_entity_type = None
    approval_entity_id = None
    email_triggered = False
    email_recipients = []
    email_subject = None
    email_body = None
    used_rag = False

    if hasattr(result, "tool_calls") and result.tool_calls:
        for tc in result.tool_calls:
            tool_fn = next((t for t in tools if t.name == tc["name"]), None)
            if tc["name"] in RAG_TOOL_NAMES:
                used_rag = True
            if tool_fn:
                try:
                    tool_result = await tool_fn.ainvoke(tc["args"])
                    tool_calls.append({"name": tc["name"], "args": tc["args"], "result": tool_result})

                    tool_messages.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tc["id"],
                        name=tc["name"],
                    ))

                    if isinstance(tool_result, dict):
                        if tool_result.get("approval_required"):
                            approval_required = True
                            if "leave_id" in tool_result:
                                approval_entity_type = "leave"
                                approval_entity_id = str(tool_result["leave_id"])
                            elif "ticket_id" in tool_result:
                                approval_entity_type = "it_action"
                                approval_entity_id = str(tool_result["ticket_id"])
                            elif "request_id" in tool_result:
                                approval_entity_type = "asset_request"
                                approval_entity_id = str(tool_result["request_id"])
                            elif "claim_id" in tool_result:
                                approval_entity_type = "reimbursement"
                                approval_entity_id = str(tool_result["claim_id"])

                        if tool_result.get("email_triggered"):
                            email_triggered = True
                            email_recipients = tool_result.get("email_recipients", [])
                            email_subject = tool_result.get("email_subject")
                            email_body = tool_result.get("email_body")

                except RBACViolation as e:
                    tool_messages.append(ToolMessage(
                        content=f"Permission denied: {e}",
                        tool_call_id=tc["id"],
                        name=tc["name"],
                    ))
                    return {
                        "error": str(e),
                        "response": str(e),
                        "response_type": "error",
                        "intent": infer_intent_from_tool_calls(tool_calls),
                        "messages": _sanitize_history([
                            *state.get("messages", []),
                            HumanMessage(content=state["raw_query"]),
                            result,
                            *tool_messages,
                        ]),
                    }
                except Exception as e:  # noqa: BLE001
                    tool_messages.append(ToolMessage(
                        content=f"Tool '{tc['name']}' failed: {e}",
                        tool_call_id=tc["id"],
                        name=tc["name"],
                    ))
            else:
                tool_messages.append(ToolMessage(
                    content=f"Tool '{tc['name']}' is not available.",
                    tool_call_id=tc["id"],
                    name=tc["name"],
                ))

    # ── Post-tool synthesis ──────────────────────────────────────────────
    final_message = result
    if tool_messages:
        synthesis_messages = [*messages, result, *tool_messages]
        synthesis_start = time.time()
        synthesis_llm = llm_with_tools.with_config(
            {"tags": ["execute_llm", "synthesis"], "run_name": "synthesis_pass"}
        )
        final_message = await synthesis_llm.ainvoke(synthesis_messages)
        latency += int((time.time() - synthesis_start) * 1000)

    final_content = final_message.content if isinstance(final_message.content, str) else str(final_message.content)

    # Infer intent from which tools were called
    inferred_intent = infer_intent_from_tool_calls(tool_calls)

    new_messages = [
        *state.get("messages", []),
        HumanMessage(content=state["raw_query"]),
        result,
        *tool_messages,
        *([final_message] if tool_messages else []),
    ]
    new_messages = _sanitize_history(new_messages)

    state_update = {
        "messages": new_messages,
        "tool_calls": tool_calls,
        "response": final_content,
        "latency_ms": latency,
        "intent": inferred_intent,
        "llm_model": settings.LLM_HR,
        "metadata": {
            **state.get("metadata", {}),
            "used_rag": used_rag,
        },
    }

    if approval_required:
        state_update["approval_required"] = True
        state_update["approval_entity_type"] = approval_entity_type
        state_update["approval_entity_id"] = approval_entity_id

    if email_triggered:
        state_update["email_triggered"] = True
        state_update["email_recipients"] = email_recipients
        state_update["email_subject"] = email_subject
        state_update["email_body"] = email_body

    return state_update


# ── Node 3: Evaluate (only for RAG responses) ────────────────────────────────

async def eval_node(state: AgentState) -> AgentState:
    if state.get("error"):
        return {"eval_score": {"score": 0.0, "relevance": 0.0, "completeness": 0.0,
                               "rbac_compliant": True, "critique": ""}}

    llm = get_llm("evaluator")
    result = await llm.ainvoke([
        SystemMessage(content=EVAL_SYSTEM),
        HumanMessage(content=f"Query: {state['raw_query']}\n\nResponse: {state['response']}\n\n"
                              f"User role: {state['user_role'].value}"),
    ])
    try:
        score_data: EvalScore = json.loads(result.content)
        return {"eval_score": score_data}
    except Exception:
        return {"eval_score": {"score": 1.0, "relevance": 1.0, "completeness": 1.0,
                               "rbac_compliant": True, "critique": ""}}


def route_after_execute(state: AgentState) -> Literal["eval_node", "save_memory"]:
    """Run evaluator only for RAG/policy responses; skip for tool actions."""
    if state.get("error"):
        return "save_memory"
    if state.get("approval_required"):
        return "save_memory"

    # Only evaluate if a RAG tool was used (free-form policy answers)
    used_rag = state.get("metadata", {}).get("used_rag", False)
    if used_rag:
        return "eval_node"

    return "save_memory"


def route_after_eval(state: AgentState) -> Literal["execute_node", "save_memory"]:
    """Bounded retry: re-run execute if eval score is low."""
    if state.get("error"):
        return "save_memory"
    if not state.get("response"):
        return "save_memory"

    score = state.get("eval_score", {}).get("score", 1.0)
    retry_count = state.get("retry_count", 0)

    if score < settings.GEPA_EVAL_THRESHOLD and retry_count < settings.GEPA_MAX_RETRIES:
        state["retry_count"] = retry_count + 1
        state["retry_critique"] = state.get("eval_score", {}).get("critique", "")
        return "execute_node"

    return "save_memory"


# ── Node 4: Save memory ──────────────────────────────────────────────────────

async def save_memory_node(state: AgentState) -> AgentState:
    from app.database import AsyncSessionLocal
    from app.models import UserMemory
    from sqlalchemy.dialects.postgresql import insert

    async with AsyncSessionLocal() as db:
        stmt = insert(UserMemory).values(
            user_id=state["user_id"],
            memory_key="last_agent_used",
            memory_value={"intent": state.get("intent", "general.unknown")},
            source="inferred",
        ).on_conflict_do_update(
            index_elements=["user_id", "memory_key"],
            set_={"memory_value": {"intent": state.get("intent", "general.unknown")},
                  "updated_at": func.now()},
        )
        await db.execute(stmt)
        await db.commit()
    return {}


# ── Node 5: Final respond ────────────────────────────────────────────────────

async def respond_node(state: AgentState) -> AgentState:
    if state.get("response"):
        return {
            "messages": [
                *state.get("messages", []),
                AIMessage(content=state["response"]),
            ]
        }
    return {}


# ── Build the graph ───────────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    """Build the simplified StateGraph (uncompiled).

    New flow:
      scope_gate → execute_node → (eval_node) → save_memory → respond → END
    """
    graph = StateGraph(AgentState)

    graph.add_node("scope_gate",    scope_gate_node)
    graph.add_node("execute_node",  execute_node)
    graph.add_node("eval_node",     eval_node)
    graph.add_node("save_memory",   save_memory_node)
    graph.add_node("respond",       respond_node)

    graph.set_entry_point("scope_gate")

    graph.add_conditional_edges("scope_gate", route_after_scope_gate, {
        "execute_node": "execute_node",
        "respond":      "respond",
    })

    graph.add_conditional_edges("execute_node", route_after_execute, {
        "eval_node":   "eval_node",
        "save_memory": "save_memory",
    })

    graph.add_conditional_edges("eval_node", route_after_eval, {
        "execute_node": "execute_node",
        "save_memory":  "save_memory",
    })

    graph.add_edge("save_memory", "respond")
    graph.add_edge("respond",     END)

    return graph


# Default in-memory compiled workflow.
workflow = _build_graph().compile(checkpointer=MemorySaver())

_pool: AsyncConnectionPool | None = None
_checkpointer: AsyncPostgresSaver | None = None


def _psycopg_conn_string() -> str:
    """Convert the SQLAlchemy/asyncpg URL to a plain psycopg DSN."""
    url = str(settings.DATABASE_URL)
    return url.replace("postgresql+asyncpg://", "postgresql://")


async def init_workflow() -> None:
    """Swap the in-memory workflow for a PostgreSQL-persisted one."""
    global workflow, _pool, _checkpointer
    if _pool is not None:
        return

    _pool = AsyncConnectionPool(
        conninfo=_psycopg_conn_string(),
        max_size=settings.DB_POOL_SIZE,
        kwargs={"autocommit": True, "prepare_threshold": 0},
        open=False,
    )
    await _pool.open()
    _checkpointer = AsyncPostgresSaver(_pool)
    await _checkpointer.setup()
    workflow = _build_graph().compile(checkpointer=_checkpointer)


async def close_workflow() -> None:
    """Close the checkpoint connection pool on FastAPI shutdown."""
    global _pool, _checkpointer
    if _pool is not None:
        await _pool.close()
        _pool = None
        _checkpointer = None


async def run_workflow(user_ctx: dict, query: str, session_id: str | None = None) -> AgentState:
    sid = session_id or str(uuid.uuid4())
    state = initial_state(user_ctx, query, session_id=sid)

    config = {
        "configurable": {"thread_id": sid},
        "recursion_limit": 12,
    }
    final_state = await workflow.ainvoke(state, config=config)
    return final_state


async def run_workflow_stream(
    user_ctx: dict, query: str, session_id: str | None = None
):
    """Async generator that yields streaming events from the workflow.

    Yields tuples of (event_type, payload):
      - ("token", str)            — a content token from the execute LLM
      - ("done",  dict)           — final metadata (session_id, intent, etc.)
      - ("error", str)            — error message
    """
    sid = session_id or str(uuid.uuid4())
    state = initial_state(user_ctx, query, session_id=sid)
    config = {
        "configurable": {"thread_id": sid},
        "recursion_limit": 12,
    }

    final_state: dict = {}
    try:
        async for event in workflow.astream_events(state, config=config, version="v2"):
            kind = event.get("event")
            tags = event.get("tags") or []

            if kind == "on_chat_model_stream" and "execute_llm" in tags:
                chunk = event["data"].get("chunk")
                if chunk is None:
                    continue
                content = getattr(chunk, "content", "") or ""
                if isinstance(content, str) and content:
                    yield ("token", content)

            elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                output = event["data"].get("output") or {}
                if isinstance(output, dict):
                    final_state.update(output)
    except Exception as exc:  # noqa: BLE001
        yield ("error", str(exc))
        return

    yield (
        "done",
        {
            "session_id": final_state.get("session_id", sid),
            "intent": final_state.get("intent", "general.unknown"),
            "agent_used": final_state.get("agent_used"),
            "approval_required": final_state.get("approval_required", False),
            "response": final_state.get("response", ""),
            "metadata": final_state.get("metadata", {}),
        },
    )