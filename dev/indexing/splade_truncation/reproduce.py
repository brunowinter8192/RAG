"""SPLADE sparse vector density analysis and pgvector insert test.

Problem: SPLADE server (sentence_transformers SparseEncoder) was observed producing vectors
with 14k-30k non-zero elements instead of the expected 100-200. pgvector sparsevec type has
a hard limit of 16,000 non-zero elements — exceeding it crashes indexing with
psycopg2.errors.ProgramLimitExceeded.

Investigation findings:
- Prod DB data (33k chunks): 100-370 nnz — all correct
- Freshly restarted SPLADE server: 100-200 nnz — correct
- Long-running SPLADE server (8h+): 14k-30k nnz — corrupted
- 20 stress-test batches after restart: stable at 100-200 nnz
- Correlation: old server = corrupt, fresh server = OK
- Causation: UNKNOWN — laufzeit, memory pressure, concurrent requests not isolated

Status quo: server_manager.py provides auto-restart via idle timeout (5min), which may
prevent the corruption by not allowing long-running server state. Whether this actually
fixes the root cause is unverified. A monitoring script that periodically checks nnz counts
on the running server would be needed to confirm.

See also: RAG-bj2 (format_sparsevec safety-net truncation — defensive fix, not yet implemented)

Usage:
    POSTGRES_DB=rag_test ./venv/bin/python dev/indexing/splade_truncation/reproduce.py \\
        --input data/documents/searxng/Meta_Search_Engine_Optimization.json

    # All 5 IR-Papers at once
    POSTGRES_DB=rag_test ./venv/bin/python dev/indexing/splade_truncation/reproduce.py \\
        --input data/documents/searxng/Meta_Search_Engine_Optimization.json \\
                data/documents/searxng/QPP_GenRE_Query_Performance_Prediction.json \\
                data/documents/searxng/IR_Evaluation_Without_Relevance_Judgments.json \\
                data/documents/searxng/Interleaved_Search_Evaluation.json \\
                data/documents/searxng/Clickthrough_Search_Optimization.json

    # Analysis only (no DB insert)
    ./venv/bin/python dev/indexing/splade_truncation/reproduce.py --analyze-only \\
        --input data/documents/searxng/Meta_Search_Engine_Optimization.json
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.rag.sparse_embedder import sparse_embed_workflow
from src.rag.indexer import format_sparsevec, get_connection, ensure_schema

PGVECTOR_MAX_NNZ = 16000
BATCH_SIZE = 32


def load_chunks(json_paths: list[str]) -> list[dict]:
    """Load chunks from one or more pre-chunked JSON files."""
    all_chunks = []
    for json_path in json_paths:
        path = Path(json_path)
        with open(path) as f:
            data = json.load(f)
        doc_name = path.stem
        for c in data.get("chunks", []):
            all_chunks.append({
                "document": doc_name,
                "chunk_index": c["index"],
                "content": c["content"],
            })
    return all_chunks


def analyze_distribution(results: list[dict]) -> None:
    """Print distribution stats for non-zero element counts."""
    counts = [r["nnz"] for r in results]
    if not counts:
        print("No results to analyze.")
        return

    counts_sorted = sorted(counts)
    n = len(counts_sorted)

    print(f"\n{'='*60}")
    print(f"SPLADE Non-Zero Element Distribution ({n} chunks)")
    print(f"{'='*60}")
    print(f"  Min:    {min(counts):>6}")
    print(f"  Max:    {max(counts):>6}")
    print(f"  Mean:   {statistics.mean(counts):>9.1f}")
    print(f"  Median: {statistics.median(counts):>9.1f}")
    print(f"  Stdev:  {statistics.stdev(counts):>9.1f}" if n > 1 else "")
    print(f"  P95:    {counts_sorted[int(n * 0.95)]:>6}")
    print(f"  P99:    {counts_sorted[int(n * 0.99)]:>6}")

    exceeding = [r for r in results if r["nnz"] > PGVECTOR_MAX_NNZ]
    print(f"\n  Chunks > {PGVECTOR_MAX_NNZ}: {len(exceeding)}/{n}")
    if exceeding:
        print(f"\n  {'Document':<45} {'Chunk':>5} {'NNZ':>6}")
        print(f"  {'-'*45} {'-'*5} {'-'*6}")
        for r in sorted(exceeding, key=lambda x: -x["nnz"]):
            print(f"  {r['document']:<45} {r['chunk_index']:>5} {r['nnz']:>6}")

    # Histogram buckets
    buckets = [100, 200, 500, 1000, 2000, 5000, 10000, 16000, 30522]
    print(f"\n  Histogram:")
    prev = 0
    for b in buckets:
        count = sum(1 for c in counts if prev < c <= b)
        bar = "#" * min(count, 50)
        if count > 0:
            print(f"  {prev+1:>6}-{b:>5}: {count:>4}  {bar}")
        prev = b


def reproduce(json_paths: list[str], analyze_only: bool) -> None:
    chunks = load_chunks(json_paths)
    if not chunks:
        print("No chunks loaded.")
        return

    print(f"Loaded {len(chunks)} chunks from {len(json_paths)} file(s)")

    # Generate SPLADE embeddings in batches
    results = []
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]
        print(f"  Embedding batch {i // BATCH_SIZE + 1} ({len(batch)} chunks)...")
        sparse_vecs = sparse_embed_workflow(texts)

        for chunk, sparse in zip(batch, sparse_vecs):
            nnz = len(sparse["indices"])
            results.append({
                "document": chunk["document"],
                "chunk_index": chunk["chunk_index"],
                "nnz": nnz,
                "sparse": sparse,
            })

    analyze_distribution(results)

    if analyze_only:
        print("\n--analyze-only: skipping DB insert.")
        return

    # Attempt INSERT into rag_test
    print(f"\n{'='*60}")
    print("DB INSERT TEST (rag_test)")
    print(f"{'='*60}")

    conn = get_connection()
    ensure_schema(conn)

    succeeded = 0
    failed = 0
    errors = []

    for r in results:
        try:
            sparsevec_str = format_sparsevec(r["sparse"])
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO documents (content, collection, document, chunk_index, total_chunks, embedding, sparse_embedding)
                    VALUES (%s, %s, %s, %s, %s, NULL, %s)
                    """,
                    ("test", "splade_truncation_test", r["document"], r["chunk_index"], 1, sparsevec_str)
                )
            conn.commit()
            succeeded += 1
        except Exception as e:
            conn.rollback()
            failed += 1
            error_info = {
                "document": r["document"],
                "chunk_index": r["chunk_index"],
                "nnz": r["nnz"],
                "error": str(e).strip(),
            }
            errors.append(error_info)
            print(f"  FAILED: {r['document']} chunk {r['chunk_index']} (nnz={r['nnz']}): {type(e).__name__}")

    # Cleanup test data
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents WHERE collection = 'splade_truncation_test'")
    conn.commit()
    conn.close()

    print(f"\n  Results: {succeeded} succeeded, {failed} failed")
    if errors:
        print(f"\n  Failed chunks:")
        for e in errors:
            print(f"    {e['document']} chunk {e['chunk_index']} (nnz={e['nnz']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce SPLADE truncation bug")
    parser.add_argument("--input", nargs="+", required=True, help="Path(s) to chunks.json files")
    parser.add_argument("--analyze-only", action="store_true", help="Skip DB insert, only analyze element counts")
    args = parser.parse_args()

    reproduce(args.input, args.analyze_only)
