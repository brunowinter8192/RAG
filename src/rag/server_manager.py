# INFRASTRUCTURE
import logging
import os
import signal
import subprocess
import threading
import time
from pathlib import Path

import httpx

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
RAG_ROOT = Path(__file__).parent.parent.parent

logging.basicConfig(
    filename=LOG_DIR / "server_manager.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

IDLE_TIMEOUT = int(os.getenv("RAG_SERVER_IDLE_TIMEOUT", "300"))  # 5 minutes default
TIMESTAMP_DIR = Path("/tmp")
WATCHDOG_INTERVAL = 30  # seconds between idle checks

_watchdog_started = False
_watchdog_lock = threading.Lock()


# SERVER DEFINITIONS — Single Source of Truth
SERVERS = {
    "embedding": {
        "port": 8081,
        "health_url": "http://localhost:8081/health",
        "cmd": [
            str(RAG_ROOT / "llama.cpp/build/bin/llama-server"),
            "-m", str(RAG_ROOT / "models/Qwen3-Embedding-8B-Q8_0.gguf"),
            "--embedding", "--host", "0.0.0.0", "--port", "8081",
            "-ngl", "99", "-c", "2048", "-np", "1", "-b", "4096", "-ub", "4096",
        ],
        "timeout": 90,
        "required_for": ["search", "index"],
    },
    "reranker": {
        "port": 8082,
        "health_url": "http://localhost:8082/health",
        "cmd": [
            str(RAG_ROOT / "llama.cpp/build/bin/llama-server"),
            "-m", str(RAG_ROOT / "models/qwen3-reranker-0.6b-q8_0.gguf"),
            "--rerank", "--host", "0.0.0.0", "--port", "8082",
            "-ngl", "99", "-c", "32768", "-ub", "4096", "-b", "4096",
        ],
        "timeout": 90,
        "required_for": ["rerank"],
    },
    "splade": {
        "port": 8083,
        "health_url": "http://localhost:8083/health",
        "cmd": [
            str(RAG_ROOT / "venv/bin/python"), "-m", "uvicorn",
            "src.rag.splade_server:app", "--host", "0.0.0.0", "--port", "8083",
        ],
        "cwd": str(RAG_ROOT),
        "timeout": 60,
        "required_for": ["search", "index"],
    },
}


# PUBLIC API

def status() -> dict[str, dict]:
    """Return status of all servers: {name: {running, pid, port}}."""
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


def start(name: str) -> bool:
    """Start a server. Returns True if started, False if already running."""
    if name not in SERVERS:
        raise ValueError(f"Unknown server: {name}. Available: {list(SERVERS.keys())}")

    cfg = SERVERS[name]
    pid = find_pid_on_port(cfg["port"])
    if pid is not None:
        if check_health(name):
            logging.info(f"{name} already running on port {cfg['port']} (PID {pid})")
            return False
        # Port occupied but unhealthy — kill stale process
        logging.warning(f"{name} port {cfg['port']} occupied by PID {pid} but unhealthy, killing")
        stop(name)

    logging.info(f"Starting {name} on port {cfg['port']}...")
    cwd = cfg.get("cwd", None)
    subprocess.Popen(
        cfg["cmd"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=cwd,
    )

    # Wait for health
    timeout = cfg["timeout"]
    for i in range(timeout):
        time.sleep(1)
        if check_health(name):
            pid = find_pid_on_port(cfg["port"])
            logging.info(f"{name} started on port {cfg['port']} (PID {pid}) after {i+1}s")
            return True

    raise RuntimeError(f"Failed to start {name} after {timeout}s")


def stop(name: str) -> bool:
    """Stop a server. Kills ALL processes on the port. Returns True if stopped, False if not running."""
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

    # Wait for all processes to exit
    for _ in range(10):
        time.sleep(0.5)
        remaining = find_all_pids_on_port(cfg["port"])
        if not remaining:
            logging.info(f"{name} stopped")
            return True

    # Force kill remaining
    for pid in find_all_pids_on_port(cfg["port"]):
        try:
            os.kill(pid, signal.SIGKILL)
            logging.warning(f"{name} force-killed (PID {pid})")
        except ProcessLookupError:
            pass
    return True


def restart(name: str) -> bool:
    """Restart a server."""
    stop(name)
    return start(name)


def start_all() -> dict[str, str]:
    """Start all servers. Returns {name: 'started'|'already_running'|'error: ...'}."""
    results = {}
    for name in SERVERS:
        try:
            started = start(name)
            results[name] = "started" if started else "already_running"
        except Exception as e:
            results[name] = f"error: {e}"
    return results


def stop_all() -> dict[str, str]:
    """Stop all servers. Returns {name: 'stopped'|'not_running'}."""
    results = {}
    for name in SERVERS:
        stopped = stop(name)
        results[name] = "stopped" if stopped else "not_running"
    return results


def ensure_ready(target: str) -> None:
    """Ensure server(s) are running. Accepts server name or operation.

    Server names: 'embedding', 'reranker', 'splade' — starts that specific server.
    Operations: 'search' (embedding + splade), 'index' (embedding + splade),
                'rerank' (reranker), 'search_rerank' (embedding + splade + reranker)
    """
    # Direct server name
    if target in SERVERS:
        if not check_health(target):
            start(target)
        touch_timestamp(target)
        _ensure_watchdog()
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

    _ensure_watchdog()


# INTERNAL FUNCTIONS

def check_health(name: str) -> bool:
    """Check if a server responds to health check."""
    cfg = SERVERS[name]
    try:
        resp = httpx.get(cfg["health_url"], timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


def find_pid_on_port(port: int) -> int | None:
    """Find the PID of the process listening on a port. Returns None if port is free."""
    pids = find_all_pids_on_port(port)
    return pids[0] if pids else None


def find_all_pids_on_port(port: int) -> list[int]:
    """Find all PIDs listening on a port."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return [int(p) for p in result.stdout.strip().split("\n") if p.strip()]
    except Exception:
        pass
    return []


def touch_timestamp(name: str) -> None:
    """Update the last-used timestamp file for a server."""
    ts_file = TIMESTAMP_DIR / f"rag-server-{name}-last-used"
    ts_file.write_text(str(time.time()))


def get_last_used(name: str) -> float:
    """Get the last-used timestamp for a server. Returns 0 if never used."""
    ts_file = TIMESTAMP_DIR / f"rag-server-{name}-last-used"
    try:
        return float(ts_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def _ensure_watchdog() -> None:
    """Start the idle-timeout watchdog thread if not already running."""
    global _watchdog_started
    with _watchdog_lock:
        if _watchdog_started:
            return
        _watchdog_started = True

    thread = threading.Thread(target=_watchdog_loop, daemon=True)
    thread.start()
    logging.info(f"Watchdog started (idle timeout: {IDLE_TIMEOUT}s)")


def _watchdog_loop() -> None:
    """Background loop that stops idle servers."""
    while True:
        time.sleep(WATCHDOG_INTERVAL)
        now = time.time()
        for name, cfg in SERVERS.items():
            if not check_health(name):
                continue
            last_used = get_last_used(name)
            if last_used == 0:
                continue
            idle_seconds = now - last_used
            if idle_seconds > IDLE_TIMEOUT:
                logging.info(f"Watchdog: {name} idle for {idle_seconds:.0f}s (>{IDLE_TIMEOUT}s), stopping")
                stop(name)


# CLI ENTRY POINT (called from workflow.py)

def cli_server(args: list[str]) -> None:
    """Handle 'workflow.py server' subcommand."""
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
