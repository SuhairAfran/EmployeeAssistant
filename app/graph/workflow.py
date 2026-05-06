"""
LangGraph Workflow — with GEPA pattern
======================================

Graph shape:
                      ┌─────────────┐
                      │ intent_node │  (cheap model: gpt-4o-mini)
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │  role_check │  (RBAC gate — no LLM needed)
                      └──────┬──────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         hr_agent       it_agent     finance_agent
              └──────────────┼──────────────┘
                             │
                      ┌──────▼──────┐
                  ┌───│  plan_node  │ ◄──── retry_critique
                  │   └──────┬──────┘
                  │          │ GEPA Plan
                  │   ┌──────▼──────┐
                  │   │ execute_node│  (tools + RAG)
                  │   └──────┬──────┘
                  │          │
                  │   ┌──────▼──────┐
                  │   │  eval_node  │  (GEPA Evaluate)
                  │   └──────┬──────┘
                  │          │ score < threshold → retry
                  └──────────┘
                             │ score ≥ threshold
                      ┌──────▼──────┐
                      │human_in_loop│  (interrupt() if approval needed)
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │email_notify │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │ save_memory │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │   respond   │
                      └─────────────┘
"""
from __future__ import annotations

import json
import time
import uuid
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt

from app.agents import AgentState, EvalScore, initial_state
from app.config import settings
from app.middleware import RBACViolation, rbac_guard
from app.models import UserRole


# ── LLM instances (dynamic routing) ──────────────────────────────────────────

def get_llm(model_key: str, temperature: float = settings.LLM_TEMPERATURE) -> ChatOpenAI:
    model_name = getattr(settings, f"LLM_{model_key.upper()}", settings.LLM_HR)
    
    # Optional kwargs for custom LLM proxy / disabling SSL verification
    kwargs = {}
    if not settings.OPENAI_VERIFY_SSL:
        import httpx
        kwargs["http_client"] = httpx.Client(verify=False)
        kwargs["http_async_client"] = httpx.AsyncClient(verify=False)
    
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL

    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=settings.OPENAI_API_KEY,
        **kwargs
    )


# ── Node 1: Intent detection ──────────────────────────────────────────────────

INTENT_SYSTEM = """You are an intent classifier for an enterprise HR/IT/Finance AI copilot.
Classify the user query into exactly ONE intent code. Respond ONLY with valid JSON.

Intent codes:
HR: hr.policy_query, hr.leave_apply, hr.leave_check_balance, hr.leave_view_history,
    hr.leave_cancel, hr.leave_check_status
IT: it.ticket_create, it.ticket_status, it.asset_request, it.ticket_view
Finance: finance.payslip_fetch, finance.reimbursement_submit, finance.reimbursement_status,
         finance.tax_query
Meta: general.greeting, general.unknown

Response format: {"intent": "<code>", "confidence": <0.0-1.0>}"""


async def intent_node(state: AgentState) -> AgentState:
    llm = get_llm("intent")
    result = await llm.ainvoke([
        SystemMessage(content=INTENT_SYSTEM),
        HumanMessage(content=state["raw_query"]),
    ])
    try:
        parsed = json.loads(result.content)
        return {
            "intent": parsed["intent"],
            "intent_confidence": parsed["confidence"],
            "llm_model": settings.LLM_INTENT,
        }
    except Exception:
        return {"intent": "general.unknown", "intent_confidence": 0.0}


# ── Node 2: Role / RBAC gate ──────────────────────────────────────────────────

INTENT_PERM_MAP: dict[str, str] = {
    "hr.policy_query":           "hr:policy:read",
    "hr.leave_apply":            "hr:leave:apply",
    "hr.leave_check_balance":    "hr:leave:view_own",
    "hr.leave_view_history":     "hr:leave:view_own",
    "hr.leave_cancel":           "hr:leave:apply",
    "hr.leave_check_status":     "hr:leave:view_own",
    "it.ticket_create":          "it:ticket:create",
    "it.ticket_status":          "it:ticket:view_own",
    "it.ticket_view":            "it:ticket:view_own",
    "it.asset_request":          "it:asset:request",
    "finance.payslip_fetch":     "finance:payslip:view_own",
    "finance.reimbursement_submit": "finance:claim:submit",
    "finance.reimbursement_status": "finance:claim:view_own",
    "finance.tax_query":         "finance:tax:view_own",
}

