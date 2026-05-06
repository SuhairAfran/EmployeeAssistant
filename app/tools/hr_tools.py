from datetime import date
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models import LeaveRequest, LeaveBalance, LeaveType, LeaveStatus

# ==========================================
# INPUT SCHEMAS
# ==========================================

class LeaveBalanceInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting their leave balance.")
    year: int = Field(description="The current year to check the balance for.")

class ApplyLeaveInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee applying for leave.")
    start_date: date = Field(description="The start date of the leave (YYYY-MM-DD).")
    end_date: date = Field(description="The end date of the leave (YYYY-MM-DD).")
    leave_type: LeaveType = Field(description="The type of leave (e.g., 'sick', 'casual', 'earned').")
    business_days: float = Field(description="The total number of working days requested.")
    reason: str = Field(description="A brief reason for the leave.")

class CancelLeaveInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee canceling their leave.")
    leave_id: str = Field(description="The UUID of the leave request to cancel.")

# ==========================================
# TOOLS
# ==========================================

@tool("get_leave_balance", args_schema=LeaveBalanceInput)
async def get_leave_balance(user_id: str, year: int) -> str:
    """
    Fetch the current leave balances for an employee from the database. 
    Use this when an employee asks how many days off they have left.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(LeaveBalance).where(
                and_(LeaveBalance.user_id == user_id, LeaveBalance.year == year)
            )
            result = await db.execute(stmt)
            balances = result.scalars().all()
            
            if not balances:
                return "I couldn't find any leave balance records for you in the system for this year."
            
            response = "Here are your current leave balances:\n"
            for b in balances:
                response += f"- **{b.leave_type.value.capitalize()} Leave**: {b.available_days} days available (out of {b.entitled_days} entitled).\n"
            
            return response
            
    except Exception as e:
        return f"Error fetching leave balance: {str(e)}"

@tool("apply_for_leave", args_schema=ApplyLeaveInput)
async def apply_for_leave(user_id: str, start_date: date, end_date: date, leave_type: LeaveType, business_days: float, reason: str) -> Dict[str, Any]:
    """
    Submit a new leave request for an employee to the database.
    Use this when an employee explicitly states they want to book time off.
    """
    try:
        if end_date < start_date:
            return {"error": "The end date cannot be before the start date."}

        async with AsyncSessionLocal() as db:
            new_leave = LeaveRequest(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                leave_type=leave_type,
                business_days=business_days,
                reason=reason,
                status=LeaveStatus.pending
            )
            db.add(new_leave)
            await db.commit()
            await db.refresh(new_leave)
            
            generated_leave_id = str(new_leave.id)

        # Trigger the LangGraph Human-in-the-loop and Email Automation!
        return {
            "status": "success",
            "message": f"Leave request for {start_date} to {end_date} has been drafted.",
            "approval_required": True,       
            "leave_id": generated_leave_id,  
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], # TODO: Fetch actual manager email via graph context
            "email_subject": f"Leave Approval Required: Employee {user_id}",
            "email_body": f"Please approve {leave_type.value} leave from {start_date} to {end_date}. Reason: {reason}"
        }

    except Exception as e:
        return {"error": f"Failed to submit leave request to the database: {str(e)}"}

@tool("cancel_leave", args_schema=CancelLeaveInput)
async def cancel_leave(user_id: str, leave_id: str) -> str:
    """
    Cancel an existing pending or approved leave request in the database.
    Use this when an employee wants to revoke a previously booked holiday.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(LeaveRequest).where(
                and_(LeaveRequest.id == leave_id, LeaveRequest.user_id == user_id)
            )
            result = await db.execute(stmt)
            leave_request = result.scalar_one_or_none()
            
            if not leave_request:
                return "Leave request not found or you do not have permission to cancel it."
            
            if leave_request.status in [LeaveStatus.cancelled, LeaveStatus.rejected]:
                return f"This leave request is already marked as {leave_request.status.value}."
                
            leave_request.status = LeaveStatus.cancelled
            await db.commit()
        
        return f"Leave request has been successfully canceled."
    except Exception as e:
        return f"Failed to cancel leave request: {str(e)}"