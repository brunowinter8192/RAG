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
MAX_TOKENS = 4000
CHARS_PER_TOKEN = 3  # Conservative estimate (actual ~4 for English)


# ORCHESTRATOR
def embed_workflow(texts: Union[str, list[str]]) -> list[list[float]]:
    if isinstance(texts, str):
        texts = [texts]
    texts = [truncate_to_max_tokens(t, MAX_TOKENS) for t in texts]
    embeddings = generate_embeddings(texts)
    logging.info(f"Embedded {len(texts)} texts")
    return embeddings


# FUNCTIONS

# Truncate text to approximate max tokens (char-based, no API call)
def truncate_to_max_tokens(text: str, max_tokens: int) -> str:
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    logging.warning(f"Truncated text from {len(text)} to {max_chars} chars (~{max_tokens} tokens)")
    return text[:max_chars]


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
