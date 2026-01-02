# INFRASTRUCTURE
import logging
import os
from pathlib import Path

import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

from .embedder import embed_workflow

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"

logging.basicConfig(
    filename=LOG_DIR / "retriever.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "rag")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "rag")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rag")
DEFAULT_TOP_K = 5


# ORCHESTRATORS

def search_workflow(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    collection: str | None = None,
    document: str | None = None,
    neighbors: int = 0
) -> list[dict]:
    conn = get_connection()
    query_vector = embed_query(query)
    results = search_vectors(conn, query_vector, top_k, collection, document)
    if neighbors > 0:
        results = expand_results(conn, results, neighbors)
    conn.close()
    logging.info(f"Search '{query[:50]}...' returned {len(results)} results (neighbors={neighbors})")
    return results


def list_collections_workflow() -> list[dict]:
    conn = get_connection()
    results = query_collections(conn)
    conn.close()
    return results


def list_documents_workflow(collection: str) -> list[dict]:
    conn = get_connection()
    results = query_documents(conn, collection)
    conn.close()
    return results


def read_document_workflow(collection: str, document: str, start_chunk: int, num_chunks: int = 5) -> dict:
    conn = get_connection()
    chunks = fetch_chunk_range(conn, collection, document, start_chunk, start_chunk + num_chunks - 1)
    conn.close()
    return {
        'content': merge_chunks(chunks),
        'collection': collection,
        'document': document,
        'start_chunk': start_chunk,
        'num_chunks': len(chunks)
    }


# FUNCTIONS

# Get PostgreSQL connection
def get_connection():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )
    register_vector(conn)
    return conn


# Embed search query
def embed_query(query: str) -> list[float]:
    embeddings = embed_workflow(query)
    return embeddings[0]


# Search vectors in PostgreSQL using cosine distance
def search_vectors(
    conn,
    query_vector: list[float],
    top_k: int,
    collection: str | None = None,
    document: str | None = None
) -> list[dict]:
    where_clauses = []
    where_params = []

    if collection:
        where_clauses.append("collection = %s")
        where_params.append(collection)
    if document:
        where_clauses.append("document = %s")
        where_params.append(document)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    params = [query_vector] + where_params + [query_vector, top_k]

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT content, collection, document, chunk_index,
                   1 - (embedding <=> %s::vector) as score
            FROM documents
            {where_sql}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            params
        )
        rows = cur.fetchall()

    return [
        {
            "content": row[0],
            "collection": row[1],
            "document": row[2],
            "chunk_index": row[3],
            "score": round(float(row[4]), 4)
        }
        for row in rows
    ]


# Expand results with neighboring chunks, deduplicated and merged
def expand_results(conn, results: list[dict], neighbors: int) -> list[dict]:
    groups = group_by_document(results, neighbors)
    expanded = []

    for (collection, document), group_data in groups.items():
        ranges = find_contiguous_ranges(group_data['indices'])
        hit_scores = group_data['hit_scores']

        for start_idx, end_idx in ranges:
            chunks = fetch_chunk_range(conn, collection, document, start_idx, end_idx)
            range_score = max(
                (score for idx, score in hit_scores.items() if start_idx <= idx <= end_idx),
                default=0
            )
            expanded.append({
                'content': merge_chunks(chunks),
                'collection': collection,
                'document': document,
                'chunk_index': start_idx,
                'score': range_score
            })

    expanded.sort(key=lambda r: (r['collection'], r['document'], r['chunk_index']))
    return expanded


# Merge chunks with overlap deduplication
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


# Group results by document and collect all needed indices with hit scores
def group_by_document(results: list[dict], neighbors: int) -> dict:
    groups = {}
    for r in results:
        key = (r['collection'], r['document'])
        if key not in groups:
            groups[key] = {'indices': set(), 'hit_scores': {}}

        idx = r['chunk_index']
        groups[key]['hit_scores'][idx] = r['score']
        for i in range(max(0, idx - neighbors), idx + neighbors + 1):
            groups[key]['indices'].add(i)

    return groups


# Find contiguous ranges from a set of indices
def find_contiguous_ranges(indices: set) -> list[tuple]:
    if not indices:
        return []

    sorted_indices = sorted(indices)
    ranges = []
    start = sorted_indices[0]
    end = start

    for idx in sorted_indices[1:]:
        if idx == end + 1:
            end = idx
        else:
            ranges.append((start, end))
            start = idx
            end = idx

    ranges.append((start, end))
    return ranges


# Fetch chunks for a contiguous range
def fetch_chunk_range(conn, collection: str, document: str, start_idx: int, end_idx: int) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT content, chunk_index
            FROM documents
            WHERE collection = %s AND document = %s
              AND chunk_index BETWEEN %s AND %s
            ORDER BY chunk_index
            """,
            (collection, document, start_idx, end_idx)
        )
        rows = cur.fetchall()

    return [{"content": row[0], "chunk_index": row[1]} for row in rows]


# Format search results for display
def format_results(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"--- Result {i} (score: {r['score']}) ---")
        lines.append(f"Collection: {r['collection']} | Document: {r['document']}")
        lines.append(r['content'])
        lines.append("")
    return "\n".join(lines)


# Query all collections with chunk counts
def query_collections(conn) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT collection, COUNT(*) as chunk_count
            FROM documents
            GROUP BY collection
            ORDER BY collection
        """)
        rows = cur.fetchall()
    return [{"collection": row[0], "chunks": row[1]} for row in rows]


# Query all documents in a collection with chunk counts
def query_documents(conn, collection: str) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT document, COUNT(*) as chunk_count
            FROM documents
            WHERE collection = %s
            GROUP BY document
            ORDER BY document
        """, (collection,))
        rows = cur.fetchall()
    return [{"document": row[0], "chunks": row[1]} for row in rows]


# Format collections list for display
def format_collections(results: list[dict]) -> str:
    if not results:
        return "No collections indexed."
    lines = ["Indexed Collections:", ""]
    for r in results:
        lines.append(f"  {r['collection']} ({r['chunks']} chunks)")
    return "\n".join(lines)


# Format documents list for display
def format_documents(results: list[dict]) -> str:
    if not results:
        return "No documents in this collection."
    lines = ["Documents:", ""]
    for r in results:
        lines.append(f"  {r['document']} ({r['chunks']} chunks)")
    return "\n".join(lines)
