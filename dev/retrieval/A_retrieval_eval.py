# INFRASTRUCTURE
import argparse
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "indexing"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import httpx

import p1_retriever as _retriever
from eval_config import BASELINE, COLLECTION, SWEEP_RANGES

EMBEDDING_HEALTH_URL = os.getenv("EMBEDDING_HEALTH_URL", "http://localhost:8081/health")
SPLADE_HEALTH_URL = "http://localhost:8083/health"
RERANKER_HEALTH_URL = "http://localhost:8082/health"

# Modes where score_threshold is not meaningful (score scale not comparable to cosine)
THRESHOLD_IGNORED_MODES = {"hybrid", "hybrid+rerank", "bm25"}
# Modes where query_prefix has no effect (no dense embedding step)
PREFIX_NOOP_MODES = {"sparse", "bm25"}


# ORCHESTRATOR

def run_baseline(collection: str, queries_path: str, config: dict) -> None:
    _check_servers([config["mode"]])
    queries = _load_queries(queries_path)
    chunk_counts = _fetch_collection_chunk_counts(collection)
    print(f"Running baseline: {len(queries)} queries | mode={config['mode']} | top_k={config['top_k']}")

    query_results = []
    for entry in queries:
        hits = _run_query(entry["query"], collection, config)
        query_results.append({
            "entry": entry,
            "hits": hits,
            "doc_match": _check_document_match(entry["expected_documents"], hits),
            "snippet_match": _check_snippet_match(entry["expected_snippets"], hits),
            "rank_metrics": _compute_rank_metrics(hits, entry["expected_documents"], chunk_counts, config["top_k"]),
        })

    _write_report(query_results, collection, config, label="baseline")


def run_sweep(collection: str, queries_path: str, param: str, base_config: dict) -> None:
    if param not in SWEEP_RANGES:
        print(f"ERROR: '{param}' is not a sweepable parameter. Valid: {sorted(SWEEP_RANGES)}")
        sys.exit(1)

    values = SWEEP_RANGES[param]
    modes_in_sweep = [base_config["mode"]] if param != "mode" else values
    _check_servers(modes_in_sweep)

    queries = _load_queries(queries_path)
    chunk_counts = _fetch_collection_chunk_counts(collection)
    print(f"Running sweep: {param} over {values} | {len(queries)} queries | collection={collection}")

    comparison_rows = []
    for val in values:
        config = {**base_config, param: val}
        query_results = []
        for entry in queries:
            hits = _run_query(entry["query"], collection, config)
            query_results.append({
                "entry": entry,
                "hits": hits,
                "doc_match": _check_document_match(entry["expected_documents"], hits),
                "snippet_match": _check_snippet_match(entry["expected_snippets"], hits),
                "rank_metrics": _compute_rank_metrics(hits, entry["expected_documents"], chunk_counts, config["top_k"]),
            })

        label = f"sweep_{param}_{val}"
        _write_report(query_results, collection, config, label=label, sweep_param=param)
        avg_doc, avg_snip, avg_ndcg, avg_mrr, avg_recall_k = _compute_avg_metrics(query_results)
        comparison_rows.append((param, val, config["mode"], avg_doc, avg_snip, avg_ndcg, avg_mrr, avg_recall_k))

    _write_sweep_comparison(comparison_rows, param, base_config)


# FUNCTIONS

# Check required servers are healthy based on modes
def _check_servers(modes: list[str]) -> None:
    checks = []
    if any(m not in PREFIX_NOOP_MODES for m in modes):  # dense embedding needed for all except sparse/bm25
        checks.append(("embedding (8081)", EMBEDDING_HEALTH_URL))
    if any(m in modes for m in ["sparse", "hybrid", "cc", "cc+rerank", "hybrid+rerank"]):
        checks.append(("SPLADE (8083)", SPLADE_HEALTH_URL))
    if any("rerank" in m for m in modes):
        checks.append(("reranker (8082)", RERANKER_HEALTH_URL))
    for name, url in checks:
        try:
            resp = httpx.get(url, timeout=3.0)
            if resp.status_code != 200:
                print(f"ERROR: {name} server unhealthy (HTTP {resp.status_code}). Start servers: ./start.sh")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: {name} server not reachable ({e}). Start servers: ./start.sh")
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
    print("ERROR: queries file must contain a JSON object with 'queries' key or a JSON array")
    sys.exit(1)


