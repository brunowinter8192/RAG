# INFRASTRUCTURE
import json
import sys
from datetime import datetime
from pathlib import Path

import httpx
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "indexing"))

import p2_embedder

COLLECTION = "RAG_MCP"
DIMENSIONS = [256, 512, 768, 1024, 2048, 4096]
TOP_K = 10
QUERIES_PATH = Path(__file__).parent / "queries_rag_mcp.json"
REPORTS_DIR = Path(__file__).parent / "A_mrl_sweep_reports"
INSTRUCT_PREFIX = "Instruct: Given a search query, retrieve relevant passages that answer the query\nQuery: "
EMBEDDING_HEALTH_URL = "http://localhost:8081/health"

DB_HOST = "localhost"
DB_PORT = 5433
DB_USER = "rag"
DB_PASSWORD = "rag"
DB_NAME = "rag_test"


# ORCHESTRATOR

def run_mrl_sweep() -> None:
    _check_embedding_server()
    queries = _load_queries()
    print(f"Loaded {len(queries)} queries")

    conn = _get_connection()
    print("Fetching document embeddings from DB...")
    doc_rows = _fetch_document_embeddings(conn, COLLECTION)
    print(f"Fetched {len(doc_rows)} document chunks")

    print("Embedding queries at full 4096d...")
    query_embeddings = _embed_queries(queries)

    dim_results = {}
    for dim in DIMENSIONS:
        print(f"Evaluating {dim}d...")
        dim_results[dim] = _evaluate_dimension(queries, query_embeddings, doc_rows, dim)

    conn.close()
    _write_report(queries, dim_results)


# FUNCTIONS

# Verify embedding server is reachable before starting
def _check_embedding_server() -> None:
    try:
        resp = httpx.get(EMBEDDING_HEALTH_URL, timeout=3.0)
        if resp.status_code != 200:
            print(f"ERROR: embedding server unhealthy (HTTP {resp.status_code}). Run: ./start.sh")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: embedding server not reachable ({e}). Run: ./start.sh")
        sys.exit(1)


# Load query list from queries_rag_mcp.json
def _load_queries() -> list[dict]:
    with open(QUERIES_PATH) as f:
        data = json.load(f)
    return data["queries"]


# Open psycopg2 connection to rag_test with pgvector registered
def _get_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )
    register_vector(conn)
    return conn


# Fetch all document rows with embeddings for a collection
def _fetch_document_embeddings(conn, collection: str) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT content, collection, document, chunk_index, embedding FROM documents WHERE collection = %s",
            (collection,),
        )
        rows = cur.fetchall()
    return [
        {
            "content": row[0],
            "collection": row[1],
            "document": row[2],
            "chunk_index": row[3],
            "embedding": np.array(row[4], dtype=np.float32),
        }
        for row in rows
    ]


# Embed all queries at full model dimension (4096d), return as numpy arrays
def _embed_queries(queries: list[dict]) -> list[np.ndarray]:
    texts = [q["query"] for q in queries]
    raw = p2_embedder.embed(texts, prefix=INSTRUCT_PREFIX)
    return [np.array(emb, dtype=np.float32) for emb in raw]


# Truncate a vector to dim and L2-normalize
def _truncate_normalize(vec: np.ndarray, dim: int) -> np.ndarray:
    v = vec[:dim].copy()
    norm = np.linalg.norm(v)
    if norm > 0:
        v = v / norm
    return v


# Evaluate all queries at a single MRL dimension, return per-query results
def _evaluate_dimension(
    queries: list[dict],
    query_embeddings: list[np.ndarray],
    doc_rows: list[dict],
    dim: int,
) -> list[dict]:
    doc_embs = np.stack([_truncate_normalize(row["embedding"], dim) for row in doc_rows])

    results = []
    for query, qemb_full in zip(queries, query_embeddings):
        qvec = _truncate_normalize(qemb_full, dim)
        scores = doc_embs @ qvec
        top_indices = np.argsort(scores)[::-1][:TOP_K]

        hits = []
        for idx in top_indices:
            row = doc_rows[idx]
            hits.append({
                "content": row["content"],
                "document": row["document"],
                "chunk_index": row["chunk_index"],
                "score": float(scores[idx]),
            })

        doc_match = _check_document_match(query["expected_documents"], hits)
        snippet_match = _check_snippet_match(query["expected_snippets"], hits)
        results.append({
            "entry": query,
            "hits": hits,
            "doc_match": doc_match,
            "snippet_match": snippet_match,
        })

    return results


# Check which expected documents appear in hits
def _check_document_match(expected_docs: list[str], hits: list[dict]) -> list[dict]:
    results = []
    for doc in expected_docs:
        ranks = [rank for rank, h in enumerate(hits, 1) if h.get("document") == doc]
        results.append({"doc": doc, "found": bool(ranks), "ranks": ranks})
    return results


# Check which expected snippets appear as substrings in any hit's content
def _check_snippet_match(expected_snippets: list[str], hits: list[dict]) -> list[dict]:
    results = []
    for snippet in expected_snippets:
        found_rank = None
        for rank, h in enumerate(hits, 1):
            if snippet.lower() in h.get("content", "").lower():
                found_rank = rank
                break
        results.append({"snippet": snippet, "found": found_rank is not None, "rank": found_rank})
    return results


