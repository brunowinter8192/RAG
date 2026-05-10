# INFRASTRUCTURE
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx

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
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", str(RAG_ROOT / "models/Qwen3-Embedding-8B-Q8_0.gguf"))
EMBEDDING_PORT = int(os.getenv("EMBEDDING_PORT", "8081"))
RERANKER_MODEL_PATH = os.getenv("RERANKER_MODEL_PATH", str(RAG_ROOT / "models/qwen3-reranker-0.6b-q8_0.gguf"))
RERANKER_PORT = int(os.getenv("RERANKER_PORT", "8082"))
SPLADE_PORT = int(os.getenv("SPLADE_PORT", "8083"))
SPLADE_MODEL = "naver/splade-v3"

SERVERS = {
    "embedding": {
        "port": EMBEDDING_PORT,
        "health_url": f"http://localhost:{EMBEDDING_PORT}/health",
        "cmd": [
            LLAMA_SERVER_PATH,
            "-m", EMBEDDING_MODEL_PATH,
            "--embedding", "--host", "0.0.0.0", "--port", str(EMBEDDING_PORT),
            "-ngl", "99", "-c", "2048", "-np", "1", "-b", "4096", "-ub", "4096",
        ],
        "timeout": 90,
        "required_for": ["search", "index"],
    },
    "reranker": {
        "port": RERANKER_PORT,
        "health_url": f"http://localhost:{RERANKER_PORT}/health",
        "cmd": [
            LLAMA_SERVER_PATH,
            "-m", RERANKER_MODEL_PATH,
            "--rerank", "--host", "0.0.0.0", "--port", str(RERANKER_PORT),
            "-ngl", "99", "-c", "32768", "-ub", "4096", "-b", "4096",
        ],
        "timeout": 90,
        "required_for": ["rerank"],
    },
    "splade": {
        "port": SPLADE_PORT,
        "health_url": f"http://localhost:{SPLADE_PORT}/health",
        "cmd": [
            str(RAG_ROOT / "venv/bin/python"), "-m", "uvicorn",
            "src.rag.splade_server:app", "--host", "0.0.0.0", "--port", str(SPLADE_PORT),
        ],
        "cwd": str(RAG_ROOT),
        "timeout": 60,
        "required_for": ["search", "index"],
    },
}


# ORCHESTRATOR

# Return status of all servers: running, pid, port, healthy per server name
def status() -> dict[str, dict]:
    result = {}
    for name, cfg in SERVERS.items():
        pid = find_pid_on_port(cfg["port"])
        result[name] = {
            "running": pid is not None,
            "pid": pid,
            "port": cfg["port"],
            "healthy": check_health(name) if pid else False,
        }
    return result


# Start a preset server; log-redirected, state file written immediately after Popen
def start(name: str) -> bool:
    if name not in SERVERS:
        raise ValueError(f"Unknown server: {name}. Available: {list(SERVERS.keys())}")

    cfg = SERVERS[name]
    pid = find_pid_on_port(cfg["port"])
    if pid is not None:
        if check_health(name):
            logging.info(f"{name} already running on port {cfg['port']} (PID {pid})")
            return False
        logging.warning(f"{name} port {cfg['port']} occupied by PID {pid} but unhealthy, killing")
        stop(name)

    binary = Path(cfg["cmd"][0])
    if not binary.exists():
        raise RuntimeError(
            f"Cannot start {name}: {binary} not found. "
            f"Start GPU servers from the RAG project: cd <RAG_ROOT> && ./start.sh"
        )

    logging.info(f"Starting {name} on port {cfg['port']}...")
    cwd = cfg.get("cwd", None)

    # Splade writes via Python logging to splade_server.log — do not redirect stdout
    if name == "splade":
        log_path = LOG_DIR / "splade_server.log"
        log_fh = subprocess.DEVNULL
        log_stderr = subprocess.DEVNULL
    else:
        log_path = LOG_DIR / f"llama-port-{cfg['port']}.log"
        log_fh = open(log_path, "w")
        log_stderr = subprocess.STDOUT

    proc = subprocess.Popen(cfg["cmd"], stdout=log_fh, stderr=log_stderr, cwd=cwd)
    if log_fh is not subprocess.DEVNULL:
        log_fh.close()  # parent closes; child retains its fd copy

    model_path, model_name = _extract_model_info(cfg["cmd"], name)
    _write_state_file(
        pid=proc.pid, port=cfg["port"],
        model_path=model_path, model_name=model_name,
        mode=_mode_for_preset(name),
        name=name,
        log_path=str(log_path),
    )

    timeout = cfg["timeout"]
    try:
        for i in range(timeout):
            time.sleep(1)
            if check_health(name):
                actual_pid = find_pid_on_port(cfg["port"])
                # Rare on macOS: shell-wrapped cmd may have a different listening PID than proc.pid
                if actual_pid is not None and actual_pid != proc.pid:
                    _write_state_file(
                        pid=actual_pid, port=cfg["port"],
                        model_path=model_path, model_name=model_name,
                        mode=_mode_for_preset(name),
                        name=name,
                        log_path=str(log_path),
                    )
                logging.info(
                    f"{name} started on port {cfg['port']} "
                    f"(PID {actual_pid or proc.pid}) after {i + 1}s"
                )
                return True
        raise RuntimeError(f"Failed to start {name} after {timeout}s")
    except Exception:
        _unlink_state_file(cfg["port"])
        raise


