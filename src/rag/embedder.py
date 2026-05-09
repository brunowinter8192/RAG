# INFRASTRUCTURE
import logging
import os
from pathlib import Path
from typing import Union

import httpx
from dotenv import load_dotenv

from .server_manager import ensure_ready, get_port
from . import error_log, server_lock

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "embedder.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Qwen3-Embedding-8B")
MAX_TOKENS = 4000
CHARS_PER_TOKEN = 3


def _embedding_url() -> str:
    return f"http://localhost:{get_port('embedding')}/v1/embeddings"


# ORCHESTRATOR
def embed_workflow(texts: Union[str, list[str]], prefix: str | None = None) -> list[list[float]]:
    ensure_ready("embedding")
    if isinstance(texts, str):
        texts = [texts]
    texts = [truncate_to_max_tokens(t, MAX_TOKENS) for t in texts]
    embeddings = generate_embeddings(texts, prefix)
    logging.info(f"Embedded {len(texts)} texts")
    return embeddings


# FUNCTIONS

# Truncate text to approximate max tokens
def truncate_to_max_tokens(text: str, max_tokens: int) -> str:
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    logging.warning(f"Truncated text from {len(text)} to {max_chars} chars (~{max_tokens} tokens)")
    return text[:max_chars]


# Generate embeddings via llama-server API
def generate_embeddings(texts: list[str], prefix: str | None = None) -> list[list[float]]:
    if prefix:
        texts = [f"{prefix}{t}" for t in texts]
    try:
        with server_lock.acquire("embedding"):
            response = httpx.post(
                _embedding_url(),
                json={"input": texts, "model": EMBEDDING_MODEL},
                timeout=300.0
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
    except server_lock.ServerBusyError as e:
        error_log.write("embedding", "busy", str(e), caller_pid=os.getpid())
        raise
    except httpx.HTTPStatusError as e:
        error_log.write("embedding", f"http_{e.response.status_code}", str(e))
        raise
    except httpx.ConnectError as e:
        error_log.write("embedding", "connection_refused", str(e))
        raise
    except httpx.TimeoutException as e:
        error_log.write("embedding", "timeout", str(e))
        raise
    except httpx.RequestError as e:
        error_log.write("embedding", "request_error", str(e))
        raise