# Run a single query with full config and return hits list
def _run_query(query: str, collection: str, config: dict) -> list[dict]:
    mode = config["mode"]
    top_k = config["top_k"]
    alpha = config["alpha"]
    rrf_k = config["rrf_k"]
    score_threshold = config["score_threshold"]
    query_prefix = config["query_prefix"]

    try:
        if mode == "dense":
            hits = _retriever.retrieve_dense(query, collection, top_k, query_prefix=query_prefix)
        elif mode == "sparse":
            hits = _retriever.retrieve_sparse(query, collection, top_k)
        elif mode == "bm25":
            hits = _retriever.retrieve_bm25(query, collection, top_k)
        elif mode == "hybrid":
            hits = _retriever.retrieve_hybrid(query, collection, top_k, rrf_k=rrf_k, query_prefix=query_prefix)
        elif mode == "cc":
            hits = _retriever.retrieve_cc(query, collection, top_k, alpha=alpha, query_prefix=query_prefix)
        elif mode == "cc+rerank":
            hits = _retriever.retrieve_cc_rerank(query, collection, top_k, alpha=alpha, query_prefix=query_prefix)
        elif mode == "hybrid+rerank":
            hits = _retriever.retrieve_hybrid(query, collection, top_k * 5, rrf_k=rrf_k, query_prefix=query_prefix)
            hits = _retriever.rerank(query, hits, top_k)
        else:
            hits = []
    except Exception as e:
        print(f"WARNING: query failed ({e}): {query[:60]}")
        return []

    if score_threshold > 0.0 and mode not in THRESHOLD_IGNORED_MODES:
        hits = [h for h in hits if h.get("score", 0) >= score_threshold]

    return hits


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


# Fetch per-document chunk counts for collection (needed for IDCG denominator and Recall@K)
def _fetch_collection_chunk_counts(collection: str) -> dict[str, int]:
    from p4_db import get_connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT document, COUNT(*) FROM documents WHERE collection = %s GROUP BY document",
                (collection,)
            )
            return {row[0]: row[1] for row in cur.fetchall()}
    finally:
        conn.close()


# Compute NDCG@K with binary relevance (rel=1 if hit.document in expected_docs_set)
# DCG@k = Σ (2^rel_i - 1) / log2(i+1), IDCG = DCG of perfect ranking using total_relevant
# Capped at 1.0: if the same document spans multiple ranks, DCG can technically exceed IDCG
def _compute_ndcg_at_k(hits: list[dict], expected_docs_set: set, total_relevant: int, k: int) -> float:
    rels = [1 if h.get("document") in expected_docs_set else 0 for h in hits[:k]]
    dcg = sum(r / math.log2(i + 2) for i, r in enumerate(rels))
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(total_relevant, k)))
    return min(1.0, dcg / idcg) if idcg > 0 else 0.0


# Compute MRR@K: 1/rank of first relevant hit in top K, 0 if none
def _compute_mrr_at_k(hits: list[dict], expected_docs_set: set, k: int) -> float:
    for rank, h in enumerate(hits[:k], 1):
        if h.get("document") in expected_docs_set:
            return 1.0 / rank
    return 0.0


# Compute Recall@K: chunks retrieved from expected docs in top K / total relevant chunks in collection
def _compute_recall_at_k(hits: list[dict], expected_docs_set: set, total_relevant: int, k: int) -> float:
    if total_relevant == 0:
        return 0.0
    retrieved_relevant = sum(1 for h in hits[:k] if h.get("document") in expected_docs_set)
    return retrieved_relevant / total_relevant


# Bundle NDCG@K, MRR@K, Recall@K for a single query
def _compute_rank_metrics(hits: list[dict], expected_docs: list[str], chunk_counts: dict[str, int], k: int) -> dict:
    expected_set = set(expected_docs)
    total_relevant = sum(chunk_counts.get(d, 0) for d in expected_docs)
    return {
        "ndcg_at_k": _compute_ndcg_at_k(hits, expected_set, total_relevant, k),
        "mrr_at_k": _compute_mrr_at_k(hits, expected_set, k),
        "recall_at_k": _compute_recall_at_k(hits, expected_set, total_relevant, k),
        "k": k,
    }


