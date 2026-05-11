from __future__ import annotations

import argparse
import asyncio
import glob
import os
import re
import sys
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import delete

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from app.config import settings  # noqa: E402
from app.database import AsyncSessionLocal  # noqa: E402
from app.models import DocDepartment, RAGChunk, RAGDocument, UserRole  # noqa: E402

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_docs"))
PDF_SKIP_PAGES = {1, 2, 3}
PARENT_MAX_WORDS = 900
CHILD_CHUNK_SIZE = 900
CHILD_CHUNK_OVERLAP = 120

HEADER_PATTERNS = [
    re.compile(r"^\s*master\s+employee\s+policies\s*$", re.IGNORECASE),
    re.compile(r"^\s*doc\s*no\.?\s*:?\s*ns-?pol-?\d+\s+doc\s*version\s*:?\s*\d+(\.\d+)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*doc\s*no\.?\s*:?\s*(ns-?pol-?\d+)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*ns-?pol-?\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*doc\s*version\s*:?\s*(\d+(\.\d+)?)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*\d+\.\d+\s*$"),
]

FOOTER_PATTERNS = [
    re.compile(r"^\s*classification\s+internal\s+page\s*no\.?\s*:?\s*\d*\s*\|?\s*$", re.IGNORECASE),
    re.compile(r"^\s*p\s*a\s*g\s*e\s*$", re.IGNORECASE),
    re.compile(r"^\s*page\s*no\.?\s*:?\s*\d*\s*\|?\s*$", re.IGNORECASE),
    re.compile(r"^\s*page\s+\d+(\s+of\s+\d+)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*\d+\s*\|?\s*$"),
]

_NOISE_LINE = re.compile(r"^\s*[\W_]*\s*$")
_TABLE_CATEGORIES = {"Table"}
_HEADING_CATEGORIES = {"Title"}


@dataclass
class ParentSection:
    title: str
    text: str
    page_start: int | None
    page_end: int | None
    element_types: list[str]


def _matches_any(line: str, patterns: list[re.Pattern]) -> bool:
    return any(p.match(line) for p in patterns)


def _word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))


def clean_pdf_page(text: str) -> str:
    edge_patterns = HEADER_PATTERNS + FOOTER_PATTERNS
    lines = text.splitlines()

    start = 0
    while start < len(lines):
        line = lines[start]
        if _NOISE_LINE.match(line) or _matches_any(line, edge_patterns):
            start += 1
            continue
        break

    end = len(lines)
    while end > start:
        line = lines[end - 1]
        if _NOISE_LINE.match(line) or _matches_any(line, edge_patterns):
            end -= 1
            continue
        break

    return "\n".join(lines[start:end])


def _is_document_artifact(text: str, category: str) -> bool:
    normalized = " ".join(text.split())
    if not normalized:
        return True
    if _matches_any(normalized, HEADER_PATTERNS + FOOTER_PATTERNS):
        return True
    if category.lower() in {"header", "footer"} and normalized.lower() in {"classification", "internal"}:
        return True
    return False


def _looks_like_heading(text: str, category: str) -> bool:
    normalized = " ".join(text.split())
    words = normalized.split()
    if category in _HEADING_CATEGORIES and 1 <= len(words) <= 14:
        return True
    if len(words) > 14 or normalized.startswith(("•", "-", "▪")):
        return False
    if normalized.lower().endswith("policy"):
        return True
    if re.match(r"^[A-Z][A-Za-z &/()\-]+:$", normalized):
        return True
    return False


def _element_text(element: Any) -> str:
    text = getattr(element, "text", None)
    if text is None:
        text = str(element)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def _element_category(element: Any) -> str:
    category = getattr(element, "category", None)
    if category:
        return str(category)
    return element.__class__.__name__


def _element_page(element: Any) -> int | None:
    metadata = getattr(element, "metadata", None)
    page = getattr(metadata, "page_number", None) if metadata else None
    return int(page) if page is not None else None


