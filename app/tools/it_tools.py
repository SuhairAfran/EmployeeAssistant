import uuid
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models import (
    ITTicket, TicketCategory, TicketPriority, TicketStatus,
    AssetRequest, AssetType, RequestStatus
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
    Use this when an employee reports a broken device, access issue, or software bug.
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

        # Trigger an email to the IT helpdesk
        return {
            "status": "success",
            "message": f"IT Ticket {ticket_no} has been successfully created.",
            "ticket_id": ticket_id,
            "ticket_no": ticket_no,
            "email_triggered": True,
            "email_recipients": ["it-support@company.com"],
            "email_subject": f"New IT Ticket [{priority.value.upper()}]: {subject}",
            "email_body": f"User {user_id} reported an issue in category {category.value}.\n\nDescription: {description}"
        }

    except Exception as e:
        return {"error": f"Failed to create IT ticket: {str(e)}"}

@tool("get_ticket_status", args_schema=GetTicketStatusInput)
async def get_ticket_status(user_id: str, ticket_no: str) -> str:
    """
    Check the current status and resolution notes of an IT ticket.
    Use this when an employee asks for an update on a ticket they submitted.
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
    Submit a request for a new IT asset (hardware or software).
    Use this when an employee asks for a new laptop, monitor, or license.
    Requires manager approval.
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

        # Trigger Manager Approval Process!
        return {
            "status": "success",
            "message": f"Your request for a {asset_type.value.replace('_', ' ')} has been submitted and is pending manager approval.",
            "approval_required": True,
            "request_id": request_id,
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], 
            "email_subject": f"Asset Request Approval: {asset_type.value.capitalize()}",
            "email_body": f"Employee {user_id} is requesting a {asset_type.value.replace('_', ' ')}.\n\nJustification: {justification}"
        }

    except Exception as e:
        return {"error": f"Failed to submit asset request: {str(e)}"}