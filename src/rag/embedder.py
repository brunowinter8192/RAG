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
RAG_ROOT = Path(__file__).parent.parent.parent

logging.basicConfig(
    filename=LOG_DIR / "embedder.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

EMBEDDING_URL = os.getenv("EMBEDDING_URL", "http://localhost:8081/v1/embeddings")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Qwen3-Embedding-8B")
HEALTH_URL = "http://localhost:8081/health"
MAX_TOKENS = 4000
CHARS_PER_TOKEN = 3

_server_checked = False


# ORCHESTRATOR
def embed_workflow(texts: Union[str, list[str]]) -> list[list[float]]:
    ensure_server_running()
    if isinstance(texts, str):
        texts = [texts]
    texts = [truncate_to_max_tokens(t, MAX_TOKENS) for t in texts]
    embeddings = generate_embeddings(texts)
    logging.info(f"Embedded {len(texts)} texts")
    return embeddings


# FUNCTIONS

# Ensure embedding server is running, start if needed
def ensure_server_running():
    global _server_checked
    if _server_checked:
        return

    if not check_server_health():
        logging.info("Embedding server not running, starting...")
        start_embedding_server()
        for _ in range(30):
            time.sleep(1)
            if check_server_health():
                logging.info("Embedding server started")
                break
        else:
            raise RuntimeError("Failed to start embedding server after 30s")

    _server_checked = True


# Check if embedding server is healthy
def check_server_health() -> bool:
    try:
        resp = httpx.get(HEALTH_URL, timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


# Start llama-server in background
def start_embedding_server():
    cmd = [
        str(RAG_ROOT / "llama.cpp/build/bin/llama-server"),
        "-m", str(RAG_ROOT / "models/Qwen3-Embedding-8B-Q8_0.gguf"),
        "--embedding",
        "--host", "0.0.0.0",
        "--port", "8081",
        "-ngl", "99",
        "-ub", "4096",
        "-b", "4096"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Truncate text to approximate max tokens
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
