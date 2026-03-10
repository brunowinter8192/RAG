#!/usr/bin/env python3

# INFRASTRUCTURE
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag.retriever import get_connection

RAG_ROOT = Path(__file__).parent.parent.parent
LLAMA_SERVER = RAG_ROOT / "llama.cpp/build/bin/llama-server"
MODEL_PATH = RAG_ROOT / "models/qwen3-reranker-0.6b-q8_0.gguf"
RERANKER_URL = "http://localhost:8082/v1/rerank"
HEALTH_URL = "http://localhost:8082/health"
OUTPUT_DIR = Path(__file__).parent / "03_batch_results"
PORT = "8082"
BATCH_SIZES = [512, 1024, 2048, 4096]
N_CHUNKS = 15
TEST_QUERY = "What is the main topic of this document?"


# ORCHESTRATOR
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    chunks = load_chunks_from_db(N_CHUNKS)
    print(f"Loaded {len(chunks)} chunks from DB\n")

    results = []
    print(f"{'batch_size':>10} | {'status':>6} | {'duration_ms':>12}")
    print("-" * 35)

    for batch_size in BATCH_SIZES:
        kill_server()
        proc = start_server(batch_size)
        if not wait_for_health(proc):
            results.append({"batch_size": batch_size, "status": -1, "duration_ms": 0, "error": "server failed to start"})
            print(f"{batch_size:>10} | {'FAIL':>6} | {'---':>12}")
            continue

        result = send_rerank_request(chunks)
        result["batch_size"] = batch_size
        results.append(result)
        print(f"{batch_size:>10} | {result['status']:>6} | {result['duration_ms']:>12.0f}")
        kill_server()

    save_results(results)


# FUNCTIONS

# Load real chunks from PostgreSQL
def load_chunks_from_db(n):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT content FROM documents ORDER BY collection, document, chunk_index LIMIT %s", (n,))
        rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


# Kill any existing process on port 8082
def kill_server():
    result = subprocess.run(["lsof", "-ti", f":{PORT}"], capture_output=True, text=True)
    pids = result.stdout.strip()
    if pids:
        for pid in pids.split("\n"):
            subprocess.run(["kill", "-9", pid], capture_output=True)
        time.sleep(1)


# Start llama-server with given batch size
def start_server(batch_size):
    cmd = [
        str(LLAMA_SERVER),
        "-m", str(MODEL_PATH),
        "--rerank",
        "--host", "0.0.0.0",
        "--port", PORT,
        "-ngl", "99",
        "-c", "32768",
        "-b", str(batch_size),
    ]
    print(f"\nStarting server with -b {batch_size}...", end="", flush=True)
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Wait for health endpoint
def wait_for_health(proc, timeout=30):
    for _ in range(timeout):
        if proc.poll() is not None:
            return False
        try:
            resp = httpx.get(HEALTH_URL, timeout=2.0)
            if resp.status_code == 200:
                print(" ready")
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


# Send rerank request with chunks
def send_rerank_request(chunks):
    start = time.monotonic()
    try:
        resp = httpx.post(
            RERANKER_URL,
            json={"query": TEST_QUERY, "documents": chunks, "top_n": len(chunks)},
            timeout=60.0
        )
        duration_ms = (time.monotonic() - start) * 1000
        return {"n_chunks": len(chunks), "status": resp.status_code, "duration_ms": duration_ms, "response_body": resp.text[:500]}
    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        return {"n_chunks": len(chunks), "status": -1, "duration_ms": duration_ms, "response_body": str(e)}


# Save results to JSON file
def save_results(results):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = OUTPUT_DIR / f"run_{ts}.json"
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {outfile.name}")


if __name__ == "__main__":
    main()
