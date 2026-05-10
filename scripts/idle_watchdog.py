#!/usr/bin/env python3
"""Idle watchdog — stop GPU servers that have been idle > IDLE_TIMEOUT seconds.

Designed to run every 15 minutes via launchd. Reads last-used timestamps
from ~/.rag-locks/rag-server-{name}-last-used and stops any server that
has been idle longer than the configured threshold.

Postgres is never stopped — only GPU servers (embedding, reranker, splade).
"""
import os
import sys
from pathlib import Path

# Make src.rag imports work regardless of cwd
_RAG_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_RAG_ROOT))

os.environ.setdefault("RAG_PROJECT_ROOT", str(_RAG_ROOT))

from src.rag.server_manager import SERVERS, IDLE_TIMEOUT, get_last_used, check_health, stop
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def main() -> None:
    now = time.time()
    for name in SERVERS:
        if not check_health(name):
            continue
        last_used = get_last_used(name)
        if last_used == 0:
            logging.info(f"{name}: never used, skipping")
            continue
        idle_secs = now - last_used
        if idle_secs > IDLE_TIMEOUT:
            mins = int(idle_secs // 60)
            logging.info(
                f"{name}: idle {mins}m > {IDLE_TIMEOUT // 60}m threshold — stopping"
            )
            stop(name)
        else:
            remaining = int((IDLE_TIMEOUT - idle_secs) // 60)
            logging.info(f"{name}: idle {int(idle_secs // 60)}m, {remaining}m until shutdown")


if __name__ == "__main__":
    main()
