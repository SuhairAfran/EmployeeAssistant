"""
SQLAlchemy ORM models — mirrors schema.sql exactly.
Import everything from here: `from app.models import User, LeaveRequest, ...`
"""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY, Boolean, CheckConstraint, Column, Date, DateTime,
    Enum, ForeignKey, Index, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ── Enums (match PostgreSQL enums in schema.sql) ──────────────────────────────

class UserRole(str, enum.Enum):
    employee     = "employee"
    manager      = "manager"
    hr_team      = "hr_team"
    it_team      = "it_team"
    finance_team = "finance_team"
    admin        = "admin"

class LeaveStatus(str, enum.Enum):
    pending   = "pending"
    approved  = "approved"
    rejected  = "rejected"
    cancelled = "cancelled"

class LeaveType(str, enum.Enum):
    casual        = "casual"
    sick          = "sick"
    earned        = "earned"
    maternity     = "maternity"
    paternity     = "paternity"
    bereavement   = "bereavement"
    compensatory  = "compensatory"
    unpaid        = "unpaid"

class TicketStatus(str, enum.Enum):
    open        = "open"
    in_progress = "in_progress"
    on_hold     = "on_hold"
    resolved    = "resolved"
    closed      = "closed"

class TicketPriority(str, enum.Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"

class TicketCategory(str, enum.Enum):
    laptop           = "laptop"
    vpn              = "vpn"
    email            = "email"
    printer          = "printer"
    network          = "network"
    software_install = "software_install"
    hardware         = "hardware"
    access           = "access"
    other            = "other"

class AssetStatus(str, enum.Enum):
    available = "available"
    assigned  = "assigned"
    in_repair = "in_repair"
    retired   = "retired"
    lost      = "lost"

class AssetType(str, enum.Enum):
    laptop           = "laptop"
    monitor          = "monitor"
    keyboard         = "keyboard"
    mouse            = "mouse"
    vpn_token        = "vpn_token"
    software_license = "software_license"
    headset          = "headset"
    docking_station  = "docking_station"
    other            = "other"

class RequestStatus(str, enum.Enum):
    pending          = "pending"
    manager_approved = "manager_approved"
    it_approved      = "it_approved"
    rejected         = "rejected"
    fulfilled        = "fulfilled"
    cancelled        = "cancelled"

class ReimbursementCategory(str, enum.Enum):
    travel          = "travel"
    internet        = "internet"
    food            = "food"
    client_meeting  = "client_meeting"
    training        = "training"
    office_supplies = "office_supplies"
    other           = "other"

class ReimbursementStatus(str, enum.Enum):
    draft        = "draft"
    submitted    = "submitted"
    under_review = "under_review"
    approved     = "approved"
    rejected     = "rejected"
    paid         = "paid"

class ApprovalEntity(str, enum.Enum):
    leave           = "leave"
    asset_request   = "asset_request"
    reimbursement   = "reimbursement"
    it_action       = "it_action"

class ApprovalDecision(str, enum.Enum):
    pending   = "pending"
    approved  = "approved"
    rejected  = "rejected"
    escalated = "escalated"

class DocDepartment(str, enum.Enum):
    hr      = "hr"
    it      = "it"
    finance = "finance"
    general = "general"


# ── Mixins ────────────────────────────────────────────────────────────────────

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )


# ── Core models ───────────────────────────────────────────────────────────────