INTENT_ROUTE_MAP: dict[str, str] = {
    "hr":      "hr_agent",
    "it":      "it_agent",
    "finance": "finance_agent",
    "general": "unknown",
}


async def role_check_node(state: AgentState) -> AgentState:
    intent = state["intent"]
    required_perm = INTENT_PERM_MAP.get(intent)
    if required_perm:
        try:
            rbac_guard(state["user_role"], required_perm)
        except RBACViolation as e:
            return {
                "error": str(e),
                "response": "You don't have permission to perform this action.",
                "response_type": "error",
                "route_to": "unknown",
            }
    # Derive routing from intent prefix
    prefix = intent.split(".")[0]
    return {"route_to": INTENT_ROUTE_MAP.get(prefix, "unknown")}


def route_after_role_check(state: AgentState) -> Literal[
    "hr_agent", "it_agent", "finance_agent", "plan_node", "respond"
]:
    if state.get("error"):
        return "respond"
    return state.get("route_to", "respond")  # type: ignore


# ── Nodes 3a/3b/3c: Department context nodes ──────────────────────────────────
# These add department-specific context to the state before GEPA planning.

async def hr_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "hr_agent",
        "llm_model": settings.LLM_HR,
        "metadata": {**state.get("metadata", {}), "department": "hr"},
    }


async def it_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "it_agent",
        "llm_model": settings.LLM_IT,
        "metadata": {**state.get("metadata", {}), "department": "it"},
    }


async def finance_agent_node(state: AgentState) -> AgentState:
    return {
        "agent_used": "finance_agent",
        "llm_model": settings.LLM_FINANCE,
        "metadata": {**state.get("metadata", {}), "department": "finance"},
    }


# ── Node 4: GEPA — Plan ───────────────────────────────────────────────────────

PLAN_SYSTEM = """You are a planning agent for an enterprise AI system. Given a user request,
write a structured resolution plan BEFORE calling any tools.

Respond ONLY with JSON:
{
  "steps": ["step 1...", "step 2...", ...],
  "tools_needed": ["tool_name_1", "tool_name_2"],
  "reasoning": "why these steps in this order"
}

If a previous attempt failed, a critique will be provided. Adjust the plan accordingly."""


async def plan_node(state: AgentState) -> AgentState:
    llm = get_llm(state.get("agent_used", "hr").split("_")[0])

    messages = [SystemMessage(content=PLAN_SYSTEM)]

    # Include critique on retry
    if state.get("retry_critique"):
        messages.append(HumanMessage(
            content=f"Previous attempt failed. Critique:\n{state['retry_critique']}\n\n"
                    f"Original request: {state['raw_query']}"
        ))
    else:
        messages.append(HumanMessage(content=state["raw_query"]))

    result = await llm.ainvoke(messages)
    try:
        plan = json.loads(result.content)
        return {"plan": plan}
    except Exception:
        return {
            "plan": {
                "steps": ["Retrieve relevant information", "Generate response"],
                "tools_needed": [],
                "reasoning": "Fallback plan",
            }
        }


# ── Node 5: Execute (tools + RAG) ─────────────────────────────────────────────

EXECUTE_SYSTEM = """You are an enterprise AI assistant. Follow the plan and call the
appropriate tools to answer the user's request accurately.

User context:
- Name: {user_name}
- Role: {user_role}
- Department ID: {department_id}

Current plan:
{plan}

Be factual, cite sources when using documents, and respect the user's role permissions."""