# Format rank list as compact string like "Rank 1, 2, 5" or "-"
def _format_ranks(ranks: list[int]) -> str:
    if not ranks:
        return "-"
    return ", ".join(str(r) for r in ranks)


# Build config table lines for report header
def _config_header_lines(config: dict, sweep_param: str | None = None) -> list[str]:
    lines = ["", "**Config:**", "", "| Param | Value | Note |", "|-------|-------|------|"]
    mode = config["mode"]
    for key, val in config.items():
        note = ""
        if key == "score_threshold" and mode in THRESHOLD_IGNORED_MODES:
            note = "⚠ ignored — score scale not comparable for rrf/bm25/rerank"
        elif key == "query_prefix" and mode in PREFIX_NOOP_MODES:
            note = "no-op — no dense embedding step for sparse/bm25"
        marker = " ← swept" if key == sweep_param else ""
        lines.append(f"| {key} | {val}{marker} | {note} |")
    return lines


# Write MD evaluation report to A_retrieval_eval_reports/
def _write_report(query_results: list[dict], collection: str, config: dict, label: str, sweep_param: str | None = None) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(__file__).parent / "A_retrieval_eval_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"eval_{label}_{timestamp}.md"

    mode = config["mode"]
    threshold_ignored = mode in THRESHOLD_IGNORED_MODES and config["score_threshold"] > 0.0
    prefix_noop = mode in PREFIX_NOOP_MODES

    lines = [
        f"# Retrieval Evaluation: {collection}",
        f"",
        f"**Label:** {label} | **Timestamp:** {timestamp}",
    ]

    if threshold_ignored:
        lines += [
            "",
            f"> ⚠ **Note:** score_threshold={config['score_threshold']} ignored for mode=`{mode}` — score scales not comparable for rrf/bm25/rerank.",
        ]
    if prefix_noop:
        lines += [
            "",
            f"> ℹ **Note:** query_prefix={config['query_prefix']} is a no-op for mode=`{mode}` — no dense embedding step.",
        ]

    lines += _config_header_lines(config, sweep_param)
    lines += ["", "---"]

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
            status = f"Found in Rank {sm['rank']}" if sm["found"] else "MISSING"
            lines.append(f"- \"{sm['snippet']}\" — {status}")

        rm = qr.get("rank_metrics")
        if rm:
            k = rm["k"]
            lines += [
                f"",
                f"**Rank Metrics @{k}:**",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| NDCG@{k} | {rm['ndcg_at_k']:.3f} |",
                f"| MRR@{k} | {rm['mrr_at_k']:.3f} |",
                f"| Recall@{k} (chunk-level) | {rm['recall_at_k']:.1%} |",
            ]

        lines += [f"", f"---"]

    lines += _build_summary(query_results)

    report_path.write_text("\n".join(lines) + "\n")
    print(f"Report: {report_path}")


# Compute average doc recall, snippet recall, and rank metrics across all query results
def _compute_avg_metrics(query_results: list[dict]) -> tuple[float, float, float, float, float]:
    doc_recalls = []
    snip_recalls = []
    ndcg_vals = []
    mrr_vals = []
    recall_k_vals = []
    for qr in query_results:
        doc_match = qr["doc_match"]
        snippet_match = qr["snippet_match"]
        rm = qr.get("rank_metrics", {})
        doc_recalls.append(sum(1 for d in doc_match if d["found"]) / len(doc_match) if doc_match else 0)
        snip_recalls.append(sum(1 for s in snippet_match if s["found"]) / len(snippet_match) if snippet_match else 0)
        ndcg_vals.append(rm.get("ndcg_at_k", 0.0))
        mrr_vals.append(rm.get("mrr_at_k", 0.0))
        recall_k_vals.append(rm.get("recall_at_k", 0.0))
    total = len(query_results)
    return (
        sum(doc_recalls) / total if total else 0,
        sum(snip_recalls) / total if total else 0,
        sum(ndcg_vals) / total if total else 0,
        sum(mrr_vals) / total if total else 0,
        sum(recall_k_vals) / total if total else 0,
    )


