from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

# Import your graph and database components
from app.config import settings
from app.database import AsyncSessionLocal, check_db_connection
from app.graph.workflow import run_workflow, workflow
from app.middleware import (
    RequestLoggingMiddleware, 
    RateLimitMiddleware, 
    setup_redis, 
    close_redis, 
    enrich_request, 
    load_role_permissions
)

# Set up structured logging
logger = structlog.get_logger("app.lifecycle")

# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the FastAPI application."""
    # Startup: Load RBAC permissions (fail-open for local dev)
    try:
        async with AsyncSessionLocal() as db:
            await load_role_permissions(db)
        logger.info("rbac_loaded")
    except Exception as e:
        logger.warning("rbac_load_skipped", error=str(e), hint="RBAC permissions not loaded — admin role bypasses all checks")

    # Redis: optional for local dev (rate limiter will fail-open)
    try:
        await setup_redis()
        logger.info("redis_connected")
    except Exception as e:
        logger.warning("redis_skipped", error=str(e), hint="Rate limiting disabled — Redis not available")

    logger.info("startup_complete", app=settings.APP_NAME, env=settings.APP_ENV)
        
    yield  # The app is running
    
    # Shutdown
    try:
        await close_redis()
    except Exception:
        pass
    logger.info("shutdown_initiated", app=settings.APP_NAME)


# ── App Initialization ────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="LangGraph-powered AI backend for HR, IT, and Finance.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

# ── Middlewares ───────────────────────────────────────────────────────────────

# CORS Middleware for frontend communication
# Normalize origins: handle both AnyHttpUrl objects and plain strings
_origins = []
for o in settings.ALLOWED_ORIGINS:
    origin_str = str(o).rstrip("/")
    _origins.append(origin_str)

# Always allow localhost:3000 in development
if settings.DEBUG:
    for dev_origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
        if dev_origin not in _origins:
            _origins.append(dev_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting via Redis Token Bucket
app.add_middleware(RateLimitMiddleware)

# Structured request logging
app.add_middleware(RequestLoggingMiddleware)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    agent_used: str | None
    approval_required: bool
    metadata: dict

class ApprovalCallback(BaseModel):
    session_id: str
    decision: str
    note: str = ""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """System health check endpoint."""
    try:
        db_ok = await check_db_connection()
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "db": db_ok,
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "debug": settings.DEBUG,
    }


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    body: ChatRequest,
    user_ctx: dict = Depends(enrich_request),
):
    """Main conversational endpoint."""
    try:
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error("chat_endpoint_error", error=str(e), session_id=body.session_id)
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")


@app.post("/api/v1/approve", tags=["Approvals"])
async def handle_approval(
    body: ApprovalCallback,
    user_ctx: dict = Depends(enrich_request),
):
    """Resumes a paused LangGraph workflow after a manager makes an approval decision."""
    from langgraph.types import Command
    from app.models import UserRole
    
    if user_ctx.get("user_role") not in [UserRole.manager, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Only managers or admins can perform approvals.")

    try:
        config = {"configurable": {"thread_id": body.session_id}}
        
        await workflow.ainvoke(
            Command(resume={"decision": body.decision, "note": body.note}),
            config=config,
        )
        return {"status": "ok", "decision": body.decision, "session_id": body.session_id}
        
    except Exception as e:
        logger.error("approval_endpoint_error", error=str(e), session_id=body.session_id)
        raise HTTPException(status_code=500, detail="Failed to resume workflow after approval.")