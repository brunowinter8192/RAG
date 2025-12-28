# INFRASTRUCTURE
import logging
import os
from typing import Union

import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename='src/rag/logs/embedder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

EMBEDDING_URL = os.getenv("EMBEDDING_URL", "http://localhost:8081/v1/embeddings")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Qwen3-Embedding-8B")


# ORCHESTRATOR
def embed_workflow(texts: Union[str, list[str]]) -> list[list[float]]:
    if isinstance(texts, str):
        texts = [texts]
    embeddings = generate_embeddings(texts)
    logging.info(f"Embedded {len(texts)} texts")
    return embeddings


# FUNCTIONS

# Generate embeddings via llama-server API
def generate_embeddings(texts: list[str]) -> list[list[float]]:
    response = httpx.post(
        EMBEDDING_URL,
        json={"input": texts, "model": EMBEDDING_MODEL},
        timeout=300.0
    )
    response.raise_for_status()
    data = response.json()
    return [item["embedding"] for item in data["data"]]
