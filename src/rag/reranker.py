# INFRASTRUCTURE
import logging
import os
import subprocess
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
RAG_ROOT = Path(__file__).parent.parent.parent

logging.basicConfig(
    filename=LOG_DIR / "reranker.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

RERANKER_URL = os.getenv("RERANKER_URL", "http://localhost:8082/v1/rerank")
RERANKER_HEALTH_URL = "http://localhost:8082/health"
RERANKER_MODEL_PATH = RAG_ROOT / "models" / "Qwen3-Reranker-8B-Q8_0.gguf"

_server_checked = False


# ORCHESTRATOR
def rerank_workflow(query: str, documents: list[dict], top_k: int) -> list[dict]:
    ensure_reranker_running()
    contents = [doc['content'] for doc in documents]
    ranked = rerank_documents(query, contents)
    results = []
    for item in ranked[:top_k]:
        doc = documents[item['index']].copy()
        doc['score'] = round(item['relevance_score'], 6)
        results.append(doc)
    logging.info(f"Reranked {len(documents)} docs to top {top_k} for '{query[:50]}...'")
    return results


# FUNCTIONS

# Ensure reranker server is running, start if needed
def ensure_reranker_running():
    global _server_checked
    if _server_checked:
        return

    if not check_reranker_health():
        logging.info("Reranker server not running, starting...")
        start_reranker_server()
        for _ in range(30):
            time.sleep(1)
            if check_reranker_health():
                logging.info("Reranker server started")
                break
        else:
            raise RuntimeError("Failed to start reranker server after 30s")

    _server_checked = True


# Check if reranker server is healthy
def check_reranker_health() -> bool:
    try:
        resp = httpx.get(RERANKER_HEALTH_URL, timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


# Start reranker llama-server in background
def start_reranker_server():
    cmd = [
        "llama-server",
        "-m", str(RERANKER_MODEL_PATH),
        "--rerank",
        "--host", "0.0.0.0",
        "--port", "8082",
        "-ngl", "99",
        "-c", "32768",
        "-ub", "4096",
        "-b", "4096",
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Rerank documents against query via llama-server API
def rerank_documents(query: str, contents: list[str]) -> list[dict]:
    response = httpx.post(
        RERANKER_URL,
        json={
            "query": query,
            "documents": contents,
            "top_n": len(contents)
        },
        timeout=60.0
    )
    response.raise_for_status()
    data = response.json()
    results = data.get("results", data)
    return sorted(results, key=lambda x: x['relevance_score'], reverse=True)
