# INFRASTRUCTURE
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from mcp.types import TextContent

from src.rag.retriever import search_workflow, format_results

mcp = FastMCP("RAG")


# TOOLS

@mcp.tool
def search(
    query: Annotated[str, Field(description="Search query to find relevant documents or code")],
    top_k: Annotated[int, Field(description="Number of results to return (1-20)")] = 5,
    collection: Annotated[str | None, Field(description="Filter by collection name (folder in data/documents/)")] = None,
    document: Annotated[str | None, Field(description="Filter by document name (e.g. 'chapter1.md')")] = None
) -> list[TextContent]:
    """Use when user needs to find relevant documents, code snippets, or information from the indexed knowledge base. Good for answering questions, finding examples, or locating specific content."""
    results = search_workflow(query, min(top_k, 20), collection, document)
    return [TextContent(type="text", text=format_results(results))]


if __name__ == "__main__":
    mcp.run()
