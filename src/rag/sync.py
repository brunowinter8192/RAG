# INFRASTRUCTURE
"""Project doc indexing — manifest-driven sync with hash-based change detection.

Each project that wants its docs indexed places a `.rag-docs.json` at its root:

    {
      "collection": "Trading_internal",
      "include": [
        "decisions/*.md",
        "concepts/*.md",
        "strategies/**/*.md",
        "CLAUDE.md"
      ]
    }

`sync_docs_workflow(project_root)` reads the manifest, expands the globs,
hashes every matched file, diffs against the `indexed_files` table in
postgres, and performs only the necessary add/update/remove operations.
Unchanged files are skipped — no embedder calls.
"""

import hashlib
import json
import logging
from pathlib import Path

from .chunker import chunk_workflow
from .db import get_connection
from .indexer import (
    BATCH_SIZE,
    delete_chunks,
    ensure_schema,
    parallel_embed,
    store_chunks,
)
from .server_manager import ensure_ready

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "sync.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

MANIFEST_NAME = ".rag-docs.json"


# ORCHESTRATOR

def sync_docs_workflow(
    project_root: str | Path,
    chunk_size: int = 2000,
    overlap: int = 400,
) -> dict:
    """Sync project docs into RAG collection per `.rag-docs.json` manifest.

    Returns a result dict:
        {
          "collection": str,
          "added": list[str],
          "updated": list[str],
          "removed": list[str],
          "unchanged": list[str],
          "total_chunks_indexed": int,
        }
    """
    project_root = Path(project_root).expanduser().resolve()

    if not project_root.is_dir():
        raise FileNotFoundError(f"Project root not found: {project_root}")

    manifest = read_manifest(project_root)
    collection = manifest["collection"]
    includes = manifest["include"]

    files = expand_globs(project_root, includes)

    conn = get_connection(purpose="ddl")
    ensure_schema(conn)
    ensure_indexed_files_table(conn)

    db_hashes = get_db_hashes(conn, collection)
    current_hashes = {rel: compute_hash(path) for rel, path in files.items()}

    added = sorted(r for r in current_hashes if r not in db_hashes)
    removed = sorted(r for r in db_hashes if r not in current_hashes)
    updated = sorted(
        r for r in current_hashes
        if r in db_hashes and current_hashes[r] != db_hashes[r]
    )
    unchanged = sorted(
        r for r in current_hashes
        if r in db_hashes and current_hashes[r] == db_hashes[r]
    )

    to_index = added + updated

    # Embedder + SPLADE only needed when we have new content to embed.
    # Removed-only runs are pure DB deletes — no GPU cost.
    if to_index:
        ensure_ready("index")

    total_chunks = 0
    for rel in to_index:
        n = index_file(
            conn, files[rel],
            collection=collection,
            document=rel,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        upsert_hash(conn, collection, rel, current_hashes[rel])
        total_chunks += n

    for rel in removed:
        delete_chunks(conn, collection, rel)
        delete_indexed_file(conn, collection, rel)

    conn.close()

    logging.info(
        f"sync_docs {collection}: +{len(added)} ~{len(updated)} -{len(removed)} ={len(unchanged)} "
        f"({total_chunks} chunks indexed)"
    )

    return {
        "collection": collection,
        "added": added,
        "updated": updated,
        "removed": removed,
        "unchanged": unchanged,
        "total_chunks_indexed": total_chunks,
    }


# FUNCTIONS

# Read and validate .rag-docs.json
def read_manifest(project_root: Path) -> dict:
    path = project_root / MANIFEST_NAME
    if not path.is_file():
        raise FileNotFoundError(
            f"No {MANIFEST_NAME} found in {project_root}. "
            f"Create one with: {{\"collection\": \"<name>\", \"include\": [\"<glob>\", ...]}}"
        )
    data = json.loads(path.read_text())
    if "collection" not in data or "include" not in data:
        raise ValueError(
            f"Manifest must have 'collection' and 'include' keys: {path}"
        )
    if not isinstance(data["collection"], str) or not data["collection"]:
        raise ValueError(f"Manifest 'collection' must be a non-empty string: {path}")
    if not isinstance(data["include"], list) or not data["include"]:
        raise ValueError(
            f"Manifest 'include' must be a non-empty list of glob patterns: {path}"
        )
    return data


# Expand glob patterns relative to project_root
def expand_globs(project_root: Path, includes: list[str]) -> dict[str, Path]:
    """Return {relative_path_str: absolute_Path} for every .md file matched.

    Files matched by multiple patterns are de-duplicated via the relative-path key.
    Only `.md` files are kept.
    """
    seen: dict[str, Path] = {}
    for pattern in includes:
        for path in project_root.glob(pattern):
            if path.is_file() and path.suffix == ".md":
                rel = str(path.relative_to(project_root))
                seen[rel] = path
    return seen


# Compute SHA256 of file content
def compute_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Ensure the indexed_files tracking table exists
def ensure_indexed_files_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS indexed_files (
                collection TEXT NOT NULL,
                document TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                last_indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (collection, document)
            )
        """)
    conn.commit()


# Fetch stored hashes for a collection
def get_db_hashes(conn, collection: str) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT document, sha256 FROM indexed_files WHERE collection = %s",
            (collection,),
        )
        return {row[0]: row[1] for row in cur.fetchall()}


# Upsert (collection, document) → sha256 entry
def upsert_hash(conn, collection: str, document: str, sha256: str) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO indexed_files (collection, document, sha256, last_indexed_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (collection, document) DO UPDATE
            SET sha256 = EXCLUDED.sha256, last_indexed_at = NOW()
        """, (collection, document, sha256))
    conn.commit()


# Remove tracker row for a removed file
def delete_indexed_file(conn, collection: str, document: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM indexed_files WHERE collection = %s AND document = %s",
            (collection, document),
        )
    conn.commit()


# Chunk + embed + store a single file. Replaces existing chunks for that document.
def index_file(
    conn,
    file_path: Path,
    collection: str,
    document: str,
    chunk_size: int = 2000,
    overlap: int = 400,
) -> int:
    raw_chunks = chunk_workflow(str(file_path), chunk_size, overlap)

    # Always clear existing chunks first (handles updated AND empty-now cases)
    delete_chunks(conn, collection, document)

    if not raw_chunks:
        return 0

    total = len(raw_chunks)
    chunks = [
        {
            "content": c["content"],
            "collection": collection,
            "document": document,
            "chunk_index": i,
            "total_chunks": total,
        }
        for i, c in enumerate(raw_chunks)
    ]

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]
        embeddings, sparse = parallel_embed(texts)
        store_chunks(conn, batch, embeddings, sparse)

    return total
