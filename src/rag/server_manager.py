# INFRASTRUCTURE
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

IDLE_TIMEOUT = int(os.getenv("RAG_SERVER_IDLE_TIMEOUT", "900"))
TIMESTAMP_DIR = Path("/tmp")
WATCHDOG_INTERVAL = 30
WATCHDOG_PID_FILE = Path.home() / ".rag-locks" / "watchdog.pid"

LLAMA_SERVER_PATH = os.getenv("LLAMA_SERVER_PATH", str(RAG_ROOT / "llama.cpp/build/bin/llama-server"))
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", str(RAG_ROOT / "models/Qwen3-Embedding-8B-Q8_0.gguf"))
EMBEDDING_PORT = int(os.getenv("EMBEDDING_PORT", "8081"))
RERANKER_MODEL_PATH = os.getenv("RERANKER_MODEL_PATH", str(RAG_ROOT / "models/qwen3-reranker-0.6b-q8_0.gguf"))
RERANKER_PORT = int(os.getenv("RERANKER_PORT", "8082"))
SPLADE_PORT = int(os.getenv("SPLADE_PORT", "8083"))

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


# Start a server; returns True if started, False if already running
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
    subprocess.Popen(
        cfg["cmd"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=cwd,
    )

    timeout = cfg["timeout"]
    for i in range(timeout):
        time.sleep(1)
        if check_health(name):
            pid = find_pid_on_port(cfg["port"])
            logging.info(f"{name} started on port {cfg['port']} (PID {pid}) after {i+1}s")
            return True

    raise RuntimeError(f"Failed to start {name} after {timeout}s")


# Stop a server; kills ALL processes on the port; returns True if stopped, False if not running
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
            return True

    for pid in find_all_pids_on_port(cfg["port"]):
        try:
            os.kill(pid, signal.SIGKILL)
            logging.warning(f"{name} force-killed (PID {pid})")
        except ProcessLookupError:
            pass
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


# Write last-used timestamp for a server to a temp file
def touch_timestamp(name: str) -> None:
    ts_file = TIMESTAMP_DIR / f"rag-server-{name}-last-used"
    ts_file.write_text(str(time.time()))


# Read last-used timestamp for a server; returns 0.0 if never used
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


# Background loop that stops servers idle beyond IDLE_TIMEOUT
def _watchdog_loop() -> None:
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


# Handle 'workflow.py server' subcommand
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
