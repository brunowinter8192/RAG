# INFRASTRUCTURE
import os

import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
POSTGRES_USER = os.getenv("POSTGRES_USER", "rag")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "rag")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rag")


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


# Validate that collection exists in database
def validate_collection(conn, collection: str):
    existing = [r['collection'] for r in query_collections(conn)]
    if collection not in existing:
        raise ValueError(f"Collection '{collection}' not found. Available: {', '.join(existing)}")


# Add document filter clause (LIKE if value contains %, else exact match)
def add_document_filter(where_clauses: list, where_params: list, document: str):
    if '%' in document:
        where_clauses.append("document LIKE %s")
    else:
        where_clauses.append("document = %s")
    where_params.append(document)


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
def query_documents(conn, collection: str, document: str | None = None) -> list[dict]:
    where_clauses = ["collection = %s"]
    where_params = [collection]
    if document:
        add_document_filter(where_clauses, where_params, document)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT document, COUNT(*) as chunk_count
            FROM documents
            WHERE {' AND '.join(where_clauses)}
            GROUP BY document
            ORDER BY document
        """, where_params)
        rows = cur.fetchall()
    return [{"document": row[0], "chunks": row[1]} for row in rows]


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
