import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager

import json

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import structlog

from app.config import settings
from app.database import AsyncSessionLocal, check_db_connection
from app.graph.workflow import (
    close_workflow,
    init_workflow,
    run_workflow,
    run_workflow_stream,
)
from app.middleware import (
    RequestLoggingMiddleware, 
    RateLimitMiddleware, 
    setup_redis, 
    close_redis, 
    enrich_request, 
    load_role_permissions
)
from app.api.routes.auth import router as auth_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.self_service import router as self_service_router


logger = structlog.get_logger("app.lifecycle")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the FastAPI application."""
    try:
        async with AsyncSessionLocal() as db:
            await load_role_permissions(db)
        logger.info("rbac_loaded")
    except Exception as e:
        logger.warning("rbac_load_skipped", error=str(e), hint="RBAC permissions not loaded — admin role bypasses all checks")

    try:
        await setup_redis()
        logger.info("redis_connected")
    except Exception as e:
        logger.warning("redis_skipped", error=str(e), hint="Rate limiting disabled — Redis not available")

    try:
        await init_workflow()
        logger.info("workflow_checkpointer_ready", backend="postgres")
    except Exception as e:
        logger.warning(
            "workflow_checkpointer_fallback",
            error=str(e),
            hint="Chat history will not persist — using in-memory checkpointer",
        )

    logger.info("startup_complete", app=settings.APP_NAME, env=settings.APP_ENV)
        
    yield
    

    try:
        await close_workflow()
    except Exception:
        pass
    try:
        await close_redis()
    except Exception:
        pass
    logger.info("shutdown_initiated", app=settings.APP_NAME)


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
    for dev_origin in ["http://localhost:3000", "http://127.0.0.1:3000", "http://172.16.21.161:3000"]:
        if dev_origin not in _origins:
            _origins.append(dev_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router)
app.include_router(approvals_router)
app.include_router(self_service_router)



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


@app.post("/api/v1/chat/stream", tags=["Chat"])
async def chat_stream(
    body: ChatRequest,
    user_ctx: dict = Depends(enrich_request),
):
    """Streaming version of /api/v1/chat — emits Server-Sent Events.

    Event format: each event is a JSON object on a single SSE `data:` line:
      {"type": "token", "content": "..."}    incremental text token
      {"type": "done",  "session_id": ...,
                        "intent": ..., "approval_required": ...,
                        "metadata": {...}}    final event
      {"type": "error", "message": "..."}    error event
    """

    async def event_generator():
        try:
            async for kind, payload in run_workflow_stream(
                user_ctx=user_ctx,
                query=body.message,
                session_id=body.session_id,
            ):
                if kind == "token":
                    yield f"data: {json.dumps({'type': 'token', 'content': payload})}\n\n"
                elif kind == "done":
                    payload_out = {"type": "done", **payload}
                    yield f"data: {json.dumps(payload_out)}\n\n"
                elif kind == "error":
                    yield f"data: {json.dumps({'type': 'error', 'message': payload})}\n\n"
        except Exception as e:  # noqa: BLE001
            logger.error("chat_stream_error", error=str(e), session_id=body.session_id)
            yield f"data: {json.dumps({'type': 'error', 'message': 'Stream failed.'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        },
    )

@app.get("/api/v1/chat/history/{session_id}", tags=["Chat"])
async def get_history(
    session_id: str,
    user_ctx: dict = Depends(enrich_request),
):
    """Retrieve chat history for a session."""
    from app.graph.workflow import get_chat_history
    history = await get_chat_history(session_id)
    return {"messages": history}