"""Quick smoke-test: verify RAG tool imports + run a live query."""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.tools.rag_tools import search_knowledge
from app.models import UserRole

async def main():
    print("Testing RAG search as 'employee' role...")
    result = await search_knowledge("What is the leave policy?", UserRole.employee)
    print(result)

asyncio.run(main())
