# INFRASTRUCTURE
import json
import logging
import os
from pathlib import Path

import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

from .embedder import embed_workflow
from .sparse_embedder import sparse_embed_workflow

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"

logging.basicConfig(
    filename=LOG_DIR / "indexer.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
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
    documents = {c["document"] for c in chunks}
    for doc in sorted(documents):
        deleted = delete_chunks(conn, collection, doc)
        if deleted > 0:
            print(f"Deleted {deleted} existing chunks for {collection}/{doc}")

    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]
        embeddings = embed_workflow(texts)
        sparse_embeddings = sparse_embed_workflow(texts)
        store_chunks(conn, batch, embeddings, sparse_embeddings)
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
        cur.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS sparse_embedding sparsevec(30522)")
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


# Format sparse vector for pgvector sparsevec type: '{idx1:val1,idx2:val2}/dimensions'
def format_sparsevec(sparse: dict, dimensions: int = 30522) -> str:
    pairs = ",".join(f"{idx}:{val}" for idx, val in zip(sparse["indices"], sparse["values"]))
    return f"{{{pairs}}}/{dimensions}"


# Store chunks with dense and sparse embeddings in PostgreSQL
def store_chunks(conn, chunks: list[dict], embeddings: list[list[float]], sparse_embeddings: list[dict]) -> None:
    skipped = 0
    with conn.cursor() as cur:
        for chunk, embedding, sparse in zip(chunks, embeddings, sparse_embeddings):
            if embedding is None or all(v is None for v in embedding):
                logging.warning(f"NULL embedding skipped: collection={chunk['collection']} chunk_index={chunk['chunk_index']}")
                skipped += 1
                continue
            cur.execute(
                """
                INSERT INTO documents (content, collection, document, chunk_index, total_chunks, embedding, sparse_embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    chunk["content"],
                    chunk["collection"],
                    chunk["document"],
                    chunk["chunk_index"],
                    chunk["total_chunks"],
                    embedding,
                    format_sparsevec(sparse)
                )
            )
    conn.commit()
    if skipped:
        logging.warning(f"Skipped {skipped} chunks with NULL embeddings")
