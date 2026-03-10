#!/usr/bin/env python3

# INFRASTRUCTURE
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

RAG_ROOT = Path(__file__).parent.parent.parent
LLAMA_SERVER = RAG_ROOT / "llama.cpp/build/bin/llama-server"
MODEL_PATH = RAG_ROOT / "models/qwen3-reranker-0.6b-q8_0.gguf"
LOG_DIR = Path(__file__).parent / "01_server_logs"
HEALTH_URL = "http://localhost:8082/health"
PORT = "8082"

_log_files = []


# ORCHESTRATOR
def main():
    LOG_DIR.mkdir(exist_ok=True)
    kill_existing_server()
    proc = start_server()
    wait_for_health(proc)
    print(f"\nServer PID: {proc.pid}")
    print(f"Logs: {LOG_DIR.name}/")
    print("Press Ctrl+C to stop server")
    wait_for_interrupt(proc)


# FUNCTIONS

# Kill any existing process on port 8082
def kill_existing_server():
    result = subprocess.run(
        ["lsof", "-ti", f":{PORT}"],
        capture_output=True, text=True
    )
    pids = result.stdout.strip()
    if pids:
        for pid in pids.split("\n"):
            print(f"Killing existing server (PID {pid})")
            subprocess.run(["kill", "-9", pid])
        time.sleep(1)


# Start llama-server with stderr capture (same flags as reranker.py:77-85)
def start_server():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stderr_log = LOG_DIR / f"stderr_{ts}.log"
    stdout_log = LOG_DIR / f"stdout_{ts}.log"

    cmd = [
        str(LLAMA_SERVER),
        "-m", str(MODEL_PATH),
        "--rerank",
        "--host", "0.0.0.0",
        "--port", PORT,
        "-ngl", "99",
        "-c", "32768",
    ]

    print(f"Starting: {' '.join(cmd)}")
    print(f"stderr -> {stderr_log.name}")
    print(f"stdout -> {stdout_log.name}")

    stderr_f = open(stderr_log, "w")
    stdout_f = open(stdout_log, "w")
    _log_files.extend([stderr_f, stdout_f])

    return subprocess.Popen(cmd, stdout=stdout_f, stderr=stderr_f)


# Wait for health endpoint to respond
def wait_for_health(proc, timeout=30):
    print("Waiting for health check...", end="", flush=True)
    for _ in range(timeout):
        if proc.poll() is not None:
            print(f"\nServer exited with code {proc.returncode}")
            print("Check stderr log for details")
            sys.exit(1)
        try:
            resp = httpx.get(HEALTH_URL, timeout=2.0)
            if resp.status_code == 200:
                print(" ready")
                return
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(1)
    print(f"\nTimeout after {timeout}s")
    sys.exit(1)


# Wait for Ctrl+C, then cleanup
def wait_for_interrupt(proc):
    def handler(_sig, _frame):
        print("\nStopping server...")
        proc.terminate()
        proc.wait(timeout=5)
        for f in _log_files:
            f.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    proc.wait()


if __name__ == "__main__":
    main()
