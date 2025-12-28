# INFRASTRUCTURE
import logging
import uuid
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# From chunker.py: Chunk files into semantic units
from .chunker import chunk_workflow

# From embedder.py: Generate embeddings
from .embedder import embed_workflow

logging.basicConfig(
    filename='src/rag/logs/indexer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

COLLECTION_NAME = "documents"
VECTOR_SIZE = 4096
QDRANT_PATH = "./qdrant_storage"


# ORCHESTRATOR
def index_workflow(input_dir: str, file_patterns: list[str] = None) -> int:
    if file_patterns is None:
        file_patterns = ["*.md", "*.txt", "*.py", "*.js", "*.ts"]

    client = get_client()
    ensure_collection(client)

    files = collect_files(input_dir, file_patterns)
    total_indexed = 0

    for file_path in files:
        chunks = chunk_workflow(str(file_path))
        if not chunks:
            continue

        texts = [c["content"] for c in chunks]
        embeddings = embed_workflow(texts)

        points = create_points(chunks, embeddings)
        store_points(client, points)
        total_indexed += len(points)

    logging.info(f"Indexed {total_indexed} chunks from {len(files)} files")
    return total_indexed


# FUNCTIONS

# Get or create Qdrant client
def get_client() -> QdrantClient:
    return QdrantClient(path=QDRANT_PATH)


# Ensure collection exists with correct schema
def ensure_collection(client: QdrantClient) -> None:
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        logging.info(f"Created collection: {COLLECTION_NAME}")


# Collect files matching patterns from directory
def collect_files(input_dir: str, patterns: list[str]) -> list[Path]:
    root = Path(input_dir)
    files = []
    for pattern in patterns:
        files.extend(root.rglob(pattern))
    logging.info(f"Found {len(files)} files in {input_dir}")
    return files


# Create Qdrant points from chunks and embeddings
def create_points(chunks: list[dict], embeddings: list[list[float]]) -> list[PointStruct]:
    return [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "content": chunk["content"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "total_chunks": chunk["total_chunks"]
            }
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]


# Store points in Qdrant
def store_points(client: QdrantClient, points: list[PointStruct]) -> None:
    client.upsert(collection_name=COLLECTION_NAME, points=points)
