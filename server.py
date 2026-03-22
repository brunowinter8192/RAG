# INFRASTRUCTURE
from fastmcp import FastMCP
from mcp.types import TextContent

from src.rag.retriever import (
    search_workflow, format_results,
    search_keyword_workflow,
    search_hybrid_workflow,
    list_collections_workflow, format_collections,
    list_documents_workflow, format_documents,
    read_document_workflow
)

mcp = FastMCP("RAG")


# FUNCTIONS

@mcp.tool
def search(
    query: str,
    collection: str,
    top_k: int = 20,
    document: str | None = None,
    neighbors: int = 0
) -> list[TextContent]:
    """Semantic search over documents."""
    results = search_workflow(query, top_k, collection, document, min(neighbors, 2))
    return [TextContent(type="text", text=format_results(results))]


@mcp.tool
def search_hybrid(
    query: str,
    collection: str,
    top_k: int = 20,
    document: str | None = None,
    neighbors: int = 0,
    rerank: bool = True
) -> list[TextContent]:
    """Hybrid semantic + keyword search."""
    results = search_hybrid_workflow(query, top_k, collection, document, min(neighbors, 2), rerank)
    return [TextContent(type="text", text=format_results(results))]


@mcp.tool
def search_keyword(
    query: str,
    collection: str,
    top_k: int = 20,
    document: str | None = None
) -> list[TextContent]:
    """Keyword search for exact terms."""
    results = search_keyword_workflow(query, top_k, collection, document)
    return [TextContent(type="text", text=format_results(results))]


@mcp.tool
def list_collections() -> list[TextContent]:
    """List indexed collections."""
    results = list_collections_workflow()
    return [TextContent(type="text", text=format_collections(results))]


@mcp.tool
def list_documents(
    collection: str,
    document: str | None = None
) -> list[TextContent]:
    """List documents in a collection."""
    results = list_documents_workflow(collection, document)
    return [TextContent(type="text", text=format_documents(results))]


@mcp.tool
def read_document(
    collection: str,
    document: str,
    start_chunk: int,
    num_chunks: int = 10
) -> list[TextContent]:
    """Read document chunks."""
    num_chunks = max(num_chunks, 10)
    num_chunks = min(num_chunks, 20)
    result = read_document_workflow(collection, document, start_chunk, num_chunks)
    text = f"Document: {result['document']} | Chunks {result['start_chunk']}-{result['start_chunk'] + result['num_chunks'] - 1}\n\n{result['content']}"
    return [TextContent(type="text", text=text)]


if __name__ == "__main__":
    mcp.run()
