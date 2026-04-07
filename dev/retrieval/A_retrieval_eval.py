# INFRASTRUCTURE
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "indexing"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import httpx

import p1_retriever as _retriever

EMBEDDING_HEALTH_URL = "http://localhost:8081/health"


# ORCHESTRATOR

def run_eval(collection: str, queries_path: str, top_k: int, modes: list[str]) -> None:
    _check_embedding_server()

    queries = _load_queries(queries_path)
    print(f"Running eval: {len(queries)} queries x {len(modes)} modes on '{collection}' top_k={top_k}")

    for mode in modes:
        query_results = []
        for entry in queries:
            hits = _run_query(entry["query"], collection, top_k, mode)
            doc_match = _check_document_match(entry["expected_documents"], hits)
            snippet_match = _check_snippet_match(entry["expected_snippets"], hits)
            query_results.append({
                "entry": entry,
                "hits": hits,
                "doc_match": doc_match,
                "snippet_match": snippet_match,
            })

        _write_report(query_results, collection, top_k, mode)


# FUNCTIONS

# Check embedding server is healthy before running
def _check_embedding_server() -> None:
    try:
        resp = httpx.get(EMBEDDING_HEALTH_URL, timeout=3.0)
        if resp.status_code != 200:
            print(f"ERROR: embedding server unhealthy (HTTP {resp.status_code}). Start servers: ./start.sh")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: embedding server not reachable ({e}). Start servers: ./start.sh")
        sys.exit(1)


# Load query objects from JSON file
def _load_queries(queries_path: str) -> list[dict]:
    path = Path(queries_path)
    if not path.exists():
        print(f"ERROR: queries file not found: {queries_path}")
        sys.exit(1)
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "queries" in data:
        return data["queries"]
    if isinstance(data, list):
        return data
    print(f"ERROR: queries file must contain a JSON object with 'queries' key or a JSON array")
    sys.exit(1)


# Run a single query in one mode and return hits list
def _run_query(query: str, collection: str, top_k: int, mode: str) -> list[dict]:
    try:
        if mode == "dense":
            return _retriever.retrieve_dense(query, collection, top_k)
        return []
    except Exception as e:
        print(f"WARNING: query failed ({e}): {query[:60]}")
        return []


# Check which expected documents were found and at which ranks
def _check_document_match(expected_docs: list[str], hits: list[dict]) -> list[dict]:
    results = []
    for doc in expected_docs:
        ranks = [rank for rank, h in enumerate(hits, 1) if h.get("document") == doc]
        results.append({"doc": doc, "found": bool(ranks), "ranks": ranks})
    return results


# Check which expected snippets were found as substrings in any hit's content
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


# Format rank list as compact string like "Rank 1, 2, 5" or "-"
def _format_ranks(ranks: list[int]) -> str:
    if not ranks:
        return "-"
    return ", ".join(str(r) for r in ranks)


# Write MD evaluation report to A_retrieval_eval_reports/
def _write_report(query_results: list[dict], collection: str, top_k: int, mode: str) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(__file__).parent / "A_retrieval_eval_reports"
    report_path = report_dir / f"eval_{mode}_{timestamp}.md"
    report_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Retrieval Evaluation: {collection}",
        f"",
        f"**Mode:** {mode} | **Top-k:** {top_k} | **Timestamp:** {timestamp}",
        f"",
        f"---",
    ]

    for qi, qr in enumerate(query_results, start=1):
        entry = qr["entry"]
        doc_match = qr["doc_match"]
        snippet_match = qr["snippet_match"]

        doc_found = sum(1 for d in doc_match if d["found"])
        doc_total = len(doc_match)
        doc_pct = int(100 * doc_found / doc_total) if doc_total else 0

        snip_found = sum(1 for s in snippet_match if s["found"])
        snip_total = len(snippet_match)
        snip_pct = int(100 * snip_found / snip_total) if snip_total else 0

        lines += [f"", f"## Query {qi}: \"{entry['query']}\"", f""]

        lines.append(f"**Document Match:** {doc_found}/{doc_total} ({doc_pct}%)")
        for dm in doc_match:
            ranks_str = _format_ranks(dm["ranks"])
            status = f"Found (Rank {ranks_str})" if dm["found"] else "MISSING"
            lines.append(f"- {dm['doc']} — {status}")

        lines.append(f"")
        lines.append(f"**Snippet Match:** {snip_found}/{snip_total} ({snip_pct}%)")
        for sm in snippet_match:
            if sm["found"]:
                status = f"Found in Rank {sm['rank']}"
            else:
                status = "MISSING"
            lines.append(f"- \"{sm['snippet']}\" — {status}")

        lines.append(f"")
        lines.append(f"---")

    lines += _build_summary(query_results)

    report_path.write_text("\n".join(lines) + "\n")
    print(f"Report: {report_path}")