async def execute_node(state: AgentState) -> AgentState:
    from app.tools import get_tools_for_intent

    llm = get_llm(state.get("agent_used", "hr").split("_")[0])
    tools = get_tools_for_intent(state["intent"], state["user_role"])
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    plan_text = "\n".join(
        f"{i+1}. {s}" for i, s in enumerate(state.get("plan", {}).get("steps", []))
    )

    messages = [
        SystemMessage(content=EXECUTE_SYSTEM.format(
            user_name=state["user_name"],
            user_role=state["user_role"].value,
            department_id=state.get("department_id", "N/A"),
            plan=plan_text,
        )),
        *state.get("messages", []),
        HumanMessage(content=state["raw_query"]),
    ]

    start = time.time()
    result = await llm_with_tools.ainvoke(messages)
    latency = int((time.time() - start) * 1000)

    tool_calls = []
    
    # ── NEW: Track state updates requested by tools ──
    approval_required = False
    approval_entity_type = None
    approval_entity_id = None
    email_triggered = False
    email_recipients = []
    email_subject = None
    email_body = None

    if hasattr(result, "tool_calls") and result.tool_calls:
        for tc in result.tool_calls:
            tool_fn = next((t for t in tools if t.name == tc["name"]), None)
            if tool_fn:
                try:
                    tool_result = await tool_fn.ainvoke(tc["args"])
                    tool_calls.append({"name": tc["name"], "args": tc["args"], "result": tool_result})
                    
                    # ── NEW: Parse tool outputs to trigger graph nodes ──
                    if isinstance(tool_result, dict):
                        if tool_result.get("approval_required"):
                            approval_required = True
                            
                            # Dynamically determine the entity type based on what ID was returned
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
                    return {"error": str(e), "response": str(e), "response_type": "error"}

    # Compile the final state updates
    state_update = {
        "messages": [*state.get("messages", []), HumanMessage(content=state["raw_query"]), result],
        "tool_calls": tool_calls,
        "response": result.content if isinstance(result.content, str) else str(result.content),
        "latency_ms": latency,
    }

    # ── NEW: Inject parsed variables back into the AgentState ──
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


# ── Node 6: GEPA — Evaluate ───────────────────────────────────────────────────

EVAL_SYSTEM = """You are a quality evaluator for an enterprise AI system.
Score the agent's response on four dimensions (0.0–1.0 each):
  - relevance: does the response directly address the user's query?
  - completeness: does it provide all needed information?
  - rbac_compliant: does it respect the user's role and not expose unauthorized data?
  - overall: weighted average

Respond ONLY with JSON:
{
  "score": <float>,
  "relevance": <float>,
  "completeness": <float>,
  "rbac_compliant": <bool>,
  "critique": "specific feedback if score < 0.80, empty string otherwise"
}"""


async def eval_node(state: AgentState) -> AgentState:
    if state.get("error"):
        # Don't evaluate error states
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


def route_after_eval(state: AgentState) -> Literal["plan_node", "human_in_loop"]:
    score = state.get("eval_score", {}).get("score", 1.0)
    retry_count = state.get("retry_count", 0)

    if score < settings.GEPA_EVAL_THRESHOLD and retry_count < settings.GEPA_MAX_RETRIES:
        return "plan_node"   # loop back with critique
    return "human_in_loop"


# ── Node 7: Human-in-loop ─────────────────────────────────────────────────────

async def human_in_loop_node(state: AgentState) -> AgentState:
    """
    If approval is required, pause the graph via interrupt().
    The graph resumes when the approver's decision is injected
    via graph.invoke(Command(resume={"decision": "approved", "note": "..."})).
    """
    if not state.get("approval_required"):
        return {}

    # Pause here — LangGraph serialises state and waits
    decision_input = interrupt({
        "message": f"Approval required for {state.get('approval_entity_type')}",
        "entity_id": state.get("approval_entity_id"),
        "requested_by": state["user_name"],
        "request_summary": state["raw_query"],
    })

    return {
        "approval_decision": decision_input.get("decision"),
        "approval_note": decision_input.get("note"),
    }


# ── Node 8: Email notification ────────────────────────────────────────────────

