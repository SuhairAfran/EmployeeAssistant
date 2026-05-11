"""
Auth Routes
===========
Real email/password login backed by bcrypt + JWT.

Endpoints:
  POST /api/v1/auth/login   → exchange email+password for an access token
  GET  /api/v1/auth/me      → return the current authenticated user
  POST /api/v1/auth/logout  → no-op for stateless JWT (client clears token)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import create_access_token, get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

# Bcrypt context — schemes match the seeded password hash format ($2b$).
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Schemas ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    employee_id: str
    email: str
    full_name: str
    role: str
    department_id: str | None
    manager_id: str | None
    designation: str | None
    gender: str
    is_married: bool


TokenResponse.model_rebuild()


def _user_to_out(user: User) -> UserOut:
    return UserOut(
        id=str(user.id),
        employee_id=user.employee_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        department_id=str(user.department_id) if user.department_id else None,
        manager_id=str(user.manager_id) if user.manager_id else None,
        designation=user.designation,
        gender=user.gender,
        is_married=user.is_married,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Validate credentials and return a JWT bearer token."""
    from app.config import settings

    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    try:
        password_ok = pwd_context.verify(body.password, user.password_hash)
    except Exception:
        password_ok = False

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(
        user_id=str(user.id),
        role=user.role.value,
        email=user.email,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        user=_user_to_out(user),
    )


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    """Return the user identified by the Authorization bearer token."""
    return _user_to_out(user)


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Stateless JWT logout — client must discard the token."""
    return {"status": "ok", "detail": "Token discarded by client."}
