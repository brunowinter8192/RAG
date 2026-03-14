import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.rag.embedder import embed_workflow
from src.rag.indexer import get_connection, load_chunks_json, parallel_embed, store_chunks
from src.rag.sparse_embedder import sparse_embed_workflow

BATCH_SIZE = 32


def benchmark_batch(texts: list[str]) -> dict:
    t0 = time.perf_counter()
    embeddings = embed_workflow(texts)
    t_dense = time.perf_counter() - t0

    t0 = time.perf_counter()
    sparse_embeddings = sparse_embed_workflow(texts)
    t_sparse = time.perf_counter() - t0

    t0 = time.perf_counter()
    emb_par, sparse_par = parallel_embed(texts)
    t_parallel = time.perf_counter() - t0

    return {
        "dense": t_dense,
        "sparse": t_sparse,
        "parallel": t_parallel,
        "n_texts": len(texts),
    }


def benchmark_db_insert(conn, chunks: list[dict], embeddings: list[list[float]], sparse_embeddings: list[dict]) -> float:
    t0 = time.perf_counter()
    store_chunks(conn, chunks, embeddings, sparse_embeddings)
    return time.perf_counter() - t0


def main():
    parser = argparse.ArgumentParser(description="Indexing pipeline benchmark")
    parser.add_argument("--input", required=True, help="Path to chunks.json")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--max-batches", type=int, default=0, help="Limit number of batches (0 = all)")
    parser.add_argument("--skip-db", action="store_true", help="Skip DB insert timing")
    args = parser.parse_args()

    chunks = load_chunks_json(args.input)
    total = len(chunks)
    print(f"Loaded {total} chunks from {args.input}")
    print(f"Batch size: {args.batch_size}")
    print()

    conn = None if args.skip_db else get_connection()

    # Header
    print(f"{'Batch':>6}  {'Dense':>8}  {'Sparse':>8}  {'Parallel':>8}  {'DB':>8}  {'Total':>8}")
    print("-" * 60)

    batch_num = 0
    total_dense = total_sparse = total_parallel = total_db = 0.0
    t_start = time.perf_counter()

    for i in range(0, total, args.batch_size):
        if args.max_batches and batch_num >= args.max_batches:
            break

        batch = chunks[i:i + args.batch_size]
        texts = [c["content"] for c in batch]

        result = benchmark_batch(texts)
        total_dense += result["dense"]
        total_sparse += result["sparse"]
        total_parallel += result["parallel"]

        t_db = 0.0
        if conn:
            embeddings, sparse_embeddings = parallel_embed(texts)
            t_db = benchmark_db_insert(conn, batch, embeddings, sparse_embeddings)
            total_db += t_db

        batch_total = result["parallel"] + t_db
        batch_num += 1

        print(
            f"{batch_num:>6}  "
            f"{result['dense']:>7.2f}s  "
            f"{result['sparse']:>7.2f}s  "
            f"{result['parallel']:>7.2f}s  "
            f"{t_db:>7.2f}s  "
            f"{batch_total:>7.2f}s"
        )

    t_total = time.perf_counter() - t_start

    print("-" * 60)
    print(f"\nSummary ({batch_num} batches, {min(batch_num * args.batch_size, total)} chunks):")
    print(f"  Dense total:    {total_dense:>7.2f}s  (avg {total_dense/batch_num:.2f}s/batch)")
    print(f"  Sparse total:   {total_sparse:>7.2f}s  (avg {total_sparse/batch_num:.2f}s/batch)")
    print(f"  Parallel total: {total_parallel:>7.2f}s  (avg {total_parallel/batch_num:.2f}s/batch)")
    if conn:
        print(f"  DB total:       {total_db:>7.2f}s  (avg {total_db/batch_num:.2f}s/batch)")
    print(f"  Wall time:      {t_total:>7.2f}s")
    print(f"  Throughput:     {min(batch_num * args.batch_size, total) / t_total:.1f} chunks/s")

    if conn:
        conn.close()


if __name__ == "__main__":
    main()