async def email_notify_node(state: AgentState) -> AgentState:
    if not state.get("email_triggered"):
        return {}

    from app.tools.email_tools import send_email_via_power_automate
    await send_email_via_power_automate(
        recipients=state["email_recipients"],
        subject=state.get("email_subject", ""),
        body=state.get("email_body", ""),
    )
    return {}


# ── Node 9: Save memory ───────────────────────────────────────────────────────

async def save_memory_node(state: AgentState) -> AgentState:
    from app.database import AsyncSessionLocal
    from app.models import UserMemory
    from sqlalchemy.dialects.postgresql import insert

    async with AsyncSessionLocal() as db:
        stmt = insert(UserMemory).values(
            user_id=state["user_id"],
            memory_key="last_agent_used",
            memory_value={"agent": state.get("agent_used"), "intent": state["intent"]},
            source="inferred",
        ).on_conflict_do_update(
            index_elements=["user_id", "memory_key"],
            set_={"memory_value": {"agent": state.get("agent_used"), "intent": state["intent"]},
                  "updated_at": "now()"},
        )
        await db.execute(stmt)
        await db.commit()
    return {}


# ── Node 10: Final respond ────────────────────────────────────────────────────

async def respond_node(state: AgentState) -> AgentState:
    """Append the final AI response to the message history."""
    if state.get("response"):
        return {
            "messages": [
                *state.get("messages", []),
                AIMessage(content=state["response"]),
            ]
        }
    return {}


# ── Build the graph ───────────────────────────────────────────────────────────

def build_workflow() -> StateGraph:
    graph = StateGraph(AgentState)

    # Register all nodes
    graph.add_node("intent_node",       intent_node)
    graph.add_node("role_check",        role_check_node)
    graph.add_node("hr_agent",          hr_agent_node)
    graph.add_node("it_agent",          it_agent_node)
    graph.add_node("finance_agent",     finance_agent_node)
    graph.add_node("plan_node",         plan_node)
    graph.add_node("execute_node",      execute_node)
    graph.add_node("eval_node",         eval_node)
    graph.add_node("human_in_loop",     human_in_loop_node)
    graph.add_node("email_notify",      email_notify_node)
    graph.add_node("save_memory",       save_memory_node)
    graph.add_node("respond",           respond_node)

    # Entry
    graph.set_entry_point("intent_node")

    # Linear edges
    graph.add_edge("intent_node", "role_check")
    graph.add_conditional_edges("role_check", route_after_role_check, {
        "hr_agent":      "hr_agent",
        "it_agent":      "it_agent",
        "finance_agent": "finance_agent",
        "plan_node":     "plan_node",
        "respond":       "respond",
    })

    # Department nodes → plan
    for dept in ("hr_agent", "it_agent", "finance_agent"):
        graph.add_edge(dept, "plan_node")

    graph.add_edge("plan_node",    "execute_node")
    graph.add_edge("execute_node", "eval_node")

    # GEPA conditional: retry or proceed
    graph.add_conditional_edges("eval_node", route_after_eval, {
        "plan_node":     "plan_node",    # retry with critique
        "human_in_loop": "human_in_loop",
    })

    graph.add_edge("human_in_loop", "email_notify")
    graph.add_edge("email_notify",  "save_memory")
    graph.add_edge("save_memory",   "respond")
    graph.add_edge("respond",       END)

    # Checkpointer enables interrupt() + resume
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer, interrupt_before=["human_in_loop"])


# ── Singleton graph instance ──────────────────────────────────────────────────

workflow = build_workflow()


async def run_workflow(user_ctx: dict, query: str, session_id: str | None = None) -> AgentState:
    """
    Entry point for the chat API route.

    Args:
        user_ctx: dict from enrich_request() dependency
        query:    raw user message
        session_id: existing session ID (for multi-turn) or None for new session

    Returns:
        Final AgentState with 'response' populated.
    """
    sid = session_id or str(uuid.uuid4())
    state = initial_state(user_ctx, query, session_id=sid)

    config = {"configurable": {"thread_id": sid}}
    final_state = await workflow.ainvoke(state, config=config)
    return final_state