"""
FastMCP Server
==============
Exposes all enterprise tools as MCP-compatible endpoints.
LangGraph agents call these tools through the MCP protocol.

Run standalone:  python -m app.mcp.server
Or mount on FastAPI: app.mount("/mcp", mcp_app)
"""
from __future__ import annotations

from datetime import date
from typing import Annotated

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from app.config import settings

mcp = FastMCP(
    name="Enterprise AI Copilot Tools",
    version="1.0.0",
    instructions="Tools for HR, IT, and Finance operations. Always validate RBAC before calling.",
)


# ── Input schemas (Pydantic — FastMCP uses these for validation) ──────────────

class LeaveApplyInput(BaseModel):
    user_id:     str
    leave_type:  str   = Field(..., description="casual|sick|earned|maternity|paternity|bereavement")
    start_date:  date
    end_date:    date
    reason:      str   = ""
    is_half_day: bool  = False
    half_day_slot: str = Field("", description="morning|afternoon — only if is_half_day=True")


class LeaveBalanceInput(BaseModel):
    user_id: str
    year:    int = Field(default_factory=lambda: date.today().year)


class TicketCreateInput(BaseModel):
    user_id:     str
    category:    str   = Field(..., description="laptop|vpn|email|printer|network|software_install|hardware|access|other")
    subject:     str
    description: str
    priority:    str   = "medium"


class AssetRequestInput(BaseModel):
    user_id:       str
    asset_type:    str = Field(..., description="laptop|monitor|keyboard|mouse|vpn_token|software_license")
    justification: str


class PayslipFetchInput(BaseModel):
    user_id:   str
    pay_month: str = Field(..., description="YYYY-MM (e.g. 2024-03)")


class ReimbursementSubmitInput(BaseModel):
    user_id:      str
    category:     str   = Field(..., description="travel|internet|food|client_meeting|training")
    amount:       float
    currency:     str   = "INR"
    description:  str
    expense_date: date
    receipt_url:  str   = ""


class ApprovalInput(BaseModel):
    approval_id: str
    decision:    str  = Field(..., description="approved|rejected")
    note:        str  = ""


# ── HR Tools ──────────────────────────────────────────────────────────────────

@mcp.tool(description="Apply for leave. Validates dates, checks overlaps and holiday calendar.")
async def apply_leave(data: LeaveApplyInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import HolidayCalendar, LeaveBalance, LeaveRequest, LeaveType
    from sqlalchemy import and_, select

    async with AsyncSessionLocal() as db:
        # 1. Validate leave type
        try:
            ltype = LeaveType(data.leave_type)
        except ValueError:
            return {"success": False, "error": f"Invalid leave type: {data.leave_type}"}

        # 2. Check date validity
        if data.start_date < date.today():
            return {"success": False, "error": "Cannot apply leave for past dates."}
        if data.end_date < data.start_date:
            return {"success": False, "error": "end_date must be ≥ start_date."}

        # 3. Check overlapping leaves
        overlap = await db.scalar(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.user_id == data.user_id,
                    LeaveRequest.status.in_(["pending", "approved"]),
                    LeaveRequest.start_date <= data.end_date,
                    LeaveRequest.end_date   >= data.start_date,
                )
            )
        )
        if overlap:
            return {"success": False, "error": f"Overlapping leave exists ({overlap.id})."}

        # 4. Count business days (exclude weekends + holidays)
        holidays = set(
            row.holiday_date for row in (
                await db.execute(
                    select(HolidayCalendar.holiday_date).where(
                        HolidayCalendar.holiday_date.between(data.start_date, data.end_date)
                    )
                )
            ).scalars()
        )
        bdays = 0
        cur = data.start_date
        from datetime import timedelta
        while cur <= data.end_date:
            if cur.weekday() < 5 and cur not in holidays:  # Mon–Fri, non-holiday
                bdays += 1
            cur += timedelta(days=1)
        if data.is_half_day:
            bdays = 0.5

        # 5. Check leave balance
        balance = await db.scalar(
            select(LeaveBalance).where(
                and_(
                    LeaveBalance.user_id == data.user_id,
                    LeaveBalance.year == data.start_date.year,
                    LeaveBalance.leave_type == ltype,
                )
            )
        )
        if not balance or balance.available_days < bdays:
            return {"success": False, "error": f"Insufficient {ltype.value} leave balance."}

        # 6. Create leave request
        leave = LeaveRequest(
            user_id=data.user_id,
            leave_type=ltype,
            start_date=data.start_date,
            end_date=data.end_date,
            business_days=bdays,
            reason=data.reason,
            is_half_day=data.is_half_day,
            half_day_slot=data.half_day_slot or None,
        )
        db.add(leave)
        balance.pending_days += bdays
        await db.commit()
        await db.refresh(leave)

    return {
        "success": True,
        "leave_id": str(leave.id),
        "business_days": bdays,
        "status": "pending",
        "message": f"Leave applied successfully ({bdays} day(s)). Pending manager approval.",
        "approval_required": True,
    }


