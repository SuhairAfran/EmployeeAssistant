import uuid
from typing import Any, Dict, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_, or_
from app.database import AsyncSessionLocal
from app.models import (
    ITTicket, TicketCategory, TicketPriority, TicketStatus,
    AssetRequest, AssetType, RequestStatus, KnownIssue,
)

# ==========================================
# INPUT SCHEMAS
# ==========================================

class CreateTicketInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee creating the ticket.")
    category: TicketCategory = Field(description="The category of the issue (e.g., 'laptop', 'vpn', 'access').")
    subject: str = Field(description="A brief summary of the issue.")
    description: str = Field(description="Detailed explanation of the problem.")
    priority: TicketPriority = Field(description="Urgency of the issue ('low', 'medium', 'high', 'critical').")

class GetTicketStatusInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee checking the ticket.")
    ticket_no: str = Field(description="The specific ticket number (e.g., 'TKT-12345').")

class RequestAssetInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting the asset.")
    asset_type: AssetType = Field(description="The type of asset requested (e.g., 'laptop', 'monitor', 'software_license').")
    justification: str = Field(description="The business reason for requesting this asset.")

# ==========================================
# TOOLS
# ==========================================

@tool("create_it_ticket", args_schema=CreateTicketInput)
async def create_it_ticket(user_id: str, category: TicketCategory, subject: str, description: str, priority: TicketPriority) -> Dict[str, Any]:
    """
    Create a new IT support ticket in the database.

    TRIGGER PHRASES: "raise an IT ticket", "create a ticket", "I have a
    tech issue", "my laptop is broken", "VPN not working", "can't access
    [system]", "need IT help", "report an IT problem", "software bug",
    "password reset", "access request", "email not working".

    BEFORE calling: you MUST have a subject and description from the user.
    Infer category from context (laptop, vpn, email, access, software,
    hardware, network, printer, other). Default priority to 'medium'
    unless the user indicates urgency.

    TIP: Before creating a ticket, consider calling search_known_issues
    first to check if a workaround exists. If one does, offer it to the
    user and only create a ticket if they still want one.

    DO NOT call this for asset requests — use request_it_asset instead.
    """
    try:
        # Generate a readable ticket number
        ticket_no = f"TKT-{uuid.uuid4().hex[:6].upper()}"

        async with AsyncSessionLocal() as db:
            new_ticket = ITTicket(
                ticket_no=ticket_no,
                user_id=user_id,
                category=category,
                subject=subject,
                description=description,
                priority=priority,
                status=TicketStatus.open
            )
            db.add(new_ticket)
            await db.commit()
            await db.refresh(new_ticket)
            
            ticket_id = str(new_ticket.id)

        return {
            "status": "success",
            "message": (
                f"IT ticket {ticket_no} has been created with priority "
                f"{priority.value.upper()}. The IT helpdesk will respond per "
                f"the SLA for your priority."
            ),
            "ticket_id": ticket_id,
            "ticket_no": ticket_no,
        }

    except Exception as e:
        return {"error": f"Failed to create IT ticket: {str(e)}"}

