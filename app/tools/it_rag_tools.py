"""IT-specific RAG tool wrapper.

Exposes a state-bound ``search_it_policies`` LangChain tool to the LLM. The
LLM only controls the semantic ``query`` argument; the user's role and the
IT department are injected from trusted workflow state via a factory.
"""
from __future__ import annotations

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from app.models import DocDepartment, UserRole
from app.services.rag_service import search_policy_context


class ITPolicySearchInput(BaseModel):
    query: str = Field(
        description=(
            "The IT policy / FAQ question or topic to look up. Use natural "
            "language; the retriever handles semantic matching."
        )
    )


def build_it_policy_tool(user_role: UserRole) -> BaseTool:
    """Build a state-bound IT policy search tool for the given user role.

    The returned tool exposes only ``query`` to the LLM. The role and IT
    department are baked in from trusted backend state so the model cannot
    bypass RBAC by lying about identity.
    """

    @tool("search_it_policies", args_schema=ITPolicySearchInput)
    async def search_it_policies(query: str) -> str:
        """Search the IT policy / handbook knowledge base for the answer
        to an IT-related policy or procedure question. Covers: VPN setup,
        password policy, software installation, asset request procedures,
        hardware troubleshooting guides, security policies, WFH/remote
        access, network configuration, BYOD policy, etc.

        TRIGGER PHRASES: "what is the IT policy on [X]", "how do I set
        up VPN", "password requirements", "can I install software",
        "IT security policy", "remote access policy", "BYOD policy",
        "how to connect to the network", "IT onboarding checklist".

        Returns the most relevant policy sections, which you MUST
        reason over to answer the user — even when the exact keywords
        do not appear verbatim.

        DO NOT call this for reporting IT problems or creating tickets
        — use create_it_ticket instead. DO NOT call this for known
        issue lookups — use search_known_issues instead. DO NOT call
        this for HR policy questions — use search_hr_policies instead.
        """
        return await search_policy_context(
            query=query,
            user_role=user_role,
            department=DocDepartment.it,
        )

    return search_it_policies