@mcp.tool(description="Get leave balance for a user for the current or specified year.")
async def get_leave_balance(data: LeaveBalanceInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import LeaveBalance
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(LeaveBalance).where(
                LeaveBalance.user_id == data.user_id,
                LeaveBalance.year == data.year,
            )
        )).scalars().all()

    return {
        "user_id": data.user_id,
        "year": data.year,
        "balances": [
            {
                "type": row.leave_type.value,
                "entitled": float(row.entitled_days),
                "used": float(row.used_days),
                "pending": float(row.pending_days),
                "available": float(row.available_days),
            }
            for row in rows
        ],
    }


# ── IT Tools ──────────────────────────────────────────────────────────────────

@mcp.tool(description="Create an IT support ticket. Checks for duplicates and known issues first.")
async def create_ticket(data: TicketCreateInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import ITTicket, KnownIssue, MaintenanceSchedule, TicketCategory, TicketPriority
    from sqlalchemy import and_, select
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        # 1. Check active maintenance
        maint = await db.scalar(
            select(MaintenanceSchedule).where(
                and_(
                    MaintenanceSchedule.starts_at <= now,
                    MaintenanceSchedule.ends_at   >= now,
                    MaintenanceSchedule.affected_system.ilike(f"%{data.category}%"),
                )
            )
        )
        if maint:
            return {
                "success": False,
                "info": f"Planned maintenance in progress: '{maint.title}'. Expected end: {maint.ends_at.isoformat()}",
                "ticket_created": False,
            }

        # 2. Check known issues
        known = await db.scalar(
            select(KnownIssue).where(
                and_(
                    KnownIssue.category == data.category,
                    KnownIssue.is_active.is_(True),
                )
            )
        )
        if known:
            return {
                "success": True,
                "info": f"Known issue: {known.title}. Workaround: {known.workaround or 'None available'}",
                "ticket_created": False,
                "message": "A known issue matches your request. No ticket raised; see workaround above.",
            }

        # 3. Check duplicate open ticket
        dupe = await db.scalar(
            select(ITTicket).where(
                and_(
                    ITTicket.user_id == data.user_id,
                    ITTicket.category == data.category,
                    ITTicket.status.in_(["open", "in_progress"]),
                )
            )
        )
        if dupe:
            return {
                "success": True,
                "info": f"You already have an open ticket ({dupe.ticket_no}) for '{data.category}'.",
                "ticket_id": str(dupe.id),
                "ticket_no": dupe.ticket_no,
                "ticket_created": False,
            }

        # 4. Create ticket
        ticket = ITTicket(
            user_id=data.user_id,
            category=TicketCategory(data.category),
            subject=data.subject,
            description=data.description,
            priority=TicketPriority(data.priority),
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

    return {
        "success": True,
        "ticket_id": str(ticket.id),
        "ticket_no": ticket.ticket_no,
        "priority": ticket.priority.value,
        "status": "open",
        "ticket_created": True,
        "message": f"Ticket {ticket.ticket_no} created. You'll receive email confirmation shortly.",
    }


@mcp.tool(description="Check inventory and submit an asset request (laptop, monitor, etc).")
async def request_asset(data: AssetRequestInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import AssetRequest, AssetType, ITInventory
    from sqlalchemy import and_, select

    async with AsyncSessionLocal() as db:
        # Check availability
        available = await db.scalar(
            select(ITInventory).where(
                and_(
                    ITInventory.asset_type == data.asset_type,
                    ITInventory.status == "available",
                )
            )
        )

        req = AssetRequest(
            user_id=data.user_id,
            asset_type=AssetType(data.asset_type),
            justification=data.justification,
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)

    return {
        "success": True,
        "request_id": str(req.id),
        "asset_type": data.asset_type,
        "inventory_available": available is not None,
        "status": "pending",
        "approval_required": True,
        "message": "Asset request submitted. Manager approval required.",
    }


# ── Finance Tools ─────────────────────────────────────────────────────────────

@mcp.tool(description="Fetch payslip details for a specific month (YYYY-MM).")
async def fetch_payslip(data: PayslipFetchInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import PayrollRecord
    from sqlalchemy import select
    from datetime import date as dt

    year, month = map(int, data.pay_month.split("-"))
    pay_month_date = dt(year, month, 1)

    async with AsyncSessionLocal() as db:
        record = await db.scalar(
            select(PayrollRecord).where(
                PayrollRecord.user_id == data.user_id,
                PayrollRecord.pay_month == pay_month_date,
            )
        )

    if not record:
        return {"success": False, "error": f"No payslip found for {data.pay_month}."}

    return {
        "success": True,
        "pay_month": data.pay_month,
        "gross_salary": float(record.gross_salary),
        "net_salary": float(record.net_salary),
        "breakdown": {
            "basic": float(record.basic),
            "hra": float(record.hra),
            "allowances": float(record.allowances),
        },
        "deductions": {
            "pf_employee": float(record.pf_employee),
            "tds": float(record.tds),
            "professional_tax": float(record.professional_tax),
            "other": float(record.other_deductions),
        },
        "payslip_url": record.payslip_url,
    }


@mcp.tool(description="Submit a reimbursement claim with expense details and receipt URL.")
async def submit_reimbursement(data: ReimbursementSubmitInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import Reimbursement, ReimbursementCategory
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        claim = Reimbursement(
            user_id=data.user_id,
            category=ReimbursementCategory(data.category),
            amount=data.amount,
            currency=data.currency,
            description=data.description,
            expense_date=data.expense_date,
            receipt_url=data.receipt_url or None,
            status="submitted",
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        await db.commit()
        await db.refresh(claim)

    return {
        "success": True,
        "claim_id": str(claim.id),
        "claim_no": claim.claim_no,
        "amount": float(claim.amount),
        "currency": claim.currency,
        "status": "submitted",
        "approval_required": True,
        "message": f"Claim {claim.claim_no} submitted for ₹{claim.amount:.2f}. Finance team will review.",
    }


# ── Approval Tool (cross-department) ──────────────────────────────────────────

@mcp.tool(description="Record an approval decision for a leave, asset request, or reimbursement.")
async def record_approval(data: ApprovalInput) -> dict:
    from app.database import AsyncSessionLocal
    from app.models import Approval, ApprovalDecision
    from sqlalchemy import select
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        approval = await db.get(Approval, data.approval_id)
        if not approval:
            return {"success": False, "error": "Approval record not found."}
        if approval.decision != ApprovalDecision.pending:
            return {"success": False, "error": f"Already decided: {approval.decision.value}"}

        approval.decision = ApprovalDecision(data.decision)
        approval.note = data.note
        approval.decided_at = datetime.now(timezone.utc)
        await db.commit()

    return {
        "success": True,
        "approval_id": data.approval_id,
        "decision": data.decision,
        "message": f"Approval {data.decision} recorded.",
    }


# ── Inventory status (IT team only) ───────────────────────────────────────────

@mcp.tool(description="View current IT inventory status and available assets. IT team only.")
async def inventory_status(asset_type: str = "") -> dict:
    from app.database import AsyncSessionLocal
    from app.models import ITInventory
    from sqlalchemy import select, func

    async with AsyncSessionLocal() as db:
        q = select(
            ITInventory.asset_type,
            ITInventory.status,
            func.count().label("count"),
        ).group_by(ITInventory.asset_type, ITInventory.status)

        if asset_type:
            q = q.where(ITInventory.asset_type == asset_type)

        rows = (await db.execute(q)).all()

    summary: dict = {}
    for row in rows:
        atype = row.asset_type.value
        summary.setdefault(atype, {})[row.status.value] = row.count

    return {"inventory": summary}


# ── Run MCP server standalone ─────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(host=settings.MCP_HOST, port=settings.MCP_PORT, transport="sse")