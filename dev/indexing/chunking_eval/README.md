# Chunking Evaluation

Evaluates chunking strategy variants (chunk size, overlap, separator set) using **Document-Level Recall@K**. Because chunk IDs change when chunk size changes, traditional chunk-level qrels are invalid across variants. Solution: ground truth links queries to documents, not chunks.

## Concept

For each variant, the sweep:
1. Chunks all `.md` source files using the variant's parameters
2. Indexes into a test DB collection (e.g., `test_c500`, `test_c750_md`)
3. Runs hybrid retrieval per query and checks whether any top-K result belongs to the relevant document
4. Reports Recall@3, Recall@5, Recall@10 per variant

## Variants

| Code | Chunk Size | Overlap | Separators |
|------|-----------|---------|------------|
| A    | 500       | 100     | default    |
| B    | 750       | 150     | default    |
| C    | 1000      | 200     | default    |
| D    | 1500      | 300     | default    |
| E    | 500       | 100     | markdown   |
| F    | 750       | 150     | markdown   |

**Default separators:** `\n\n`, `\n`, `. `, `! `, `? `, ` `

**Markdown separators:** `# `, `## `, `### `, `\n---\n`, ` ``` `, `\n\n`, `\n`, `. `, ` `

## Setup

Create the test database (one-time):
```bash
bash dev/indexing/chunking_eval/setup_test_db.sh
```

GPU servers must be running for indexing and eval:
```bash
./start.sh
```

## Usage

```bash
# Full sweep (all 6 variants)
./venv/bin/python dev/indexing/chunking_eval/chunking_sweep.py \
    --source-dir data/documents/RAG_MCP \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --db-name rag_test

# Specific variants only
./venv/bin/python dev/indexing/chunking_eval/chunking_sweep.py \
    --source-dir data/documents/RAG_MCP \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --db-name rag_test \
    --variants A,C,E

# Dry run: chunk stats only, no embed/index/eval
./venv/bin/python dev/indexing/chunking_eval/chunking_sweep.py \
    --source-dir data/documents/RAG_MCP \
    --dataset dev/indexing/chunking_eval/datasets/rag_mcp_doc_level.json \
    --dry-run
```

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--source-dir` | required | Directory with `.md` files to chunk |
| `--dataset` | required | Path to document-level dataset JSON |
| `--db-name` | `rag_test` | PostgreSQL database name (NOT `rag`) |
| `--variants` | `A,B,C,D,E,F` | Comma-separated variant codes |
| `--dry-run` | off | Chunk + show stats only, skip embed/index/eval |

## Dataset Format

```json
{
  "queries": {
    "q01": "What embedding dimensions does Qwen3 support?"
  },
  "doc_qrels": {
    "q01": ["arxiv__2506.05176__qwen3-embedding.md"]
  }
}
```

`doc_qrels` maps query IDs to lists of relevant document filenames. A query is considered a hit at rank K if any of the top-K retrieved chunks belongs to a relevant document.

## Output

Results are printed as a comparison table and saved to `dev/indexing/chunking_eval/results/sweep_<timestamp>.json`.

```
Chunking Sweep Results
======================================================================
Variant      Chunks  Avg_Size   Recall@3   Recall@5  Recall@10
----------------------------------------------------------------------
A (500)         482       438      0.850      0.920      0.960
B (750)         321       685      0.830      0.900      0.950
C (1000)        241       910      0.810      0.890      0.940
...
```
