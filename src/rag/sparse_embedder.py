# INFRASTRUCTURE
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Union

import httpx
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
RAG_ROOT = Path(__file__).parent.parent.parent

logging.basicConfig(
    filename=LOG_DIR / "sparse_embedder.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SPLADE_URL = os.getenv("SPLADE_URL", "http://localhost:8083/v1/sparse-embeddings")
SPLADE_HEALTH_URL = "http://localhost:8083/health"

_server_checked = False


# ORCHESTRATOR
def sparse_embed_workflow(texts: Union[str, list[str]]) -> list[dict]:
    ensure_server_running()
    if isinstance(texts, str):
        texts = [texts]
    sparse_embeddings = generate_sparse_embeddings(texts)
    logging.info(f"Sparse embedded {len(texts)} texts")
    return sparse_embeddings


# FUNCTIONS

# Ensure SPLADE server is running, start if needed
def ensure_server_running():
    global _server_checked
    if _server_checked:
        return

    if not check_server_health():
        logging.info("SPLADE server not running, starting...")
        start_splade_server()
        for _ in range(30):
            time.sleep(1)
            if check_server_health():
                logging.info("SPLADE server started")
                break
        else:
            raise RuntimeError("Failed to start SPLADE server after 30s")

    _server_checked = True


# Check if SPLADE server is healthy
def check_server_health() -> bool:
    try:
        resp = httpx.get(SPLADE_HEALTH_URL, timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


# Start SPLADE server via uvicorn in background
def start_splade_server():
    cmd = [
        str(RAG_ROOT / "venv/bin/python"), "-m", "uvicorn",
        "src.rag.splade_server:app",
        "--host", "0.0.0.0", "--port", "8083"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Generate sparse embeddings via SPLADE server API
def generate_sparse_embeddings(texts: list[str]) -> list[dict]:
    response = httpx.post(
        SPLADE_URL,
        json={"input": texts, "model": "splade"},
        timeout=300.0
    )
    response.raise_for_status()
    data = response.json()
    return [item["sparse_vector"] for item in data["data"]]
