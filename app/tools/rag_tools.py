"""
app/tools/rag_tools.py
======================
RAG retrieval tool for LangGraph agents.

Performs RBAC-filtered semantic search against the PostgreSQL `rag_chunks`
table using pgvector's cosine distance. This is the "Retrieval" half of the
RAG pipeline — the "Generation" half happens when the LLM agent reads the
returned context and formulates an answer.

How it works (simplified):
    1. The user's natural-language query is converted into a 1536-dim vector
       by calling OpenAI's `text-embedding-3-small`.
    2. We ask pgvector to find the K nearest chunk vectors using
       cosine distance (1 − cosine_similarity).
    3. We JOIN rag_chunks → rag_documents and filter by the caller's
       `user_role`, so a user can only see documents their role is
       allowed to access (the roles_allowed ARRAY on rag_documents).
    4. Results are returned as a formatted string the LLM can cite.

Security:
    - The `user_role` is **never** sourced from the LLM's output.
      It is injected server-side from the authenticated session context.
    - Even if the LLM hallucinates a different role, the SQL filter
      enforces the real role from the JWT/session.
"""
from __future__ import annotations

import logging
from typing import Annotated

import httpx
from langchain_core.tools import tool
from openai import AsyncOpenAI
from sqlalchemy import select, func

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import RAGChunk, RAGDocument, UserRole

logger = logging.getLogger(__name__)

# ── OpenAI client for embedding generation ────────────────────────────────────
# Uses the same verify=False workaround for environments with SSL inspection
# (corporate proxies, Zscaler, etc.)  Remove `verify=False` in production
# if your environment has proper CA certs.
_http_client = httpx.AsyncClient(verify=False)
_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, http_client=_http_client)


async def _embed_query(text: str) -> list[float]:
    """
    Generate a 1536-dimensional embedding for a single query string.

    We call the same model used during ingestion (text-embedding-3-small)
    to ensure the query vector lives in the same mathematical space as the
    stored chunk vectors.  Mixing models would give meaningless distances.
    """
    response = await _openai.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=[text],
    )
    return response.data[0].embedding


async def search_knowledge(
    query: str,
    user_role: UserRole,
    top_k: int | None = None,
) -> str:
    """
    Perform RBAC-filtered semantic search over the enterprise knowledge base.

    This function is the core retrieval engine:
      1. Embed the query using OpenAI.
      2. Find the top-K closest chunks via pgvector cosine distance.
      3. Filter results so only documents the user's role can access are returned.
      4. Format the results for the LLM to read and cite.

    Args:
        query:     The natural-language question from the user.
        user_role: The authenticated user's role (injected from session, NOT from LLM).
        top_k:     Number of results to return. Defaults to settings.RAG_TOP_K (5).

    Returns:
        A formatted string of the retrieved knowledge chunks, or a message
        indicating no relevant documents were found.
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K

    # ── Step 1: Generate query embedding ──────────────────────────────────────
    logger.info("Generating embedding for query: %s...", query[:80])
    query_embedding = await _embed_query(query)

    # ── Step 2: Build the cosine distance query with RBAC filter ──────────────
    #
    # pgvector's `cosine_distance(v)` computes: 1 − (A·B / (‖A‖ × ‖B‖))
    #
    # A distance of 0 = identical meaning, 1 = orthogonal (unrelated),
    # 2 = diametrically opposite.  We ORDER BY distance ASC to get the
    # closest matches first.
    #
    # RBAC filter: `RAGDocument.roles_allowed.any(user_role.value)`
    # This translates to the PostgreSQL expression:
    #     'employee' = ANY(rag_documents.roles_allowed)
    # which checks if the user's role string exists in the ARRAY column.
    distance = RAGChunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(
            RAGChunk.content,
            RAGChunk.chunk_index,
            RAGDocument.filename,
            RAGDocument.department,
            distance.label("distance"),
        )
        .join(RAGDocument, RAGChunk.document_id == RAGDocument.id)
        .where(
            RAGDocument.is_active == True,                                 # noqa: E712 — SQLAlchemy needs ==
            RAGDocument.roles_allowed.any(user_role.value),                # RBAC: role must be in the allowed list
        )
        .order_by(distance.asc())
        .limit(top_k)
    )

    # ── Step 3: Execute and format results ────────────────────────────────────
    async with AsyncSessionLocal() as db:
        result = await db.execute(stmt)
        rows = result.all()

    if not rows:
        logger.info("No matching documents found for role=%s", user_role.value)
        return (
            "No relevant documents were found in the knowledge base for your query. "
            "This may be because no documents match your search, or your role "
            f"({user_role.value}) does not have access to the relevant documents."
        )

    # ── Step 4: Build a clean, citation-friendly response ─────────────────────
    chunks: list[str] = []
    for i, row in enumerate(rows, 1):
        similarity_pct = (1 - row.distance) * 100  # convert distance → similarity %
        chunks.append(
            f"[Source {i}] {row.filename} (Dept: {row.department.value}, "
            f"Chunk #{row.chunk_index}, Relevance: {similarity_pct:.1f}%)\n"
            f"{row.content}"
        )

    header = (
        f"Found {len(rows)} relevant knowledge chunks "
        f"(role: {user_role.value}):\n"
        + "─" * 60
    )
    return header + "\n\n" + "\n\n".join(chunks)


# ── LangChain-compatible tool wrapper ─────────────────────────────────────────
# This is the callable that gets registered in the tool registry and bound to
# the LLM agent.  The `user_role` is NOT passed by the LLM — it is injected
# by the graph's execute_node from the AgentState before invoking the tool.

@tool
async def search_enterprise_knowledge(query: str) -> str:
    """Search the company knowledge base for policy documents, guidelines, and procedures.

    Use this tool when the user asks about company policies, leave rules,
    IT guidelines, finance procedures, or any other enterprise documentation.

    Args:
        query: The user's question or search query about company policies/procedures.
    """
    # When called from LangGraph, user_role will be injected by the executor.
    # For safety, we default to "employee" (most restrictive access).
    # The actual injection happens in get_tools_for_intent → _wrap_with_role().
    return await search_knowledge(query, UserRole.employee)


def create_rag_tool_with_role(user_role: UserRole):
    """
    Factory: returns a LangChain @tool bound to a specific user role.

    This is the production pattern:
      - `get_tools_for_intent()` calls this with the real user's role.
      - The returned tool is bound to the LLM, which can only call it
        with `query`.  The role is baked-in and tamper-proof.

    Why not pass the role as a tool parameter?
      Because the LLM could hallucinate or inject a different role.
      By closing over the role at registration time, we guarantee the
      SQL filter always uses the authenticated role from the JWT/session.
    """
    @tool
    async def search_enterprise_knowledge(query: str) -> str:
        """Search the company knowledge base for policy documents, guidelines, and procedures.

        Use this tool when the user asks about company policies, leave rules,
        IT guidelines, finance procedures, or any other enterprise documentation.

        Args:
            query: The user's question or search query about company policies/procedures.
        """
        return await search_knowledge(query, user_role)

    return search_enterprise_knowledge
