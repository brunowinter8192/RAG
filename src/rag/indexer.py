# INFRASTRUCTURE
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

from .embedder import embed_workflow
from .sparse_embedder import sparse_embed_workflow

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

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
BATCH_SIZE = 32


# ORCHESTRATOR


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
    skipped_total = 0
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]
        embeddings, sparse_embeddings = parallel_embed(texts)
        skipped = store_chunks(conn, batch, embeddings, sparse_embeddings)
        skipped_total += skipped
        suffix = f" ({skipped} NULL skipped)" if skipped else ""
        print(f"Indexed {min(i + BATCH_SIZE, total)}/{total} chunks{suffix}")

    conn.close()
    indexed = total - skipped_total
    logging.info(f"Indexed {indexed}/{total} chunks from {json_path} ({skipped_total} skipped)")
    return indexed


# Delete chunks by collection and/or document; optionally remove source MDs from data/documents/
def delete_workflow(
    collection: str | None = None,
    document: str | None = None,
    remove_source: bool = False,
) -> dict:
    if not collection and not document:
        raise ValueError("At least --collection or --document required")
    if remove_source and not collection:
        raise ValueError("--remove-source requires --collection")
    conn = get_connection()
    deleted = delete_chunks(conn, collection, document)
    conn.close()
    files_removed: list[str] = []
    if remove_source:
        import shutil
        from .server_manager import RAG_ROOT
        coll_dir = RAG_ROOT / "data" / "documents" / collection
        if document:
            for candidate in (coll_dir / document, coll_dir / "raw" / document):
                if candidate.exists() and candidate.is_file():
                    candidate.unlink()
                    files_removed.append(str(candidate))
        elif coll_dir.exists() and coll_dir.is_dir():
            shutil.rmtree(coll_dir)
            files_removed.append(str(coll_dir))
    return {"chunks_deleted": deleted, "files_removed": files_removed}


# Backfill sparse embeddings for chunks that have NULL sparse_embedding
def backfill_splade_workflow(collection: str) -> int:
    conn = get_connection()
    ensure_schema(conn)

    rows = fetch_null_sparse(conn, collection)
    if not rows:
        print(f"No chunks with NULL sparse_embedding in {collection}")
        conn.close()
        return 0

    total = len(rows)
    updated = 0
    for i in range(0, total, BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        ids = [r[0] for r in batch]
        texts = [r[1] for r in batch]
        sparse_embeddings = sparse_embed_workflow(texts)
        update_sparse(conn, ids, sparse_embeddings)
        updated += len(batch)
        print(f"Backfilled {min(updated, total)}/{total} chunks")

    conn.close()
    logging.info(f"Backfilled {total} sparse embeddings for {collection}")
    return total


# FUNCTIONS

# Generate dense and sparse embeddings in parallel.
# `search_document: ` prefix is REQUIRED for Qwen3-Embedding-8B — without it, ~3-4% of
# code-heavy chunks (those starting with bare `import` statements or similar dense
# code patterns) silently produce all-None embeddings due to a tokenizer edge case.
# See decisions/OldThemes/null_embedding_qwen3_prefix.md for the full diagnosis.
def parallel_embed(texts: list[str]) -> tuple[list[list[float]], list[dict]]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        emb_future = executor.submit(embed_workflow, texts, "search_document: ")
        sparse_future = executor.submit(sparse_embed_workflow, texts)
        return emb_future.result(), sparse_future.result()


# Load chunks from JSON file
def load_chunks_json(json_path: str) -> list[dict]:
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"chunks.json not found: {json_path}")

    with open(path) as f:
        data = json.load(f)

    collection = data.get("collection", path.parent.name)
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
        cur.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS sparse_embedding sparsevec(30522)")
        cur.execute("""
            DO $$ BEGIN
                ALTER TABLE documents ADD COLUMN tsv tsvector
                    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
            EXCEPTION WHEN duplicate_column THEN NULL;
            END $$
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_documents_tsv ON documents USING gin(tsv)")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_unique ON documents(collection, document, chunk_index)")
    conn.commit()
    logging.info("Schema ensured")


# Delete all chunks for a collection
def delete_collection(conn, collection: str) -> int:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents WHERE collection = %s", (collection,))
        deleted = cur.rowcount
    conn.commit()
    return deleted


# Check if a document has a complete chunk set in the documents table.
# Complete means COUNT(*) > 0 AND COUNT(*) == MAX(total_chunks) — every
# expected chunk-row is present. Used by workflow.py index-dir / index-file
# to detect documents that were indexed before indexed_files tracking
# existed (adopt-on-complete pattern: register hash without re-embed).
def doc_is_complete(conn, collection: str, document: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*), MAX(total_chunks)
            FROM documents
            WHERE collection = %s AND document = %s
            """,
            (collection, document),
        )
        actual, expected = cur.fetchone()
    return actual is not None and actual > 0 and actual == expected


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


# Store chunks with dense and sparse embeddings in PostgreSQL. Returns count of
# chunks SKIPPED because the embedding model returned a NULL vector.
def store_chunks(conn, chunks: list[dict], embeddings: list[list[float]], sparse_embeddings: list[dict]) -> int:
    skipped = 0
    with conn.cursor() as cur:
        for chunk, embedding, sparse in zip(chunks, embeddings, sparse_embeddings):
            if embedding is None or all(v is None for v in embedding):
                logging.warning(f"NULL embedding skipped: collection={chunk['collection']} document={chunk['document']} chunk_index={chunk['chunk_index']}")
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
    return skipped


# Fetch chunks with NULL sparse_embedding for backfill
def fetch_null_sparse(conn, collection: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, content FROM documents
            WHERE collection = %s AND sparse_embedding IS NULL
            ORDER BY id
            """,
            (collection,)
        )
        return cur.fetchall()


# Update sparse_embedding for given chunk IDs
def update_sparse(conn, ids: list[int], sparse_embeddings: list[dict]) -> None:
    with conn.cursor() as cur:
        for chunk_id, sparse in zip(ids, sparse_embeddings):
            cur.execute(
                "UPDATE documents SET sparse_embedding = %s WHERE id = %s",
                (format_sparsevec(sparse), chunk_id)
            )
    conn.commit()
