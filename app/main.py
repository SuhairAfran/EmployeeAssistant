"""
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import structlog

from app.config import settings
from app.database import AsyncSessionLocal, check_db_connection
from app.graph.workflow import run_workflow
from app.middleware import RequestLoggingMiddleware, enrich_request, load_role_permissions

logger = structlog.get_logger("app.lifecycle")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with AsyncSessionLocal() as db:
        await load_role_permissions(db)   # cache RBAC in memory
    logger.info("startup_complete", rbac="loaded", app=settings.APP_NAME, env=settings.APP_ENV)
    yield
    # Shutdown
    logger.info("shutdown")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured request logging — must be added AFTER CORS so it wraps all
# requests as the outermost middleware (Starlette processes last-added first).
app.add_middleware(RequestLoggingMiddleware)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    db_ok = await check_db_connection()
    return {"status": "ok" if db_ok else "degraded", "db": db_ok}


# ── Chat endpoint ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None    # omit to start a new session


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    agent_used: str | None
    approval_required: bool
    metadata: dict


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user_ctx: dict = Depends(enrich_request),
):
    """
    Main conversational endpoint.
    Runs the full LangGraph workflow (intent → RBAC → GEPA → response).
    """
    final_state = await run_workflow(
        user_ctx=user_ctx,
        query=body.message,
        session_id=body.session_id,
    )

    return ChatResponse(
        response=final_state.get("response", "I'm sorry, I couldn't process that request."),
        session_id=final_state["session_id"],
        intent=final_state.get("intent", "general.unknown"),
        agent_used=final_state.get("agent_used"),
        approval_required=final_state.get("approval_required", False),
        metadata=final_state.get("metadata", {}),
    )


# ── Approval callback endpoint ────────────────────────────────────────────────

class ApprovalCallback(BaseModel):
    session_id: str
    decision:   str    # 'approved' | 'rejected'
    note:       str = ""


@app.post("/api/v1/approve")
async def handle_approval(
    body: ApprovalCallback,
    user_ctx: dict = Depends(enrich_request),
):
    """
    Called by the manager/approver UI to resume a paused LangGraph workflow.
    Injects the decision back into the interrupted graph via Command.
    """
    from langgraph.types import Command

    config = {"configurable": {"thread_id": body.session_id}}
    await run_workflow.__wrapped__.ainvoke(   # type: ignore
        Command(resume={"decision": body.decision, "note": body.note}),
        config=config,
    )
    return {"status": "ok", "decision": body.decision}