def _load_pdf_elements(filepath: str) -> list[dict[str, Any]]:
    try:
        from unstructured.partition.pdf import partition_pdf

        strategy = os.getenv("UNSTRUCTURED_PDF_STRATEGY", "fast")
        try:
            elements = partition_pdf(
                filename=filepath,
                strategy=strategy,
                infer_table_structure=True,
                extract_images_in_pdf=False,
            )
        except Exception as exc:
            print(f"  {strategy} partition failed ({exc}); retrying with fast strategy...")
            elements = partition_pdf(
                filename=filepath,
                strategy="fast",
                infer_table_structure=True,
            )

        blocks: list[dict[str, Any]] = []
        for element in elements:
            page = _element_page(element)
            if page in PDF_SKIP_PAGES:
                continue
            category = _element_category(element)
            text = _element_text(element)
            if _is_document_artifact(text, category):
                continue
            if category in _TABLE_CATEGORIES:
                text = f"Table:\n{text}"
            blocks.append({"text": text, "category": category, "page": page})
        return blocks
    except Exception as exc:
        print(f"  unstructured failed ({exc}); falling back to PyPDFLoader...")
        from langchain_community.document_loaders import PyPDFLoader

        blocks = []
        for page_doc in PyPDFLoader(filepath).load():
            page_zero_based = page_doc.metadata.get("page")
            page = page_zero_based + 1 if isinstance(page_zero_based, int) else None
            if page in PDF_SKIP_PAGES:
                continue
            text = clean_pdf_page(page_doc.page_content)
            if text.strip():
                blocks.append({"text": text, "category": "NarrativeText", "page": page})
        return blocks


def _load_txt_blocks(filepath: str) -> list[dict[str, Any]]:
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    return [{"text": text, "category": "NarrativeText", "page": None}]


def load_blocks(filepath: str) -> list[dict[str, Any]]:
    if filepath.lower().endswith(".pdf"):
        return _load_pdf_elements(filepath)
    if filepath.lower().endswith(".txt"):
        return _load_txt_blocks(filepath)
    return []


def _split_large_parent(section: ParentSection) -> list[ParentSection]:
    if _word_count(section.text) <= PARENT_MAX_WORDS:
        return [section]

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " "],
        chunk_size=PARENT_MAX_WORDS * 6,
        chunk_overlap=80,
    )
    parts = splitter.split_text(section.text)
    split_sections = []
    for idx, part in enumerate(parts):
        split_sections.append(ParentSection(
            title=f"{section.title} (part {idx + 1})",
            text=part,
            page_start=section.page_start,
            page_end=section.page_end,
            element_types=section.element_types,
        ))
    return split_sections


def build_parent_sections(blocks: list[dict[str, Any]]) -> list[ParentSection]:
    parents: list[ParentSection] = []
    current_title = "Document Introduction"
    current_parts: list[str] = []
    current_types: list[str] = []
    page_start: int | None = None
    page_end: int | None = None

    def flush() -> None:
        nonlocal current_parts, current_types, page_start, page_end
        text = "\n\n".join(p for p in current_parts if p.strip()).strip()
        if text:
            section = ParentSection(
                title=current_title,
                text=text,
                page_start=page_start,
                page_end=page_end,
                element_types=sorted(set(current_types)),
            )
            parents.extend(_split_large_parent(section))
        current_parts = []
        current_types = []
        page_start = None
        page_end = None

    for block in blocks:
        text = block["text"].strip()
        category = block["category"]
        page = block.get("page")

        if _looks_like_heading(text, category):
            flush()
            current_title = " ".join(text.split())
            continue

        current_parts.append(text)
        current_types.append(category)
        if page is not None:
            page_start = page if page_start is None else min(page_start, page)
            page_end = page if page_end is None else max(page_end, page)

    flush()
    return parents


def build_child_documents(parent_sections: list[ParentSection], filename: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", "; ", ", ", " "],
        chunk_size=CHILD_CHUNK_SIZE,
        chunk_overlap=CHILD_CHUNK_OVERLAP,
    )

    children: list[Document] = []
    for parent_idx, parent in enumerate(parent_sections):
        child_texts = splitter.split_text(parent.text)
        for child_idx, child_text in enumerate(child_texts):
            retrieval_text = f"{parent.title}\n{child_text}"
            children.append(Document(
                page_content=retrieval_text,
                metadata={
                    "source": filename,
                    "section_title": parent.title,
                    "parent_index": parent_idx,
                    "child_index": child_idx,
                    "parent_text": parent.text,
                    "page_start": parent.page_start,
                    "page_end": parent.page_end,
                    "element_types": parent.element_types,
                    "has_table": "Table" in parent.element_types,
                },
            ))
    return children