class Department(TimestampMixin, Base):
    __tablename__ = "departments"

    id:        Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:      Mapped[str]       = mapped_column(String(100), unique=True, nullable=False)
    code:      Mapped[str]       = mapped_column(String(20), unique=True, nullable=False)
    head_id:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", use_alter=True))
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="department",
                                               foreign_keys="User.department_id")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id:            Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id:   Mapped[str]        = mapped_column(String(20), unique=True, nullable=False)
    email:         Mapped[str]        = mapped_column(String(255), unique=True, nullable=False)
    full_name:     Mapped[str]        = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str]        = mapped_column(Text, nullable=False)
    role:          Mapped[UserRole]   = mapped_column(Enum(UserRole), default=UserRole.employee, nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    manager_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    designation:   Mapped[str | None] = mapped_column(String(150))
    date_of_joining: Mapped[date | None] = mapped_column(Date)
    is_active:     Mapped[bool]       = mapped_column(Boolean, default=True, nullable=False)
    preferred_lang: Mapped[str]       = mapped_column(String(10), default="en", nullable=False)

    # Relationships
    department: Mapped["Department | None"] = relationship(
        "Department", back_populates="users", foreign_keys=[department_id]
    )
    manager:    Mapped["User | None"]       = relationship("User", remote_side="User.id",
                                                           foreign_keys=[manager_id])
    leave_requests:  Mapped[list["LeaveRequest"]]  = relationship(back_populates="user")
    tickets:         Mapped[list["ITTicket"]]       = relationship(back_populates="user",
                                                                   foreign_keys="ITTicket.user_id")
    asset_requests:  Mapped[list["AssetRequest"]]  = relationship(back_populates="user")
    reimbursements:  Mapped[list["Reimbursement"]] = relationship(back_populates="user")
    memory_entries:  Mapped[list["UserMemory"]]    = relationship(back_populates="user")

    def has_permission(self, perm_code: str) -> bool:
        """Quick check — call after loading role_permissions into session context."""
        from app.middleware.rbac import ROLE_PERMISSIONS
        return perm_code in ROLE_PERMISSIONS.get(self.role, set())


class Permission(Base):
    __tablename__ = "permissions"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code:        Mapped[str]       = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    module:      Mapped[str]       = mapped_column(String(50), nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role:    Mapped[UserRole]  = mapped_column(Enum(UserRole), primary_key=True)
    perm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("permissions.id", ondelete="CASCADE"),
                                               primary_key=True)


# ── HR Module ─────────────────────────────────────────────────────────────────

class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("user_id", "year", "leave_type"),)

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    year:          Mapped[int]
    leave_type:    Mapped[LeaveType] = mapped_column(Enum(LeaveType), nullable=False)
    entitled_days: Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    used_days:     Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    pending_days:  Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    carried_over:  Mapped[float]     = mapped_column(Numeric(5, 1), default=0)
    updated_at:    Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def available_days(self) -> float:
        return self.entitled_days + self.carried_over - self.used_days - self.pending_days


class LeaveRequest(TimestampMixin, Base):
    __tablename__ = "leave_requests"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="valid_dates"),
        CheckConstraint("business_days > 0", name="valid_business_days"),
    )

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    leave_type:    Mapped[LeaveType]    = mapped_column(Enum(LeaveType), nullable=False)
    start_date:    Mapped[date]         = mapped_column(Date, nullable=False)
    end_date:      Mapped[date]         = mapped_column(Date, nullable=False)
    business_days: Mapped[float]        = mapped_column(Numeric(4, 1), nullable=False)
    reason:        Mapped[str | None]   = mapped_column(Text)
    status:        Mapped[LeaveStatus]  = mapped_column(Enum(LeaveStatus), default=LeaveStatus.pending)
    applied_at:    Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_by:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at:   Mapped[datetime | None]  = mapped_column(DateTime(timezone=True))
    reviewer_note: Mapped[str | None]   = mapped_column(Text)
    is_half_day:   Mapped[bool]         = mapped_column(Boolean, default=False)
    half_day_slot: Mapped[str | None]   = mapped_column(String(10))

    user: Mapped["User"] = relationship(back_populates="leave_requests", foreign_keys=[user_id])


class HolidayCalendar(Base):
    __tablename__ = "holiday_calendar"

    id:           Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    holiday_date: Mapped[date]      = mapped_column(Date, nullable=False)
    name:         Mapped[str]       = mapped_column(String(200), nullable=False)
    is_optional:  Mapped[bool]      = mapped_column(Boolean, default=False)


# ── IT Module ─────────────────────────────────────────────────────────────────

class ITTicket(TimestampMixin, Base):
    __tablename__ = "it_tickets"

    id:             Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_no:      Mapped[str]            = mapped_column(String(20), unique=True, nullable=False)
    user_id:        Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category:       Mapped[TicketCategory] = mapped_column(Enum(TicketCategory), nullable=False)
    subject:        Mapped[str]            = mapped_column(String(500), nullable=False)
    description:    Mapped[str]            = mapped_column(Text, nullable=False)
    priority:       Mapped[TicketPriority] = mapped_column(Enum(TicketPriority), default=TicketPriority.medium)
    status:         Mapped[TicketStatus]   = mapped_column(Enum(TicketStatus), default=TicketStatus.open)
    assigned_to:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    parent_ticket:  Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("it_tickets.id"))
    resolution:     Mapped[str | None]     = mapped_column(Text)
    is_known_issue: Mapped[bool]           = mapped_column(Boolean, default=False)
    outage_ref:     Mapped[str | None]     = mapped_column(String(100))
    resolved_at:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sla_due_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user:     Mapped["User"] = relationship(back_populates="tickets", foreign_keys=[user_id])
    comments: Mapped[list["ITTicketComment"]] = relationship(back_populates="ticket")


