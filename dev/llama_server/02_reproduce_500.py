#!/usr/bin/env python3

# INFRASTRUCTURE
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag.retriever import get_connection

RERANKER_URL = "http://localhost:8082/v1/rerank"
HEALTH_URL = "http://localhost:8082/health"
OUTPUT_DIR = Path(__file__).parent / "02_responses"
TEST_QUERY = "What is the main topic of this document?"

MODE_DB = "db"
MODE_SYNTHETIC = "synthetic"
MODE_VERIFY = "verify"
MODE_COMPARE = "compare"

DB_CHUNK_COUNTS = [5, 8, 10, 12, 13, 14, 15, 20]
SYNTHETIC_CHUNK_CHARS = 2000
SYNTHETIC_CHUNK_COUNTS = [5, 10, 15, 20, 25, 30, 40, 50]

VERIFY_QUERY = "What is the recipe to make bread?"
VERIFY_DOCS = [
    "voici la recette pour faire du pain, il faut de la farine de l eau et du levain et du sel",
    "it is a bear",
    "bread recipe : floor, water, yest, salt",
    "The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.",
    "here is the ingedients to bake bread : 500g floor, 350g water, 120g fresh refresh yest, 15g salt",
    "recipe to make cookies : floor, eggs, water, chocolat",
    "here is the recipe to make bread : 500g floor, 350g water, 120g fresh refresh yest, 15g salt",
    "il fait tres beau aujourd hui",
    "je n ai pas faim, je ne veux pas manger",
    "je suis a paris",
]
VERIFY_EXPECTED_TOP3 = {0, 2, 4, 6}

COMPARE_PORT_B = 8083
COMPARE_QUERY = "PostgreSQL authentication methods"


# ORCHESTRATOR
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    mode = parse_mode()

    if mode == MODE_VERIFY:
        run_verify()
    elif mode == MODE_COMPARE:
        run_compare()
    else:
        check_server_health(RERANKER_URL.rsplit("/", 2)[0])
        run_stress_test(mode)


# Run stress test (db or synthetic mode)
def run_stress_test(mode):
    if mode == MODE_DB:
        chunks = load_chunks_from_db()
        chunk_counts = DB_CHUNK_COUNTS
        print(f"Mode: DB chunks ({len(chunks)} loaded, ~{avg_len(chunks):.0f} chars/chunk)\n")
    else:
        chunks = generate_synthetic_chunks(max(SYNTHETIC_CHUNK_COUNTS), SYNTHETIC_CHUNK_CHARS)
        chunk_counts = SYNTHETIC_CHUNK_COUNTS
        print(f"Mode: Synthetic ({len(chunks)} chunks, {SYNTHETIC_CHUNK_CHARS} chars/chunk)\n")

    results = []
    print(f"{'n_chunks':>10} | {'status':>6} | {'duration_ms':>12} | {'content_len':>12}")
    print("-" * 55)

    for n in chunk_counts:
        if n > len(chunks):
            print(f"{n:>10} | {'SKIP':>6} | {'---':>12} | not enough chunks")
            continue
        result = send_rerank_request(RERANKER_URL, TEST_QUERY, chunks[:n])
        results.append(result)
        print(f"{result['n_chunks']:>10} | {result['status']:>6} | {result['duration_ms']:>12.0f} | {result['content_length']:>12}")
        if result['status'] == 500:
            print("           ^ Check 01_server_logs/ for stderr details")

    save_results(results, mode)


# Sanity check with known-answer test (Issue #16407 test data)
def run_verify():
    print("=== VERIFY: Sanity Check (Issue #16407 test data) ===\n")
    check_server_health(RERANKER_URL.rsplit("/", 2)[0])

    result = send_rerank_request(RERANKER_URL, VERIFY_QUERY, VERIFY_DOCS)
    if result['status'] != 200:
        print(f"FAIL: Server returned {result['status']}")
        sys.exit(1)

    ranked = json.loads(result['response_body'])
    if 'results' in ranked:
        ranked = ranked['results']
    ranked.sort(key=lambda x: x['relevance_score'], reverse=True)

    print(f"Query: {VERIFY_QUERY}\n")
    print(f"{'rank':>4} | {'index':>5} | {'score':>12} | document")
    print("-" * 70)
    for i, item in enumerate(ranked):
        idx = item['index']
        score = item['relevance_score']
        doc = VERIFY_DOCS[idx][:60]
        marker = " <-- bread" if idx in VERIFY_EXPECTED_TOP3 else ""
        print(f"{i+1:>4} | {idx:>5} | {score:>12.6f} | {doc}{marker}")

    top3_indices = {ranked[i]['index'] for i in range(3)}
    overlap = top3_indices & VERIFY_EXPECTED_TOP3
    print(f"\nTop-3 indices: {top3_indices}")
    print(f"Expected bread docs: {VERIFY_EXPECTED_TOP3}")
    print(f"Overlap: {len(overlap)}/3")

    min_score = min(item['relevance_score'] for item in ranked)
    max_score = max(item['relevance_score'] for item in ranked)
    print(f"Score range: {min_score:.6f} - {max_score:.6f}")

    if max_score < 0.001:
        print("\nFAIL: Scores near zero — GGUF conversion likely broken (Issue #16407)")
        sys.exit(1)
    elif len(overlap) < 2:
        print("\nFAIL: Ranking incorrect — bread docs not in top 3")
        sys.exit(1)
    else:
        print("\nPASS: Scores healthy, ranking correct")

    save_results(ranked, "verify")


