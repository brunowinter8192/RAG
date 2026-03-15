import argparse
import json
import sys
from pathlib import Path

import pytrec_eval

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from eval_config import K_VALUES, METRICS, DATASETS_DIR, RESULTS_DIR


# Load dataset from JSON file, auto-build corpus from source chunks or DB
def load_dataset(name: str) -> dict:
    path = Path(DATASETS_DIR) / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    with open(path) as f:
        dataset = json.load(f)

    if "corpus" not in dataset and "source_json" in dataset:
        source_path = Path(dataset["source_json"])
        if not source_path.exists():
            raise FileNotFoundError(f"Source JSON not found: {source_path}")
        with open(source_path) as f:
            source = json.load(f)
        document = source.get("document", source_path.stem + ".md")
        dataset["corpus"] = {
            f"chunk_{c['index']}": {"text": c["content"], "document": document}
            for c in source.get("chunks", [])
        }

    if "corpus" not in dataset and dataset.get("corpus_from_db"):
        dataset["corpus"] = load_corpus_from_db(dataset["collection"])

    return dataset


# Load corpus from PostgreSQL for a given collection
def load_corpus_from_db(collection: str) -> dict:
    from src.rag.retriever import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT content, collection, document, chunk_index FROM documents WHERE collection = %s ORDER BY document, chunk_index",
        (collection,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {
        f"chunk_{chunk_index}_{document}": {"text": content, "document": document}
        for content, _collection, document, chunk_index in rows
    }



# Evaluate retriever results against ground truth using pytrec_eval
def evaluate(qrels: dict, results: dict) -> dict:
    evaluator = pytrec_eval.RelevanceEvaluator(qrels, METRICS)
    scores = evaluator.evaluate(results)

    aggregated = {}
    for k in K_VALUES:
        for metric_prefix, label in [("ndcg_cut_", "NDCG"), ("recall_", "Recall"), ("P_", "P")]:
            key = f"{label}@{k}"
            values = [scores[qid][f"{metric_prefix}{k}"] for qid in scores]
            aggregated[key] = round(sum(values) / len(values), 4) if values else 0.0

    return aggregated


# Print evaluation results as formatted table
def print_results(retriever_name: str, metrics: dict):
    print(f"\n{'='*50}")
    print(f"Retriever: {retriever_name}")
    print(f"{'='*50}")
    print(f"{'Metric':<12} {'@3':>8} {'@5':>8} {'@10':>8}")
    print(f"{'-'*36}")

    for label in ["NDCG", "Recall", "P"]:
        vals = [f"{metrics.get(f'{label}@{k}', 0):.4f}" for k in K_VALUES]
        print(f"{label:<12} {vals[0]:>8} {vals[1]:>8} {vals[2]:>8}")


# Save results to JSON
def save_results(retriever_name: str, dataset_name: str, metrics: dict):
    results_dir = Path(RESULTS_DIR)
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f"{dataset_name}_{retriever_name}.json"
    with open(path, "w") as f:
        json.dump({"retriever": retriever_name, "dataset": dataset_name, "metrics": metrics}, f, indent=2)
    print(f"\nSaved to {path}")


# Print comparison table for multiple retrievers
def print_comparison_table(all_metrics: list[tuple[str, dict]]):
    print(f"\n{'='*80}")
    print("Retriever Comparison")
    print(f"{'='*80}")

    header = f"{'Retriever':<30}"
    for label in ["NDCG", "Recall", "P"]:
        for k in K_VALUES:
            header += f" {label}@{k:>2}"
    print(header)
    print("-" * 80)

    for name, metrics in all_metrics:
        row = f"{name:<30}"
        for label in ["NDCG", "Recall", "P"]:
            for k in K_VALUES:
                row += f" {metrics.get(f'{label}@{k}', 0):>6.4f}"
        print(row)


def main():
    parser = argparse.ArgumentParser(description="RAG Retrieval Evaluation")
    parser.add_argument("--dataset", required=True, help="Dataset name (without .json)")
    parser.add_argument("--retriever", default="dense", choices=["dense", "sparse", "hybrid"])
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--truncate-dims", type=int, default=None, help="MRL dimension truncation")
    parser.add_argument("--rrf-k", type=int, default=60, help="RRF k parameter for hybrid fusion")
    parser.add_argument("--mrl-sweep", action="store_true", help="Run MRL sweep over multiple dims")
    parser.add_argument("--hybrid-sweep", action="store_true", help="Run Dense, Sparse, Hybrid side by side")
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)
    corpus = dataset["corpus"]
    queries = dataset["queries"]
    qrels = dataset["qrels"]

    if args.mrl_sweep:
        from retrievers.dense import DenseRetriever
        dims_to_test = [256, 512, 1024, 2048, None]
        print(f"\nMRL Sweep: {len(dims_to_test)} configurations")
        print(f"Dataset: {args.dataset} ({len(queries)} queries, {len(corpus)} docs)")

        for dims in dims_to_test:
            retriever = DenseRetriever(truncate_dims=dims)
            results = retriever.search(corpus, queries, args.top_k)
            metrics = evaluate(qrels, results)
            print_results(retriever.name(), metrics)
            save_results(retriever.name(), args.dataset, metrics)
        return

    if args.hybrid_sweep:
        from retrievers.dense import DenseRetriever
        from retrievers.sparse import SparseRetriever
        from retrievers.hybrid import HybridRetriever
        print(f"\nHybrid Sweep: Dense vs Sparse vs Hybrid")
        print(f"Dataset: {args.dataset} ({len(queries)} queries, {len(corpus)} docs)")

        dense = DenseRetriever(truncate_dims=args.truncate_dims)
        sparse = SparseRetriever()
        hybrid = HybridRetriever(dense, sparse, rrf_k=args.rrf_k)

        all_metrics = []
        for retriever in [dense, sparse, hybrid]:
            results = retriever.search(corpus, queries, args.top_k)
            metrics = evaluate(qrels, results)
            all_metrics.append((retriever.name(), metrics))
            save_results(retriever.name(), args.dataset, metrics)

        print_comparison_table(all_metrics)
        return

    if args.retriever == "dense":
        from retrievers.dense import DenseRetriever
        retriever = DenseRetriever(truncate_dims=args.truncate_dims)
    elif args.retriever == "sparse":
        from retrievers.sparse import SparseRetriever
        retriever = SparseRetriever()
    elif args.retriever == "hybrid":
        from retrievers.dense import DenseRetriever
        from retrievers.sparse import SparseRetriever
        from retrievers.hybrid import HybridRetriever
        dense = DenseRetriever(truncate_dims=args.truncate_dims)
        sparse = SparseRetriever()
        retriever = HybridRetriever(dense, sparse, rrf_k=args.rrf_k)

    print(f"Dataset: {args.dataset} ({len(queries)} queries, {len(corpus)} docs)")
    print(f"Retriever: {retriever.name()}")
    print(f"Top-K: {args.top_k}")

    results = retriever.search(corpus, queries, args.top_k)
    metrics = evaluate(qrels, results)
    print_results(retriever.name(), metrics)
    save_results(retriever.name(), args.dataset, metrics)


if __name__ == "__main__":
    main()