# Stop a server; kills ALL processes on the port; unlinks state file on success
def stop(name: str) -> bool:
    if name not in SERVERS:
        raise ValueError(f"Unknown server: {name}. Available: {list(SERVERS.keys())}")

    cfg = SERVERS[name]
    pids = find_all_pids_on_port(cfg["port"])
    if not pids:
        logging.info(f"{name} not running on port {cfg['port']}")
        return False

    logging.info(f"Stopping {name} (PIDs {pids}) on port {cfg['port']}...")
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    for _ in range(10):
        time.sleep(0.5)
        remaining = find_all_pids_on_port(cfg["port"])
        if not remaining:
            logging.info(f"{name} stopped")
            _unlink_state_file(cfg["port"])
            return True

    for pid in find_all_pids_on_port(cfg["port"]):
        try:
            os.kill(pid, signal.SIGKILL)
            logging.warning(f"{name} force-killed (PID {pid})")
        except ProcessLookupError:
            pass
    _unlink_state_file(cfg["port"])
    return True


# Restart a server
def restart(name: str) -> bool:
    stop(name)
    return start(name)


# Start all servers; returns name → 'started'|'already_running'|'error: ...'
def start_all() -> dict[str, str]:
    results = {}
    for name in SERVERS:
        try:
            started = start(name)
            results[name] = "started" if started else "already_running"
        except Exception as e:
            results[name] = f"error: {e}"
    return results


# Stop all servers; returns name → 'stopped'|'not_running'
def stop_all() -> dict[str, str]:
    results = {}
    for name in SERVERS:
        stopped = stop(name)
        results[name] = "stopped" if stopped else "not_running"
    return results


# Ensure server(s) for a name or operation are running, starting if needed
def ensure_ready(target: str) -> None:
    # Direct server name
    if target in SERVERS:
        if not check_health(target):
            start(target)
        touch_timestamp(target)
        _ensure_watchdog_process()
        return

    # Operation-based lookup
    if target == "search_rerank":
        needed_ops = ["search", "rerank"]
    else:
        needed_ops = [target]

    needed_servers = set()
    for op in needed_ops:
        for name, cfg in SERVERS.items():
            if op in cfg["required_for"]:
                needed_servers.add(name)

    for name in needed_servers:
        if not check_health(name):
            start(name)
        touch_timestamp(name)

    _ensure_watchdog_process()


# FUNCTIONS

# Check if a server responds to its health endpoint
def check_health(name: str) -> bool:
    cfg = SERVERS[name]
    try:
        resp = httpx.get(cfg["health_url"], timeout=2.0)
        return resp.status_code == 200
    except Exception as e:
        logging.warning(f"Health check failed: {e}")
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


# Write last-used timestamp for a server to a temp file (migration compat — kept for GPU pane)
def touch_timestamp(name: str) -> None:
    ts_file = TIMESTAMP_DIR / f"rag-server-{name}-last-used"
    ts_file.write_text(str(time.time()))


# Read last-used timestamp for a server; returns 0.0 if never used (migration compat)
def get_last_used(name: str) -> float:
    ts_file = TIMESTAMP_DIR / f"rag-server-{name}-last-used"
    try:
        return float(ts_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


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
            _stop_by_state(state, state_file)


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
    for pid in orphan_pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    logging.info(f"Watchdog purge: killed {n_orphans} orphan llama-server PID(s)")


# Return PIDs of all running llama-server processes via pgrep
def pgrep_llama_server() -> list[int]:
    try:
        result = subprocess.run(
            ["pgrep", "-f", "llama-server"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return [int(p) for p in result.stdout.strip().split("\n") if p.strip()]
    except Exception:
        pass
    return []


# Health check by port (no SERVERS lookup — works for preset and arbitrary servers)
def _check_health_port(port: int) -> bool:
    try:
        return httpx.get(f"http://localhost:{port}/health", timeout=2.0).status_code == 200
    except Exception:
        return False


# SIGTERM → wait → SIGKILL a server described by its state dict; unlinks state file
def _stop_by_state(state: dict, state_file: Path) -> None:
    pid, port = state["pid"], state["port"]
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        state_file.unlink(missing_ok=True)
        return
    for _ in range(10):
        time.sleep(0.5)
        if not _pid_alive(pid):
            state_file.unlink(missing_ok=True)
            return
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    state_file.unlink(missing_ok=True)


# Return True if the process is alive (os.kill(pid, 0) succeeds)
def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


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


# Remove state file for a port; safe if never written or already gone
def _unlink_state_file(port: int) -> None:
    path = TIMESTAMP_DIR / f"server-port-{port}.json"
    path.unlink(missing_ok=True)


# Extract (model_path, model_name) from a preset's cmd list
def _extract_model_info(cmd: list[str], name: str) -> tuple[str, str]:
    if name == "splade":
        return SPLADE_MODEL, SPLADE_MODEL
    # llama-server presets: cmd[0]=binary, cmd[1]="-m", cmd[2]=model_path
    model_path = cmd[2]
    return model_path, Path(model_path).stem


# Map preset name to mode string stored in state file
def _mode_for_preset(name: str) -> str:
    return {"embedding": "embedding", "reranker": "rerank", "splade": "splade"}.get(name, "unknown")


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
        if target:
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
        if target:
            stopped = stop(target)
            print(f"{target}: {'stopped' if stopped else 'not running'}")
        else:
            results = stop_all()
            for name, result in results.items():
                print(f"{name}: {result}")

    elif action == "restart":
        if target:
            restart(target)
            print(f"{target}: restarted")
        else:
            stop_all()
            results = start_all()
            for name, result in results.items():
                print(f"{name}: {result}")

    else:
        print(f"Unknown action: {action}. Use: status, start, stop, restart")
