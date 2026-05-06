from typing import List
from langchain_core.tools import BaseTool
from app.models import UserRole

# Import all domain tools
from app.tools.rag_tools import search_company_policies
from app.tools.hr_tools import get_leave_balance, apply_for_leave, cancel_leave
from app.tools.it_tools import create_it_ticket, get_ticket_status, request_it_asset
from app.tools.finance_tools import fetch_payslip, submit_reimbursement

def get_tools_for_intent(intent: str, user_role: UserRole) -> List[BaseTool]:
    """
    Returns the specific list of LangChain tools available for a given intent.
    This prevents overwhelming the LLM with unnecessary tools and enforces RBAC.
    """
    tools = []
    
    # 1. RAG / Policy Tools (Available to almost everyone based on intent)
    if "policy" in intent or intent == "general.unknown":
        tools.append(search_company_policies)
        
    # 2. HR Tools
    if intent.startswith("hr.leave"):
        tools.extend([get_leave_balance, apply_for_leave, cancel_leave])
        
    # 3. IT Tools
    elif intent.startswith("it"):
        tools.extend([create_it_ticket, get_ticket_status, request_it_asset])
        
    # 4. Finance Tools
    elif intent.startswith("finance"):
        tools.extend([fetch_payslip, submit_reimbursement])
        
    return tools