# INFRASTRUCTURE
import logging
from qdrant_client import QdrantClient

# From embedder.py: Generate embeddings
from .embedder import embed_workflow

logging.basicConfig(
    filename='src/rag/logs/retriever.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

COLLECTION_NAME = "documents"
QDRANT_PATH = "./qdrant_storage"
DEFAULT_TOP_K = 5


# ORCHESTRATOR
def search_workflow(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    client = get_client()
    query_vector = embed_query(query)
    results = search_vectors(client, query_vector, top_k)
    formatted = format_results(results)
    logging.info(f"Search '{query[:50]}...' returned {len(formatted)} results")
    return formatted


# FUNCTIONS

# Get Qdrant client
def get_client() -> QdrantClient:
    return QdrantClient(path=QDRANT_PATH)


# Embed search query
def embed_query(query: str) -> list[float]:
    embeddings = embed_workflow(query)
    return embeddings[0]


# Search vectors in Qdrant
def search_vectors(client: QdrantClient, query_vector: list[float], top_k: int) -> list:
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return results


# Format results for output
def format_results(results: list) -> list[dict]:
    return [
        {
            "content": r.payload.get("content", ""),
            "source": r.payload.get("source", ""),
            "chunk_index": r.payload.get("chunk_index", 0),
            "score": round(r.score, 4)
        }
        for r in results
    ]
