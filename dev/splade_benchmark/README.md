# SPLADE Parallel Embedding Benchmark

Measures wall time for sequential vs parallel execution of dense (port 8081) and sparse/SPLADE (port 8083) embedding servers.

## What It Tests

- Sequential: `embed_workflow` then `sparse_embed_workflow`
- Parallel: both run concurrently via `ThreadPoolExecutor(max_workers=2)`
- Batch sizes: 8, 16, 32, 64 texts
- Verifies outputs are identical between both strategies

## How to Run

Both embedding servers must be running before starting the benchmark.

```bash
cd /path/to/RAG
./venv/bin/python dev/splade_benchmark/benchmark.py
```

## Expected Output

```
Sequential vs Parallel Embedding Benchmark
============================================================
 Batch    Sequential      Parallel   Speedup   Identical
------------------------------------------------------------
     8         4.21s         2.31s     1.82x        YES
    16         8.43s         4.58s     1.84x        YES
    32        16.70s         8.95s     1.87x        YES
    64        33.20s        17.80s     1.86x        YES
============================================================
```

Expected speedup: ~1.5-2x depending on server load and GPU memory bandwidth.
