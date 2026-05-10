# INFRASTRUCTURE
import json
import logging
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx

from . import error_log

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
RAG_ROOT = Path(os.getenv("RAG_PROJECT_ROOT", str(Path(__file__).parent.parent.parent)))

logging.basicConfig(
    filename=LOG_DIR / "server_manager.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

IDLE_TIMEOUT = int(os.getenv("RAG_SERVER_IDLE_TIMEOUT", "3600"))
TIMESTAMP_DIR = Path.home() / ".rag-locks"
WATCHDOG_INTERVAL = 30
WATCHDOG_PID_FILE = Path.home() / ".rag-locks" / "watchdog.pid"

LLAMA_SERVER_PATH = os.getenv("LLAMA_SERVER_PATH", str(RAG_ROOT / "llama.cpp/build/bin/llama-server"))
EMBEDDING_8B_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", str(RAG_ROOT / "models/Qwen3-Embedding-8B-Q8_0.gguf"))
EMBEDDING_06B_MODEL_PATH = os.getenv("EMBEDDING_06B_MODEL_PATH", str(RAG_ROOT / "models/Qwen3-Embedding-0.6B-Q8_0.gguf"))
RERANKER_06B_MODEL_PATH = os.getenv("RERANKER_MODEL_PATH", str(RAG_ROOT / "models/qwen3-reranker-0.6b-q8_0.gguf"))
RERANKER_8B_MODEL_PATH = os.getenv("RERANKER_8B_MODEL_PATH", str(RAG_ROOT / "models/Qwen3-Reranker-8B-Q8_0.gguf"))
SPLADE_MODEL = "naver/splade-v3"

EMBEDDING_8B_PORT = int(os.getenv("EMBEDDING_PORT", "8081"))
EMBEDDING_06B_PORT = int(os.getenv("EMBEDDING_06B_PORT", "8084"))
RERANKER_06B_PORT = int(os.getenv("RERANKER_PORT", "8082"))
RERANKER_8B_PORT = int(os.getenv("RERANKER_8B_PORT", "8085"))
SPLADE_PORT = int(os.getenv("SPLADE_PORT", "8083"))

# Insertion order matters: when client calls find_server_url("embedding") and
# multiple variants are running, the FIRST matching entry in iteration order
# wins. Keep the canonical default for each class FIRST.
#
# default=True → started by `rag-cli server start` without args + by ensure_ready
#                for search/index workflows. Non-default variants are visible as
#                presets but only start when explicitly named.
SERVERS = {
    "embedding-8b": {
        "default_port": EMBEDDING_8B_PORT,
        "model_path": EMBEDDING_8B_MODEL_PATH,
        "mode": "embedding",
        "type": "llama",
        "extra_flags": ["-ngl", "99", "-c", "2048", "-np", "1", "-b", "4096", "-ub", "4096"],
        "timeout": 90,
        "required_for": ["search", "index"],
        "default": True,
    },
    "embedding-0.6b": {
        "default_port": EMBEDDING_06B_PORT,
        "model_path": EMBEDDING_06B_MODEL_PATH,
        "mode": "embedding",
        "type": "llama",
        "extra_flags": ["-ngl", "99", "-c", "2048", "-np", "1", "-b", "4096", "-ub", "4096"],
        "timeout": 90,
        "required_for": ["search", "index"],
        "default": False,
    },
    "reranker-0.6b": {
        "default_port": RERANKER_06B_PORT,
        "model_path": RERANKER_06B_MODEL_PATH,
        "mode": "rerank",
        "type": "llama",
        "extra_flags": ["-ngl", "99", "-c", "32768", "-ub", "4096", "-b", "4096"],
        "timeout": 90,
        "required_for": ["rerank"],
        "default": True,
    },
    "reranker-8b": {
        "default_port": RERANKER_8B_PORT,
        "model_path": RERANKER_8B_MODEL_PATH,
        "mode": "rerank",
        "type": "llama",
        "extra_flags": ["-ngl", "99", "-c", "32768", "-ub", "4096", "-b", "4096"],
        "timeout": 90,
        "required_for": ["rerank"],
        "default": False,
    },
    "splade": {
        "default_port": SPLADE_PORT,
        "model_path": SPLADE_MODEL,
        "mode": "splade",
        "type": "uvicorn",
        "uvicorn_app": "src.rag.splade_server:app",
        "timeout": 60,
        "required_for": ["search", "index"],
        "default": True,
    },
}

# Preset names — arbitrary starts may not collide with these
_PRESET_NAMES: frozenset[str] = frozenset(SERVERS.keys())

# Map class-name (embedding / reranker / splade) → list of preset variant names,
# in default-first order. Used by find_server_url() prefix-match for backward
# compatibility with client calls find_server_url("embedding") etc.
_CLASS_MAP: dict[str, list[str]] = {}
for _n, _c in SERVERS.items():
    _CLASS_MAP.setdefault(_c["mode"] if _c["mode"] != "rerank" else "reranker", []).append(_n)
# splade class name matches its mode already; keep insertion order = default first


# ORCHESTRATOR

# Return status of all servers: running, pid, port, healthy per server name
def status() -> dict[str, dict]:
    result = {}
    for name, cfg in SERVERS.items():
        url = find_server_url(name)
        if url:
            port = int(url.split(":")[-1])
        else:
            port = cfg["default_port"]
        pid = find_pid_on_port(port)
        result[name] = {
            "running": pid is not None,
            "pid": pid,
            "port": port,
            "healthy": _check_health_port(port) if pid else False,
        }
    return result


# Start a preset server; resolves port dynamically, writes state file immediately after Popen
def start(name: str) -> bool:
    if name not in SERVERS:
        raise ValueError(f"Unknown server: {name}. Available: {list(SERVERS.keys())}")

    cfg = SERVERS[name]
    error_log.write(name, "start_initiated", f"start({name}) called",
                    caller="start", model_path=cfg["model_path"], default_port=cfg["default_port"])

    # Check for live state file with this name — single-instance enforcement
    for sf in sorted(TIMESTAMP_DIR.glob("server-port-*.json")):
        try:
            state = json.loads(sf.read_text())
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            continue
        if state.get("name") == name and _pid_alive(state["pid"]):
            if _check_health_port(state["port"]):
                logging.info(f"{name} already running on port {state['port']} (PID {state['pid']})")
                return False
            # Alive but unhealthy → stop and restart on a fresh port
            logging.warning(f"{name} alive on port {state['port']} but unhealthy, stopping for restart")
            error_log.write(name, "single_instance_alive_replaced",
                            f"existing {name} alive on port {state['port']} (PID {state['pid']}) but unhealthy — replacing",
                            caller="start", existing_pid=state["pid"], existing_port=state["port"])
            _stop_by_state(state, sf,
                           caller="start",
                           reason=f"alive but _check_health_port({state['port']}) returned False at start-time")
            break

    port = _resolve_port(cfg["default_port"])

    if cfg["type"] == "llama":
        binary = Path(LLAMA_SERVER_PATH)
        if not binary.exists():
            raise RuntimeError(
                f"Cannot start {name}: {binary} not found. "
                f"cd <RAG_ROOT> && ./start.sh"
            )
        cmd = _build_llama_cmd(cfg["model_path"], port, cfg["mode"], cfg["extra_flags"])
        log_path = LOG_DIR / f"llama-port-{port}.log"
        log_fh = open(log_path, "w")
        log_stderr = subprocess.STDOUT
        cwd = None
        model_name = Path(cfg["model_path"]).stem
    else:  # uvicorn (splade)
        venv_python = str(RAG_ROOT / "venv/bin/python")
        if not Path(venv_python).exists():
            raise RuntimeError(f"Cannot start {name}: {venv_python} not found.")
        cmd = _build_uvicorn_cmd(cfg["uvicorn_app"], port)
        log_path = LOG_DIR / "splade_server.log"
        log_fh = open(log_path, "w")
        log_stderr = subprocess.STDOUT
        cwd = str(RAG_ROOT)
        model_name = cfg["model_path"]

    logging.info(f"Starting {name} on port {port}...")
    proc = subprocess.Popen(cmd, stdout=log_fh, stderr=log_stderr, cwd=cwd)
    if log_fh is not subprocess.DEVNULL:
        log_fh.close()  # parent closes; child retains its fd copy

    _write_state_file(
        pid=proc.pid, port=port,
        model_path=cfg["model_path"], model_name=model_name,
        mode=cfg["mode"], name=name,
        log_path=str(log_path),
    )

    timeout = cfg["timeout"]
    try:
        for i in range(timeout):
            time.sleep(1)
            if _check_health_port(port):
                actual_pid = find_pid_on_port(port)
                if actual_pid is not None and actual_pid != proc.pid:
                    _write_state_file(
                        pid=actual_pid, port=port,
                        model_path=cfg["model_path"], model_name=model_name,
                        mode=cfg["mode"], name=name,
                        log_path=str(log_path),
                    )
                final_pid = actual_pid or proc.pid
                logging.info(
                    f"{name} started on port {port} "
                    f"(PID {final_pid}) after {i + 1}s"
                )
                error_log.write(name, "start_succeeded",
                                f"{name} healthy on port {port} after {i + 1}s",
                                caller="start", pid=final_pid, port=port, elapsed_s=i + 1)
                return True
        raise RuntimeError(f"Failed to start {name} after {timeout}s")
    except Exception:
        _unlink_state_file(port, caller="start", reason=f"start({name}) failed: did not become healthy in {cfg['timeout']}s")
        raise


# Stop a preset server; finds actual port via state file, falls back to default port
def stop(name: str) -> bool:
    if name not in SERVERS:
        raise ValueError(f"Unknown server: {name}. Available: {list(SERVERS.keys())}")

    cfg = SERVERS[name]
    url = find_server_url(name)
    port = int(url.split(":")[-1]) if url else cfg["default_port"]

    pids = find_all_pids_on_port(port)
    if not pids:
        logging.info(f"{name} not running on port {port}")
        return False

    logging.info(f"Stopping {name} (PIDs {pids}) on port {port}...")
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    for _ in range(10):
        time.sleep(0.5)
        remaining = find_all_pids_on_port(port)
        if not remaining:
            logging.info(f"{name} stopped")
            _unlink_state_file(port, caller="stop", reason=f"stop({name}): exited cleanly after SIGTERM")
            return True

    for pid in find_all_pids_on_port(port):
        try:
            os.kill(pid, signal.SIGKILL)
            logging.warning(f"{name} force-killed (PID {pid})")
        except ProcessLookupError:
            pass
    _unlink_state_file(port, caller="stop", reason=f"stop({name}): force-killed after 5s SIGTERM grace expired")
    return True


# Restart a server
def restart(name: str) -> bool:
    stop(name)
    return start(name)


# Start an arbitrary llama-server; port is optional (None → fully dynamic)
def start_arbitrary(model_path: str, port: int | None, mode: str, name: str | None = None) -> bool:
    if mode not in {"embedding", "rerank"}:
        raise ValueError(
            f"mode must be 'embedding' or 'rerank' for arbitrary start (got '{mode}'). "
            f"Use the 'splade' preset for SPLADE."
        )

    # Name collision check — must come before port resolution
    if name is not None:
        if name in _PRESET_NAMES:
            raise ValueError(
                f"Name {name!r} is a preset name; use `rag-cli server start {name}` instead."
            )
        for sf in TIMESTAMP_DIR.glob("server-port-*.json"):
            try:
                state = json.loads(sf.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            if state.get("name") == name and _pid_alive(state["pid"]):
                raise ValueError(
                    f"Name {name!r} already in use by server on port {state['port']}. "
                    f"Choose a different --name or stop the existing server first."
                )

    port = _resolve_port(port)

    # Check for existing managed server on this port
    state_file = TIMESTAMP_DIR / f"server-port-{port}.json"
    if state_file.exists():
        try:
            existing = json.loads(state_file.read_text())
            if _pid_alive(existing["pid"]) and _check_health_port(port):
                label = existing.get("name") or f"port-{port}"
                logging.info(f"Arbitrary start: {label} already running on port {port}")
                return False
        except (json.JSONDecodeError, KeyError, OSError):
            pass
        state_file.unlink(missing_ok=True)

    pid = find_pid_on_port(port)
    if pid is not None:
        raise RuntimeError(f"Port {port} in use by PID {pid} (not managed by box). Stop it first.")

    binary = Path(LLAMA_SERVER_PATH)
    if not binary.exists():
        raise RuntimeError(
            f"llama-server not found at {binary}. Build it or set LLAMA_SERVER_PATH."
        )

    mode_flag = "--embedding" if mode == "embedding" else "--rerank"
    cmd = [
        LLAMA_SERVER_PATH, "-m", model_path,
        mode_flag, "--host", "0.0.0.0", "--port", str(port),
        "-ngl", "99",
    ]
    model_name = Path(model_path).stem
    log_path = LOG_DIR / f"llama-port-{port}.log"

    logging.info(f"Starting arbitrary {mode} server on port {port} ({model_name})...")

    log_fh = open(log_path, "w")
    proc = subprocess.Popen(cmd, stdout=log_fh, stderr=subprocess.STDOUT)
    log_fh.close()

    _write_state_file(
        pid=proc.pid, port=port,
        model_path=model_path, model_name=model_name,
        mode=mode, name=name,
        log_path=str(log_path),
    )

    timeout = 90
    label_for_log = name or f"port-{port}"
    error_log.write(label_for_log, "start_initiated",
                    f"start_arbitrary({label_for_log}, port={port}) called",
                    caller="start_arbitrary", model_path=model_path, mode=mode)
    try:
        for i in range(timeout):
            time.sleep(1)
            if _check_health_port(port):
                actual_pid = find_pid_on_port(port)
                if actual_pid is not None and actual_pid != proc.pid:
                    _write_state_file(
                        pid=actual_pid, port=port,
                        model_path=model_path, model_name=model_name,
                        mode=mode, name=name,
                        log_path=str(log_path),
                    )
                final_pid = actual_pid or proc.pid
                logging.info(
                    f"Arbitrary server {label_for_log} started on port {port} "
                    f"(PID {final_pid}) after {i + 1}s"
                )
                error_log.write(label_for_log, "start_succeeded",
                                f"{label_for_log} healthy on port {port} after {i + 1}s",
                                caller="start_arbitrary", pid=final_pid, port=port, elapsed_s=i + 1)
                return True
        raise RuntimeError(f"Failed to start arbitrary server on port {port} after {timeout}s")
    except Exception:
        _unlink_state_file(port, caller="start_arbitrary", reason=f"start_arbitrary({name or 'unnamed'}, port={port}) failed: did not become healthy in {timeout}s")
        raise


# Resolve a class-name (embedding / reranker / splade) to the default variant preset name.
# Returns the input unchanged if not a class name.
def _resolve_class_to_default(name: str) -> str:
    variants = _CLASS_MAP.get(name)
    if not variants:
        return name
    for v in variants:
        if SERVERS[v].get("default"):
            return v
    return variants[0]  # fallback: first in insertion order


# Start all default servers (one per class); non-default variants must be started by name.
# Returns name → 'started'|'already_running'|'error: ...'
def start_all() -> dict[str, str]:
    results = {}
    for name, cfg in SERVERS.items():
        if not cfg.get("default"):
            continue
        try:
            started = start(name)
            results[name] = "started" if started else "already_running"
        except Exception as e:
            results[name] = f"error: {e}"
    return results


# Stop ALL servers (both default and non-default), regardless of whether they're running.
# Returns name → 'stopped'|'not_running'
def stop_all() -> dict[str, str]:
    results = {}
    for name in SERVERS:
        stopped = stop(name)
        results[name] = "stopped" if stopped else "not_running"
    return results


# Ensure server(s) for a name, class-name, or operation are running, starting if needed.
# Class-name calls (e.g. ensure_ready("embedding")) ensure the default variant.
def ensure_ready(target: str) -> None:
    # Direct preset name
    if target in SERVERS:
        if not check_health(target):
            start(target)
        _ensure_watchdog_process()
        return

    # Class name → default variant
    if target in _CLASS_MAP:
        preset = _resolve_class_to_default(target)
        # If ANY variant of this class is already healthy, we're done.
        for v in _CLASS_MAP[target]:
            if check_health(v):
                _ensure_watchdog_process()
                return
        # Otherwise start the default variant.
        start(preset)
        _ensure_watchdog_process()
        return

    # Operation-based lookup — only consider DEFAULT variants per class.
    if target == "search_rerank":
        needed_ops = ["search", "rerank"]
    else:
        needed_ops = [target]

    needed_servers: set[str] = set()
    for op in needed_ops:
        for name, cfg in SERVERS.items():
            if op in cfg["required_for"] and cfg.get("default"):
                needed_servers.add(name)

    for name in needed_servers:
        # Skip if any variant of this class is already healthy.
        cls = "reranker" if SERVERS[name]["mode"] == "rerank" else SERVERS[name]["mode"]
        if any(check_health(v) for v in _CLASS_MAP.get(cls, [name])):
            continue
        start(name)

    _ensure_watchdog_process()


# FUNCTIONS

# Return http://localhost:{port} for a running server matching name.
# Match strategy:
#   1. Exact match wins (e.g. find_server_url("embedding-8b")).
#   2. Class-prefix fallback for legacy callers: find_server_url("embedding")
#      → returns the FIRST running variant in SERVERS insertion order
#      (i.e. the default variant if it's running, else next).
# Client modules (embedder.py / reranker.py / sparse_embedder.py) call with
# class-name strings — the prefix path keeps them working without changes
# when SERVERS holds multiple variants per class.
def find_server_url(name: str) -> str | None:
    states_by_name: dict[str, dict] = {}
    for sf in sorted(TIMESTAMP_DIR.glob("server-port-*.json")):
        try:
            state = json.loads(sf.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        sn = state.get("name")
        if sn:
            states_by_name[sn] = state

    # 1. Exact match
    if name in states_by_name:
        return f"http://localhost:{states_by_name[name]['port']}"

    # 2. Class-prefix fallback: iterate variants in SERVERS insertion order,
    #    return first one that's running.
    variants = _CLASS_MAP.get(name, [])
    for v in variants:
        if v in states_by_name:
            return f"http://localhost:{states_by_name[v]['port']}"

    return None


# Check if a server responds; looks up actual port via state file, falls back to default.
# Accepts preset name OR class name (embedding / reranker / splade) — class falls back to
# default variant's default_port when nothing is running.
def check_health(name: str) -> bool:
    url = find_server_url(name)
    if url:
        port = int(url.split(":")[-1])
    elif name in SERVERS:
        port = SERVERS[name]["default_port"]
    elif name in _CLASS_MAP:
        port = SERVERS[_resolve_class_to_default(name)]["default_port"]
    else:
        return False
    try:
        resp = httpx.get(f"http://localhost:{port}/health", timeout=2.0)
        return resp.status_code == 200
    except Exception as e:
        logging.warning(f"Health check failed for {name} on port {port}: {e}")
        return False


# Find the first PID listening on a port; returns None if port is free
def find_pid_on_port(port: int) -> int | None:
    pids = find_all_pids_on_port(port)
    return pids[0] if pids else None


# Find all PIDs listening on a port
def find_all_pids_on_port(port: int) -> list[int]:
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return [int(p) for p in result.stdout.strip().split("\n") if p.strip()]
    except Exception as e:
        logging.warning(f"PID lookup failed: {e}")
    return []


# Spawn detached watchdog process if not already running; PID tracked in WATCHDOG_PID_FILE
def _ensure_watchdog_process() -> None:
    if WATCHDOG_PID_FILE.exists():
        try:
            pid = int(WATCHDOG_PID_FILE.read_text().strip())
            os.kill(pid, 0)
            return
        except (ProcessLookupError, ValueError, OSError):
            pass
    WATCHDOG_PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.Popen(
        [sys.executable, '-m', 'src.rag.watchdog_main'],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(RAG_ROOT),
    )
    WATCHDOG_PID_FILE.write_text(str(p.pid))
    logging.info(f"Watchdog process spawned (PID {p.pid}, idle timeout: {IDLE_TIMEOUT}s)")


# Background loop: purge orphans on entry, then tick idle-stop logic every WATCHDOG_INTERVAL
def _watchdog_loop() -> None:
    _purge_orphans()
    while True:
        time.sleep(WATCHDOG_INTERVAL)
        _watchdog_tick()


# Per-tick: purge orphans, then idle-stop any server whose log hasn't been touched > IDLE_TIMEOUT
def _watchdog_tick() -> None:
    _purge_orphans()
    now = time.time()
    for state_file in TIMESTAMP_DIR.glob("server-port-*.json"):
        try:
            state = json.loads(state_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            continue
        pid, port = state["pid"], state["port"]
        if not _pid_alive(pid):
            name = state.get("name") or f"port-{port}"
            error_log.write(name, "watchdog_unlinked_dead",
                            f"state file claimed PID {pid} on port {port} but process is dead — auto-unlinking stale state",
                            caller="watchdog", pid=pid, port=port,
                            state_file=str(state_file))
            state_file.unlink(missing_ok=True)
            continue
        if not _check_health_port(port):
            continue
        log = Path(state["log_path"])
        try:
            idle = now - log.stat().st_mtime
        except FileNotFoundError:
            logging.warning(f"Watchdog: log missing at {log}, skipping idle check")
            continue
        if idle > IDLE_TIMEOUT:
            label = state.get("name") or f"port-{port}"
            logging.info(f"Watchdog: {label} idle {idle:.0f}s, stopping")
            _stop_by_state(state, state_file,
                           caller="watchdog",
                           reason=f"idle {idle:.0f}s exceeds IDLE_TIMEOUT={IDLE_TIMEOUT}s (log {state['log_path']})")


# Kill llama-server PIDs not registered in any state file (continuous orphan enforcement)
def _purge_orphans() -> None:
    registered_pids: set[int] = set()
    for sf in TIMESTAMP_DIR.glob("server-port-*.json"):
        try:
            registered_pids.add(json.loads(sf.read_text())["pid"])
        except (json.JSONDecodeError, FileNotFoundError, KeyError, OSError):
            continue
    live_pids = set(pgrep_llama_server())
    orphan_pids = live_pids - registered_pids
    if not orphan_pids:
        return
    n_orphans = len(orphan_pids)
    for pid in orphan_pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.time() + 5.0
    while time.time() < deadline:
        time.sleep(0.5)
        still = {p for p in orphan_pids if _pid_alive(p)}
        if not still:
            break
        orphan_pids = still
    sigkilled: list[int] = []
    for pid in orphan_pids:
        try:
            os.kill(pid, signal.SIGKILL)
            sigkilled.append(pid)
        except ProcessLookupError:
            pass
    logging.info(f"Watchdog purge: killed {n_orphans} orphan llama-server PID(s)")
    error_log.write("orphan", "watchdog_killed_orphan",
                    f"purge killed {n_orphans} unregistered llama-server PID(s)",
                    caller="watchdog", n_pids=n_orphans, sigkilled=sigkilled)


# Return PIDs of all running llama-server processes via pgrep -x (exact comm match)
def pgrep_llama_server() -> list[int]:
    try:
        result = subprocess.run(
            ["pgrep", "-x", "llama-server"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return [int(p) for p in result.stdout.strip().split("\n") if p.strip()]
    except Exception:
        pass
    return []


# Health check by port (no SERVERS lookup — works for preset and arbitrary servers)
# Retries on transient failure: callers may take destructive action (stop+restart)
# on a False return — a single httpx timeout (GPU busy, network hiccup) must not
# trigger that. Default: 3 attempts (2 retries) with 300ms backoff. Total worst
# case ~6.6s on full failure.
def _check_health_port(port: int, retries: int = 2, backoff_s: float = 0.3) -> bool:
    for attempt in range(retries + 1):
        try:
            if httpx.get(f"http://localhost:{port}/health", timeout=2.0).status_code == 200:
                return True
        except Exception:
            pass
        if attempt < retries:
            time.sleep(backoff_s)
    return False


# SIGTERM → wait → SIGKILL a server described by its state dict; unlinks state file.
# caller + reason are LIFECYCLE EVIDENCE: every kill of a managed process must leave
# a trail in error_log (server-name, port, pid, kill-method, who-asked, why).
def _stop_by_state(state: dict, state_file: Path, *, caller: str, reason: str) -> None:
    pid, port = state["pid"], state["port"]
    name = state.get("name") or f"port-{port}"

    error_log.write(name, "stop_initiated", reason,
                    pid=pid, port=port, caller=caller, state_file=str(state_file))

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        error_log.write(name, "stop_completed", "process already dead at SIGTERM",
                        pid=pid, port=port, caller=caller, kill_method="not_required")
        state_file.unlink(missing_ok=True)
        return

    for _ in range(10):
        time.sleep(0.5)
        if not _pid_alive(pid):
            error_log.write(name, "stop_completed", "exited cleanly after SIGTERM",
                            pid=pid, port=port, caller=caller, kill_method="sigterm")
            state_file.unlink(missing_ok=True)
            return

    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    error_log.write(name, "stop_completed", "force-killed after 5s SIGTERM grace expired",
                    pid=pid, port=port, caller=caller, kill_method="sigkill")
    state_file.unlink(missing_ok=True)


# Return True if the process is alive (os.kill(pid, 0) succeeds)
def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


# OS-assigned free port via socket(0)+bind+close
def _allocate_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


# Return default_port if free, else allocate dynamic; None → always dynamic
def _resolve_port(default_port: int | None) -> int:
    if default_port is None:
        return _allocate_port()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', default_port))
            return default_port
    except OSError:
        dynamic = _allocate_port()
        logging.info(f"Default port {default_port} busy, using dynamic port {dynamic}")
        return dynamic


# Build llama-server cmd for a given model, port, mode, and extra flags
def _build_llama_cmd(model_path: str, port: int, mode: str, extra_flags: list[str]) -> list[str]:
    mode_flag = "--embedding" if mode == "embedding" else "--rerank"
    return [
        LLAMA_SERVER_PATH, "-m", model_path,
        mode_flag, "--host", "0.0.0.0", "--port", str(port),
        *extra_flags,
    ]


# Build uvicorn cmd for a given app and port
def _build_uvicorn_cmd(uvicorn_app: str, port: int) -> list[str]:
    return [
        str(RAG_ROOT / "venv/bin/python"), "-m", "uvicorn",
        uvicorn_app, "--host", "0.0.0.0", "--port", str(port),
    ]


# Write ~/.rag-locks/server-port-{port}.json with box state immediately after Popen
def _write_state_file(*, pid: int, port: int, model_path: str, model_name: str,
                      mode: str, name: str | None, log_path: str) -> Path:
    state = {
        "pid": pid, "port": port,
        "model_path": model_path, "model_name": model_name,
        "mode": mode,
        "start_time": time.time(),
        "log_path": log_path,
        "name": name,
    }
    path = TIMESTAMP_DIR / f"server-port-{port}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))
    return path


# Remove state file for a port; safe if never written or already gone.
# caller + reason are LIFECYCLE EVIDENCE — every state-file removal logged
# so any future "where did my server go?" investigation has a starting point.
def _unlink_state_file(port: int, *, caller: str, reason: str) -> None:
    path = TIMESTAMP_DIR / f"server-port-{port}.json"
    if path.exists():
        try:
            state = json.loads(path.read_text())
            name = state.get("name") or f"port-{port}"
            pid = state.get("pid")
        except (json.JSONDecodeError, OSError):
            name = f"port-{port}"
            pid = None
        error_log.write(name, "state_unlinked", reason,
                        pid=pid, port=port, caller=caller, state_file=str(path))
    path.unlink(missing_ok=True)


# Handle 'workflow.py server' / 'rag-cli server' subcommand
def cli_server(args: list[str]) -> None:
    if not args:
        args = ["status"]

    action = args[0]
    target = args[1] if len(args) > 1 else None

    if action == "status":
        st = status()
        print(f"{'Server':<12} {'Port':<6} {'Status':<10} {'PID':<8} {'Healthy'}")
        print("-" * 50)
        for name, info in st.items():
            status_str = "RUNNING" if info["running"] else "STOPPED"
            pid_str = str(info["pid"]) if info["pid"] else "-"
            health_str = "YES" if info["healthy"] else "NO"
            print(f"{name:<12} {info['port']:<6} {status_str:<10} {pid_str:<8} {health_str}")

    elif action == "start":
        if "--model" in args:
            model_path = _parse_flag(args, "--model")
            port_str = _parse_flag(args, "--port")
            mode = _parse_flag(args, "--mode")
            label_name = _parse_flag(args, "--name")
            if not model_path or not mode:
                print("Error: --model and --mode are required for arbitrary start")
                return
            port = int(port_str) if port_str else None
            try:
                started = start_arbitrary(model_path, port, mode, label_name)
                label = label_name or (f"port-{port}" if port else "dynamic")
                print(f"{label}: {'started' if started else 'already running'}")
            except Exception as e:
                print(f"Error: {e}")
        elif target:
            try:
                started = start(target)
                print(f"{target}: {'started' if started else 'already running'}")
            except Exception as e:
                print(f"{target}: error — {e}")
        else:
            results = start_all()
            for name, result in results.items():
                print(f"{name}: {result}")

    elif action == "stop":
        if "--port" in args:
            port_str = _parse_flag(args, "--port")
            if not port_str:
                print("Error: --port requires a value")
                return
            port = int(port_str)
            sf = TIMESTAMP_DIR / f"server-port-{port}.json"
            if not sf.exists():
                print(f"No managed server on port {port}")
                return
            try:
                state = json.loads(sf.read_text())
                _stop_by_state(state, sf,
                               caller="cli_server_stop",
                               reason=f"user-requested stop via 'rag-cli server stop --port {port}'")
                label = state.get("name") or f"port-{port}"
                print(f"{label}: stopped")
            except Exception as e:
                print(f"Error: {e}")
        elif target:
            stopped = stop(target)
            print(f"{target}: {'stopped' if stopped else 'not running'}")
        else:
            results = stop_all()
            for name, result in results.items():
                print(f"{name}: {result}")

    elif action == "restart":
        if "--port" in args:
            port_str = _parse_flag(args, "--port")
            if not port_str:
                print("Error: --port requires a value")
                return
            port = int(port_str)
            sf = TIMESTAMP_DIR / f"server-port-{port}.json"
            if not sf.exists():
                print(f"No managed server on port {port}")
                return
            try:
                state = json.loads(sf.read_text())
                _stop_by_state(state, sf,
                               caller="cli_server_restart",
                               reason=f"user-requested restart via 'rag-cli server restart --port {port}'")
                preset_name = state.get("name")
                if preset_name and preset_name in SERVERS:
                    start(preset_name)
                    print(f"{preset_name}: restarted")
                else:
                    start_arbitrary(state["model_path"], port, state["mode"], state.get("name"))
                    label = state.get("name") or f"port-{port}"
                    print(f"{label}: restarted")
            except Exception as e:
                print(f"Error: {e}")
        elif target:
            restart(target)
            print(f"{target}: restarted")
        else:
            stop_all()
            results = start_all()
            for name, result in results.items():
                print(f"{name}: {result}")

    elif action == "list":
        _cli_list()

    elif action == "tail":
        n = 30
        name_arg = None
        i = 1
        while i < len(args):
            if args[i] == "-n" and i + 1 < len(args):
                n = int(args[i + 1]); i += 2
            elif args[i] in SERVERS:
                name_arg = args[i]; i += 1
            else:
                i += 1
        # Resolve log_path via state file (Box-aware: dynamic ports in log name).
        log_paths: dict[str, Path] = {}
        for sf in TIMESTAMP_DIR.glob("server-port-*.json"):
            try:
                st = json.loads(sf.read_text())
                if st.get("name") and st.get("log_path"):
                    log_paths[st["name"]] = Path(st["log_path"])
            except (json.JSONDecodeError, OSError):
                continue
        names = [name_arg] if name_arg else list(SERVERS.keys())
        for srv in names:
            if len(names) > 1:
                print(f"=== {srv} ===")
            log_path = log_paths.get(srv)
            if log_path is None or not log_path.exists():
                print(f"  (no log — {srv} not running or never started)")
            else:
                for line in log_path.read_text().splitlines()[-n:]:
                    print(line)
            if len(names) > 1:
                print()

    elif action == "errors":
        from collections import Counter
        from datetime import datetime as _dt
        today = "--today" in args
        verbose = "--verbose" in args
        if verbose:
            entries = error_log.read_today() if today else error_log.read_all()
            for e in reversed(entries):
                ts = _dt.fromisoformat(e["ts"]).astimezone().strftime("%Y-%m-%d %H:%M:%S")
                extras = " ".join(f"{k}={v}" for k, v in e.items()
                                  if k not in {"ts", "server", "code", "msg"})
                print(f"{ts} | {e['server']} | {e['code']} | {e['msg']}" + (f" | {extras}" if extras else ""))
        else:
            entries = error_log.read_today()
            by_server: dict = {name: [] for name in SERVERS}
            for e in entries:
                by_server.setdefault(e["server"], []).append(e["code"])
            printed = False
            for srv, codes in by_server.items():
                if not codes:
                    continue
                counts = Counter(codes)
                detail = ", ".join(f"{code}×{cnt}" for code, cnt in counts.items())
                n_word = "entry" if len(codes) == 1 else "entries"
                print(f"{srv}: {len(codes)} {n_word} today ({detail})")
                printed = True
            if not printed:
                print("No lifecycle entries today.")

    elif action == "presets":
        as_json = "--json" in args
        if as_json:
            import json as _json
            payload = []
            for name, cfg in SERVERS.items():
                payload.append({
                    "name": name,
                    "mode": cfg["mode"],
                    "model_path": cfg["model_path"],
                    "default_port": cfg["default_port"],
                    "default": cfg.get("default", False),
                    "type": cfg["type"],
                    "required_for": cfg["required_for"],
                })
            print(_json.dumps(payload, indent=2))
        else:
            print(f"{'NAME':<18} {'MODE':<10} {'PORT':<6} {'DEF':<4} MODEL")
            print("-" * 100)
            for name, cfg in SERVERS.items():
                model_short = cfg["model_path"].rsplit("/", 1)[-1]
                default_mark = "yes" if cfg.get("default") else "-"
                print(f"{name:<18} {cfg['mode']:<10} {cfg['default_port']:<6} {default_mark:<4} {model_short}")

    else:
        print(f"Unknown action: {action}. Use: status, start, stop, restart, list, tail, errors, presets")


# Print table of all box-managed servers from state files
def _cli_list() -> None:
    state_files = sorted(TIMESTAMP_DIR.glob("server-port-*.json"))
    if not state_files:
        print("No managed servers")
        return

    rows = []
    for sf in state_files:
        try:
            state = json.loads(sf.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        log_path = Path(state.get("log_path", ""))
        try:
            idle_s = time.time() - log_path.stat().st_mtime
            idle_str = _format_idle(idle_s)
        except (FileNotFoundError, OSError):
            idle_str = "?"
        healthy = _check_health_port(state["port"])
        rows.append({
            "name":   state.get("name") or f"port-{state['port']}",
            "mode":   state.get("mode", "?"),
            "port":   state["port"],
            "pid":    state["pid"],
            "model":  state.get("model_name", "?"),
            "idle":   idle_str,
            "status": "healthy" if healthy else "unhealthy",
        })

    if not rows:
        print("No managed servers")
        return

    w_name  = max(4, max(len(r["name"])  for r in rows))
    w_mode  = max(4, max(len(r["mode"])  for r in rows))
    w_port  = 5
    w_pid   = max(3, max(len(str(r["pid"])) for r in rows))
    w_model = max(5, max(len(r["model"]) for r in rows))
    w_idle  = max(4, max(len(r["idle"])  for r in rows))

    header = (
        f"{'NAME':<{w_name}}  {'MODE':<{w_mode}}  {'PORT':<{w_port}}  "
        f"{'PID':<{w_pid}}  {'MODEL':<{w_model}}  {'IDLE':<{w_idle}}  STATUS"
    )
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['name']:<{w_name}}  {r['mode']:<{w_mode}}  {r['port']:<{w_port}}  "
            f"{r['pid']:<{w_pid}}  {r['model']:<{w_model}}  {r['idle']:<{w_idle}}  {r['status']}"
        )


# Format idle seconds as 'Xm YYs' (< 1h) or 'Xh YYm' (>= 1h)
def _format_idle(seconds: float) -> str:
    s = int(seconds)
    if s < 3600:
        m, sec = divmod(s, 60)
        return f"{m}m {sec:02d}s"
    h, rem = divmod(s, 3600)
    return f"{h}h {rem // 60:02d}m"


# Get value of --flag from an args list; returns None if not found
def _parse_flag(args: list[str], flag: str) -> str | None:
    try:
        idx = args.index(flag)
        return args[idx + 1]
    except (ValueError, IndexError):
        return None
