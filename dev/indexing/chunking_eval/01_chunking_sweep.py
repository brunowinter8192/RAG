# INFRASTRUCTURE
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

K_VALUES = [3, 5, 10]

VARIANTS = {
    "A": {"chunk_size": 500,  "overlap": 100, "separators": "default"},
    "B": {"chunk_size": 750,  "overlap": 150, "separators": "default"},
    "C": {"chunk_size": 1000, "overlap": 200, "separators": "default"},
    "D": {"chunk_size": 1500, "overlap": 300, "separators": "default"},
    "E": {"chunk_size": 500,  "overlap": 100, "separators": "markdown"},
    "F": {"chunk_size": 750,  "overlap": 150, "separators": "markdown"},
}

DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", " "]
MARKDOWN_SEPARATORS = ["# ", "## ", "### ", "\n---\n", "```\n", "\n\n", "\n", ". ", " "]


# ORCHESTRATOR

def run_sweep(source_dir: str, dataset_path: str, db_name: str, variant_codes: list[str], dry_run: bool):
    os.environ["POSTGRES_DB"] = db_name

    from src.rag.chunker import recursive_split, merge_with_overlap, chunk_workflow
    from src.rag.indexer import index_json_workflow

    dataset = load_dataset(dataset_path)
    source_files = list(Path(source_dir).glob("*.md"))
    if not source_files:
        print(f"No .md files found in {source_dir}")
        sys.exit(1)

    print(f"Source documents: {len(source_files)}")
    print(f"Queries: {len(dataset['queries'])}")
    print(f"Variants: {', '.join(variant_codes)}")
    print()

    all_results = []

    with tempfile.TemporaryDirectory(prefix="chunking_sweep_") as tmpdir:
        for code in variant_codes:
            if code not in VARIANTS:
                print(f"Unknown variant: {code}, skipping")
                continue

            cfg = VARIANTS[code]
            collection = collection_name(code, cfg)
            print(f"=== Variant {code}: chunk_size={cfg['chunk_size']}, overlap={cfg['overlap']}, separators={cfg['separators']} ===")

            chunks_by_doc = chunk_all_documents(source_files, cfg, recursive_split, merge_with_overlap, chunk_workflow)
            stats = compute_stats(chunks_by_doc)
            print(f"  Chunks: {stats['total']}, Avg size: {stats['avg']}, Min: {stats['min']}, Max: {stats['max']}")

            if dry_run:
                all_results.append((code, cfg, stats, None))
                continue

            coll_dir = Path(tmpdir) / collection
            coll_dir.mkdir()
            write_chunks_json(chunks_by_doc, coll_dir)

            print(f"  Indexing into {db_name}/{collection}...")
            total_indexed = 0
            for json_path in sorted(coll_dir.glob("*.json")):
                indexed = index_json_workflow(str(json_path))
                total_indexed += indexed
            print(f"  Indexed {total_indexed} chunks")

            print(f"  Running document-level eval...")
            metrics = document_level_eval(dataset["queries"], dataset["doc_qrels"], collection)
            recall_str = "  ".join(f"Recall@{k}={metrics[f'Recall@{k}']:.3f}" for k in K_VALUES)
            print(f"  {recall_str}")

            all_results.append((code, cfg, stats, metrics))
            print()

    if not dry_run:
        print_comparison_table(all_results)
        save_results(all_results, dataset_path)
    else:
        print_dry_run_table(all_results)


# FUNCTIONS

# Load document-level dataset from JSON
def load_dataset(dataset_path: str) -> dict:
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    with open(path) as f:
        return json.load(f)


# Chunk all .md files in source_dir for a given variant config
def chunk_all_documents(source_files, cfg, recursive_split, merge_with_overlap, chunk_workflow):
    chunks_by_doc = {}
    separators = MARKDOWN_SEPARATORS if cfg["separators"] == "markdown" else DEFAULT_SEPARATORS

    for md_file in sorted(source_files):
        if cfg["separators"] == "markdown":
            with open(md_file, encoding="utf-8") as f:
                content = f.read()
            splits = recursive_split(content, separators, cfg["chunk_size"])
            text_chunks = merge_with_overlap(splits, cfg["chunk_size"], cfg["overlap"])
            chunks = [{"content": c, "index": i, "total_chunks": len(text_chunks)} for i, c in enumerate(text_chunks) if c.strip()]
        else:
            result = chunk_workflow(str(md_file), chunk_size=cfg["chunk_size"], overlap=cfg["overlap"])
            chunks = [{"content": c["content"], "index": c["index"], "total_chunks": c["total_chunks"]} for c in result]

        if chunks:
            chunks_by_doc[md_file.name] = chunks

    return chunks_by_doc


