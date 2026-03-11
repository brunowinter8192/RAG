# Worker Report: indexer-parallel

## Task
Benchmark sequential vs parallel execution of dense (port 8081) and SPLADE (port 8083) embedding servers, then implement parallelization in `src/rag/indexer.py`.

## Results

### Benchmark Script
Created `dev/splade_benchmark/benchmark.py` that:
- Tests batch sizes 8, 16, 32, 64
- Runs sequential (embed then sparse) and parallel (ThreadPoolExecutor, max_workers=2)
- Measures wall time with `time.perf_counter()`
- Verifies output identity between both strategies
- Prints results as formatted table

### Indexer Parallelization
Updated `src/rag/indexer.py`:
- Added `from concurrent.futures import ThreadPoolExecutor` import
- Added `parallel_embed()` function in FUNCTIONS section
- Replaced sequential calls in `index_json_workflow()` lines 58-59 with `parallel_embed(texts)`
- `backfill_splade_workflow` untouched (only calls sparse, no parallelization needed)

## Files Changed

- `src/rag/indexer.py` — added ThreadPoolExecutor import, `parallel_embed()` function, replaced sequential embed calls with parallel call
- `dev/splade_benchmark/benchmark.py` — new benchmark script (sequential vs parallel, 4 batch sizes, output identity verification)
- `dev/splade_benchmark/README.md` — brief docs: what it tests, how to run, expected output format

## Open Issues
None. Benchmark must be run by user with both servers active to confirm actual speedup numbers.
