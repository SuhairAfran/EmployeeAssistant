from datetime import date, datetime
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_, or_
from app.database import AsyncSessionLocal
from app.models import LeaveRequest, LeaveBalance, LeaveType, LeaveStatus, User

# ==========================================
# INPUT SCHEMAS
# ==========================================

class LeaveBalanceInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting their leave balance.")
    year: int = Field(description="The current year to check the balance for.")

class ApplyLeaveInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee applying for leave.")
    start_date: date = Field(description="The confirmed start date of the leave (YYYY-MM-DD). Ask the user if missing.")
    end_date: date = Field(description="The confirmed end date of the leave (YYYY-MM-DD). Use start_date for a single-day leave; ask the user if unclear.")
    leave_type: LeaveType = Field(description="The confirmed leave type, such as sick, casual, earned, bereavement, maternity, paternity, miscarriage, unpaid, or compensatory. Ask the user if unclear.")
    business_days: float = Field(description="The estimated working days requested. The server recomputes this; use 1.0 for a single working day.")
    reason: str = Field(description="A brief user-provided reason for the leave. Ask the user if missing; do not invent one.")

class CancelLeaveInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee canceling their leave.")
    leave_id: str = Field(description="The UUID of the leave request to cancel.")

class ViewLeaveHistoryInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee viewing their leave history.")

class ViewTeamLeavesInput(BaseModel):
    manager_id: str = Field(description="The UUID of the manager viewing their team's leaves.")

class ViewDepartmentOnLeaveTodayInput(BaseModel):
    user_id: str = Field(description="The UUID of the user checking who is on leave today in their department.")
    target_name: str = Field(description="The name of the person to check (e.g., 'Alice Smith').")

# ==========================================
# TOOLS
# ==========================================

