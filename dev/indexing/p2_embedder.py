# INFRASTRUCTURE
import logging
import math

import httpx

logger = logging.getLogger(__name__)

EMBEDDING_URL = "http://localhost:8081/v1/embeddings"
EMBEDDING_MODEL = "Qwen3-Embedding-8B"
MAX_CHARS = 4000 * 3
MRL_DIMS = 1024


# FUNCTIONS

# Generate dense embeddings via llama-server, returns full 4096d vectors
def embed(texts: list[str], prefix: str | None = None) -> list[list[float]]:
    texts = [t[:MAX_CHARS] for t in texts]
    if prefix:
        texts = [f"{prefix}{t}" for t in texts]
    response = httpx.post(
        EMBEDDING_URL,
        json={"input": texts, "model": EMBEDDING_MODEL},
        timeout=300.0,
    )
    response.raise_for_status()
    data = response.json()
    return [item["embedding"] for item in data["data"]]


# Truncate embeddings to MRL dims and L2 renormalize
def truncate_mrl(embeddings: list[list[float]], dims: int = MRL_DIMS) -> list[list[float]]:
    result = []
    for emb in embeddings:
        truncated = emb[:dims]
        norm = math.sqrt(sum(v * v for v in truncated))
        if norm > 0:
            truncated = [v / norm for v in truncated]
        result.append(truncated)
    return result
