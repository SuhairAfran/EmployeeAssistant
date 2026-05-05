import os
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pydantic import BaseModel, Field

CHROMA_PERSIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "chroma_db"))

# Initialize connection to the Vector DB
vectorstore = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever(
    search_type="mmr", # Maximal Marginal Relevance for diversity
    search_kwargs={"k": 5, "fetch_k": 20} # Top-K=5
)

class PolicySearchInput(BaseModel):
    query: str = Field(description="The specific policy question or search query.")
    user_role: str = Field(description="The role of the user making the request (e.g., employee, manager, hr).")
    department: str = Field(description="The department to filter by (e.g., hr, it, finance).")

@tool("search_company_policies", args_schema=PolicySearchInput)
def search_company_policies(query: str, user_role: str, department: str) -> str:
    """
    Search the company knowledge base for HR, IT, or Finance policies.
    Use this tool whenever the user asks about rules, allowances, processes, or guides.
    """
    try:
        # 1. Define Metadata Filters (RBAC & Department)
        # Chroma uses simple string matching. We ensure the user's role is in the allowed string.
        search_filter = {
            "$and": [
                {"department": {"$eq": department.lower()}},
                {"roles_allowed": {"$contains": user_role.lower()}}
            ]
        }

        # 2. Execute Retrieval
        docs = vectorstore.similarity_search(
            query=query,
            k=5,
            filter=search_filter
        )

        if not docs:
            return f"No relevant {department.upper()} policies found for your query. Either the policy does not exist, or you do not have permission to view it."

        # 3. Format output with citations
        formatted_results = f"--- Retrieved {department.upper()} Policies ---\n\n"
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown Document")
            formatted_results += f"[Source {i}: {source}]\n{doc.page_content}\n\n"

        return formatted_results

    except Exception as e:
        return f"Error retrieving documents: {str(e)}"