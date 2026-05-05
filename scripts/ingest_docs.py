"""
RAG Document Ingestion Pipeline
================================
Scans the `rag_docs/` directory, loads PDFs (and other supported formats),
splits them into semantic chunks, generates OpenAI embeddings, and stores
everything in the PostgreSQL `rag_documents` + `rag_chunks` tables.

Usage:
    python -m scripts.ingest_docs                         # ingest all departments
    python -m scripts.ingest_docs --department hr          # ingest only HR docs
    python -m scripts.ingest_docs --department finance --force  # re-ingest (overwrite)

Directory layout expected:
    rag_docs/
    ├── hr/
    │   ├── leave_policy.pdf
    │   └── attendance_policy.pdf
    ├── it/
    │   └── vpn_setup_guide.pdf
    └── finance/
        └── reimbursement_policy.pdf

Each subfolder name becomes the `department` tag on the RAGDocument record.

HOW VECTOR CHUNKING WORKS (in simple terms)
--------------------------------------------
1. **Loading**: We read each PDF/DOCX file into raw text using LangChain's
   document loaders (backed by the `unstructured` library).

2. **Splitting / Chunking**: A 50-page policy document is too large to fit
   inside an LLM's context window alongside the user's question.  So we
   "chunk" it — break it into overlapping pieces of ~512 characters each.

   Why overlap?  Imagine a sentence that starts at character 500 and ends
   at character 530.  Without overlap, it would be cut in half across two
   chunks and lose its meaning.  A 50-character overlap ensures that
   boundary sentences appear fully in at least one chunk.

   We use `RecursiveCharacterTextSplitter` which tries to split on natural
   boundaries (paragraphs → sentences → words → characters) rather than
   blindly slicing every 512 chars.

3. **Embedding**: Each chunk is fed to OpenAI's `text-embedding-3-small`
   model, which returns a 1536-dimensional vector — a list of 1536 floats
   that *numerically represent the meaning* of that text.

   Chunks about "maternity leave" and "parental leave" will have vectors
   that are very close in this 1536-dimensional space, even though the
   words are different.

4. **Storage**: The vector is stored alongside the chunk text in the
   `rag_chunks` table using the `pgvector` PostgreSQL extension.  At
   query time, we compute the vector of the user's question and ask
   pgvector for the K nearest chunks — that's the "Retrieval" in RAG.

5. **RBAC metadata**: Each document carries `roles_allowed` (e.g.,
   ["employee", "hr_team"]) and `department` tags.  At retrieval time,
   the system filters out chunks the current user's role is not allowed
   to see, ensuring RBAC extends into the RAG pipeline.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so `app.*` imports resolve
# when running as `python -m scripts.ingest_docs` from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from openai import AsyncOpenAI
from sqlalchemy import select, delete

from app.config import settings
from app.models import RAGDocument, RAGChunk, DocDepartment
from app.database import AsyncSessionLocal

# ── LangChain imports for loading and splitting ──────────────────────────────

from langchain_text_splitters import RecursiveCharacterTextSplitter


# ── Configuration ────────────────────────────────────────────────────────────

RAG_DOCS_DIR = PROJECT_ROOT / "rag_docs"

# Default RBAC mapping: which roles may see docs from each department.
# You can override these per-file by placing a sidecar `.meta.json` later.
DEFAULT_ROLES_BY_DEPT: dict[str, list[str]] = {
    "hr":      ["employee", "manager", "hr_team", "admin"],
    "it":      ["employee", "manager", "it_team", "admin"],
    "finance": ["employee", "manager", "finance_team", "admin"],
    "general": ["employee", "manager", "hr_team", "it_team", "finance_team", "admin"],
}

# Supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}

# OpenAI client (reads OPENAI_API_KEY from env automatically)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# ── Text Splitter ────────────────────────────────────────────────────────────
# RecursiveCharacterTextSplitter tries these separators in order:
#   "\n\n" (paragraph) → "\n" (newline) → " " (space) → "" (char-level)
# It picks the highest-level separator that keeps each chunk under `chunk_size`.

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,       # 512 characters per chunk
    chunk_overlap=settings.CHUNK_OVERLAP, # 50 characters overlap between consecutive chunks
    length_function=len,                  # measure chunk size by character count
    is_separator_regex=False,
)


# ── File loading ─────────────────────────────────────────────────────────────

def load_file_text(file_path: Path) -> str:
    """
    Load a document into raw text.

    For PDFs, we use the `unstructured` library via LangChain's loader.
    For plain text / markdown, we just read the file directly.
    """
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        try:
            from langchain_community.document_loaders import UnstructuredFileLoader
            loader = UnstructuredFileLoader(str(file_path), mode="elements")
            docs = loader.load()
            # Combine all elements into a single string
            return "\n\n".join(doc.page_content for doc in docs if doc.page_content.strip())
        except ImportError:
            # Fallback: try PyPDF2 if unstructured is not installed
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
            return "\n\n".join(doc.page_content for doc in docs if doc.page_content.strip())

    elif ext in (".docx", ".doc"):
        from langchain_community.document_loaders import UnstructuredFileLoader
        loader = UnstructuredFileLoader(str(file_path), mode="elements")
        docs = loader.load()
        return "\n\n".join(doc.page_content for doc in docs if doc.page_content.strip())

    elif ext in (".txt", ".md"):
        return file_path.read_text(encoding="utf-8")

    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ── Embedding generation ─────────────────────────────────────────────────────

async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Call OpenAI's embedding API in a single batch.

    The `text-embedding-3-small` model returns 1536-dimensional vectors.
    We batch all chunks of a single document into one API call to minimize
    round trips and cost.

    OpenAI's batch limit is 2048 inputs — for very large docs, we chunk
    the API calls themselves.
    """
    embeddings: list[list[float]] = []
    batch_size = 2048  # OpenAI max inputs per request

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = await openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=batch,
        )
        embeddings.extend([item.embedding for item in response.data])

    return embeddings


