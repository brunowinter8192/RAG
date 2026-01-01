# INFRASTRUCTURE
import logging
import os

import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

from .embedder import embed_workflow

load_dotenv()

logging.basicConfig(
    filename='src/rag/logs/retriever.log',
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
    document: str | None = None
) -> list[dict]:
    conn = get_connection()
    query_vector = embed_query(query)
    results = search_vectors(conn, query_vector, top_k, collection, document)
    conn.close()
    logging.info(f"Search '{query[:50]}...' returned {len(results)} results")
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


# Format search results for display
def format_results(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"--- Result {i} (score: {r['score']}) ---")
        lines.append(f"Collection: {r['collection']} | Document: {r['document']}")
        lines.append(r['content'][:500])
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
