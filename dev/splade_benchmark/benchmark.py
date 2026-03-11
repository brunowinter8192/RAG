import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.rag.embedder import embed_workflow
from src.rag.sparse_embedder import sparse_embed_workflow

BATCH_SIZES = [8, 16, 32, 64]

SAMPLE_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "Natural language processing enables machines to understand human language. "
    "Retrieval-augmented generation combines search with language model generation. "
    "Sparse embeddings capture keyword-level lexical features for exact matching. "
    "Dense embeddings encode semantic meaning in high-dimensional vector spaces."
)


def generate_texts(n: int) -> list[str]:
    return [f"[{i}] {SAMPLE_TEXT}" for i in range(n)]


def run_sequential(texts: list[str]) -> tuple[list, list, float]:
    start = time.perf_counter()
    embeddings = embed_workflow(texts)
    sparse_embeddings = sparse_embed_workflow(texts)
    elapsed = time.perf_counter() - start
    return embeddings, sparse_embeddings, elapsed


def run_parallel(texts: list[str]) -> tuple[list, list, float]:
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as executor:
        emb_future = executor.submit(embed_workflow, texts)
        sparse_future = executor.submit(sparse_embed_workflow, texts)
        embeddings = emb_future.result()
        sparse_embeddings = sparse_future.result()
    elapsed = time.perf_counter() - start
    return embeddings, sparse_embeddings, elapsed


def verify_identical(emb_seq, sparse_seq, emb_par, sparse_par) -> bool:
    if len(emb_seq) != len(emb_par):
        return False
    if len(sparse_seq) != len(sparse_par):
        return False
    for a, b in zip(emb_seq, emb_par):
        if a != b:
            return False
    for a, b in zip(sparse_seq, sparse_par):
        if a != b:
            return False
    return True


def main():
    print("Sequential vs Parallel Embedding Benchmark")
    print("=" * 60)
    print(f"{'Batch':>6}  {'Sequential':>12}  {'Parallel':>12}  {'Speedup':>8}  {'Identical':>10}")
    print("-" * 60)

    for batch_size in BATCH_SIZES:
        texts = generate_texts(batch_size)

        emb_seq, sparse_seq, t_seq = run_sequential(texts)
        emb_par, sparse_par, t_par = run_parallel(texts)

        speedup = t_seq / t_par if t_par > 0 else 0
        identical = verify_identical(emb_seq, sparse_seq, emb_par, sparse_par)

        print(
            f"{batch_size:>6}  "
            f"{t_seq:>10.2f}s  "
            f"{t_par:>10.2f}s  "
            f"{speedup:>7.2f}x  "
            f"{'YES' if identical else 'NO':>10}"
        )

    print("=" * 60)


if __name__ == "__main__":
    main()
