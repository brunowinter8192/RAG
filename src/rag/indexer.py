# INFRASTRUCTURE
import json
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
    filename=LOG_DIR / "indexer.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "rag")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "rag")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rag")
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "4096"))


# ORCHESTRATORS

BATCH_SIZE = 32


# Index from chunks.json (pre-chunked, LLM-cleaned)
def index_json_workflow(json_path: str) -> int:
    conn = get_connection()
    ensure_schema(conn)

    chunks = load_chunks_json(json_path)
    if not chunks:
        conn.close()
        return 0

    collection = chunks[0]["collection"]
    deleted = delete_collection(conn, collection)
    if deleted > 0:
        print(f"Deleted {deleted} existing chunks for {collection}")

    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]
        embeddings = embed_workflow(texts)
        store_chunks(conn, batch, embeddings)
        print(f"Indexed {min(i + BATCH_SIZE, total)}/{total} chunks")

    conn.close()
    logging.info(f"Indexed {total} chunks from {json_path}")
    return total


# Delete chunks by collection and/or document
def delete_workflow(collection: str | None = None, document: str | None = None) -> int:
    if not collection and not document:
        raise ValueError("At least --collection or --document required")
    conn = get_connection()
    deleted = delete_chunks(conn, collection, document)
    conn.close()
    return deleted


# FUNCTIONS

# Load chunks from JSON file
def load_chunks_json(json_path: str) -> list[dict]:
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"chunks.json not found: {json_path}")

    with open(path) as f:
        data = json.load(f)

    collection = path.parent.name
    document = data.get("document", path.stem + ".md")
    raw_chunks = data.get("chunks", [])
    total = len(raw_chunks)

    return [
        {
            "content": c["content"],
            "collection": collection,
            "document": c.get("document", document),
            "chunk_index": c["index"],
            "total_chunks": total
        }
        for c in raw_chunks
    ]


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


# Ensure pgvector extension and table exist
def ensure_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                collection TEXT NOT NULL,
                document TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                total_chunks INTEGER NOT NULL,
                embedding vector({VECTOR_DIMENSION})
            )
        """)
        # Note: pgvector limits index to 2000 dims, Qwen3 has 4096
        # For small collections (<10k), sequential scan is fast enough
        # For larger collections, consider dimensionality reduction
    conn.commit()
    logging.info("Schema ensured")


# Delete all chunks for a collection
def delete_collection(conn, collection: str) -> int:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents WHERE collection = %s", (collection,))
        deleted = cur.rowcount
    conn.commit()
    return deleted


# Delete chunks by collection and/or document
def delete_chunks(conn, collection: str | None, document: str | None) -> int:
    conditions = []
    params = []
    if collection:
        conditions.append("collection = %s")
        params.append(collection)
    if document:
        conditions.append("document = %s")
        params.append(document)

    where = " AND ".join(conditions)
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM documents WHERE {where}", params)
        deleted = cur.rowcount
    conn.commit()
    return deleted


# Store chunks with embeddings in PostgreSQL
def store_chunks(conn, chunks: list[dict], embeddings: list[list[float]]) -> None:
    with conn.cursor() as cur:
        for chunk, embedding in zip(chunks, embeddings):
            cur.execute(
                """
                INSERT INTO documents (content, collection, document, chunk_index, total_chunks, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    chunk["content"],
                    chunk["collection"],
                    chunk["document"],
                    chunk["chunk_index"],
                    chunk["total_chunks"],
                    embedding
                )
            )
    conn.commit()