class ITTicketComment(Base):
    __tablename__ = "it_ticket_comments"

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id:   Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("it_tickets.id", ondelete="CASCADE"))
    author_id:   Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    comment:     Mapped[str]       = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool]      = mapped_column(Boolean, default=False)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["ITTicket"] = relationship(back_populates="comments")


class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedule"

    id:              Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title:           Mapped[str]       = mapped_column(String(300), nullable=False)
    affected_system: Mapped[str]       = mapped_column(String(200), nullable=False)
    starts_at:       Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at:         Mapped[datetime]  = mapped_column(DateTime(timezone=True), nullable=False)
    description:     Mapped[str | None] = mapped_column(Text)
    created_by:      Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at:      Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())


class KnownIssue(Base):
    __tablename__ = "known_issues"

    id:          Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title:       Mapped[str]            = mapped_column(String(300), nullable=False)
    category:    Mapped[TicketCategory] = mapped_column(Enum(TicketCategory), nullable=False)
    description: Mapped[str]            = mapped_column(Text, nullable=False)
    workaround:  Mapped[str | None]     = mapped_column(Text)
    is_active:   Mapped[bool]           = mapped_column(Boolean, default=True)
    reported_at: Mapped[datetime]       = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ITInventory(TimestampMixin, Base):
    __tablename__ = "it_inventory"

    id:            Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_tag:     Mapped[str]        = mapped_column(String(50), unique=True, nullable=False)
    asset_type:    Mapped[AssetType]  = mapped_column(Enum(AssetType), nullable=False)
    brand:         Mapped[str | None] = mapped_column(String(100))
    model:         Mapped[str | None] = mapped_column(String(200))
    serial_no:     Mapped[str | None] = mapped_column(String(100), unique=True)
    status:        Mapped[AssetStatus] = mapped_column(Enum(AssetStatus), default=AssetStatus.available)
    assigned_to:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_at:   Mapped[datetime | None]  = mapped_column(DateTime(timezone=True))
    purchase_date: Mapped[date | None]      = mapped_column(Date)
    warranty_until: Mapped[date | None]     = mapped_column(Date)
    location:      Mapped[str | None]       = mapped_column(String(200))
    notes:         Mapped[str | None]       = mapped_column(Text)


class AssetRequest(TimestampMixin, Base):
    __tablename__ = "asset_requests"

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:       Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    asset_type:    Mapped[AssetType]    = mapped_column(Enum(AssetType), nullable=False)
    justification: Mapped[str]          = mapped_column(Text, nullable=False)
    status:        Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.pending)
    manager_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    manager_action: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    manager_note:  Mapped[str | None]   = mapped_column(Text)
    it_actioned_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    it_action_at:  Mapped[datetime | None]   = mapped_column(DateTime(timezone=True))
    it_note:       Mapped[str | None]   = mapped_column(Text)
    asset_id:      Mapped[uuid.UUID | None]  = mapped_column(UUID(as_uuid=True), ForeignKey("it_inventory.id"))

    user: Mapped["User"] = relationship(back_populates="asset_requests", foreign_keys=[user_id])


# ── Finance Module ────────────────────────────────────────────────────────────

class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    __table_args__ = (UniqueConstraint("user_id", "pay_month"),)

    id:               Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pay_month:        Mapped[date]      = mapped_column(Date, nullable=False)
    gross_salary:     Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    basic:            Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    hra:              Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    allowances:       Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    pf_employee:      Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    pf_employer:      Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    tds:              Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    professional_tax: Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    other_deductions: Mapped[float]     = mapped_column(Numeric(12, 2), default=0)
    net_salary:       Mapped[float]     = mapped_column(Numeric(12, 2), nullable=False)
    payslip_url:      Mapped[str | None] = mapped_column(Text)
    generated_at:     Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class Reimbursement(TimestampMixin, Base):
    __tablename__ = "reimbursements"
    __table_args__ = (CheckConstraint("amount > 0", name="positive_amount"),)

    id:            Mapped[uuid.UUID]             = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_no:      Mapped[str]                   = mapped_column(String(20), unique=True, nullable=False)
    user_id:       Mapped[uuid.UUID]             = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category:      Mapped[ReimbursementCategory] = mapped_column(Enum(ReimbursementCategory), nullable=False)
    amount:        Mapped[float]                 = mapped_column(Numeric(10, 2), nullable=False)
    currency:      Mapped[str]                   = mapped_column(String(3), default="INR")
    description:   Mapped[str]                   = mapped_column(Text, nullable=False)
    expense_date:  Mapped[date]                  = mapped_column(Date, nullable=False)
    receipt_url:   Mapped[str | None]            = mapped_column(Text)
    status:        Mapped[ReimbursementStatus]   = mapped_column(Enum(ReimbursementStatus), default=ReimbursementStatus.draft)
    submitted_at:  Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    reviewed_by:   Mapped[uuid.UUID | None]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at:   Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    reviewer_note: Mapped[str | None]            = mapped_column(Text)
    paid_at:       Mapped[datetime | None]       = mapped_column(DateTime(timezone=True))
    payment_ref:   Mapped[str | None]            = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="reimbursements", foreign_keys=[user_id])


