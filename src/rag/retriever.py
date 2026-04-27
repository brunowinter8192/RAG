# INFRASTRUCTURE
import logging
from pathlib import Path

from .db import get_connection, validate_collection, query_collections, query_documents, fetch_chunk_range
from .search_primitives import embed_query, search_vectors, bm25_search, splade_search
from .fusion import cc_fusion
from .expansion import expand_results, merge_chunks
from .formatting import format_results, format_collections, format_documents
from .reranker import rerank_workflow

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "retriever.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DEFAULT_TOP_K = 5
HYBRID_CANDIDATES = 50
RERANK_CANDIDATES = 50


# ORCHESTRATOR

def search_workflow(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    collection: str | None = None,
    document: str | None = None,
    neighbors: int = 0
) -> list[dict]:
    top_k = max(top_k, 20)
    top_k = min(top_k, 50)
    conn = get_connection()
    if collection:
        validate_collection(conn, collection)
    query_vector = embed_query(query)
    results = search_vectors(conn, query_vector, top_k, collection, document)
    if neighbors > 0:
        results = expand_results(conn, results, neighbors)
    results = filter_by_score(results, 0.5)
    conn.close()
    logging.info(f"Search '{query[:50]}...' returned {len(results)} results (neighbors={neighbors})")
    return results


def list_collections_workflow() -> list[dict]:
    conn = get_connection()
    results = query_collections(conn)
    conn.close()
    return results


def list_documents_workflow(collection: str, document: str | None = None) -> list[dict]:
    conn = get_connection()
    validate_collection(conn, collection)
    results = query_documents(conn, collection, document)
    conn.close()
    return results


def read_document_workflow(collection: str, document: str, start_chunk: int, num_chunks: int = 5) -> dict:
    num_chunks = max(num_chunks, 10)
    conn = get_connection()
    validate_collection(conn, collection)
    chunks = fetch_chunk_range(conn, collection, document, start_chunk, start_chunk + num_chunks - 1)
    conn.close()
    return {
        'content': merge_chunks(chunks),
        'collection': collection,
        'document': document,
        'start_chunk': start_chunk,
        'num_chunks': len(chunks)
    }


def search_hybrid_workflow(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    collection: str | None = None,
    document: str | None = None,
    neighbors: int = 0,
    rerank: bool = False
) -> list[dict]:
    top_k = max(top_k, 20)
    top_k = min(top_k, 50)
    conn = get_connection()
    if collection:
        validate_collection(conn, collection)
    query_vector = embed_query(query)
    vector_results = search_vectors(conn, query_vector, HYBRID_CANDIDATES, collection, document)
    keyword_results = splade_search(conn, query, HYBRID_CANDIDATES, collection, document)
    rrf_top = RERANK_CANDIDATES if rerank else top_k
    results = cc_fusion(vector_results, keyword_results, rrf_top)
    if rerank:
        results = rerank_workflow(query, results, top_k)
        results = filter_by_score(results, 0.3)
    else:
        results = filter_by_score(results, 0.01)
    if neighbors > 0:
        results = expand_results(conn, results, neighbors)
    conn.close()
    logging.info(f"Hybrid search '{query[:50]}...' returned {len(results)} results (vec={len(vector_results)}, splade={len(keyword_results)}, rerank={rerank})")
    return results


def search_keyword_workflow(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    collection: str | None = None,
    document: str | None = None
) -> list[dict]:
    top_k = max(top_k, 20)
    top_k = min(top_k, 50)
    conn = get_connection()
    if collection:
        validate_collection(conn, collection)
    results = bm25_search(conn, query, top_k, collection, document)
    results = filter_by_score(results, 0.05)
    conn.close()
    logging.info(f"BM25 search '{query[:50]}...' returned {len(results)} results")
    return results


# FUNCTIONS

# Filter results below minimum relevance score
def filter_by_score(results: list[dict], min_score: float) -> list[dict]:
    return [r for r in results if r['score'] >= min_score]
