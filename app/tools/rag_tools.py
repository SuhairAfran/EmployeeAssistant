"""RAG retrieval tool — queries Supabase Postgres (pgvector) for policy chunks.

Replaces the previous ChromaDB-based implementation. RBAC is enforced at the
SQL level by filtering on `rag_documents.department` and the
`rag_documents.roles_allowed` array.
"""
from __future__ import annotations

from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import DocDepartment, RAGChunk, RAGDocument, UserRole


# ── Embedding client (shared) ─────────────────────────────────────────────────

def _build_embedder() -> OpenAIEmbeddings:
    kwargs: dict = {
        "api_key": settings.OPENAI_API_KEY,
        "model": settings.EMBEDDING_MODEL,
    }
    if not getattr(settings, "OPENAI_VERIFY_SSL", True):
        import httpx
        kwargs["http_client"] = httpx.Client(verify=False)
        kwargs["http_async_client"] = httpx.AsyncClient(verify=False)
    return OpenAIEmbeddings(**kwargs)


_embedder = _build_embedder()


# ── Helpers ───────────────────────────────────────────────────────────────────

# Map free-text user_role / department strings (as they arrive from the LLM
# tool call) to the canonical enum values used in Postgres.
_ROLE_ALIASES = {
    "employee": UserRole.employee,
    "manager": UserRole.manager,
    "hr": UserRole.hr_team,
    "hr_team": UserRole.hr_team,
    "it": UserRole.it_team,
    "it_team": UserRole.it_team,
    "finance": UserRole.finance_team,
    "finance_team": UserRole.finance_team,
    "admin": UserRole.admin,
}

_DEPT_ALIASES = {
    "hr": DocDepartment.hr,
    "it": DocDepartment.it,
    "finance": DocDepartment.finance,
    "general": DocDepartment.general,
}


def _normalize_role(role: str) -> UserRole | None:
    return _ROLE_ALIASES.get(role.strip().lower())


def _normalize_department(dept: str) -> DocDepartment | None:
    return _DEPT_ALIASES.get(dept.strip().lower())


# ── Tool ──────────────────────────────────────────────────────────────────────

class PolicySearchInput(BaseModel):
    query: str = Field(description="The specific policy question or search query.")
    user_role: str = Field(description="Role of the user (employee, manager, hr, it, finance, admin).")
    department: str = Field(description="Department to filter by (hr, it, finance, general).")


@tool("search_company_policies", args_schema=PolicySearchInput)
async def search_company_policies(query: str, user_role: str, department: str) -> str:
    """Search the company knowledge base for HR / IT / Finance policies.

    Use this tool whenever the user asks about rules, allowances, processes,
    or guides. Results are filtered by department and the caller's role.
    """
    role_enum = _normalize_role(user_role)
    dept_enum = _normalize_department(department)

    if role_enum is None:
        return f"Unknown user_role '{user_role}'. Cannot perform RBAC-filtered search."
    if dept_enum is None:
        return f"Unknown department '{department}'. Valid: hr, it, finance, general."

    try:
        # Embed the query
        query_vector = await _embedder.aembed_query(query)

        async with AsyncSessionLocal() as db:
            # Cosine-distance ordered ANN search with RBAC + department filters.
            stmt = (
                select(
                    RAGChunk.content,
                    RAGChunk.metadata_,
                    RAGDocument.filename,
                    RAGChunk.embedding.cosine_distance(query_vector).label("distance"),
                )
                .join(RAGDocument, RAGChunk.document_id == RAGDocument.id)
                .where(RAGDocument.is_active.is_(True))
                .where(RAGDocument.department == dept_enum)
                .where(RAGDocument.roles_allowed.any(role_enum))
                .order_by(RAGChunk.embedding.cosine_distance(query_vector))
                .limit(settings.RAG_TOP_K * 4)
            )
            result = await db.execute(stmt)
            rows = result.all()

        if not rows:
            return (
                f"No relevant {department.upper()} policies found for your query. "
                "Either the policy does not exist, or you do not have permission to view it."
            )

        formatted = f"--- Retrieved {department.upper()} Policies ---\n\n"
        seen_parent_keys: set[tuple[str, int | str]] = set()
        for i, row in enumerate(rows, 1):
            similarity = 1.0 - float(row.distance)
            metadata = row.metadata_ or {}
            section_title = metadata.get("section_title", "Relevant policy section")
            parent_index = metadata.get("parent_index", f"chunk-{i}")
            parent_key = (row.filename, parent_index)
            if parent_key in seen_parent_keys:
                continue
            seen_parent_keys.add(parent_key)
            if len(seen_parent_keys) > settings.RAG_TOP_K:
                break
            parent_text = metadata.get("parent_text") or row.content
            page_start = metadata.get("page_start")
            page_end = metadata.get("page_end")
            page_ref = ""
            if page_start and page_end:
                page_ref = f" | pages={page_start}-{page_end}" if page_start != page_end else f" | page={page_start}"
            formatted += (
                f"[Source {len(seen_parent_keys)}: {row.filename} | section={section_title}"
                f"{page_ref} | similarity={similarity:.2f}]\n"
                f"{parent_text}\n\n"
            )
        return formatted

    except Exception as e:
        return f"Error retrieving documents: {e}"