# Write sweep comparison MD report with all swept values + baseline fixed params
def _write_sweep_comparison(rows: list[tuple], param: str, base_config: dict) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = Path(__file__).parent / "A_retrieval_eval_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"sweep_{param}_{timestamp}.md"

    fixed = {k: v for k, v in base_config.items() if k != param}
    fixed_str = ", ".join(f"{k}={v}" for k, v in fixed.items())

    lines = [
        f"# Retrieval Sweep: {param}",
        f"",
        f"**Swept:** `{param}` over `{SWEEP_RANGES[param]}`",
        f"**Fixed (BASELINE):** {fixed_str}",
        f"**Timestamp:** {timestamp}",
    ]

    if param == "score_threshold":
        affected = [v for v in SWEEP_RANGES[param] if v > 0.0]
        if affected and base_config["mode"] in THRESHOLD_IGNORED_MODES:
            lines += [
                "",
                f"> ⚠ **Note:** score_threshold ignored for mode=`{base_config['mode']}` — score scales not comparable for rrf/bm25/rerank. All threshold values will produce identical results.",
            ]
    if param == "query_prefix" and base_config["mode"] in PREFIX_NOOP_MODES:
        lines += [
            "",
            f"> ℹ **Note:** query_prefix is a no-op for mode=`{base_config['mode']}` — no dense embedding step for sparse/bm25. True/False results will be identical.",
        ]

    lines += [
        "",
        f"| {param} | Mode | Doc Recall | Snippet Recall | NDCG@K | MRR@K | Recall@K |",
        f"|{'-'*len(param)}-|------|-----------|----------------|--------|-------|---------|",
    ]
    for swept_param, val, mode, avg_doc, avg_snip, avg_ndcg, avg_mrr, avg_recall_k in rows:
        lines.append(f"| {val} | {mode} | {avg_doc:.0%} | {avg_snip:.0%} | {avg_ndcg:.3f} | {avg_mrr:.3f} | {avg_recall_k:.1%} |")

    report_path.write_text("\n".join(lines) + "\n")
    print(f"Sweep comparison: {report_path}")


