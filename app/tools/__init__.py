from typing import List
from langchain_core.tools import BaseTool
from app.models import UserRole

# Import the RAG tool we just created
from app.tools.rag_tools import search_company_policies

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
        tools.append(get_leave_balance)
        tools.append(apply_for_leave)
        tools.append(cancel_leave)
        pass
        
    # 3. IT Tools
    elif intent.startswith("it"):
        # tools.append(create_it_ticket)
        # tools.append(check_ticket_status)
        pass
        
    # 4. Finance Tools
    elif intent.startswith("finance"):
        # tools.append(fetch_payslip)
        # tools.append(submit_reimbursement)
        pass
        
    return tools