# ── Core ingestion logic ─────────────────────────────────────────────────────

async def ingest_single_document(
    file_path: Path,
    department: str,
    force: bool = False,
) -> int:
    """
    Ingest one document file: load → chunk → embed → store.

    Returns the number of chunks inserted.
    """
    filename = file_path.name
    dept_enum = DocDepartment(department)
    roles_allowed = DEFAULT_ROLES_BY_DEPT.get(department, ["employee"])

    async with AsyncSessionLocal() as db:
        # ── Check if already ingested ─────────────────────────────────────
        existing = await db.execute(
            select(RAGDocument).where(
                RAGDocument.filename == filename,
                RAGDocument.department == dept_enum,
            )
        )
        existing_doc = existing.scalar_one_or_none()

        if existing_doc and not force:
            print(f"  ⏭️  Skipping '{filename}' (already ingested). Use --force to re-ingest.")
            return 0

        if existing_doc and force:
            # Delete old document + cascading chunks
            await db.execute(
                delete(RAGChunk).where(RAGChunk.document_id == existing_doc.id)
            )
            await db.execute(
                delete(RAGDocument).where(RAGDocument.id == existing_doc.id)
            )
            await db.flush()
            print(f"  🗑️  Deleted old version of '{filename}'.")

        # ── Step 1: Load the file into raw text ───────────────────────────
        print(f"  📄 Loading '{filename}'...")
        raw_text = load_file_text(file_path)

        if not raw_text.strip():
            print(f"  ⚠️  '{filename}' produced no text — skipping.")
            return 0

        # ── Step 2: Split into chunks ─────────────────────────────────────
        chunks = text_splitter.split_text(raw_text)
        print(f"  ✂️  Split into {len(chunks)} chunks "
              f"(chunk_size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})")

        if not chunks:
            print(f"  ⚠️  No chunks produced for '{filename}' — skipping.")
            return 0

        # ── Step 3: Generate embeddings for all chunks ────────────────────
        print(f"  🧮 Generating embeddings via '{settings.EMBEDDING_MODEL}'...")
        embeddings = await generate_embeddings(chunks)

        # ── Step 4: Create the RAGDocument record ─────────────────────────
        rag_doc = RAGDocument(
            filename=filename,
            department=dept_enum,
            doc_type=file_path.suffix.lstrip(".").upper(),
            roles_allowed=roles_allowed,
            file_url=str(file_path.relative_to(PROJECT_ROOT)),
            chunk_count=len(chunks),
            metadata_={
                "source_path": str(file_path),
                "char_count": len(raw_text),
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "embedding_model": settings.EMBEDDING_MODEL,
            },
        )
        db.add(rag_doc)
        await db.flush()  # get the generated ID

        # ── Step 5: Create RAGChunk records with embeddings ───────────────
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            rag_chunk = RAGChunk(
                document_id=rag_doc.id,
                chunk_index=idx,
                content=chunk_text,
                embedding=embedding,
                token_count=len(chunk_text.split()),  # rough word-count estimate
                metadata_={
                    "department": department,
                    "roles_allowed": roles_allowed,
                    "filename": filename,
                    "chunk_index": idx,
                },
            )
            db.add(rag_chunk)

        await db.commit()
        print(f"  ✅ Ingested '{filename}': {len(chunks)} chunks stored.")
        return len(chunks)


async def ingest_department(department: str, force: bool = False) -> int:
    """Ingest all supported files from a single department folder."""
    dept_dir = RAG_DOCS_DIR / department
    if not dept_dir.is_dir():
        print(f"⚠️  Directory not found: {dept_dir}")
        return 0

    files = [
        f for f in sorted(dept_dir.iterdir())
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        print(f"⚠️  No supported files found in {dept_dir}")
        return 0

    print(f"\n📁 Department: {department.upper()} ({len(files)} files)")
    print("─" * 50)

    total_chunks = 0
    for file_path in files:
        total_chunks += await ingest_single_document(file_path, department, force)

    return total_chunks


async def main(departments: list[str] | None = None, force: bool = False) -> None:
    """
    Main entry point for the ingestion pipeline.

    Args:
        departments: List of department names to ingest. None = all.
        force: If True, delete and re-ingest existing documents.
    """
    print("=" * 60)
    print("  RAG Document Ingestion Pipeline")
    print(f"  Embedding model : {settings.EMBEDDING_MODEL}")
    print(f"  Chunk size      : {settings.CHUNK_SIZE} chars")
    print(f"  Chunk overlap   : {settings.CHUNK_OVERLAP} chars")
    print(f"  Force re-ingest : {force}")
    print("=" * 60)

    # Discover departments from the rag_docs directory structure
    if departments is None:
        departments = [
            d.name for d in sorted(RAG_DOCS_DIR.iterdir())
            if d.is_dir() and not d.name.startswith(".")
        ]

    if not departments:
        print("❌ No department folders found in rag_docs/. Nothing to ingest.")
        return

    grand_total = 0
    for dept in departments:
        grand_total += await ingest_department(dept, force)

    print("\n" + "=" * 60)
    print(f"  ✅ Done! Total chunks ingested: {grand_total}")
    print("=" * 60)


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest policy documents into the RAG vector store."
    )
    parser.add_argument(
        "--department", "-d",
        type=str,
        default=None,
        help="Ingest only this department (hr, it, finance). Default: all.",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Re-ingest documents even if they already exist.",
    )

    args = parser.parse_args()

    dept_list = [args.department] if args.department else None
    asyncio.run(main(departments=dept_list, force=args.force))
