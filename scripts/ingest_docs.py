import os
import glob
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

# Configuration
DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_docs"))
CHROMA_PERSIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "chroma_db"))

def get_metadata_for_file(filepath: str) -> dict:
    """Determine metadata (department, roles allowed) based on file path."""
    department = "general"
    roles_allowed = "all" # Default public access
    doc_type = "policy"

    if "hr" in filepath.lower():
        department = "hr"
        # Example: Leave policies are visible to all employees
        roles_allowed = "employee,manager,hr,admin" 
    elif "it" in filepath.lower():
        department = "it"
        roles_allowed = "employee,manager,it,admin"
    elif "finance" in filepath.lower():
        department = "finance"
        # Example: Finance internal docs only for finance/admin
        if "internal" in filepath.lower():
            roles_allowed = "finance,admin"
        else:
            roles_allowed = "employee,manager,finance,admin"

    return {
        "department": department,
        "doc_type": doc_type,
        "roles_allowed": roles_allowed,
        "source": os.path.basename(filepath)
    }

def ingest_documents():
    print(f"Scanning directory: {DOCS_DIR}")
    
    documents = []
    # Find all txt and pdf files in subdirectories
    file_patterns = [os.path.join(DOCS_DIR, "**", "*.txt"), os.path.join(DOCS_DIR, "**", "*.pdf")]
    
    for pattern in file_patterns:
        for filepath in glob.glob(pattern, recursive=True):
            print(f"Loading: {filepath}")
            
            # Choose loader based on extension
            if filepath.endswith(".txt"):
                loader = TextLoader(filepath, encoding="utf-8")
            elif filepath.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
            else:
                continue
                
            docs = loader.load()
            
            # Attach dynamic metadata to each document
            meta = get_metadata_for_file(filepath)
            for doc in docs:
                doc.metadata.update(meta)
                
            documents.extend(docs)

    if not documents:
        print("No documents found! Please add files to rag_docs/hr or rag_docs/it")
        return

    print(f"Loaded {len(documents)} document pages/files.")

    # Apply Token-based Chunking (512 tokens, 50 overlap)
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512,
        chunk_overlap=50
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} semantic chunks.")

    # Embed and Store in Vector DB
    print("Embedding chunks and saving to Vector DB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    print(f"✅ Ingestion complete! Vector DB saved to {CHROMA_PERSIST_DIR}")

if __name__ == "__main__":
    ingest_documents()