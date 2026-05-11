"""
Self-Service API
================
Read-only endpoints powering the dashboard and self-service pages.

Endpoints:
    GET /api/v1/me/leave-balance        → current-year balances
    GET /api/v1/me/leave-history        → own leave requests
    GET /api/v1/me/it-tickets           → own IT tickets
    GET /api/v1/me/team/leaves-today    → team members on leave today (manager-aware)
    GET /api/v1/me/recent-activity      → recent leaves+tickets, mixed
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import get_current_user
from app.models import (
    ITTicket, LeaveBalance, LeaveRequest, LeaveStatus, User, UserRole,
)

router = APIRouter(prefix="/api/v1/me", tags=["Self-Service"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class LeaveBalanceItem(BaseModel):
    leave_type: str
    entitled_days: float
    used_days: float
    pending_days: float
    carried_over: float
    available_days: float


class LeaveHistoryItem(BaseModel):
    id: str
    leave_type: str
    start_date: str
    end_date: str
    business_days: float
    status: str
    reason: str | None
    applied_at: datetime
    reviewer_note: str | None


class ITTicketItem(BaseModel):
    id: str
    ticket_no: str
    category: str
    subject: str
    priority: str
    status: str
    created_at: datetime
    resolution: str | None


class TeamLeaveTodayItem(BaseModel):
    user_id: str
    full_name: str
    designation: str | None
    leave_type: str
    end_date: str


class ActivityItem(BaseModel):
    kind: str  # "leave" | "ticket"
    title: str
    status: str
    when: datetime


# ── Helpers ───────────────────────────────────────────────────────────────────

def _eligible_leave_types(user: User) -> set[str]:
    """Return the set of leave types this user is eligible for (used to filter
    out maternity rows for males, etc.)."""
    eligible = {"earned", "sick", "bereavement", "unpaid", "compensatory"}
    gender = (user.gender or "").lower()
    if gender == "female":
        eligible |= {"maternity", "miscarriage"}
    if gender == "male" and user.is_married:
        eligible.add("paternity")
    return eligible


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/leave-balance", response_model=list[LeaveBalanceItem])
async def my_leave_balance(
    year: int = Query(default_factory=lambda: date.today().year),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LeaveBalanceItem]:
    """Current-year leave balances filtered by eligibility."""
    result = await db.execute(
        select(LeaveBalance).where(and_(
            LeaveBalance.user_id == user.id,
            LeaveBalance.year == year,
        ))
    )
    balances = result.scalars().all()
    eligible = _eligible_leave_types(user)
    items: list[LeaveBalanceItem] = []
    for b in balances:
        lt = b.leave_type.value
        if lt not in eligible:
            continue
        items.append(LeaveBalanceItem(
            leave_type=lt,
            entitled_days=float(b.entitled_days),
            used_days=float(b.used_days),
            pending_days=float(b.pending_days),
            carried_over=float(b.carried_over),
            available_days=float(b.available_days),
        ))
    return items


@router.get("/leave-history", response_model=list[LeaveHistoryItem])
async def my_leave_history(
    limit: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LeaveHistoryItem]:
    result = await db.execute(
        select(LeaveRequest)
        .where(LeaveRequest.user_id == user.id)
        .order_by(LeaveRequest.applied_at.desc())
        .limit(limit)
    )
    return [
        LeaveHistoryItem(
            id=str(lr.id),
            leave_type=lr.leave_type.value,
            start_date=lr.start_date.isoformat(),
            end_date=lr.end_date.isoformat(),
            business_days=float(lr.business_days),
            status=lr.status.value,
            reason=lr.reason,
            applied_at=lr.applied_at,
            reviewer_note=lr.reviewer_note,
        )
        for lr in result.scalars().all()
    ]


@router.get("/it-tickets", response_model=list[ITTicketItem])
async def my_it_tickets(
    limit: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ITTicketItem]:
    result = await db.execute(
        select(ITTicket)
        .where(ITTicket.user_id == user.id)
        .order_by(ITTicket.created_at.desc())
        .limit(limit)
    )
    return [
        ITTicketItem(
            id=str(t.id),
            ticket_no=t.ticket_no,
            category=t.category.value,
            subject=t.subject,
            priority=t.priority.value,
            status=t.status.value,
            created_at=t.created_at,
            resolution=t.resolution,
        )
        for t in result.scalars().all()
    ]


@router.get("/team/leaves-today", response_model=list[TeamLeaveTodayItem])
async def team_leaves_today(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TeamLeaveTodayItem]:
    """For managers: team members on approved leave today.
    For employees: anyone in their department on approved leave today.
    """
    today = date.today()

    if user.role in (UserRole.manager, UserRole.admin, UserRole.hr_team):
        cohort_q = select(User).where(User.manager_id == user.id) \
            if user.role == UserRole.manager \
            else select(User).where(User.is_active.is_(True))
    else:
        if user.department_id is None:
            return []
        cohort_q = select(User).where(and_(
            User.department_id == user.department_id,
            User.id != user.id,
            User.is_active.is_(True),
        ))

    cohort = (await db.execute(cohort_q)).scalars().all()
    if not cohort:
        return []

    user_map = {str(u.id): u for u in cohort}

    leaves_q = await db.execute(
        select(LeaveRequest).where(and_(
            LeaveRequest.user_id.in_(list(user_map.keys())),
            LeaveRequest.status == LeaveStatus.approved,
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today,
        ))
    )

    items: list[TeamLeaveTodayItem] = []
    for lr in leaves_q.scalars().all():
        emp = user_map.get(str(lr.user_id))
        if not emp:
            continue
        items.append(TeamLeaveTodayItem(
            user_id=str(emp.id),
            full_name=emp.full_name,
            designation=emp.designation,
            leave_type=lr.leave_type.value,
            end_date=lr.end_date.isoformat(),
        ))
    return items


@router.get("/recent-activity", response_model=list[ActivityItem])
async def recent_activity(
    limit: int = Query(default=8, ge=1, le=30),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ActivityItem]:
    """Mixed feed of recent leaves + tickets for the dashboard."""
    items: list[ActivityItem] = []

    leaves = (await db.execute(
        select(LeaveRequest)
        .where(LeaveRequest.user_id == user.id)
        .order_by(LeaveRequest.applied_at.desc())
        .limit(limit)
    )).scalars().all()
    for lr in leaves:
        items.append(ActivityItem(
            kind="leave",
            title=f"{lr.leave_type.value.capitalize()} leave · {lr.start_date} → {lr.end_date}",
            status=lr.status.value,
            when=lr.applied_at,
        ))

    tickets = (await db.execute(
        select(ITTicket)
        .where(ITTicket.user_id == user.id)
        .order_by(ITTicket.created_at.desc())
        .limit(limit)
    )).scalars().all()
    for t in tickets:
        items.append(ActivityItem(
            kind="ticket",
            title=f"{t.ticket_no} · {t.subject}",
            status=t.status.value,
            when=t.created_at,
        ))

    items.sort(key=lambda x: x.when, reverse=True)
    return items[:limit]
