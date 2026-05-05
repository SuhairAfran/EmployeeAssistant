from datetime import date
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Assuming you have an async database session setup in app/database.py
from app.database import AsyncSessionLocal
from sqlalchemy import select, func, and_
# Assuming these are your SQLAlchemy models
# from app.models import LeaveRequest, User 

# ==========================================
# INPUT SCHEMAS
# ==========================================

class LeaveBalanceInput(BaseModel):
    user_id: str = Field(description="The ID of the employee requesting their leave balance.")

class ApplyLeaveInput(BaseModel):
    user_id: str = Field(description="The ID of the employee applying for leave.")
    start_date: date = Field(description="The start date of the leave (YYYY-MM-DD).")
    end_date: date = Field(description="The end date of the leave (YYYY-MM-DD).")
    leave_type: str = Field(description="The type of leave (e.g., 'sick', 'annual', 'unpaid').")
    reason: str = Field(description="A brief reason for the leave.")

class CancelLeaveInput(BaseModel):
    user_id: str = Field(description="The ID of the employee canceling their leave.")
    leave_id: int = Field(description="The specific ID of the leave request to cancel.")

# ==========================================
# TOOLS
# ==========================================

@tool("get_leave_balance", args_schema=LeaveBalanceInput)
async def get_leave_balance(user_id: str) -> str:
    """
    Fetch the current leave balance for an employee. 
    Use this when an employee asks how many days off they have left.
    """
    try:
        # MOCK DB CALL - Replace with actual SQLAlchemy logic
        # async with AsyncSessionLocal() as db:
        #     stmt = select(User.annual_leave_balance, User.sick_leave_balance).where(User.id == user_id)
        #     result = await db.execute(stmt)
        #     balance = result.first()
        
        # Simulating a database fetch
        annual_balance = 14
        sick_balance = 5
        
        return f"You currently have {annual_balance} annual leave days and {sick_balance} sick leave days remaining."
    except Exception as e:
        return f"Error fetching leave balance: {str(e)}"

@tool("apply_for_leave", args_schema=ApplyLeaveInput)
async def apply_for_leave(user_id: str, start_date: date, end_date: date, leave_type: str, reason: str) -> Dict[str, Any]:
    """
    Submit a new leave request for an employee.
    Use this when an employee explicitly states they want to book time off.
    """
    try:
        # 1. Validation Check: Ensure end_date is after start_date
        if end_date < start_date:
            return {"error": "The end date cannot be before the start date."}

        # 2. Database Insertion Logic (Mocked)
        # async with AsyncSessionLocal() as db:
        #     new_leave = LeaveRequest(
        #         user_id=user_id,
        #         start_date=start_date,
        #         end_date=end_date,
        #         leave_type=leave_type,
        #         reason=reason,
        #         status="pending_approval"
        #     )
        #     db.add(new_leave)
        #     await db.commit()
        #     await db.refresh(new_leave)
        #     generated_leave_id = new_leave.id
        
        # Simulating DB insertion
        generated_leave_id = 8492 

        # 3. Return the trigger for the Graph's Human-in-the-loop!
        return {
            "status": "success",
            "message": f"Leave request for {start_date} to {end_date} has been drafted.",
            "approval_required": True,       # This triggers the interrupt() in workflow.py
            "leave_id": generated_leave_id,  # Passes the ID to the approval node
            # We can also trigger the email node directly from here
            "email_triggered": True,
            "email_recipients": ["manager@company.com"],
            "email_subject": f"Leave Approval Required: {user_id}",
            "email_body": f"Please approve {leave_type} leave from {start_date} to {end_date}. Reason: {reason}"
        }

    except Exception as e:
        return {"error": f"Failed to submit leave request: {str(e)}"}

@tool("cancel_leave", args_schema=CancelLeaveInput)
async def cancel_leave(user_id: str, leave_id: int) -> str:
    """
    Cancel an existing pending or approved leave request.
    Use this when an employee wants to revoke a previously booked holiday.
    """
    try:
        # async with AsyncSessionLocal() as db:
        #     stmt = select(LeaveRequest).where(and_(LeaveRequest.id == leave_id, LeaveRequest.user_id == user_id))
        #     result = await db.execute(stmt)
        #     leave_request = result.scalar_one_or_none()
        #     
        #     if not leave_request:
        #         return "Leave request not found or you do not have permission to cancel it."
        #         
        #     leave_request.status = "canceled"
        #     await db.commit()
        
        return f"Leave request #{leave_id} has been successfully canceled."
    except Exception as e:
        return f"Failed to cancel leave request: {str(e)}"