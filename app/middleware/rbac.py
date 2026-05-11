"""
RBAC Middleware
==============
Two-layer enforcement:
  Layer 1 — FastAPI dependency (HTTP): validates JWT and injects current_user
  Layer 2 — Agent-level guard (LangGraph): checked inside tool/retrieval nodes

Usage in FastAPI routes:
    @router.get("/leaves")
    async def list_leaves(user = Depends(require_permission("hr:leave:view_all"))):
        ...

Usage in LangGraph tool nodes:
    from app.middleware.rbac import rbac_guard
    rbac_guard(state["user_role"], "it:ticket:view_all")
"""
from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Permission, RolePermission, User, UserRole

# ── Static role → permission map (cached at startup) ─────────────────────────
# Loaded from DB once via load_role_permissions(); used for fast in-memory checks.
ROLE_PERMISSIONS: dict[UserRole, set[str]] = {}


async def load_role_permissions(db: AsyncSession) -> None:
    """Call once at FastAPI startup to cache all role permissions."""
    result = await db.execute(
        select(RolePermission.role, Permission.code)
        .join(Permission, RolePermission.perm_id == Permission.id)
    )
    for role, code in result:
        ROLE_PERMISSIONS.setdefault(role, set()).add(code)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(user_id: str, role: str, email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# ── FastAPI dependencies ───────────────────────────────────────────────────────

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT, load user from DB, verify active status. Supports X-Mock-Role in DEBUG mode."""
    # 1. Check for mock header in DEBUG mode
    if settings.DEBUG and "x-mock-role" in request.headers:
        role_str = request.headers.get("x-mock-role", "employee")
        try:
            role_enum = UserRole(role_str)
        except ValueError:
            role_enum = UserRole.employee
            
        import uuid
        from sqlalchemy.orm import make_transient

        mock_user = User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111") if role_enum == UserRole.manager else uuid.UUID("22222222-2222-2222-2222-222222222222"),
            employee_id=f"MOCK-{role_enum.value.upper()[:3]}-001",
            email=f"mock_{role_enum.value}@company.com",
            full_name=f"Mock {role_enum.value.capitalize()}",
            password_hash="mock_not_a_real_hash",
            role=role_enum,
            department_id=None,
            manager_id=None,
            is_active=True,
            preferred_lang="en"
        )
        # Detach from any SA session so it's never accidentally flushed to DB
        make_transient(mock_user)
        return mock_user

    # 2. Normal JWT flow
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad token payload")

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def require_permission(perm_code: str):
    """FastAPI dependency factory — raises 403 if user lacks the permission."""
    async def _check(user: User = Depends(get_current_user)) -> User:
        if not _has_permission(user.role, perm_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{perm_code}' required",
            )
        return user
    return _check


def require_role(*roles: UserRole):
    """FastAPI dependency — requires one of the given roles."""
    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: one of {[r.value for r in roles]}",
            )
        return user
    return _check


# ── Agent-level guard (LangGraph nodes / tools) ───────────────────────────────

class RBACViolation(PermissionError):
    """Raised inside LangGraph tool nodes when RBAC check fails."""
    def __init__(self, role: UserRole, perm_code: str):
        super().__init__(f"Role '{role.value}' lacks permission '{perm_code}'")
        self.role = role
        self.perm_code = perm_code


def rbac_guard(role: UserRole, perm_code: str) -> None:
    """
    Raise RBACViolation if the role lacks the permission.
    Use this inside LangGraph tool nodes (not FastAPI routes).

    Example:
        async def apply_leave_tool(state: AgentState) -> AgentState:
            rbac_guard(state["user_role"], "hr:leave:apply")
            ...
    """
    if not _has_permission(role, perm_code):
        raise RBACViolation(role, perm_code)


def _has_permission(role: UserRole, perm_code: str) -> bool:
    """Check against in-memory ROLE_PERMISSIONS map. Admin always passes."""
    if role == UserRole.admin:
        return True
    return perm_code in ROLE_PERMISSIONS.get(role, set())


# ── Rate limiting middleware ───────────────────────────────────────────────────

class RateLimitMiddleware:
    """
    Simple in-process token bucket per user (not cluster-safe).
    For production, replace with Redis-backed sliding window.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self._buckets: dict[str, tuple[int, float]] = {}  # user_id → (tokens, last_refill)

    def check(self, user_id: str) -> None:
        now = time.time()
        tokens, last_refill = self._buckets.get(user_id, (self.rpm, now))

        # Refill tokens proportional to elapsed time
        elapsed = now - last_refill
        tokens = min(self.rpm, tokens + elapsed * (self.rpm / 60))

        if tokens < 1:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
                headers={"Retry-After": "5"},
            )

        self._buckets[user_id] = (tokens - 1, now)


rate_limiter = RateLimitMiddleware(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)


# ── Request enrichment (adds user context to every request) ──────────────────

async def enrich_request(request: Request, user: User = Depends(get_current_user)) -> dict:
    """
    Returns enriched context dict injected into the agent state.
    Attach via Depends() on chat endpoints.
    """
    rate_limiter.check(str(user.id))
    return {
        "user_id": str(user.id),
        "user_email": user.email,
        "user_name": user.full_name,
        "user_role": user.role,
        "department_id": str(user.department_id) if user.department_id else None,
        "manager_id": str(user.manager_id) if user.manager_id else None,
        "gender": user.gender,
        "is_married": user.is_married,
        "preferred_lang": user.preferred_lang,
    }