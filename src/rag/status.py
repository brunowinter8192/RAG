# INFRASTRUCTURE
from datetime import datetime, timezone

import httpx

from .lock import read as read_lock
from .server_manager import SERVERS, get_last_used


# ORCHESTRATOR

def gather() -> dict:
    """Gather lock state, GPU server health, and Postgres reachability."""
    return {
        "lock": _lock_status(),
        "servers": _server_status(),
        "postgres": _postgres_status(),
    }


def format_status(info: dict) -> str:
    lines = []

    # Lock
    lock = info["lock"]
    if lock["held"]:
        d = lock["data"]
        elapsed_str = _elapsed(d["started_at"])
        heartbeat_str = _elapsed(d.get("heartbeat", d["started_at"]))
        prog = d.get("progress") or {}
        prog_str = ""
        if prog:
            prog_str = (
                f"\n         Progress: {prog['done']}/{prog['total']} chunks"
                f" — {prog['current_document']}"
            )
        stale_warn = ""
        if lock.get("stale_heartbeat"):
            stale_warn = " ⚠ heartbeat stale"
        lines.append(
            f"Lock:    HELD by PID {d['pid']} ({d['command']}) "
            f"since {elapsed_str} ago"
            f" [heartbeat: {heartbeat_str}{stale_warn}]{prog_str}"
        )
    else:
        lines.append("Lock:    FREE")

    lines.append("")

    # Servers
    lines.append("Servers:")
    for name, s in info["servers"].items():
        status = "RUNNING" if s["running"] else "STOPPED"
        health = "healthy" if s["healthy"] else ("unhealthy" if s["running"] else "—")
        last = f"  last_used: {s['last_used']}" if s["last_used"] else ""
        lines.append(f"  {name:<12} :{s['port']:<5} {status:<8} {health}{last}")

    lines.append("")

    # Postgres
    pg = info["postgres"]
    if pg["reachable"]:
        lines.append(f"Postgres:  REACHABLE (:{pg['port']})")
    else:
        lines.append(f"Postgres:  UNREACHABLE (:{pg['port']}) — {pg['error']}")

    return "\n".join(lines)


# FUNCTIONS

def _lock_status() -> dict:
    data = read_lock()
    if data is None:
        return {"held": False, "data": None, "stale_heartbeat": False}
    hb = data.get("heartbeat", data.get("started_at"))
    stale = False
    if hb:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(hb)).total_seconds()
        stale = age > 60
    return {"held": True, "data": data, "stale_heartbeat": stale}


def _server_status() -> dict:
    result = {}
    for name, cfg in SERVERS.items():
        running = _port_has_listener(cfg["port"])
        healthy = False
        if running:
            try:
                resp = httpx.get(cfg["health_url"], timeout=2.0)
                healthy = resp.status_code == 200
            except Exception:
                pass
        last_used = _format_last_used(get_last_used(name))
        result[name] = {
            "running": running,
            "healthy": healthy,
            "port": cfg["port"],
            "last_used": last_used,
        }
    return result


def _postgres_status() -> dict:
    from .db import POSTGRES_PORT
    import psycopg2
    from .db import POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST, port=POSTGRES_PORT,
            user=POSTGRES_USER, password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DB, connect_timeout=2,
        )
        conn.close()
        return {"reachable": True, "port": POSTGRES_PORT, "error": None}
    except Exception as e:
        return {"reachable": False, "port": POSTGRES_PORT, "error": str(e)}


def _port_has_listener(port: int) -> bool:
    import subprocess
    try:
        r = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True, timeout=3)
        return r.returncode == 0 and bool(r.stdout.strip())
    except Exception:
        return False


def _elapsed(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        secs = int((datetime.now(timezone.utc) - dt).total_seconds())
        if secs < 0:
            secs = 0
        mins, s = divmod(secs, 60)
        hrs, m = divmod(mins, 60)
        if hrs:
            return f"{hrs}h{m:02d}m"
        if mins:
            return f"{mins}m{s:02d}s"
        return f"{secs}s"
    except Exception:
        return "?"


def _format_last_used(ts: float) -> str:
    if ts == 0:
        return ""
    import time
    secs = int(time.time() - ts)
    if secs < 0:
        secs = 0
    mins, s = divmod(secs, 60)
    hrs, m = divmod(mins, 60)
    if hrs:
        return f"{hrs}h{m:02d}m ago"
    if mins:
        return f"{mins}m{s:02d}s ago"
    return f"{secs}s ago"