# Compute aggregate metrics from per-query results
def _compute_metrics(query_results: list[dict]) -> dict:
    doc_recalls = []
    snip_recalls = []
    for qr in query_results:
        dm = qr["doc_match"]
        sm = qr["snippet_match"]
        doc_r = sum(1 for d in dm if d["found"]) / len(dm) if dm else 0.0
        snip_r = sum(1 for s in sm if s["found"]) / len(sm) if sm else 0.0
        doc_recalls.append(doc_r)
        snip_recalls.append(snip_r)
    total = len(query_results)
    avg_doc = sum(doc_recalls) / total if total else 0.0
    avg_snip = sum(snip_recalls) / total if total else 0.0
    full_doc = sum(1 for r in doc_recalls if r == 1.0)
    full_snip = sum(1 for r in snip_recalls if r == 1.0)
    return {
        "avg_doc": avg_doc,
        "avg_snip": avg_snip,
        "full_doc": full_doc,
        "full_snip": full_snip,
        "doc_recalls": doc_recalls,
        "snip_recalls": snip_recalls,
    }


# Build summary table rows (one row per dimension)
def _build_summary_table(dim_results: dict) -> list[str]:
    lines = [
        "## Summary",
        "",
        "| Dimension | Doc Recall @10 | Snippet Recall @10 | 100% Doc Match | 100% Snippet Match |",
        "|-----------|---------------|-------------------|----------------|-------------------|",
    ]
    total = len(next(iter(dim_results.values())))
    for dim in DIMENSIONS:
        m = _compute_metrics(dim_results[dim])
        lines.append(
            f"| {dim}d | {m['avg_doc']:.0%} | {m['avg_snip']:.0%}"
            f" | {m['full_doc']}/{total} | {m['full_snip']}/{total} |"
        )
    return lines


# Build by-query-type breakdown table (type x dimension)
def _build_type_table(queries: list[dict], dim_results: dict) -> list[str]:
    types = sorted(set(q["type"] for q in queries))
    lines = [
        "",
        "## By Query Type",
        "",
        "| Type | Dim | Doc Recall | Snippet Recall |",
        "|------|-----|-----------|---------------|",
    ]
    for qtype in types:
        indices = [i for i, q in enumerate(queries) if q["type"] == qtype]
        for dim in DIMENSIONS:
            qrs = [dim_results[dim][i] for i in indices]
            m = _compute_metrics(qrs)
            lines.append(
                f"| {qtype} | {dim}d | {m['avg_doc']:.0%} | {m['avg_snip']:.0%} |"
            )
    return lines


# Build per-query breakdown for queries where metrics differ across dimensions
def _build_per_query_breakdown(queries: list[dict], dim_results: dict) -> list[str]:
    lines = ["", "## Per-Query Breakdown (only queries where results differ across dimensions)", ""]
    any_entry = False

    for i, query in enumerate(queries):
        per_dim = {}
        for dim in DIMENSIONS:
            qr = dim_results[dim][i]
            dm = qr["doc_match"]
            sm = qr["snippet_match"]
            doc_found = sum(1 for d in dm if d["found"])
            snip_found = sum(1 for s in sm if s["found"])
            per_dim[dim] = {
                "doc_found": doc_found,
                "doc_total": len(dm),
                "snip_found": snip_found,
                "snip_total": len(sm),
                "doc_match": dm,
            }

        doc_scores = {dim: per_dim[dim]["doc_found"] for dim in DIMENSIONS}
        snip_scores = {dim: per_dim[dim]["snip_found"] for dim in DIMENSIONS}
        if len(set(doc_scores.values())) == 1 and len(set(snip_scores.values())) == 1:
            continue

        any_entry = True
        lines.append(f"### Query {i + 1}: \"{query['query']}\"")
        lines.append("")
        lines.append("| Dim | Doc Recall | Snippet Recall | Missing Docs |")
        lines.append("|-----|-----------|---------------|-------------|")

        for dim in DIMENSIONS:
            pd = per_dim[dim]
            missing = [d["doc"] for d in pd["doc_match"] if not d["found"]]
            missing_str = ", ".join(missing) if missing else "-"
            lines.append(
                f"| {dim}d | {pd['doc_found']}/{pd['doc_total']}"
                f" | {pd['snip_found']}/{pd['snip_total']}"
                f" | {missing_str} |"
            )
        lines.append("")

    if not any_entry:
        lines.append("*All queries produce identical results across all dimensions.*")
        lines.append("")

    return lines


# Write final MD report to A_mrl_sweep_reports/
def _write_report(queries: list[dict], dim_results: dict) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"mrl_sweep_{timestamp}.md"

    lines = [
        "# MRL Dimension Sweep: RAG_MCP",
        "",
        f"**Timestamp:** {timestamp}  ",
        f"**Dimensions tested:** {', '.join(str(d) for d in DIMENSIONS)}  ",
        f"**Queries:** {len(queries)} | **Top-k:** {TOP_K}",
        "",
        "---",
        "",
    ]

    lines += _build_summary_table(dim_results)
    lines += _build_type_table(queries, dim_results)
    lines += _build_per_query_breakdown(queries, dim_results)

    report_path.write_text("\n".join(lines) + "\n")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    run_mrl_sweep()
