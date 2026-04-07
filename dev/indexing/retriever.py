# INFRASTRUCTURE
import logging

import httpx

from embedder import embed, truncate_mrl
from sparse_embedder import embed_sparse
from db import get_connection, search_dense, search_sparse, search_hybrid

logger = logging.getLogger(__name__)

INSTRUCT_PREFIX = "Instruct: Given a search query, retrieve relevant passages that answer the query\nQuery: "
RERANKER_URL = "http://localhost:8082/v1/rerank"
CANDIDATES = 50


# FUNCTIONS

# Retrieve top results using dense embedding search
def retrieve_dense(query: str, collection: str, top_k: int = 10) -> list[dict]:
    conn = get_connection()
    emb = truncate_mrl(embed([query], prefix=INSTRUCT_PREFIX))[0]
    results = search_dense(conn, emb, collection, CANDIDATES)
    conn.close()
    return results[:top_k]


# Retrieve top results using sparse SPLADE search
def retrieve_sparse(query: str, collection: str, top_k: int = 10) -> list[dict]:
    conn = get_connection()
    sparse = embed_sparse([query])[0]
    results = search_sparse(conn, sparse, collection, CANDIDATES)
    conn.close()
    return results[:top_k]


# Retrieve top results using hybrid RRF fusion of dense + sparse
def retrieve_hybrid(query: str, collection: str, top_k: int = 10, rrf_k: int = 60) -> list[dict]:
    conn = get_connection()
    emb = truncate_mrl(embed([query], prefix=INSTRUCT_PREFIX))[0]
    sparse = embed_sparse([query])[0]
    dense_results = search_dense(conn, emb, collection, CANDIDATES)
    sparse_results = search_sparse(conn, sparse, collection, CANDIDATES)
    results = search_hybrid(conn, dense_results, sparse_results, rrf_k)
    conn.close()
    return results[:top_k]


# Rerank results using cross-encoder on port 8082
def rerank(query: str, results: list[dict], top_k: int = 10) -> list[dict]:
    contents = [r["content"] for r in results]
    response = httpx.post(
        RERANKER_URL,
        json={"query": query, "documents": contents, "top_n": len(contents)},
        timeout=60.0,
    )
    response.raise_for_status()
    data = response.json()
    ranked = sorted(data.get("results", data), key=lambda x: x["relevance_score"], reverse=True)
    reranked = []
    for item in ranked[:top_k]:
        doc = results[item["index"]].copy()
        doc["score"] = round(item["relevance_score"], 6)
        reranked.append(doc)
    return reranked
