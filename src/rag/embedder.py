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
TOKENIZE_URL = os.getenv("TOKENIZE_URL", "http://localhost:8081/tokenize")
MAX_TOKENS = 4000


# ORCHESTRATOR
def embed_workflow(texts: Union[str, list[str]]) -> list[list[float]]:
    if isinstance(texts, str):
        texts = [texts]
    texts = [truncate_to_tokens(t, MAX_TOKENS) for t in texts]
    embeddings = generate_embeddings(texts)
    logging.info(f"Embedded {len(texts)} texts")
    return embeddings


# FUNCTIONS

# Count tokens in text via llama-server API
def count_tokens(text: str) -> int:
    response = httpx.post(TOKENIZE_URL, json={"content": text}, timeout=30.0)
    response.raise_for_status()
    return len(response.json()["tokens"])


# Truncate text to max tokens using binary search
def truncate_to_tokens(text: str, max_tokens: int) -> str:
    token_count = count_tokens(text)
    if token_count <= max_tokens:
        return text

    ratio = max_tokens / token_count
    end = int(len(text) * ratio * 0.95)

    while count_tokens(text[:end]) > max_tokens:
        end = int(end * 0.9)

    logging.warning(f"Truncated text from {token_count} to ~{max_tokens} tokens")
    return text[:end]


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
