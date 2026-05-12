from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# ── Configure structlog (once at module load) ─────────────────────────────────
# This pipeline turns every log event into a JSON dict with ISO-8601 timestamps.

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,          # pull vars set in other coroutines
        structlog.processors.TimeStamper(fmt="iso"),      # "timestamp": "2026-05-05T12:00:00Z"
        structlog.processors.add_log_level,               # "level": "info"
        structlog.processors.StackInfoRenderer(),         # add stack trace if requested
        structlog.processors.format_exc_info,             # format exceptions nicely
        structlog.processors.UnicodeDecoder(),            # bytes → str
        structlog.processors.JSONRenderer(),              # final output as JSON
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),  # allow all levels
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),           # writes to stdout
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Measures wall-clock latency of every request and emits a single
    structured log line after the response is sent.

    Key design decisions:
      1. We generate a `request_id` (UUID4) and attach it as a response
         header (`X-Request-ID`).  Downstream services can propagate this
         for distributed tracing.
      2. We catch *all* unhandled exceptions so that 500s are still logged
         with the traceback attached — then we re-raise so FastAPI's
         default exception handler can return a proper error response.
      3. Health-check endpoints (/health) are logged at DEBUG to avoid
         flooding logs in environments with aggressive liveness probes.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # ── 1. Generate correlation ID ────────────────────────────────────
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # ── 2. Start the clock ────────────────────────────────────────────
        start_time = time.perf_counter()

        # Bind request-scoped fields into structlog context so that any log
        # emitted inside the endpoint handler also carries them.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        status_code = 500  # default in case call_next explodes
        try:
            response = await call_next(request)
            status_code = response.status_code

            # Attach correlation header to response
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            # ── 3. Log the 500 with full traceback ────────────────────────
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "unhandled_exception",
                status_code=500,
                duration_ms=duration_ms,
                exc_info=exc,
            )
            raise  # re-raise so FastAPI returns its standard 500 response

        finally:
            # ── 4. Emit the structured log line ───────────────────────────
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Downgrade health-check spam to DEBUG
            log_method = logger.debug if request.url.path == "/health" else logger.info
            log_method(
                "request_completed",
                status_code=status_code,
                duration_ms=duration_ms,
            )