@tool("get_ticket_status", args_schema=GetTicketStatusInput)
async def get_ticket_status(user_id: str, ticket_no: str) -> str:
    """
    Check the current status and resolution notes of a specific IT ticket.

    TRIGGER PHRASES: "check ticket status", "what happened to my ticket",
    "update on TKT-XXXX", "is my ticket resolved", "ticket progress".

    BEFORE calling: you MUST have the specific ticket number (e.g.
    'TKT-12345') from the user. If they don't know it, call view_it_tickets
    first to list their tickets.

    DO NOT call this to list all tickets — use view_it_tickets instead.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(ITTicket).where(
                and_(ITTicket.ticket_no == ticket_no, ITTicket.user_id == user_id)
            )
            result = await db.execute(stmt)
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                return f"I couldn't find a ticket with the number {ticket_no} associated with your account."
            
            response = f"**Ticket {ticket.ticket_no} Status Update:**\n"
            response += f"- **Status:** {ticket.status.value.replace('_', ' ').capitalize()}\n"
            response += f"- **Priority:** {ticket.priority.value.capitalize()}\n"
            
            if ticket.resolution:
                response += f"- **Resolution Notes:** {ticket.resolution}\n"
                
            return response
            
    except Exception as e:
        return f"Error fetching ticket status: {str(e)}"

@tool("request_it_asset", args_schema=RequestAssetInput)
async def request_it_asset(user_id: str, asset_type: AssetType, justification: str) -> Dict[str, Any]:
    """
    Submit a request for a new IT asset (hardware or software license).
    Creates a pending request that requires manager approval.

    TRIGGER PHRASES: "I need a new laptop", "request a monitor",
    "software license request", "need a keyboard/mouse/headset",
    "request IT equipment", "I need new hardware".

    BEFORE calling: you MUST have the asset_type and a business
    justification from the user. If the justification is missing, ask
    for one.

    DO NOT call this for reporting broken equipment — use
    create_it_ticket instead.
    """
    try:
        async with AsyncSessionLocal() as db:
            new_request = AssetRequest(
                user_id=user_id,
                asset_type=asset_type,
                justification=justification,
                status=RequestStatus.pending
            )
            db.add(new_request)
            await db.commit()
            await db.refresh(new_request)
            
            request_id = str(new_request.id)

        return {
            "status": "success",
            "message": (
                f"Your request for a {asset_type.value.replace('_', ' ')} has "
                f"been submitted and is pending manager approval. You will see "
                f"the status update in your dashboard once your manager decides."
            ),
            "approval_required": True,
            "request_id": request_id,
        }

    except Exception as e:
        return {"error": f"Failed to submit asset request: {str(e)}"}


# ==========================================
# ADDITIONAL TOOLS
# ==========================================

class ViewITTicketsInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee whose IT tickets to list.")


@tool("view_it_tickets", args_schema=ViewITTicketsInput)
async def view_it_tickets(user_id: str) -> str:
    """
    List all IT tickets raised by the employee, most recent first.

    TRIGGER PHRASES: "show my IT tickets", "list my tickets", "what
    tickets do I have", "my open tickets", "IT ticket history",
    "my support requests".

    DO NOT call this to check a specific ticket's status — use
    get_ticket_status with the ticket number instead.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = (
                select(ITTicket)
                .where(ITTicket.user_id == user_id)
                .order_by(ITTicket.created_at.desc())
                .limit(50)
            )
            result = await db.execute(stmt)
            tickets = result.scalars().all()

            if not tickets:
                return "You have not raised any IT tickets yet."

            response = "| Ticket | Category | Subject | Priority | Status | Raised |\n"
            response += "|--------|----------|---------|----------|--------|--------|\n"
            for t in tickets:
                response += (
                    f"| {t.ticket_no} | {t.category.value.replace('_', ' ').capitalize()} | "
                    f"{t.subject} | {t.priority.value.capitalize()} | "
                    f"{t.status.value.replace('_', ' ').capitalize()} | "
                    f"{t.created_at.strftime('%Y-%m-%d')} |\n"
                )
            return response
    except Exception as e:
        return f"Error fetching IT tickets: {str(e)}"


class SearchKnownIssuesInput(BaseModel):
    query: str = Field(description="Free-text problem description to match against known IT issues / FAQs.")
    category: Optional[TicketCategory] = Field(
        default=None,
        description="Optional category filter (e.g., 'vpn', 'laptop', 'email').",
    )


@tool("search_known_issues", args_schema=SearchKnownIssuesInput)
async def search_known_issues(query: str, category: Optional[TicketCategory] = None) -> str:
    """
    Search the IT known-issues / FAQ database for matching workarounds.

    TRIGGER PHRASES: "is there a known issue with [X]", "anyone else
    having this problem", "common fix for [X]", "IT FAQ", "known bug".

    IMPORTANT: You should call this tool BEFORE creating a ticket when a
    user describes a technical problem. A known workaround can save them
    a wait. If no match is found and the user still needs help, offer to
    create a ticket.

    DO NOT call this for policy questions — use search_it_policies for
    IT policy lookups.
    """
    try:
        async with AsyncSessionLocal() as db:
            conditions = [KnownIssue.is_active.is_(True)]
            if category is not None:
                conditions.append(KnownIssue.category == category)

            terms = [t.strip() for t in query.split() if len(t.strip()) >= 3]
            if terms:
                like_clauses = []
                for term in terms[:6]:  # cap search terms
                    pat = f"%{term}%"
                    like_clauses.append(KnownIssue.title.ilike(pat))
                    like_clauses.append(KnownIssue.description.ilike(pat))
                conditions.append(or_(*like_clauses))

            stmt = (
                select(KnownIssue)
                .where(and_(*conditions))
                .order_by(KnownIssue.reported_at.desc())
                .limit(5)
            )
            result = await db.execute(stmt)
            issues = result.scalars().all()

            if not issues:
                return (
                    "No matching known issue found in the IT knowledge base. "
                    "If the problem persists, raise a ticket and IT will help you."
                )

            response = "**Matching known issues / FAQs:**\n\n"
            for i, issue in enumerate(issues, 1):
                response += f"### {i}. {issue.title}\n"
                response += f"_Category: {issue.category.value.replace('_', ' ').capitalize()}_\n\n"
                response += f"**Problem:** {issue.description}\n\n"
                if issue.workaround:
                    response += f"**Workaround:** {issue.workaround}\n\n"
            return response.rstrip()
    except Exception as e:
        return f"Error searching known issues: {str(e)}"