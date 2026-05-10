# INFRASTRUCTURE
import logging
import os
from pathlib import Path
from typing import Union

import httpx
from dotenv import load_dotenv

from .server_manager import ensure_ready, find_server_url

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "sparse_embedder.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ORCHESTRATOR
def sparse_embed_workflow(texts: Union[str, list[str]]) -> list[dict]:
    ensure_ready("splade")
    if isinstance(texts, str):
        texts = [texts]
    sparse_embeddings = generate_sparse_embeddings(texts)
    logging.info(f"Sparse embedded {len(texts)} texts")
    return sparse_embeddings


# FUNCTIONS

# Resolve SPLADE URL: env override → state-file discovery → error
def _sparse_embed_url() -> str:
    env = os.getenv("SPLADE_URL")
    if env:
        return env
    base = find_server_url("splade")
    if not base:
        raise RuntimeError(
            "SPLADE server not running. Start with `rag-cli server start splade`."
        )
    return f"{base}/v1/sparse-embeddings"


# Generate sparse embeddings via SPLADE server API
def generate_sparse_embeddings(texts: list[str]) -> list[dict]:
    response = httpx.post(
        _sparse_embed_url(),
        json={"input": texts, "model": "splade"},
        timeout=300.0
    )
    response.raise_for_status()
    data = response.json()
    return [item["sparse_vector"] for item in data["data"]]