def get_metadata_for_file(filepath: str) -> dict:
    lower = filepath.lower()
    department = DocDepartment.general
    roles_allowed: list[UserRole] = [UserRole.employee, UserRole.manager, UserRole.admin]

    if os.sep + "hr" + os.sep in lower or "/hr/" in lower:
        department = DocDepartment.hr
        roles_allowed = [UserRole.employee, UserRole.manager, UserRole.hr_team, UserRole.admin]
    elif os.sep + "it" + os.sep in lower or "/it/" in lower:
        department = DocDepartment.it
        roles_allowed = [UserRole.employee, UserRole.manager, UserRole.it_team, UserRole.admin]
    elif os.sep + "finance" + os.sep in lower or "/finance/" in lower:
        department = DocDepartment.finance
        roles_allowed = [UserRole.employee, UserRole.manager, UserRole.finance_team, UserRole.admin]
        if "internal" in lower:
            roles_allowed = [UserRole.finance_team, UserRole.admin]

    return {"department": department, "doc_type": "policy", "roles_allowed": roles_allowed}


async def ingest(reset: bool = True) -> None:
    print(f"Scanning directory: {DOCS_DIR}")
    file_patterns = [
        os.path.join(DOCS_DIR, "**", "*.txt"),
        os.path.join(DOCS_DIR, "**", "*.pdf"),
    ]
    files: list[str] = []
    for pattern in file_patterns:
        files.extend(glob.glob(pattern, recursive=True))

    if not files:
        print("No documents found! Add files under rag_docs/<dept>/")
        return

    embedder_kwargs: dict = {"api_key": settings.OPENAI_API_KEY, "model": settings.EMBEDDING_MODEL}
    if not settings.OPENAI_VERIFY_SSL:
        import httpx
        embedder_kwargs["http_client"] = httpx.Client(verify=False)
        embedder_kwargs["http_async_client"] = httpx.AsyncClient(verify=False)
    embedder = OpenAIEmbeddings(**embedder_kwargs)

    async with AsyncSessionLocal() as db:
        if reset:
            print("Resetting existing rag_chunks and rag_documents...")
            await db.execute(delete(RAGChunk))
            await db.execute(delete(RAGDocument))
            await db.commit()

        total_children = 0
        for filepath in files:
            filename = os.path.basename(filepath)
            print(f"Loading: {filepath}")
            blocks = load_blocks(filepath)
            if not blocks:
                print("  (no content after parsing, skipping)")
                continue

            parents = build_parent_sections(blocks)
            children = build_child_documents(parents, filename)
            if not children:
                print("  (no child chunks built, skipping)")
                continue

            meta = get_metadata_for_file(filepath)
            doc_row = RAGDocument(
                filename=filename,
                department=meta["department"],
                doc_type=meta["doc_type"],
                roles_allowed=meta["roles_allowed"],
                file_url=None,
                is_active=True,
                chunk_count=len(children),
                metadata_={
                    "path": filepath,
                    "parser": "unstructured",
                    "retrieval_strategy": "parent_child",
                    "parent_count": len(parents),
                    "child_chunk_size_chars": CHILD_CHUNK_SIZE,
                    "child_chunk_overlap_chars": CHILD_CHUNK_OVERLAP,
                },
            )
            db.add(doc_row)
            await db.flush()

            texts = [child.page_content for child in children]
            print(f"  Built {len(parents)} parent sections and {len(children)} child chunks.")
            print(f"  Embedding {len(texts)} child chunks...")
            vectors = await embedder.aembed_documents(texts)

            for idx, (child, vec) in enumerate(zip(children, vectors)):
                metadata = {
                    **{k: v for k, v in child.metadata.items()
                       if isinstance(v, (str, int, float, bool, list, type(None)))},
                    "department": meta["department"].value,
                }
                db.add(RAGChunk(
                    document_id=doc_row.id,
                    chunk_index=idx,
                    content=child.page_content,
                    embedding=vec,
                    token_count=_word_count(child.page_content),
                    metadata_=metadata,
                ))

            await db.commit()
            total_children += len(children)
            print(f"  Inserted {filename}: {len(children)} child chunks.")

        print(f"\n✅ Ingestion complete. {total_children} child chunks across {len(files)} files.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest RAG docs into Supabase pgvector")
    parser.add_argument("--no-reset", action="store_true",
                        help="Do not wipe existing rag_documents/rag_chunks before ingestion")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(ingest(reset=not args.no_reset))
