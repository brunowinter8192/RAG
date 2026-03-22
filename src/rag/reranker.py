# INFRASTRUCTURE
import logging
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from .server_manager import ensure_ready

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "reranker.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

RERANKER_URL = os.getenv("RERANKER_URL", "http://localhost:8082/v1/rerank")


# ORCHESTRATOR
def rerank_workflow(query: str, documents: list[dict], top_k: int) -> list[dict]:
    ensure_ready("reranker")
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
