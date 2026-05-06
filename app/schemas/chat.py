from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's message.")
    session_id: Optional[str] = Field(None, description="Existing session ID for multi-turn conversations.")

class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    approval_required: bool = False
    metadata: Dict[str, Any] = {}

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="Must be 'approved' or 'rejected'")
    note: Optional[str] = Field(None, description="Optional reasoning for the decision")