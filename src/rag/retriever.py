# INFRASTRUCTURE
import logging
from pathlib import Path

from .db import get_connection, validate_collection, query_collections, query_documents, query_progress, fetch_chunk_range
from .search_primitives import embed_query, search_vectors, bm25_search, splade_search
from .fusion import cc_fusion
from .formatting import format_results, format_collections, format_documents, format_progress
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
    document: str | None = None
) -> list[dict]:
    top_k = max(top_k, 20)
    top_k = min(top_k, 50)
    conn = get_connection()
    if collection:
        validate_collection(conn, collection)
    query_vector = embed_query(query)
    results = search_vectors(conn, query_vector, top_k, collection, document)
    results = filter_by_score(results, 0.5)
    conn.close()
    logging.info(f"Search '{query[:50]}...' returned {len(results)} results")
    return results


def list_collections_workflow(filter: str | None = None) -> list[dict]:
    conn = get_connection()
    results = query_collections(conn, filter)
    conn.close()
    return results


def list_documents_workflow(collection: str, document: str | None = None, filter: str | None = None) -> list[dict]:
    conn = get_connection()
    validate_collection(conn, collection)
    results = query_documents(conn, collection, document, filter)
    conn.close()
    return results


def progress_workflow(collection: str) -> list[dict]:
    conn = get_connection()
    validate_collection(conn, collection)
    results = query_progress(conn, collection)
    conn.close()
    return results


def read_document_workflow(collection: str, document: str, chunk_index: int, before: int = 0, after: int = 0) -> dict:
    conn = get_connection()
    validate_collection(conn, collection)
    chunks = fetch_chunk_range(conn, collection, document, chunk_index - before, chunk_index + after)
    conn.close()
    return {
        'content': merge_chunks(chunks),
        'collection': collection,
        'document': document,
        'chunk_index': chunk_index,
        'before': before,
        'after': after,
        'chunks_returned': len(chunks)
    }


def search_hybrid_workflow(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    collection: str | None = None,
    document: str | None = None,
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


# Merge chunks into continuous text with overlap deduplication
def merge_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    result = chunks[0]['content']
    for i in range(1, len(chunks)):
        overlap = find_overlap(result, chunks[i]['content'])
        result += "\n\n" + chunks[i]['content'][overlap:]
    return result


# Find longest suffix of text1 that is prefix of text2
def find_overlap(text1: str, text2: str, max_overlap: int = 300) -> int:
    for size in range(min(len(text1), len(text2), max_overlap), 0, -1):
        if text1[-size:] == text2[:size]:
            return size
    return 0
