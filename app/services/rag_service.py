"""Shared RAG retrieval service.

This module centralizes pgvector retrieval logic so LLM-facing tools never
control trusted values like ``department`` or ``user_role``. Tool wrappers
(e.g. ``search_hr_policies``) call into this service with backend-trusted
arguments only.
"""
from __future__ import annotations

from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import DocDepartment, RAGChunk, RAGDocument, UserRole


# ── Embedding client (shared, lazily built once) ─────────────────────────────

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


_embedder: OpenAIEmbeddings | None = None


def _get_embedder() -> OpenAIEmbeddings:
    global _embedder
    if _embedder is None:
        _embedder = _build_embedder()
    return _embedder


# ── Public API ────────────────────────────────────────────────────────────────

async def search_policy_context(
    query: str,
    user_role: UserRole,
    department: DocDepartment,
) -> str:
    """Search policy chunks via pgvector and return deduplicated parent context.

    Both ``user_role`` and ``department`` must come from trusted backend state,
    never from LLM tool arguments.
    """
    if not query or not query.strip():
        return "No query provided."

    try:
        query_vector = await _get_embedder().aembed_query(query)

        async with AsyncSessionLocal() as db:
            stmt = (
                select(
                    RAGChunk.content,
                    RAGChunk.metadata_,
                    RAGDocument.filename,
                    RAGChunk.embedding.cosine_distance(query_vector).label("distance"),
                )
                .join(RAGDocument, RAGChunk.document_id == RAGDocument.id)
                .where(RAGDocument.is_active.is_(True))
                .where(RAGDocument.department == department)
                .where(RAGDocument.roles_allowed.any(user_role))
                .order_by(RAGChunk.embedding.cosine_distance(query_vector))
                .limit(settings.RAG_TOP_K * 4)
            )
            result = await db.execute(stmt)
            rows = result.all()

        if not rows:
            return (
                f"No relevant {department.value.upper()} policies found for your query. "
                "Either the policy does not exist, or you do not have permission to view it."
            )

        formatted = f"--- Retrieved {department.value.upper()} Policies ---\n\n"
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
                page_ref = (
                    f" | pages={page_start}-{page_end}"
                    if page_start != page_end
                    else f" | page={page_start}"
                )
            formatted += (
                f"[Source {len(seen_parent_keys)}: {row.filename} | section={section_title}"
                f"{page_ref} | similarity={similarity:.2f}]\n"
                f"{parent_text}\n\n"
            )
        return formatted

    except Exception as exc:  # noqa: BLE001
        return f"Error retrieving documents: {exc}"
