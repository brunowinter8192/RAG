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
    filename=LOG_DIR / "sparse_embedder.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def _splade_url() -> str:
    return f"http://localhost:{get_port('splade')}/v1/sparse-embeddings"


# ORCHESTRATOR
def sparse_embed_workflow(texts: Union[str, list[str]]) -> list[dict]:
    ensure_ready("splade")
    if isinstance(texts, str):
        texts = [texts]
    sparse_embeddings = generate_sparse_embeddings(texts)
    logging.info(f"Sparse embedded {len(texts)} texts")
    return sparse_embeddings


# FUNCTIONS

# Generate sparse embeddings via SPLADE server API
def generate_sparse_embeddings(texts: list[str]) -> list[dict]:
    try:
        with server_lock.acquire("splade"):
            response = httpx.post(
                _splade_url(),
                json={"input": texts, "model": "splade"},
                timeout=300.0
            )
            response.raise_for_status()
            data = response.json()
            return [item["sparse_vector"] for item in data["data"]]
    except server_lock.ServerBusyError as e:
        error_log.write("splade", "busy", str(e), caller_pid=os.getpid())
        raise
    except httpx.HTTPStatusError as e:
        error_log.write("splade", f"http_{e.response.status_code}", str(e))
        raise
    except httpx.ConnectError as e:
        error_log.write("splade", "connection_refused", str(e))
        raise
    except httpx.TimeoutException as e:
        error_log.write("splade", "timeout", str(e))
        raise
    except httpx.RequestError as e:
        error_log.write("splade", "request_error", str(e))
        raise
