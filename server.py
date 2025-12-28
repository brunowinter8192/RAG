# INFRASTRUCTURE
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

from src.rag.retriever import search_workflow

mcp = FastMCP("RAG")


# TOOLS

@mcp.tool
def search(
    query: Annotated[str, Field(description="Search query to find relevant documents or code")],
    top_k: Annotated[int, Field(description="Number of results to return (1-20)")] = 5
) -> list[dict]:
    """Use when user needs to find relevant documents, code snippets, or information from the indexed knowledge base. Good for answering questions, finding examples, or locating specific content."""
    return search_workflow(query, min(top_k, 20))


if __name__ == "__main__":
    mcp.run()
