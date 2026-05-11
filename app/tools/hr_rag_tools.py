"""HR-specific RAG tool wrapper.

Exposes a state-bound ``search_hr_policies`` LangChain tool to the LLM. The
LLM only controls the semantic ``query`` argument; the user's role and the
HR department are injected from trusted workflow state via a factory.
"""
from __future__ import annotations

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from app.models import DocDepartment, UserRole
from app.services.rag_service import search_policy_context


class HRPolicySearchInput(BaseModel):
    query: str = Field(
        description=(
            "The HR policy question or topic to look up. Use natural language; "
            "the retriever handles semantic matching."
        )
    )


def build_hr_policy_tool(user_role: UserRole) -> BaseTool:
    """Build a state-bound HR policy search tool for the given user role.

    The returned tool exposes only ``query`` to the LLM. The role and HR
    department are baked in from trusted backend state so the model cannot
    bypass RBAC by lying about identity.
    """

    @tool("search_hr_policies", args_schema=HRPolicySearchInput)
    async def search_hr_policies(query: str) -> str:
        """Search the HR policy knowledge base for the answer to an
        HR-related question. Covers: employee handbook, leave policy,
        attendance, dress code, code of conduct, benefits, ID cards,
        probation, notice period, grievance procedures, etc.

        TRIGGER PHRASES: "what is the dress code", "leave policy",
        "how many sick days do I get", "company holiday list", "notice
        period", "what are the office hours", "can I work from home",
        "maternity leave policy", "reimbursement policy", "ID card",
        "employee benefits", "code of conduct", "probation period",
        any "what is the policy on [X]" question.

        Returns the most relevant policy sections, which you MUST
        reason over to answer the user — even when the exact keywords
        do not appear verbatim.

        DO NOT call this for leave applications, balances, or history
        — use the leave tools instead. DO NOT call this for IT policy
        questions — use search_it_policies instead.
        """
        return await search_policy_context(
            query=query,
            user_role=user_role,
            department=DocDepartment.hr,
        )

    return search_hr_policies
