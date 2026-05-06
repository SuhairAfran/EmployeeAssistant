import uuid
from datetime import date, datetime
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sqlalchemy import select, and_, extract
from app.database import AsyncSessionLocal
from app.models import (
    PayrollRecord, Reimbursement, ReimbursementCategory, ReimbursementStatus
)

# ==========================================
# INPUT SCHEMAS
# ==========================================

class FetchPayslipInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee requesting their payslip.")
    year: int = Field(description="The year of the requested payslip (e.g., 2023).")
    month: int = Field(description="The numeric month of the requested payslip (1-12).")

class SubmitReimbursementInput(BaseModel):
    user_id: str = Field(description="The UUID of the employee submitting the claim.")
    category: ReimbursementCategory = Field(description="The category of the expense (e.g., 'travel', 'food', 'internet').")
    amount: float = Field(description="The total amount being claimed.")
    currency: str = Field(description="The 3-letter currency code (e.g., 'USD', 'INR').", default="USD")
    description: str = Field(description="A detailed explanation of the business expense.")
    expense_date: date = Field(description="The date the expense occurred (YYYY-MM-DD).")

# ==========================================
# TOOLS
# ==========================================

@tool("fetch_payslip", args_schema=FetchPayslipInput)
async def fetch_payslip(user_id: str, year: int, month: int) -> str:
    """
    Fetch the payslip details (gross salary, net salary, deductions) for a specific month.
    Use this strictly when an employee asks for their own salary or payslip information.
    """
    try:
        async with AsyncSessionLocal() as db:
            # PostgreSQL extraction for month and year matching
            stmt = select(PayrollRecord).where(
                and_(
                    PayrollRecord.user_id == user_id,
                    extract('year', PayrollRecord.pay_month) == year,
                    extract('month', PayrollRecord.pay_month) == month
                )
            )
            result = await db.execute(stmt)
            payslip = result.scalar_one_or_none()
            
            if not payslip:
                month_name = date(year, month, 1).strftime('%B')
                return f"I couldn't find a generated payslip for {month_name} {year}. Please ensure the payroll for that month has been processed."
            
            # Format the financial data nicely
            response = f"**Payslip Summary for {payslip.pay_month.strftime('%B %Y')}**\n"
            response += f"- **Gross Salary:** {payslip.gross_salary:,.2f}\n"
            response += f"- **Basic Pay:** {payslip.basic:,.2f}\n"
            response += f"- **Allowances:** {payslip.allowances:,.2f}\n"
            response += f"- **Tax Deductions (TDS):** -{payslip.tds:,.2f}\n"
            response += f"- **Net Salary:** **{payslip.net_salary:,.2f}**\n\n"
            
            if payslip.payslip_url:
                response += f"[Click here to download your full PDF payslip]({payslip.payslip_url})"
                
            return response
            
    except Exception as e:
        return f"Error fetching payslip details: {str(e)}"

@tool("submit_reimbursement", args_schema=SubmitReimbursementInput)
async def submit_reimbursement(user_id: str, category: ReimbursementCategory, amount: float, currency: str, description: str, expense_date: date) -> Dict[str, Any]:
    """
    Submit a new expense reimbursement claim to the database.
    Use this when an employee wants to get paid back for business expenses like travel or meals.
    Requires manager and finance approval.
    """
    try:
        if amount <= 0:
            return {"error": "Reimbursement amount must be greater than zero."}

        # Generate a readable claim number
        claim_no = f"EXP-{uuid.uuid4().hex[:6].upper()}"

        async with AsyncSessionLocal() as db:
            new_claim = Reimbursement(
                claim_no=claim_no,
                user_id=user_id,
                category=category,
                amount=amount,
                currency=currency.upper(),
                description=description,
                expense_date=expense_date,
                status=ReimbursementStatus.submitted
            )
            db.add(new_claim)
            await db.commit()
            await db.refresh(new_claim)
            
            claim_id = str(new_claim.id)

        # Trigger Manager Approval Process!
        return {
            "status": "success",
            "message": f"Your reimbursement claim ({claim_no}) for {currency.upper()} {amount:,.2f} has been submitted.",
            "approval_required": True,
            "claim_id": claim_id,
            "email_triggered": True,
            "email_recipients": ["manager@company.com"], 
            "email_subject": f"Expense Approval Required: {claim_no}",
            "email_body": f"Employee {user_id} submitted a {category.value} expense for {currency.upper()} {amount:,.2f}.\n\nDescription: {description}\nDate: {expense_date}"
        }

    except Exception as e:
        return {"error": f"Failed to submit reimbursement claim: {str(e)}"}