# Compute chunk statistics across all documents
def compute_stats(chunks_by_doc: dict) -> dict:
    all_chunks = [c for chunks in chunks_by_doc.values() for c in chunks]
    if not all_chunks:
        return {"total": 0, "avg": 0, "min": 0, "max": 0}
    sizes = [len(c["content"]) for c in all_chunks]
    return {
        "total": len(sizes),
        "avg": round(sum(sizes) / len(sizes)),
        "min": min(sizes),
        "max": max(sizes),
    }


# Write one chunks.json per document into the collection directory
def write_chunks_json(chunks_by_doc: dict, coll_dir: Path):
    for doc_name, chunks in chunks_by_doc.items():
        stem = Path(doc_name).stem
        json_path = coll_dir / f"{stem}.json"
        with open(json_path, "w") as f:
            json.dump({"document": doc_name, "chunks": chunks}, f, indent=2)


# Run document-level Recall@K eval for a collection using hybrid search
def document_level_eval(queries: dict, doc_qrels: dict, collection: str) -> dict:
    from src.rag.retriever import search_hybrid_workflow

    max_k = max(K_VALUES)
    hits = {k: 0 for k in K_VALUES}
    n_queries = 0

    for qid, query in queries.items():
        relevant_docs = set(doc_qrels.get(qid, []))
        if not relevant_docs:
            continue
        n_queries += 1

        try:
            results = search_hybrid_workflow(query, collection=collection, top_k=max_k, rerank=False)
        except Exception as e:
            print(f"  Warning: search failed for {qid}: {e}")
            continue

        result_docs = [r["document"] for r in results]
        for k in K_VALUES:
            top_k_docs = set(result_docs[:k])
            if top_k_docs & relevant_docs:
                hits[k] += 1

    if n_queries == 0:
        return {f"Recall@{k}": 0.0 for k in K_VALUES}

    return {f"Recall@{k}": round(hits[k] / n_queries, 4) for k in K_VALUES}


# Derive collection name from variant code and config
def collection_name(code: str, cfg: dict) -> str:
    suffix = "_md" if cfg["separators"] == "markdown" else ""
    return f"test_c{cfg['chunk_size']}{suffix}"


# Print comparison table for all variants
def print_comparison_table(all_results: list):
    print("\nChunking Sweep Results")
    print("=" * 70)
    header = f"{'Variant':<12} {'Chunks':>7} {'Avg_Size':>9}"
    for k in K_VALUES:
        header += f" {'Recall@'+str(k):>10}"
    print(header)
    print("-" * 70)

    for code, cfg, stats, metrics in all_results:
        label = f"{code} ({cfg['chunk_size']})"
        if cfg["separators"] == "markdown":
            label += " md"
        row = f"{label:<12} {stats['total']:>7} {stats['avg']:>9}"
        for k in K_VALUES:
            row += f" {metrics[f'Recall@{k}']:>10.3f}"
        print(row)


# Print dry-run table (no eval metrics)
def print_dry_run_table(all_results: list):
    print("\nDry Run — Chunk Statistics")
    print("=" * 55)
    print(f"{'Variant':<12} {'Chunks':>7} {'Avg_Size':>9} {'Min':>6} {'Max':>6}")
    print("-" * 55)
    for code, cfg, stats, _ in all_results:
        label = f"{code} ({cfg['chunk_size']})"
        if cfg["separators"] == "markdown":
            label += " md"
        print(f"{label:<12} {stats['total']:>7} {stats['avg']:>9} {stats['min']:>6} {stats['max']:>6}")


# Save sweep results to JSON
def save_results(all_results: list, dataset_path: str):
    results_dir = Path(__file__).parent / "01_reports"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"sweep_{timestamp}.json"

    output = {
        "timestamp": timestamp,
        "dataset": dataset_path,
        "variants": [],
    }
    for code, cfg, stats, metrics in all_results:
        output["variants"].append({
            "code": code,
            "config": cfg,
            "stats": stats,
            "metrics": metrics,
        })

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Chunking Strategy Sweep — Document-Level Recall@K Evaluation")
    parser.add_argument("--source-dir", required=True, help="Directory with .md files to chunk")
    parser.add_argument("--dataset", required=True, help="Path to document-level dataset JSON")
    parser.add_argument("--db-name", default="rag_test", help="PostgreSQL database name (NOT rag)")
    parser.add_argument("--variants", default="A,B,C,D,E,F", help="Comma-separated variant codes to run")
    parser.add_argument("--dry-run", action="store_true", help="Only chunk + show stats, skip embed/index/eval")
    args = parser.parse_args()

    variant_codes = [v.strip().upper() for v in args.variants.split(",")]
    run_sweep(args.source_dir, args.dataset, args.db_name, variant_codes, args.dry_run)


if __name__ == "__main__":
    main()
