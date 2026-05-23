# Box Architecture (RAG GPU Server Management)

## Status Quo (IST)

All RAG GPU processes (llama-server presets embedding/reranker, uvicorn-based splade, arbitrary llama-server starts) are managed via `rag-cli server` as the sole sanctioned interface. Each box-managed process has a state file at `~/.rag-locks/server-port-{N}.json` containing pid, port, model_path, model_name, mode, start_time, log_path, name. stdout/stderr is redirected to per-process log files at `~/.rag-locks/logs/llama-port-{N}.log` for llama-server; splade writes its own `~/.rag-locks/logs/splade_server.log` via Python `logging`. `LOG_DIR` in `server_utils.py` is fixed to `~/.rag-locks/logs/` (NOT `<project>/src/rag/logs/`) so logs survive worktree cleanup — a server spawned from a worker-worktree keeps its log path stable after worktree removal, enabling watchdog idle-stop based on log mtime regardless of where the server was started.

The watchdog (`_watchdog_loop` in `server_manager.py`) iterates state files, computes idle from log file mtime, sends SIGTERM after IDLE_TIMEOUT (default 3600s). On every tick it also runs `_purge_orphans` which kills any `pgrep -x llama-server` PID not in the state-file registry — out-of-box processes die within ~30s.

CLI surface: `rag-cli server {status|list|start|stop|restart} [name]` for presets, `rag-cli server start --model PATH --port N --mode {embedding|rerank} [--name LABEL]` for arbitrary, `rag-cli server {stop|restart} --port N` for port-targeted control.

GPU pane (Monitor_CC) reads state files: 3 fixed preset rows always visible plus dynamic arbitrary rows below. Idle countdown derives from log-mtime. Anomalies (malformed JSON, dead PID, missing log, duplicates, legacy files) logged to `Monitor_CC/src/gpu_pane/logs/gpu_pane.log` and counted in pane footer.

## Evidenz

- Live-probe verified llama-server logs 8 lines per inference request to stdout (slot status + srv log), `/health` is silent. mtime updates per request, /health does NOT trigger updates. See `dev/watchdog_scope/proposal_phaseA_v2.md (Monitor_CC)` NQ3 for the probe.
- Splade `logging.info(f"Encoded {len(req.input)} texts")` in `splade_server.py:47` writes per-request line to `splade_server.log`. Same idle mechanism applies.
- pgrep `-x` (exact comm match) avoids false-positives from processes mentioning "llama-server" in argv (e.g. workers with prompt text containing the string). Tested via `pgrep -x llama-server` returning empty when no real llama-server runs.

## Recommendation (SOLL)

Box architecture is the production state. Future evolution: dynamic ports replaces fixed default ports with socket(0)-allocated ports + state-file-based service discovery. Default ports become hints with dynamic fallback on collision.

## Quellen

- `dev/watchdog_scope/proposal_phaseA_v2.md (Monitor_CC)` — full architecture spec, NQ1-NQ6.
- `~/.claude/shared-rules/global/tool-use.md` `#### RAG CLI` — operational rules in tool-use.
