from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.schemas.chat import ChatRequest, ChatResponse
from app.graph.workflow import run_workflow
# Assuming you have a dependency that extracts the user from a JWT/API token
# from app.middleware.rbac import get_current_user_ctx

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# --- MOCK DEPENDENCY (Replace with your actual auth middleware) ---
async def get_current_user_ctx() -> Dict[str, Any]:
    """Mocks the user context that would normally come from a decoded JWT."""
    from app.models import UserRole
    return {
        "user_id": "user-uuid-1234",
        "user_email": "alice@company.com",
        "user_name": "Alice Smith",
        "user_role": UserRole.employee, # Change this to test manager/admin flows
        "department_id": "dept-uuid-hr",
    }
# ------------------------------------------------------------------

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest, 
    user_ctx: Dict[str, Any] = Depends(get_current_user_ctx)
):
    """
    Send a message to the enterprise assistant. 
    Routes automatically to HR, IT, Finance, or RAG based on intent.
    """
    try:
        # 1. Invoke the LangGraph workflow
        final_state = await run_workflow(
            user_ctx=user_ctx, 
            query=request.query, 
            session_id=request.session_id
        )

        # 2. Return the structured response
        return ChatResponse(
            session_id=final_state.get("session_id"),
            response=final_state.get("response", "I'm sorry, I couldn't process that request."),
            intent=final_state.get("intent", "unknown"),
            approval_required=final_state.get("approval_required", False),
            metadata=final_state.get("metadata", {})
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))