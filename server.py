# INFRASTRUCTURE
from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field
from mcp.types import TextContent

from src.rag.retriever import (
    search_workflow, format_results,
    search_keyword_workflow,
    list_collections_workflow, format_collections,
    list_documents_workflow, format_documents,
    read_document_workflow
)

mcp = FastMCP("RAG")


# TOOLS

@mcp.tool
def search(
    query: Annotated[str, Field(description="Search query to find relevant documents or code")],
    collection: Annotated[str, Field(description="Collection to search in (use list_collections to see available)")],
    top_k: Annotated[int, Field(description="Number of results to return (1-20)")] = 5,
    document: Annotated[str | None, Field(description="Filter by document name (e.g. 'chapter1.md')")] = None,
    neighbors: Annotated[int, Field(description="Include N chunks before/after each match for context (0-2)")] = 0
) -> list[TextContent]:
    """Use when user needs to find relevant documents, code snippets, or information from the indexed knowledge base. Good for answering questions, finding examples, or locating specific content."""
    results = search_workflow(query, min(top_k, 20), collection, document, min(neighbors, 2))
    return [TextContent(type="text", text=format_results(results))]


@mcp.tool
def search_keyword(
    query: Annotated[str, Field(description="Exact keywords to search for (e.g. 'l_suppkey', 'TPC-H')")],
    collection: Annotated[str, Field(description="Collection to search in")],
    top_k: Annotated[int, Field(description="Number of results to return (1-20)")] = 5,
    document: Annotated[str | None, Field(description="Filter by document name")] = None
) -> list[TextContent]:
    """BM25 keyword search for exact term matches. Use for finding specific definitions, technical terms, column names, or exact phrases. Complements semantic search()."""
    results = search_keyword_workflow(query, min(top_k, 20), collection, document)
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


@mcp.tool
def read_document(
    collection: Annotated[str, Field(description="Collection name")],
    document: Annotated[str, Field(description="Document name (e.g. 'chunks.md')")],
    start_chunk: Annotated[int, Field(description="Chunk index to start reading from")],
    num_chunks: Annotated[int, Field(description="Number of chunks to read (1-20)")] = 5
) -> list[TextContent]:
    """Read continuous text from a document starting at a specific chunk. Use after search to read more context around a found chunk."""
    result = read_document_workflow(collection, document, start_chunk, min(num_chunks, 20))
    text = f"Document: {result['document']} | Chunks {result['start_chunk']}-{result['start_chunk'] + result['num_chunks'] - 1}\n\n{result['content']}"
    return [TextContent(type="text", text=text)]


if __name__ == "__main__":
    mcp.run()
