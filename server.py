# INFRASTRUCTURE
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from mcp.types import TextContent

from src.rag.retriever import (
    search_workflow, format_results,
    list_collections_workflow, format_collections,
    list_documents_workflow, format_documents
)

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


@mcp.tool
def list_collections() -> list[TextContent]:
    """List all indexed collections with their chunk counts. Use to discover what knowledge bases are available."""
    results = list_collections_workflow()
    return [TextContent(type="text", text=format_collections(results))]


@mcp.tool
def list_documents(
    collection: Annotated[str, Field(description="Collection name to list documents from")]
) -> list[TextContent]:
    """List all documents in a collection with their chunk counts. Use to see what's inside a specific collection."""
    results = list_documents_workflow(collection)
    return [TextContent(type="text", text=format_documents(results))]


if __name__ == "__main__":
    mcp.run()
