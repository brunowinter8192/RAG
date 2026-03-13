import subprocess
import sys
import time
from pathlib import Path

import httpx

RAG_ROOT = Path(__file__).parent.parent.parent

LLAMA_SERVER = "llama-server"
MODEL_0_6B = RAG_ROOT / "models/qwen3-reranker-0.6b-q8_0.gguf"
MODEL_8B = RAG_ROOT / "models/Qwen3-Reranker-8B-Q8_0.gguf"

PORT_0_6B = 8082
PORT_8B = 8084

TEST_CASES = [
    {
        "query": "How to authenticate with API keys",
        "docs": [
            "API authentication requires passing your API key in the Authorization header. Use Bearer token format.",
            "The API supports multiple endpoints for data retrieval and manipulation.",
            "The weather in Berlin is cold in winter with temperatures below freezing.",
        ],
        "labels": ["relevant", "somewhat_relevant", "irrelevant"],
    },
    {
        "query": "Python error handling best practices",
        "docs": [
            "Use specific exception types instead of bare except. Always log the traceback for debugging.",
            "Python supports try-except-finally blocks for error management.",
            "JavaScript uses promises and async/await for asynchronous operations.",
        ],
        "labels": ["relevant", "somewhat_relevant", "irrelevant"],
    },
]


# Start llama-server on the given port and return the process
def start_server(model_path: Path, port: int) -> subprocess.Popen:
    cmd = [
        LLAMA_SERVER,
        "-m", str(model_path),
        "--rerank",
        "--host", "0.0.0.0",
        "--port", str(port),
        "-ngl", "99",
        "-c", "32768",
        "-ub", "4096",
        "-b", "4096",
    ]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Wait until health endpoint returns 200 or timeout
def wait_for_health(port: int, timeout: int = 120) -> bool:
    url = f"http://localhost:{port}/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(url, timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


# Call rerank API and return scores indexed by document position
def rerank(port: int, query: str, docs: list[str]) -> list[float]:
    response = httpx.post(
        f"http://localhost:{port}/v1/rerank",
        json={"query": query, "documents": docs, "top_n": len(docs)},
        timeout=60.0,
    )
    response.raise_for_status()
    data = response.json()
    results = data["results"]
    scores_by_index = {r["index"]: r["relevance_score"] for r in results}
    return [scores_by_index[i] for i in range(len(docs))]


# Validate that scores indicate a working model
def validate_scores(scores_06b: list[list[float]], scores_8b: list[list[float]]) -> bool:
    all_ok = True

    for model_name, all_scores in [("0.6B", scores_06b), ("8B", scores_8b)]:
        flat = [s for case_scores in all_scores for s in case_scores]

        if all(abs(s) < 1e-6 for s in flat):
            print(f"  FAIL [{model_name}] All scores are 0.0 — defective model")
            all_ok = False
            continue

        for i, (case, case_scores) in enumerate(zip(TEST_CASES, all_scores)):
            relevant_score = case_scores[0]
            irrelevant_score = case_scores[2]
            if relevant_score <= irrelevant_score:
                print(f"  FAIL [{model_name}] Case {i+1}: relevant ({relevant_score:.4f}) <= irrelevant ({irrelevant_score:.4f})")
                all_ok = False
            else:
                print(f"  OK   [{model_name}] Case {i+1}: relevant ({relevant_score:.4f}) > irrelevant ({irrelevant_score:.4f})")

        out_of_range = [s for s in flat if not (0.0 <= s <= 1.0)]
        if out_of_range:
            print(f"  WARN [{model_name}] {len(out_of_range)} scores outside [0, 1]: {out_of_range[:3]}")

    return all_ok


def main():
    print(f"RAG root: {RAG_ROOT}")

    print(f"Starting 0.6B server on port {PORT_0_6B}...")
    proc_06b = start_server(MODEL_0_6B, PORT_0_6B)

    print(f"Starting 8B server on port {PORT_8B}...")
    proc_8b = start_server(MODEL_8B, PORT_8B)

    try:
        print(f"Waiting for 0.6B server health check (port {PORT_0_6B})...")
        if not wait_for_health(PORT_0_6B):
            print("ERROR: 0.6B server did not become healthy within timeout")
            proc_06b.terminate()
            proc_8b.terminate()
            sys.exit(1)
        print("0.6B server ready.")

        print(f"Waiting for 8B server health check (port {PORT_8B})...")
        if not wait_for_health(PORT_8B):
            print("ERROR: 8B server did not become healthy within timeout")
            proc_06b.terminate()
            proc_8b.terminate()
            sys.exit(1)
        print("8B server ready.")

        run_comparison = True

        scores_06b = []
        scores_8b = []

        print("\nRunning rerank requests...")
        for i, case in enumerate(TEST_CASES):
            query = case["query"]
            docs = case["docs"]

            s8b = rerank(PORT_8B, query, docs)
            scores_8b.append(s8b)

            if run_comparison:
                s06b = rerank(PORT_0_6B, query, docs)
                scores_06b.append(s06b)
            else:
                scores_06b.append([None] * len(docs))

        col_q = 40
        col_d = 45
        col_s = 10

        print("\n" + "-" * (col_q + col_d + col_s * 2 + 6))
        print(f"{'Query':<{col_q}} {'Document':<{col_d}} {'0.6B':>{col_s}} {'8B':>{col_s}}")
        print("-" * (col_q + col_d + col_s * 2 + 6))

        for case, s06b_list, s8b_list in zip(TEST_CASES, scores_06b, scores_8b):
            query_short = case["query"][:col_q - 1]
            for j, (doc, label) in enumerate(zip(case["docs"], case["labels"])):
                doc_short = f"[{label}] {doc}"[:col_d - 1]
                s06b_str = f"{s06b_list[j]:.4f}" if s06b_list[j] is not None else "N/A"
                s8b_str = f"{s8b_list[j]:.4f}"
                q_col = query_short if j == 0 else ""
                print(f"{q_col:<{col_q}} {doc_short:<{col_d}} {s06b_str:>{col_s}} {s8b_str:>{col_s}}")
            print()

        print("Validation:")
        if run_comparison:
            ok = validate_scores(scores_06b, scores_8b)
        else:
            ok = validate_scores([scores_8b[i] for i in range(len(scores_8b))], scores_8b)

        if ok:
            print("\nRESULT: 8B model produces valid scores.")
        else:
            print("\nRESULT: 8B model validation FAILED. Keep using 0.6B.")
            sys.exit(1)

    finally:
        print("\nStopping servers...")
        proc_06b.terminate()
        proc_8b.terminate()
        proc_06b.wait(timeout=10)
        proc_8b.wait(timeout=10)
        print("Done.")


if __name__ == "__main__":
    main()