# ── Approvals ─────────────────────────────────────────────────────────────────

class Approval(Base):
    __tablename__ = "approvals"

    id:          Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[ApprovalEntity] = mapped_column(Enum(ApprovalEntity), nullable=False)
    entity_id:   Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), nullable=False)
    approver_id: Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    step:        Mapped[int]            = mapped_column(Integer, default=1)
    decision:    Mapped[ApprovalDecision] = mapped_column(Enum(ApprovalDecision), default=ApprovalDecision.pending)
    note:        Mapped[str | None]     = mapped_column(Text)
    decided_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at:  Mapped[datetime]       = mapped_column(DateTime(timezone=True), server_default=func.now())

    approver: Mapped["User"] = relationship(foreign_keys=[approver_id])


# ── Memory & Sessions ─────────────────────────────────────────────────────────

class UserMemory(Base):
    __tablename__ = "user_memory"
    __table_args__ = (UniqueConstraint("user_id", "memory_key"),)

    id:           Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:      Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    memory_key:   Mapped[str]       = mapped_column(String(100), nullable=False)
    memory_value: Mapped[dict]      = mapped_column(JSONB, nullable=False)
    source:       Mapped[str]       = mapped_column(String(50), default="inferred")
    updated_at:   Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="memory_entries")


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_key:   Mapped[str]       = mapped_column(String(200), unique=True, nullable=False)
    user_id:       Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    messages:      Mapped[list]      = mapped_column(JSONB, default=list)
    agent_used:    Mapped[str | None] = mapped_column(String(50))
    started_at:    Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at:      Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ── RAG Documents ─────────────────────────────────────────────────────────────

class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id:            Mapped[uuid.UUID]    = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename:      Mapped[str]          = mapped_column(String(500), nullable=False)
    department:    Mapped[DocDepartment] = mapped_column(Enum(DocDepartment), nullable=False)
    doc_type:      Mapped[str | None]   = mapped_column(String(100))
    roles_allowed: Mapped[list]         = mapped_column(ARRAY(String), default=["employee"])
    file_url:      Mapped[str | None]   = mapped_column(Text)
    ingested_at:   Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active:     Mapped[bool]         = mapped_column(Boolean, default=True)
    chunk_count:   Mapped[int]          = mapped_column(Integer, default=0)
    metadata_:     Mapped[dict]         = mapped_column("metadata", JSONB, default=dict)

    chunks: Mapped[list["RAGChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class RAGChunk(Base):
    __tablename__ = "rag_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)

    id:          Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rag_documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int]       = mapped_column(Integer, nullable=False)
    content:     Mapped[str]       = mapped_column(Text, nullable=False)
    embedding:   Mapped[Any]       = mapped_column(Vector(1536))       # pgvector
    token_count: Mapped[int | None] = mapped_column(Integer)
    metadata_:   Mapped[dict]      = mapped_column("metadata", JSONB, default=dict)
    created_at:  Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["RAGDocument"] = relationship(back_populates="chunks")


# ── Audit Log ─────────────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id:           Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:      Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id:   Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"))
    action:       Mapped[str]        = mapped_column(String(200), nullable=False)
    entity_type:  Mapped[str | None] = mapped_column(String(100))
    entity_id:    Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    agent_used:   Mapped[str | None] = mapped_column(String(100))
    tool_used:    Mapped[str | None] = mapped_column(String(100))
    llm_model:    Mapped[str | None] = mapped_column(String(100))
    status:       Mapped[str]        = mapped_column(String(50), default="success")
    error_message: Mapped[str | None] = mapped_column(Text)
    latency_ms:   Mapped[int | None] = mapped_column(Integer)
    token_count:  Mapped[int | None] = mapped_column(Integer)
    ip_address:   Mapped[Any]        = mapped_column(INET)
    metadata_:    Mapped[dict]       = mapped_column("metadata", JSONB, default=dict)
    created_at:   Mapped[datetime]   = mapped_column(DateTime(timezone=True), server_default=func.now())