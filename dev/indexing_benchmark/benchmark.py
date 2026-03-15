import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.rag.embedder import embed_workflow
from src.rag.indexer import get_connection, load_chunks_json, store_chunks
from src.rag.sparse_embedder import sparse_embed_workflow

BATCH_SIZE = 32


# Embed dense + sparse in parallel, return results and individual timings
def timed_parallel_embed(texts: list[str]) -> dict:
    timings = {}

    def timed_dense():
        t0 = time.perf_counter()
        result = embed_workflow(texts)
        timings["dense"] = time.perf_counter() - t0
        return result

    def timed_sparse():
        t0 = time.perf_counter()
        result = sparse_embed_workflow(texts)
        timings["sparse"] = time.perf_counter() - t0
        return result

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as executor:
        emb_future = executor.submit(timed_dense)
        sparse_future = executor.submit(timed_sparse)
        embeddings = emb_future.result()
        sparse_embeddings = sparse_future.result()
    timings["wall"] = time.perf_counter() - t0

    return {"embeddings": embeddings, "sparse": sparse_embeddings, "timings": timings}


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

    print(f"{'Batch':>6}  {'Dense':>8}  {'Sparse':>8}  {'Wall':>8}  {'DB':>8}")
    print("-" * 50)

    batch_num = 0
    totals = {"dense": 0.0, "sparse": 0.0, "wall": 0.0, "db": 0.0}
    t_start = time.perf_counter()

    for i in range(0, total, args.batch_size):
        if args.max_batches and batch_num >= args.max_batches:
            break

        batch = chunks[i:i + args.batch_size]
        texts = [c["content"] for c in batch]

        result = timed_parallel_embed(texts)
        t = result["timings"]
        totals["dense"] += t["dense"]
        totals["sparse"] += t["sparse"]
        totals["wall"] += t["wall"]

        t_db = 0.0
        if conn:
            t0 = time.perf_counter()
            store_chunks(conn, batch, result["embeddings"], result["sparse"])
            t_db = time.perf_counter() - t0
            totals["db"] += t_db

        batch_num += 1
        print(
            f"{batch_num:>6}  "
            f"{t['dense']:>7.2f}s  "
            f"{t['sparse']:>7.2f}s  "
            f"{t['wall']:>7.2f}s  "
            f"{t_db:>7.2f}s"
        )

    t_total = time.perf_counter() - t_start
    n_processed = min(batch_num * args.batch_size, total)

    print("-" * 50)
    print(f"\nSummary ({batch_num} batches, {n_processed} chunks):")
    print(f"  Dense total:  {totals['dense']:>7.2f}s  (avg {totals['dense']/batch_num:.2f}s/batch)")
    print(f"  Sparse total: {totals['sparse']:>7.2f}s  (avg {totals['sparse']/batch_num:.2f}s/batch)")
    print(f"  Embed wall:   {totals['wall']:>7.2f}s  (avg {totals['wall']/batch_num:.2f}s/batch)")
    if conn:
        print(f"  DB total:     {totals['db']:>7.2f}s  (avg {totals['db']/batch_num:.2f}s/batch)")
    print(f"  Wall time:    {t_total:>7.2f}s")
    print(f"  Throughput:   {n_processed / t_total:.1f} chunks/s")

    if conn:
        conn.close()


if __name__ == "__main__":
    main()
