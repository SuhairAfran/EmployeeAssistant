"""
Approvals API
=============
In-app approval workflow for managers. Replaces email-based approvals.

Endpoints:
    GET  /api/v1/approvals/pending  → all pending requests for direct reports
    GET  /api/v1/approvals/count    → lightweight badge counter for sidebar polling
    POST /api/v1/approvals/decide   → approve / reject a request

Supported entity types: leave, asset, reimbursement (reimbursement is currently
unused since Finance is disabled, but the endpoint already supports it).
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import get_current_user
from app.models import (
    AssetRequest, LeaveBalance, LeaveRequest, LeaveStatus,
    Reimbursement, ReimbursementStatus, RequestStatus, User, UserRole,
)

router = APIRouter(prefix="/api/v1/approvals", tags=["Approvals"])


# ── Schemas ───────────────────────────────────────────────────────────────────

EntityType = Literal["leave", "asset", "reimbursement"]


class PendingItem(BaseModel):
    entity_type: EntityType
    entity_id: str
    employee_id: str
    employee_name: str
    employee_designation: str | None
    submitted_at: datetime
    # Type-specific fields (sparse — only the relevant ones populated)
    leave_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    business_days: float | None = None
    asset_type: str | None = None
    justification: str | None = None
    claim_no: str | None = None
    category: str | None = None
    amount: float | None = None
    currency: str | None = None
    description: str | None = None
    reason: str | None = None


class PendingResponse(BaseModel):
    count: int
    items: list[PendingItem]


class CountResponse(BaseModel):
    count: int


class DecideRequest(BaseModel):
    entity_type: EntityType
    entity_id: str
    decision: Literal["approve", "reject"]
    note: str = Field(default="", max_length=500)


class DecideResponse(BaseModel):
    status: str = "ok"
    entity_type: EntityType
    entity_id: str
    new_status: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_manager_role(role: UserRole) -> bool:
    return role in (UserRole.manager, UserRole.admin, UserRole.hr_team)


async def _direct_report_ids(db: AsyncSession, manager: User) -> list[str]:
    """Return user_ids who report directly to this manager.

    Admins and HR see EVERYONE — they can act on any pending request.
    Regular managers see only their direct reports.
    """
    if manager.role in (UserRole.admin, UserRole.hr_team):
        result = await db.execute(select(User.id).where(User.is_active.is_(True)))
        return [str(row[0]) for row in result.all()]

    result = await db.execute(
        select(User.id).where(
            and_(User.manager_id == manager.id, User.is_active.is_(True))
        )
    )
    return [str(row[0]) for row in result.all()]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/count", response_model=CountResponse)
async def pending_count(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CountResponse:
    """Lightweight count for sidebar badge polling. Returns 0 for non-managers."""
    if not _is_manager_role(user.role):
        return CountResponse(count=0)

    report_ids = await _direct_report_ids(db, user)
    if not report_ids:
        return CountResponse(count=0)

    leave_q = select(func.count(LeaveRequest.id)).where(
        and_(LeaveRequest.user_id.in_(report_ids), LeaveRequest.status == LeaveStatus.pending)
    )
    asset_q = select(func.count(AssetRequest.id)).where(
        and_(AssetRequest.user_id.in_(report_ids), AssetRequest.status == RequestStatus.pending)
    )

    leave_count = (await db.execute(leave_q)).scalar() or 0
    asset_count = (await db.execute(asset_q)).scalar() or 0

    return CountResponse(count=leave_count + asset_count)


@router.get("/pending", response_model=PendingResponse)
async def pending_approvals(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PendingResponse:
    """Return all pending approvals for the manager's direct reports."""
    if not _is_manager_role(user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers, admins, or HR can view approvals.",
        )

    report_ids = await _direct_report_ids(db, user)
    if not report_ids:
        return PendingResponse(count=0, items=[])

    # Map user_id → User row for cheap lookup
    users_q = await db.execute(select(User).where(User.id.in_(report_ids)))
    user_map: dict[str, User] = {str(u.id): u for u in users_q.scalars().all()}

    items: list[PendingItem] = []

    # --- Leave requests ---
    leave_q = await db.execute(
        select(LeaveRequest)
        .where(and_(
            LeaveRequest.user_id.in_(report_ids),
            LeaveRequest.status == LeaveStatus.pending,
        ))
        .order_by(LeaveRequest.applied_at.desc())
    )
    for lr in leave_q.scalars().all():
        emp = user_map.get(str(lr.user_id))
        if not emp:
            continue
        items.append(PendingItem(
            entity_type="leave",
            entity_id=str(lr.id),
            employee_id=str(emp.id),
            employee_name=emp.full_name,
            employee_designation=emp.designation,
            submitted_at=lr.applied_at,
            leave_type=lr.leave_type.value,
            start_date=lr.start_date.isoformat(),
            end_date=lr.end_date.isoformat(),
            business_days=float(lr.business_days),
            reason=lr.reason,
        ))

    # --- Asset requests ---
    asset_q = await db.execute(
        select(AssetRequest)
        .where(and_(
            AssetRequest.user_id.in_(report_ids),
            AssetRequest.status == RequestStatus.pending,
        ))
        .order_by(AssetRequest.created_at.desc())
    )
    for ar in asset_q.scalars().all():
        emp = user_map.get(str(ar.user_id))
        if not emp:
            continue
        items.append(PendingItem(
            entity_type="asset",
            entity_id=str(ar.id),
            employee_id=str(emp.id),
            employee_name=emp.full_name,
            employee_designation=emp.designation,
            submitted_at=ar.created_at,
            asset_type=ar.asset_type.value,
            justification=ar.justification,
        ))

    # Sort newest first across types
    items.sort(key=lambda it: it.submitted_at, reverse=True)

    return PendingResponse(count=len(items), items=items)


