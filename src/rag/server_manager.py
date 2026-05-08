# INFRASTRUCTURE
import json
import logging
import os
import signal
import socket
import subprocess
import threading
import time
from datetime import datetime, timezone
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

LLAMA_SERVER_PATH = os.getenv("LLAMA_SERVER_PATH", str(RAG_ROOT / "llama.cpp/build/bin/llama-server"))
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", str(RAG_ROOT / "models/Qwen3-Embedding-8B-Q8_0.gguf"))
RERANKER_MODEL_PATH = os.getenv("RERANKER_MODEL_PATH", str(RAG_ROOT / "models/qwen3-reranker-0.6b-q8_0.gguf"))

_watchdog_started = False
_watchdog_lock = threading.Lock()

SERVERS = {
    "embedding": {
        "cmd": [
            LLAMA_SERVER_PATH,
            "-m", EMBEDDING_MODEL_PATH,
            "--embedding", "--host", "0.0.0.0",
            "-ngl", "99", "-c", "2048", "-np", "1", "-b", "4096", "-ub", "4096",
        ],
        "timeout": 90,
        "required_for": ["search", "index"],
    },
    "reranker": {
        "cmd": [
            LLAMA_SERVER_PATH,
            "-m", RERANKER_MODEL_PATH,
            "--rerank", "--host", "0.0.0.0",
            "-ngl", "99", "-c", "32768", "-ub", "4096", "-b", "4096",
        ],
        "timeout": 90,
        "required_for": ["rerank"],
    },
    "splade": {
        "cmd": [
            str(RAG_ROOT / "venv/bin/python"), "-m", "uvicorn",
            "src.rag.splade_server:app", "--host", "0.0.0.0",
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
    for name in SERVERS:
        port = None
        pid = None
        running = False
        try:
            data = json.loads(_port_file(name).read_text())
            port = data.get("port")
            pid = data.get("pid")
            if pid:
                os.kill(pid, 0)
                running = True
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        except ProcessLookupError:
            _port_file(name).unlink(missing_ok=True)
        result[name] = {
            "running": running,
            "pid": pid if running else None,
            "port": port if running else None,
            "healthy": check_health(name) if running else False,
        }
    return result


# Start a server; returns True if started, False if already running
def start(name: str) -> bool:
    if name not in SERVERS:
        raise ValueError(f"Unknown server: {name}. Available: {list(SERVERS.keys())}")

    cfg = SERVERS[name]

    try:
        port = get_port(name)
        if check_health(name):
            logging.info(f"{name} already running on port {port}")
            return False
        logging.warning(f"{name} on port {port} unhealthy, stopping before restart")
        stop(name)
    except RuntimeError:
        pass

    binary = Path(cfg["cmd"][0])
    if not binary.exists():
        raise RuntimeError(
            f"Cannot start {name}: {binary} not found. "
            f"Start GPU servers from the RAG project: cd <RAG_ROOT> && ./start.sh"
        )

    for attempt in range(1, 4):
        # Small race window between socket close and subprocess bind — acceptable for personal use
        port = _get_free_port()
        cmd = cfg["cmd"] + ["--port", str(port)]
        logging.info(f"Starting {name} on port {port} (attempt {attempt}/3)...")
        cwd = cfg.get("cwd", None)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=cwd,
        )

        started = False
        for i in range(cfg["timeout"]):
            time.sleep(1)
            if proc.poll() is not None:
                logging.warning(f"{name} process exited on attempt {attempt} after {i+1}s")
                break
            try:
                resp = httpx.get(f"http://localhost:{port}/health", timeout=2.0)
                if resp.status_code == 200:
                    _write_port_file(name, port, proc.pid)
                    logging.info(f"{name} started on port {port} (PID {proc.pid}) after {i+1}s")
                    started = True
                    break
            except Exception:
                pass

        if started:
            return True

        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        logging.warning(f"{name} failed on port {port} (attempt {attempt}/3)")

    raise RuntimeError(f"Failed to start {name} after 3 attempts")


# Stop a server via port file PID; returns True if stopped, False if not running
def stop(name: str) -> bool:
    if name not in SERVERS:
        raise ValueError(f"Unknown server: {name}. Available: {list(SERVERS.keys())}")

    f = _port_file(name)
    try:
        data = json.loads(f.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info(f"{name} not running (no port file)")
        return False

    pid = data.get("pid")
    port = data.get("port")

    pids = set(find_all_pids_on_port(port)) if port else set()
    if pid:
        pids.add(pid)

    if not pids:
        f.unlink(missing_ok=True)
        return False

    logging.info(f"Stopping {name} (PIDs {pids}) on port {port}...")
    for p in pids:
        try:
            os.kill(p, signal.SIGTERM)
        except ProcessLookupError:
            pass

    for _ in range(10):
        time.sleep(0.5)
        if port and not find_all_pids_on_port(port):
            break

    for p in (set(find_all_pids_on_port(port)) if port else set()):
        try:
            os.kill(p, signal.SIGKILL)
            logging.warning(f"{name} force-killed (PID {p})")
        except ProcessLookupError:
            pass

    f.unlink(missing_ok=True)
    logging.info(f"{name} stopped")
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
    if target in SERVERS:
        if not check_health(target):
            start(target)
        touch_timestamp(target)
        _ensure_watchdog()
        return

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


# FUNCTIONS

# Check if a server responds to its health endpoint
def check_health(name: str) -> bool:
    try:
        port = get_port(name)
    except RuntimeError:
        return False
    try:
        resp = httpx.get(f"http://localhost:{port}/health", timeout=2.0)
        return resp.status_code == 200
    except Exception as e:
        logging.warning(f"Health check failed for {name}: {e}")
        return False


# Read port from port file; raise RuntimeError if missing or stale (cleans up stale file)
def get_port(name: str) -> int:
    f = _port_file(name)
    try:
        data = json.loads(f.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        raise RuntimeError(f"{name} server not running (no port file)")
    pid = data.get("pid")
    if pid:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            f.unlink(missing_ok=True)
            raise RuntimeError(f"{name} server dead (stale port file cleaned up)")
    return data["port"]


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
    TIMESTAMP_DIR.mkdir(parents=True, exist_ok=True)
    ts_file = TIMESTAMP_DIR / f"rag-server-{name}-last-used"
    ts_file.write_text(str(time.time()))


# Read last-used timestamp for a server; returns 0.0 if never used
def get_last_used(name: str) -> float:
    ts_file = TIMESTAMP_DIR / f"rag-server-{name}-last-used"
    try:
        return float(ts_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def _port_file(name: str) -> Path:
    return TIMESTAMP_DIR / f"rag-server-{name}.port"


def _get_free_port() -> int:
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def _write_port_file(name: str, port: int, pid: int) -> None:
    TIMESTAMP_DIR.mkdir(parents=True, exist_ok=True)
    data = {"port": port, "pid": pid, "started_at": datetime.now(timezone.utc).isoformat()}
    tmp = _port_file(name).with_suffix(".tmp")
    tmp.write_text(json.dumps(data))
    tmp.rename(_port_file(name))


# Start the idle-timeout watchdog thread if not already running
def _ensure_watchdog() -> None:
    global _watchdog_started
    with _watchdog_lock:
        if _watchdog_started:
            return
        _watchdog_started = True

    thread = threading.Thread(target=_watchdog_loop, daemon=True)
    thread.start()
    logging.info(f"Watchdog started (idle timeout: {IDLE_TIMEOUT}s)")


# Background loop that stops servers idle beyond IDLE_TIMEOUT
def _watchdog_loop() -> None:
    while True:
        time.sleep(WATCHDOG_INTERVAL)
        now = time.time()
        for name in SERVERS:
            try:
                get_port(name)
            except RuntimeError:
                continue
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
        print(f"{'Server':<12} {'Port':<8} {'Status':<10} {'PID':<8} {'Healthy'}")
        print("-" * 52)
        for name, info in st.items():
            status_str = "RUNNING" if info["running"] else "STOPPED"
            port_str = str(info["port"]) if info["port"] else "-"
            pid_str = str(info["pid"]) if info["pid"] else "-"
            health_str = "YES" if info["healthy"] else "NO"
            print(f"{name:<12} {port_str:<8} {status_str:<10} {pid_str:<8} {health_str}")

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