# Compare rankings between two models on same data
def run_compare():
    print("=== COMPARE: 8B (port 8082) vs 0.6B (port 8083) ===\n")
    url_a = RERANKER_URL
    url_b = f"http://localhost:{COMPARE_PORT_B}/v1/rerank"

    check_server_health(url_a.rsplit("/", 2)[0])
    check_server_health(url_b.rsplit("/", 2)[0])

    chunks = load_chunks_from_db()
    print(f"Loaded {len(chunks)} chunks, using top 15\n")
    chunks = chunks[:15]

    result_a = send_rerank_request(url_a, COMPARE_QUERY, chunks)
    result_b = send_rerank_request(url_b, COMPARE_QUERY, chunks)

    if result_a['status'] != 200 or result_b['status'] != 200:
        print(f"FAIL: Model A status={result_a['status']}, Model B status={result_b['status']}")
        sys.exit(1)

    ranked_a = json.loads(result_a['response_body'])
    ranked_b = json.loads(result_b['response_body'])
    if 'results' in ranked_a:
        ranked_a = ranked_a['results']
    if 'results' in ranked_b:
        ranked_b = ranked_b['results']
    ranked_a.sort(key=lambda x: x['relevance_score'], reverse=True)
    ranked_b.sort(key=lambda x: x['relevance_score'], reverse=True)

    top5_a = [item['index'] for item in ranked_a[:5]]
    top5_b = [item['index'] for item in ranked_b[:5]]

    print(f"Query: {COMPARE_QUERY}\n")
    print(f"{'rank':>4} | {'8B idx':>6} {'8B score':>10} | {'0.6B idx':>8} {'0.6B score':>10}")
    print("-" * 55)
    for i in range(min(10, len(ranked_a), len(ranked_b))):
        a = ranked_a[i]
        b = ranked_b[i]
        print(f"{i+1:>4} | {a['index']:>6} {a['relevance_score']:>10.4f} | {b['index']:>8} {b['relevance_score']:>10.4f}")

    overlap = set(top5_a[:3]) & set(top5_b[:3])
    print(f"\nTop-3 8B:   {top5_a[:3]}")
    print(f"Top-3 0.6B: {top5_b[:3]}")
    print(f"Overlap: {len(overlap)}/3")

    if len(overlap) >= 2:
        print("\nPASS: Rankings consistent between models")
    else:
        print("\nWARN: Low overlap — review manually (may be OK if 8B is simply better)")

    save_results({"model_a": ranked_a[:10], "model_b": ranked_b[:10], "overlap": len(overlap)}, "compare")


# FUNCTIONS

# Parse CLI mode argument
def parse_mode():
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        if flag == "--synthetic":
            return MODE_SYNTHETIC
        elif flag == "--verify":
            return MODE_VERIFY
        elif flag == "--compare":
            return MODE_COMPARE
    return MODE_DB


# Average chunk length
def avg_len(chunks):
    return sum(len(c) for c in chunks) / len(chunks) if chunks else 0


# Verify reranker server is running
def check_server_health(base_url="http://localhost:8082"):
    health_url = f"{base_url}/health"
    try:
        resp = httpx.get(health_url, timeout=2.0)
        if resp.status_code != 200:
            print(f"Server not healthy at {health_url}. Run 01_capture_stderr.py first.")
            sys.exit(1)
    except Exception:
        print(f"Server not reachable at {health_url}. Run 01_capture_stderr.py first.")
        sys.exit(1)


# Load real chunks from PostgreSQL
def load_chunks_from_db():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT content FROM documents
            ORDER BY collection, document, chunk_index
            LIMIT 25
        """)
        rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


# Generate synthetic chunks of specified character length
def generate_synthetic_chunks(n, chars_per_chunk):
    base_text = (
        "def calc_αβ(x: np.ndarray) -> Dict[str, float]:\n"
        "    \"\"\"Berechne Korrelationskoeffizienten für μ±σ Werte.\"\"\"\n"
        "    résumé = {k: v for k, v in zip(x[::2], x[1::2])}\n"
        "    ∑_vals = np.sum([v**2 for v in résumé.values()])\n"
        "    return {'∑': ∑_vals, 'μ': np.mean(x), 'σ²': np.var(x)}\n\n"
        "# TODO: Handle edge cases — NaN, ±∞, empty arrays\n"
        "# See: https://arxiv.org/abs/2301.07834 §3.2\n"
        "class Übersetzer(BaseModel):\n"
        "    name: str = Field(..., description='Ünique identifier')\n"
        "    config: dict[str, Any] = {'λ': 0.01, 'η': 1e-4}\n"
    )
    chunk_text = (base_text * (chars_per_chunk // len(base_text) + 1))[:chars_per_chunk]
    return [f"Chunk {i}: {chunk_text}" for i in range(n)]


# Send rerank request with n chunks and measure response
def send_rerank_request(url, query, chunks):
    total_chars = sum(len(c) for c in chunks)
    start = time.monotonic()
    try:
        resp = httpx.post(
            url,
            json={
                "query": query,
                "documents": chunks,
                "top_n": len(chunks)
            },
            timeout=60.0
        )
        duration_ms = (time.monotonic() - start) * 1000
        return {
            "n_chunks": len(chunks),
            "status": resp.status_code,
            "duration_ms": duration_ms,
            "content_length": total_chars,
            "response_body": resp.text[:2000]
        }
    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        return {
            "n_chunks": len(chunks),
            "status": -1,
            "duration_ms": duration_ms,
            "content_length": total_chars,
            "response_body": str(e)
        }


# Save results to JSON file
def save_results(results, mode="db"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = OUTPUT_DIR / f"run_{mode}_{ts}.json"
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {outfile.name}")


if __name__ == "__main__":
    main()
