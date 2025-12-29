# INFRASTRUCTURE
import json
import logging
import os
from pathlib import Path

import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

from .chunker import chunk_workflow
from .embedder import embed_workflow

load_dotenv()

logging.basicConfig(
    filename='src/rag/logs/indexer.log',
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

BATCH_SIZE = 1
MAX_CHUNK_CHARS = 2000


# Index from chunks.json (pre-chunked, LLM-cleaned)
def index_json_workflow(json_path: str) -> int:
    conn = get_connection()
    ensure_schema(conn)

    chunks = load_chunks_json(json_path)
    if not chunks:
        conn.close()
        return 0

    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"][:MAX_CHUNK_CHARS] for c in batch]
        embeddings = embed_workflow(texts)
        store_chunks(conn, batch, embeddings)
        print(f"Indexed {min(i + BATCH_SIZE, total)}/{total} chunks")

    conn.close()
    logging.info(f"Indexed {total} chunks from {json_path}")
    return total


# Index from directory (legacy: re-chunks files)
def index_workflow(input_dir: str, file_patterns: list[str] = None) -> int:
    if file_patterns is None:
        file_patterns = ["*.md", "*.txt", "*.py", "*.js", "*.ts"]

    conn = get_connection()
    ensure_schema(conn)

    files = collect_files(input_dir, file_patterns)
    total_indexed = 0

    for file_path in files:
        chunks = chunk_workflow(str(file_path))
        if not chunks:
            continue

        texts = [c["content"] for c in chunks]
        embeddings = embed_workflow(texts)

        store_chunks(conn, chunks, embeddings)
        total_indexed += len(chunks)

    conn.close()
    logging.info(f"Indexed {total_indexed} chunks from {len(files)} files")
    return total_indexed


# FUNCTIONS

# Load chunks from JSON file
def load_chunks_json(json_path: str) -> list[dict]:
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"chunks.json not found: {json_path}")

    with open(path) as f:
        data = json.load(f)

    source = data.get("source_pdf", str(path))
    raw_chunks = data.get("chunks", [])
    total = len(raw_chunks)

    return [
        {
            "content": c["content"],
            "source": source,
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
                source TEXT NOT NULL,
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


# Collect files matching patterns from directory
def collect_files(input_dir: str, patterns: list[str]) -> list[Path]:
    root = Path(input_dir)
    files = []
    for pattern in patterns:
        files.extend(root.rglob(pattern))
    logging.info(f"Found {len(files)} files in {input_dir}")
    return files


# Store chunks with embeddings in PostgreSQL
def store_chunks(conn, chunks: list[dict], embeddings: list[list[float]]) -> None:
    with conn.cursor() as cur:
        for chunk, embedding in zip(chunks, embeddings):
            cur.execute(
                """
                INSERT INTO documents (content, source, chunk_index, total_chunks, embedding)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    chunk["content"],
                    chunk["source"],
                    chunk["chunk_index"],
                    chunk["total_chunks"],
                    embedding
                )
            )
    conn.commit()