# Build summary section with aggregate metrics
def _build_summary(query_results: list[dict]) -> list[str]:
    total = len(query_results)
    doc_recalls = []
    snip_recalls = []
    ndcg_vals = []
    mrr_vals = []
    recall_k_vals = []
    full_doc_match = 0
    full_snip_match = 0
    zero_snip_match = 0
    type_stats: dict[str, dict] = {}

    for qr in query_results:
        entry = qr["entry"]
        doc_match = qr["doc_match"]
        snippet_match = qr["snippet_match"]
        rm = qr.get("rank_metrics", {})

        doc_r = sum(1 for d in doc_match if d["found"]) / len(doc_match) if doc_match else 0
        snip_r = sum(1 for s in snippet_match if s["found"]) / len(snippet_match) if snippet_match else 0

        doc_recalls.append(doc_r)
        snip_recalls.append(snip_r)
        ndcg_vals.append(rm.get("ndcg_at_k", 0.0))
        mrr_vals.append(rm.get("mrr_at_k", 0.0))
        recall_k_vals.append(rm.get("recall_at_k", 0.0))

        if doc_r == 1.0:
            full_doc_match += 1
        if snip_r == 1.0:
            full_snip_match += 1
        if snip_r == 0.0:
            zero_snip_match += 1

        qtype = entry.get("type", "unknown")
        if qtype not in type_stats:
            type_stats[qtype] = {"count": 0, "doc_recalls": [], "snip_recalls": [], "ndcg_vals": [], "mrr_vals": [], "recall_k_vals": []}
        type_stats[qtype]["count"] += 1
        type_stats[qtype]["doc_recalls"].append(doc_r)
        type_stats[qtype]["snip_recalls"].append(snip_r)
        type_stats[qtype]["ndcg_vals"].append(rm.get("ndcg_at_k", 0.0))
        type_stats[qtype]["mrr_vals"].append(rm.get("mrr_at_k", 0.0))
        type_stats[qtype]["recall_k_vals"].append(rm.get("recall_at_k", 0.0))

    avg_doc = sum(doc_recalls) / total if total else 0
    avg_snip = sum(snip_recalls) / total if total else 0
    avg_ndcg = sum(ndcg_vals) / total if total else 0
    avg_mrr = sum(mrr_vals) / total if total else 0
    avg_recall_k = sum(recall_k_vals) / total if total else 0
    top_k_label = len(query_results[0]['hits']) if query_results else '?'
    k_label = query_results[0]['rank_metrics']['k'] if query_results and query_results[0].get('rank_metrics') else top_k_label

    lines = [
        f"",
        f"## Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Document Recall @{top_k_label} (avg) | {avg_doc:.0%} |",
        f"| Snippet Recall @{top_k_label} (avg) | {avg_snip:.0%} |",
        f"| NDCG@{k_label} (avg) | {avg_ndcg:.3f} |",
        f"| MRR@{k_label} (avg) | {avg_mrr:.3f} |",
        f"| Recall@{k_label} chunk-level (avg) | {avg_recall_k:.1%} |",
        f"| Queries with 100% doc match | {full_doc_match}/{total} |",
        f"| Queries with 100% snippet match | {full_snip_match}/{total} |",
        f"| Queries with 0 snippet match | {zero_snip_match}/{total} |",
        f"",
        f"### By Query Type",
        f"| Type | Count | Avg Doc Recall | Avg Snippet Recall | Avg NDCG@{k_label} | Avg MRR@{k_label} | Avg Recall@{k_label} |",
        f"|------|-------|---------------|-------------------|------|------|------|",
    ]

    for qtype, stats in sorted(type_stats.items()):
        avg_d = sum(stats["doc_recalls"]) / stats["count"]
        avg_s = sum(stats["snip_recalls"]) / stats["count"]
        avg_n = sum(stats["ndcg_vals"]) / stats["count"]
        avg_m = sum(stats["mrr_vals"]) / stats["count"]
        avg_rk = sum(stats["recall_k_vals"]) / stats["count"]
        lines.append(f"| {qtype} | {stats['count']} | {avg_d:.0%} | {avg_s:.0%} | {avg_n:.3f} | {avg_m:.3f} | {avg_rk:.1%} |")

    return lines


# Parse key=val override strings into a dict
def _parse_overrides(override_list: list[str], base_config: dict) -> dict:
    config = dict(base_config)
    for item in override_list or []:
        if "=" not in item:
            print(f"ERROR: --override must be key=val (got: '{item}')")
            sys.exit(1)
        key, raw_val = item.split("=", 1)
        if key not in config:
            print(f"ERROR: --override key '{key}' not in BASELINE. Valid keys: {sorted(config)}")
            sys.exit(1)
        original = base_config[key]
        if isinstance(original, bool):
            config[key] = raw_val.lower() in ("true", "1", "yes")
        elif isinstance(original, int):
            config[key] = int(raw_val)
        elif isinstance(original, float):
            config[key] = float(raw_val)
        else:
            config[key] = raw_val
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate retrieval against ground truth documents and snippets")
    parser.add_argument("--collection", default=COLLECTION, help=f"Collection to query (default: {COLLECTION})")
    parser.add_argument("--queries", default="dev/retrieval/queries_test_db.json", help="Queries JSON path")
    parser.add_argument("--baseline", action="store_true", help="Run single pass at BASELINE config values")
    parser.add_argument("--sweep", metavar="PARAM", help="Sweep PARAM over SWEEP_RANGES[PARAM]; others fixed at BASELINE")
    parser.add_argument("--override", metavar="key=val", action="append", help="Override a BASELINE key (repeatable)")
    args = parser.parse_args()

    if not args.baseline and not args.sweep:
        parser.error("Specify --baseline or --sweep PARAM")

    config = _parse_overrides(args.override, BASELINE)

    if args.sweep:
        run_sweep(args.collection, args.queries, args.sweep, config)
    else:
        run_baseline(args.collection, args.queries, config)