@tool("get_leave_balance", args_schema=LeaveBalanceInput)
async def get_leave_balance(user_id: str, year: int) -> str:
    """
    Fetch the current leave balances for an employee from the database.
    Returns a Markdown table of eligible leave types with entitled, used,
    pending, carried-over, and available days.

    TRIGGER PHRASES: "check my leave balance", "how many leaves do I have",
    "days off remaining", "leave entitlement", "how much sick/casual/earned
    leave do I have left", "show my leave balance", "available leave".

    DO NOT call this tool if the user wants to apply for leave — use
    apply_for_leave instead. DO NOT call this if the user is asking about
    their leave history/past requests — use view_leave_history instead.
    """
    try:
        async with AsyncSessionLocal() as db:
            # Fetch user to determine eligibility
            user_stmt = select(User).where(User.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                return "User not found."
            
            # Fetch all balances for the user and year
            stmt = select(LeaveBalance).where(
                and_(LeaveBalance.user_id == user_id, LeaveBalance.year == year)
            )
            result = await db.execute(stmt)
            balances = result.scalars().all()
            
            if not balances:
                return "I couldn't find any leave balance records for you in the system for this year."
            
            # Filter balances based on eligibility
            eligible_balances = []
            for b in balances:
                lt = b.leave_type.value
                # Everyone: earned, sick, bereavement, unpaid
                if lt in ['earned', 'sick', 'bereavement', 'unpaid', 'compensatory']:
                    eligible_balances.append(b)
                # Female employees: maternity, miscarriage
                elif lt in ['maternity', 'miscarriage'] and user.gender == 'female':
                    eligible_balances.append(b)
                # Married male employees: paternity
                elif lt == 'paternity' and user.gender == 'male' and user.is_married:
                    eligible_balances.append(b)
            
            # Build Markdown table
            response = "| Leave Type | Entitled | Used | Pending | Carried Over | Available |\n"
            response += "|-----------|----------|------|---------|--------------|----------|\n"
            for b in eligible_balances:
                response += f"| {b.leave_type.value.capitalize()} | {b.entitled_days} | {b.used_days} | {b.pending_days} | {b.carried_over} | {b.available_days} |\n"
            
            # Add unpaid policy note
            response += "\n**Note:** Unpaid leave is only available for medical/personal emergencies after all earned leave is exhausted."
            
            return response
            
    except Exception as e:
        return f"Error fetching leave balance: {str(e)}"

def _compute_business_days(start_date: date, end_date: date) -> float:
    """Compute business days excluding Saturdays and Sundays."""
    from datetime import timedelta
    
    if end_date < start_date:
        return 0
    
    total_days = (end_date - start_date).days + 1
    business_days = 0
    current = start_date
    
    for _ in range(total_days):
        if current.weekday() < 5:  # Monday=0, Friday=4
            business_days += 1
        current += timedelta(days=1)
    
    return float(business_days)


async def _check_holidays(start_date: date, end_date: date) -> int:
    """Count holidays in the date range from holiday_calendar."""
    from app.models import HolidayCalendar
    async with AsyncSessionLocal() as db:
        stmt = select(HolidayCalendar).where(
            and_(
                HolidayCalendar.holiday_date >= start_date,
                HolidayCalendar.holiday_date <= end_date,
                HolidayCalendar.is_optional.is_(False),
            )
        )
        result = await db.execute(stmt)
        holidays = result.scalars().all()
        return len(holidays)


@tool("apply_for_leave", args_schema=ApplyLeaveInput)
async def apply_for_leave(user_id: str, start_date: date, end_date: date, leave_type: LeaveType, business_days: float, reason: str) -> Dict[str, Any]:
    """
    Submit a new leave request for an employee to the database.
    Computes business days server-side, checks weekends/holidays, overlaps,
    and eligibility.

    TRIGGER PHRASES: "apply for leave", "book leave", "take time off",
    "I want sick/casual/earned leave", "request annual leave", "I need X
    days off from [date]", "can I take leave on [date]", "I am not well",
    "I'm sick", "I have fever", "I can't come today", "I need time off".

    BEFORE calling: you MUST have confirmed ALL FOUR of these from the user:
      1. leave_type (sick / casual / earned / bereavement / maternity /
         paternity / miscarriage / unpaid / compensatory)
      2. start_date (YYYY-MM-DD)
      3. end_date (YYYY-MM-DD) — same as start_date for a single day
      4. reason — a brief user-provided explanation; do NOT invent one
    
    CRITICAL RULES BEFORE ASKING FOR DATES:
    - Check the user's Gender and Marital Status from your context.
    - Maternity/Miscarriage leave: ONLY for females. Reject instantly for males.
    - Paternity leave: ONLY for married males. Reject instantly if female or single.
    - Do NOT ask for dates if the user is ineligible for the requested leave type.
    - Employees cannot apply for backdated leaves (start date in the past). Reject if they try.

    If ANY required detail is missing (and they are eligible), ask a concise
    follow-up for ONLY the missing detail instead of calling this tool.

    DO NOT call this tool if the user is only asking about their balance
    or history. DO NOT call this to cancel a request — use cancel_leave.
    """
    try:
        from datetime import datetime
        today = datetime.now().date()
        if start_date < today:
            return {"error": "Backdated leave applications are not allowed. The start date must be today or in the future."}

        if end_date < start_date:
            return {"error": "The end date cannot be before the start date."}

        async with AsyncSessionLocal() as db:
            # Fetch user for eligibility checks
            user_stmt = select(User).where(User.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found."}
            
            # Compute business days (excluding weekends)
            computed_business_days = _compute_business_days(start_date, end_date)
            
            # Count holidays in the range
            holiday_count = await _check_holidays(start_date, end_date)
            adjusted_business_days = max(0, computed_business_days - holiday_count)
            
            if adjusted_business_days == 0:
                return {"error": "The requested dates fall entirely on weekends or holidays. Please choose different dates."}
            
            # Check for overlapping leave requests (pending or approved)
            overlap_stmt = select(LeaveRequest).where(
                and_(
                    LeaveRequest.user_id == user_id,
                    LeaveRequest.status.in_([LeaveStatus.pending, LeaveStatus.approved]),
                    or_(
                        and_(LeaveRequest.start_date <= start_date, LeaveRequest.end_date >= start_date),
                        and_(LeaveRequest.start_date <= end_date, LeaveRequest.end_date >= end_date),
                        and_(LeaveRequest.start_date >= start_date, LeaveRequest.end_date <= end_date)
                    )
                )
            )
            overlap_result = await db.execute(overlap_stmt)
            overlapping_leaves = overlap_result.scalars().all()
            
            if overlapping_leaves:
                return {"error": "You already have a pending or approved leave request that overlaps with these dates."}
            
            # Eligibility checks based on gender/marital status
            lt = leave_type.value
            
            # Maternity and miscarriage: females only
            if lt in ['maternity', 'miscarriage'] and user.gender != 'female':
                return {"error": f"{lt.capitalize()} leave is only available for female employees."}
            
            # Paternity: married males only
            if lt == 'paternity':
                if user.gender != 'male':
                    return {"error": "Paternity leave is only available for male employees."}
                if not user.is_married:
                    return {"error": "Paternity leave is only available for married male employees."}
            
            # Unpaid: only for medical/personal emergencies after earned leave is exhausted
            if lt == 'unpaid':
                earned_stmt = select(LeaveBalance).where(
                    and_(
                        LeaveBalance.user_id == user_id,
                        LeaveBalance.year == start_date.year,
                        LeaveBalance.leave_type == LeaveType.earned
                    )
                )
                earned_result = await db.execute(earned_stmt)
                earned_balance = earned_result.scalar_one_or_none()
                
                if earned_balance and earned_balance.available_days > 0:
                    return {"error": "Unpaid leave is only available after all earned leave is exhausted. You still have earned leave available."}
                
                # Check if reason indicates medical/personal emergency
                _EMERGENCY_KEYWORDS = [
                    # Medical / health
                    "medical", "health", "hospital", "doctor", "physician", "clinic",
                    "surgery", "operation", "procedure", "treatment", "therapy",
                    "diagnosis", "checkup", "test", "scan", "mri", "xray", "x-ray",
                    "chemotherapy", "dialysis", "icu", "intensive care", "ward",
                    "admission", "admitted", "discharge", "prescription", "medication",
                    "medicine", "illness", "ill", "sick", "sickness", "disease",
                    "infection", "fever", "injury", "injured", "wound", "fracture",
                    "broken", "sprain", "concussion", "stroke", "heart attack",
                    "cardiac", "respiratory", "breathing", "asthma", "covid",
                    "quarantine", "isolation", "mental health", "anxiety", "depression",
                    "psychiatric", "counselling", "counseling", "rehab", "recovery",
                    "post-operative", "post operative", "follow-up", "follow up",
                    "ambulance", "emergency room", "er visit", "urgent care",
                    # Family / caregiving
                    "family", "parent", "father", "mother", "spouse", "husband", "wife",
                    "child", "children", "son", "daughter", "sibling", "brother",
                    "sister", "grandparent", "grandfather", "grandmother", "relative",
                    "caregiver", "caretaker", "care for", "taking care", "looking after",
                    "dependent", "newborn", "infant", "elderly", "aged", "bedridden",
                    "critical condition", "critical", "serious condition", "serious",
                    "life-threatening", "life threatening", "terminal",
                    "passed away", "death", "demise", "funeral", "mourning",
                    "bereavement", "grieving", "grief",
                    # Accidents / disasters
                    "accident", "met with", "road accident", "vehicle accident",
                    "fire", "flood", "natural disaster", "earthquake", "cyclone",
                    "storm", "damage", "loss", "evacuation", "displaced",
                    # Urgent / personal
                    "emergency", "urgent", "urgently", "crisis", "sudden", "abrupt",
                    "unexpected", "unforeseen", "unforeseeable", "unavoidable",
                    "unavoidably", "personal", "personal matter", "personal reasons",
                    "personal issue", "domestic", "home emergency", "house",
                    "legal", "court", "court hearing", "subpoena", "police",
                    "court order", "legal matter", "legal proceedings",
                ]
                if not any(keyword in reason.lower() for keyword in _EMERGENCY_KEYWORDS):
                    return {"error": "Unpaid leave is only available for medical or personal emergencies. Please provide more detail about your situation in the reason (e.g., medical condition, family emergency, accident, etc.)."}
            
            # Check available balance for paid leave types
            if lt not in ['unpaid', 'compensatory']:
                balance_stmt = select(LeaveBalance).where(
                    and_(
                        LeaveBalance.user_id == user_id,
                        LeaveBalance.year == start_date.year,
                        LeaveBalance.leave_type == leave_type
                    )
                )
                balance_result = await db.execute(balance_stmt)
                balance = balance_result.scalar_one_or_none()
                
                if not balance:
                    return {"error": f"No balance record found for {lt} leave."}
                
                if balance.available_days < adjusted_business_days:
                    return {"error": f"Insufficient {lt} leave balance. You have {balance.available_days} days available, but requested {adjusted_business_days} days."}
            
            # Create the leave request
            new_leave = LeaveRequest(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                leave_type=leave_type,
                business_days=adjusted_business_days,
                reason=reason,
                status=LeaveStatus.pending
            )
            db.add(new_leave)
            
            # Increment pending_days in leave balance (while balance is still attached)
            if lt not in ['unpaid', 'compensatory']:
                balance.pending_days += adjusted_business_days
                
            # Commit once at the end
            await db.commit()
            await db.refresh(new_leave)
            
            generated_leave_id = str(new_leave.id)

        return {
            "status": "success",
            "message": (
                f"Leave request for {start_date} to {end_date} "
                f"({adjusted_business_days} business days) has been submitted "
                f"for approval. Your manager will see it in their approvals "
                f"dashboard, and you'll see the status update in yours."
            ),
            "approval_required": True,
            "leave_id": generated_leave_id,
        }

    except Exception as e:
        return {"error": f"Failed to submit leave request to the database: {str(e)}"}

@tool("cancel_leave", args_schema=CancelLeaveInput)
async def cancel_leave(user_id: str, leave_id: str) -> str:
    """
    Cancel an existing pending leave request in the database.
    Only works while the request is still pending (not yet approved).
    Restores pending_days balance when cancelled.

    TRIGGER PHRASES: "cancel my leave", "revoke leave request", "withdraw
    my leave application", "I don't need that leave anymore", "undo my
    leave request".

    BEFORE calling: you MUST have the leave_id. If the user doesn't know
    their leave_id, call view_leave_history first to show them their
    requests, then ask which one to cancel.

    DO NOT call this to apply for new leave — use apply_for_leave.
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
            
            if leave_request.status == LeaveStatus.cancelled:
                return "This leave request is already cancelled."
            
            if leave_request.status == LeaveStatus.rejected:
                return "This leave request was rejected and cannot be cancelled."
            
            # Only allow cancellation while pending
            if leave_request.status != LeaveStatus.pending:
                return f"This leave request has been {leave_request.status.value} and cannot be cancelled. Please contact your manager or HR."
            
            # Restore pending_days balance
            lt = leave_request.leave_type.value
            if lt not in ['unpaid', 'compensatory']:
                balance_stmt = select(LeaveBalance).where(
                    and_(
                        LeaveBalance.user_id == user_id,
                        LeaveBalance.year == leave_request.start_date.year,
                        LeaveBalance.leave_type == leave_request.leave_type
                    )
                )
                balance_result = await db.execute(balance_stmt)
                balance = balance_result.scalar_one_or_none()
                
                if balance:
                    balance.pending_days = max(0, balance.pending_days - leave_request.business_days)
            
            # Mark as cancelled
            leave_request.status = LeaveStatus.cancelled
            await db.commit()
        
        return f"Leave request has been successfully cancelled."
    except Exception as e:
        return f"Failed to cancel leave request: {str(e)}"


@tool("view_leave_history", args_schema=ViewLeaveHistoryInput)
async def view_leave_history(user_id: str) -> str:
    """
    View an employee's own leave request history with type, dates, business
    days, and status.

    TRIGGER PHRASES: "show my leave history", "my leave requests", "past
    leaves", "leave status", "did my leave get approved", "what leaves
    have I taken", "show my pending leaves", "check status of my leave".

    DO NOT call this to apply for or cancel leave. DO NOT call this for
    leave balance — use get_leave_balance instead.
    """
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(LeaveRequest).where(
                LeaveRequest.user_id == user_id
            ).order_by(LeaveRequest.applied_at.desc())
            result = await db.execute(stmt)
            leaves = result.scalars().all()
            
            if not leaves:
                return "You have no leave requests in the system."
            
            response = "| Leave ID | Leave Type | Start Date | End Date | Business Days | Status | Applied On |\n"
            response += "|----------|-----------|------------|----------|---------------|--------|------------|\n"
            
            for leave in leaves:
                response += f"| {leave.id} | {leave.leave_type.value.capitalize()} | {leave.start_date} | {leave.end_date} | {leave.business_days} | {leave.status.value.capitalize()} | {leave.applied_at.strftime('%Y-%m-%d')} |\n"
            
            return response
    except Exception as e:
        return f"Error fetching leave history: {str(e)}"


@tool("view_team_leaves", args_schema=ViewTeamLeavesInput)
async def view_team_leaves(manager_id: str) -> str:
    """
    View direct reports' leave requests (manager/admin/HR only).
    Shows leave type, dates, business days, status, and employee name.

    TRIGGER PHRASES: "show my team's leaves", "team leave requests",
    "who on my team is on leave", "pending approvals", "my team's leave
    status", "show leaves for my direct reports".

    This tool is ONLY available to managers, admins, and HR team members.
    DO NOT call this for an employee's own leave history — use
    view_leave_history instead.
    """
    try:
        async with AsyncSessionLocal() as db:
            # Fetch all users whose manager_id is the given manager_id
            users_stmt = select(User).where(User.manager_id == manager_id)
            users_result = await db.execute(users_stmt)
            team_members = users_result.scalars().all()
            
            if not team_members:
                return "You have no direct reports."
            
            team_member_ids = [u.id for u in team_members]
            
            # Fetch all leave requests for team members
            leaves_stmt = select(LeaveRequest).where(
                LeaveRequest.user_id.in_(team_member_ids)
            ).order_by(LeaveRequest.applied_at.desc())
            leaves_result = await db.execute(leaves_stmt)
            leaves = leaves_result.scalars().all()
            
            if not leaves:
                return "No leave requests found for your team."
            
            # Create a mapping of user_id to full_name
            user_map = {u.id: u.full_name for u in team_members}
            
            response = "| Employee | Leave Type | Start Date | End Date | Business Days | Status | Applied On |\n"
            response += "|----------|-----------|------------|----------|---------------|--------|------------|\n"
            
            for leave in leaves:
                employee_name = user_map.get(leave.user_id, "Unknown")
                response += f"| {employee_name} | {leave.leave_type.value.capitalize()} | {leave.start_date} | {leave.end_date} | {leave.business_days} | {leave.status.value.capitalize()} | {leave.applied_at.strftime('%Y-%m-%d')} |\n"
            
            return response
    except Exception as e:
        return f"Error fetching team leaves: {str(e)}"


@tool("view_department_on_leave_today", args_schema=ViewDepartmentOnLeaveTodayInput)
async def view_department_on_leave_today(user_id: str, target_name: str) -> str:
    """
    Check if a specific person in the same department is on leave today.
    Only checks the current date, not future dates.

    TRIGGER PHRASES: "is [name] in the office today", "why isn't [name]
    at work", "is [name] on leave", "where is [name] today", "is [name]
    absent", "is [name] available today".

    BEFORE calling: you MUST have the target person's name from the user.

    DO NOT call this for checking the user's own leave — use
    view_leave_history instead. DO NOT use for team-wide leave views — use
    view_team_leaves (manager only).
    """
    try:
        async with AsyncSessionLocal() as db:
            # Fetch the requester to get their department
            requester_stmt = select(User).where(User.id == user_id)
            requester_result = await db.execute(requester_stmt)
            requester = requester_result.scalar_one_or_none()
            
            if not requester or not requester.department_id:
                return "Unable to determine your department."
            
            # Find the target person by name in the same department
            target_stmt = select(User).where(
                and_(
                    User.department_id == requester.department_id,
                    User.full_name.ilike(f"%{target_name}%")
                )
            )
            target_result = await db.execute(target_stmt)
            target = target_result.scalar_one_or_none()
            
            if not target:
                return f"Could not find anyone named '{target_name}' in your department."
            
            # Check if target has approved leave today
            today = date.today()
            leave_stmt = select(LeaveRequest).where(
                and_(
                    LeaveRequest.user_id == target.id,
                    LeaveRequest.status == LeaveStatus.approved,
                    LeaveRequest.start_date <= today,
                    LeaveRequest.end_date >= today
                )
            )
            leave_result = await db.execute(leave_stmt)
            leave = leave_result.scalar_one_or_none()
            
            if leave:
                return f"{target.full_name} is on {leave.leave_type.value} leave today from {leave.start_date} to {leave.end_date}."
            else:
                return f"{target.full_name} is not on leave today. They may simply be running late or in a meeting."
    except Exception as e:
        return f"Error checking leave status: {str(e)}"


# ==========================================
# APPROVAL TOOLS (Manager / Admin / HR only)
# ==========================================

class ApproveLeaveInput(BaseModel):
    manager_id: str = Field(
        description="The UUID of the manager/HR/admin taking the approval action. Use the user_id from user context."
    )
    leave_id: str = Field(
        description="The UUID of the leave request to approve or reject. Obtain this from view_team_leaves."
    )
    decision: str = Field(
        description="The decision: must be exactly 'approved' or 'rejected'."
    )
    note: str = Field(
        default="",
        description="Optional short note explaining the decision (e.g. 'Team coverage confirmed')."
    )
    confirmed: bool = Field(
        description=(
            "Must be True. The agent MUST ask the manager to confirm before calling this tool. "
            "Never set this to True without an explicit confirmation from the manager in the chat."
        )
    )


@tool("approve_leave", args_schema=ApproveLeaveInput)
async def approve_leave(
    manager_id: str,
    leave_id: str,
    decision: str,
    note: str = "",
    confirmed: bool = False,
) -> Dict[str, Any]:
    """
    Approve or reject a direct report's pending leave request via chat.

    AVAILABLE TO: managers, admin, hr_team only.

    TRIGGER PHRASES: "approve [name]'s leave", "reject the leave request",
    "I want to approve leave ID ...", "decline Alice's sick leave",
    "approve pending leave", "can I approve this?".

    MANDATORY FLOW — follow this exactly every time:
      1. Call view_team_leaves to show the manager their pending requests.
      2. Identify the leave_id the manager wants to act on.
      3. Summarise: employee name, leave type, dates, business days.
      4. Ask explicitly: "Do you want to APPROVE or REJECT this leave?
         Type YES to confirm."
      5. Only after the manager says YES / confirms, call this tool with
         confirmed=True.
      6. NEVER call this tool with confirmed=False — that is a hard error.
      7. NEVER invent a leave_id. Always show the manager the list first.

    SECURITY: This tool verifies that the leave requester's manager_id
    matches the acting manager_id. Cross-department approvals are blocked.
    """
    if not confirmed:
        return {
            "error": (
                "Approval not confirmed. Please ask the manager to explicitly "
                "confirm before proceeding."
            )
        }

    decision = decision.strip().lower()
    if decision not in ("approved", "rejected"):
        return {"error": f"Invalid decision '{decision}'. Must be 'approved' or 'rejected'."}

    try:
        from datetime import datetime as dt
        async with AsyncSessionLocal() as db:
            # Fetch the leave request
            leave_stmt = select(LeaveRequest).where(LeaveRequest.id == leave_id)
            leave_result = await db.execute(leave_stmt)
            leave_request = leave_result.scalar_one_or_none()

            if not leave_request:
                return {"error": f"Leave request '{leave_id}' not found."}

            if leave_request.status != LeaveStatus.pending:
                return {
                    "error": (
                        f"This leave is already '{leave_request.status.value}' "
                        "and cannot be actioned again."
                    )
                }

            # Security: verify the acting manager actually manages this employee
            employee_stmt = select(User).where(User.id == leave_request.user_id)
            employee_result = await db.execute(employee_stmt)
            employee = employee_result.scalar_one_or_none()

            if not employee:
                return {"error": "The employee associated with this leave was not found."}

            # Allow admin / hr_team to bypass the manager_id check
            acting_user_stmt = select(User).where(User.id == manager_id)
            acting_result = await db.execute(acting_user_stmt)
            acting_user = acting_result.scalar_one_or_none()

            if not acting_user:
                return {"error": "Acting user not found."}

            is_privileged = acting_user.role in (UserRole.admin, UserRole.hr_team)
            is_direct_manager = str(employee.manager_id) == str(manager_id)

            if not is_privileged and not is_direct_manager:
                return {
                    "error": (
                        f"{employee.full_name} is not your direct report. "
                        "You can only approve leaves for employees who report directly to you."
                    )
                }

            # Update leave request status
            leave_request.status = (
                LeaveStatus.approved if decision == "approved" else LeaveStatus.rejected
            )
            leave_request.reviewed_by = manager_id
            leave_request.reviewed_at = dt.utcnow()
            leave_request.reviewer_note = note or None

            # Update leave balance
            lt = leave_request.leave_type.value
            if lt not in ("unpaid", "compensatory"):
                balance_stmt = select(LeaveBalance).where(
                    and_(
                        LeaveBalance.user_id == leave_request.user_id,
                        LeaveBalance.year == leave_request.start_date.year,
                        LeaveBalance.leave_type == leave_request.leave_type,
                    )
                )
                balance_result = await db.execute(balance_stmt)
                balance = balance_result.scalar_one_or_none()

                if balance:
                    # Always clear the pending days regardless of decision
                    balance.pending_days = max(
                        0, balance.pending_days - leave_request.business_days
                    )
                    if decision == "approved":
                        # Move days into used
                        balance.used_days += leave_request.business_days

            await db.commit()

        action_word = "approved" if decision == "approved" else "rejected"
        return {
            "status": "success",
            "message": (
                f"Leave request for {employee.full_name} ({leave_request.leave_type.value} leave, "
                f"{leave_request.start_date} – {leave_request.end_date}, "
                f"{leave_request.business_days} business day(s)) has been **{action_word}**."
                + (f" Note: {note}" if note else "")
            ),
            "leave_id": str(leave_request.id),
            "decision": decision,
            "employee": employee.full_name,
        }

    except Exception as e:
        return {"error": f"Failed to process approval: {str(e)}"}