# Build summary section with aggregate metrics
def _build_summary(query_results: list[dict]) -> list[str]:
    total = len(query_results)

    doc_recalls = []
    snip_recalls = []
    full_doc_match = 0
    full_snip_match = 0
    zero_snip_match = 0

    type_stats: dict[str, dict] = {}

    for qr in query_results:
        entry = qr["entry"]
        doc_match = qr["doc_match"]
        snippet_match = qr["snippet_match"]

        doc_r = sum(1 for d in doc_match if d["found"]) / len(doc_match) if doc_match else 0
        snip_r = sum(1 for s in snippet_match if s["found"]) / len(snippet_match) if snippet_match else 0

        doc_recalls.append(doc_r)
        snip_recalls.append(snip_r)

        if doc_r == 1.0:
            full_doc_match += 1
        if snip_r == 1.0:
            full_snip_match += 1
        if snip_r == 0.0:
            zero_snip_match += 1

        qtype = entry.get("type", "unknown")
        if qtype not in type_stats:
            type_stats[qtype] = {"count": 0, "doc_recalls": [], "snip_recalls": []}
        type_stats[qtype]["count"] += 1
        type_stats[qtype]["doc_recalls"].append(doc_r)
        type_stats[qtype]["snip_recalls"].append(snip_r)

    avg_doc = sum(doc_recalls) / total if total else 0
    avg_snip = sum(snip_recalls) / total if total else 0

    lines = [
        f"",
        f"## Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Document Recall @{len(query_results[0]['hits']) if query_results else '?'} (avg) | {avg_doc:.0%} |",
        f"| Snippet Recall @{len(query_results[0]['hits']) if query_results else '?'} (avg) | {avg_snip:.0%} |",
        f"| Queries with 100% doc match | {full_doc_match}/{total} |",
        f"| Queries with 100% snippet match | {full_snip_match}/{total} |",
        f"| Queries with 0 snippet match | {zero_snip_match}/{total} |",
        f"",
        f"### By Query Type",
        f"| Type | Count | Avg Doc Recall | Avg Snippet Recall |",
        f"|------|-------|---------------|-------------------|",
    ]

    for qtype, stats in sorted(type_stats.items()):
        avg_d = sum(stats["doc_recalls"]) / stats["count"]
        avg_s = sum(stats["snip_recalls"]) / stats["count"]
        lines.append(f"| {qtype} | {stats['count']} | {avg_d:.0%} | {avg_s:.0%} |")

    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate retrieval against ground truth documents and snippets")
    parser.add_argument("--collection", default="RAG_MCP", help="Collection to query (default: RAG_MCP)")
    parser.add_argument("--queries", default="dev/retrieval/queries_rag_mcp.json", help="Queries JSON path")
    parser.add_argument("--top-k", type=int, default=10, help="Results per query (default: 10)")
    parser.add_argument("--modes", default="dense", help="Comma-separated modes (default: dense)")
    args = parser.parse_args()

    modes = [m.strip() for m in args.modes.split(",")]
    run_eval(args.collection, args.queries, args.top_k, modes)