@router.post("/decide", response_model=DecideResponse)
async def decide(
    body: DecideRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DecideResponse:
    """Approve or reject a pending request. Updates DB and balances atomically."""
    if not _is_manager_role(user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers, admins, or HR can decide approvals.",
        )

    report_ids = set(await _direct_report_ids(db, user))

    if body.entity_type == "leave":
        new_status = await _decide_leave(db, body, user, report_ids)
    elif body.entity_type == "asset":
        new_status = await _decide_asset(db, body, user, report_ids)
    elif body.entity_type == "reimbursement":
        new_status = await _decide_reimbursement(db, body, user, report_ids)
    else:  # pragma: no cover — Pydantic Literal blocks this
        raise HTTPException(status_code=400, detail="Unknown entity_type.")

    return DecideResponse(
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        new_status=new_status,
    )


# ── Decide helpers ────────────────────────────────────────────────────────────

async def _decide_leave(
    db: AsyncSession, body: DecideRequest, manager: User, report_ids: set[str]
) -> str:
    lr = (await db.execute(
        select(LeaveRequest).where(LeaveRequest.id == body.entity_id)
    )).scalar_one_or_none()

    if lr is None:
        raise HTTPException(status_code=404, detail="Leave request not found.")
    if str(lr.user_id) not in report_ids:
        raise HTTPException(
            status_code=403,
            detail="This leave request is not for one of your direct reports.",
        )
    if lr.status != LeaveStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"This leave request is already {lr.status.value} and cannot be re-decided.",
        )

    # Locate the matching balance row (paid types only)
    balance_q = await db.execute(
        select(LeaveBalance).where(and_(
            LeaveBalance.user_id == lr.user_id,
            LeaveBalance.year == lr.start_date.year,
            LeaveBalance.leave_type == lr.leave_type,
        ))
    )
    balance: Optional[LeaveBalance] = balance_q.scalar_one_or_none()

    if body.decision == "approve":
        lr.status = LeaveStatus.approved
        if balance is not None:
            balance.pending_days = max(0.0, float(balance.pending_days) - float(lr.business_days))
            balance.used_days = float(balance.used_days) + float(lr.business_days)
    else:
        lr.status = LeaveStatus.rejected
        if balance is not None:
            balance.pending_days = max(0.0, float(balance.pending_days) - float(lr.business_days))

    lr.reviewed_by = manager.id
    lr.reviewed_at = datetime.utcnow()
    lr.reviewer_note = body.note or None

    await db.commit()
    return lr.status.value


async def _decide_asset(
    db: AsyncSession, body: DecideRequest, manager: User, report_ids: set[str]
) -> str:
    ar = (await db.execute(
        select(AssetRequest).where(AssetRequest.id == body.entity_id)
    )).scalar_one_or_none()

    if ar is None:
        raise HTTPException(status_code=404, detail="Asset request not found.")
    if str(ar.user_id) not in report_ids:
        raise HTTPException(
            status_code=403,
            detail="This asset request is not for one of your direct reports.",
        )
    if ar.status != RequestStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"This asset request is already {ar.status.value} and cannot be re-decided.",
        )

    if body.decision == "approve":
        ar.status = RequestStatus.manager_approved
    else:
        ar.status = RequestStatus.rejected

    ar.manager_id = manager.id
    ar.manager_action = datetime.utcnow()
    ar.manager_note = body.note or None

    await db.commit()
    return ar.status.value


async def _decide_reimbursement(
    db: AsyncSession, body: DecideRequest, manager: User, report_ids: set[str]
) -> str:
    # Finance is currently disabled, but the endpoint is provided for parity.
    rb = (await db.execute(
        select(Reimbursement).where(Reimbursement.id == body.entity_id)
    )).scalar_one_or_none()

    if rb is None:
        raise HTTPException(status_code=404, detail="Reimbursement claim not found.")
    if str(rb.user_id) not in report_ids:
        raise HTTPException(
            status_code=403,
            detail="This claim is not for one of your direct reports.",
        )
    if rb.status not in (ReimbursementStatus.submitted, ReimbursementStatus.under_review):
        raise HTTPException(
            status_code=400,
            detail=f"Claim already {rb.status.value} and cannot be re-decided.",
        )

    rb.status = (
        ReimbursementStatus.approved if body.decision == "approve"
        else ReimbursementStatus.rejected
    )
    await db.commit()
    return rb.status.value
