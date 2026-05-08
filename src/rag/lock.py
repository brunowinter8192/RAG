# INFRASTRUCTURE
import contextlib
import fcntl
import json
import os
import pathlib
from datetime import datetime, timezone

LOCK_DIR = pathlib.Path.home() / ".rag-locks"
_FLOCK_FILE = LOCK_DIR / "rag.flock"   # held open while lock is active
_DATA_FILE = LOCK_DIR / "rag.lock"     # JSON details (written atomically)


class LockBusyError(RuntimeError):
    pass


# ORCHESTRATOR

@contextlib.contextmanager
def acquire(command: str, args: dict):
    """Acquire the global RAG lock. Raises LockBusyError if held by another process."""
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    cleanup_stale()

    fd = open(_FLOCK_FILE, "a")
    try:
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fd.close()
        _raise_busy()

    data = {
        "pid": os.getpid(),
        "command": command,
        "args": args,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "progress": {},
        "heartbeat": datetime.now(timezone.utc).isoformat(),
    }
    _write_atomic(data)

    try:
        yield
    finally:
        try:
            _DATA_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
        fd.close()


# FUNCTIONS

def update_progress(done: int, total: int, current_document: str) -> None:
    data = read()
    if data is None:
        return
    data["progress"] = {"done": done, "total": total, "current_document": current_document}
    data["heartbeat"] = datetime.now(timezone.utc).isoformat()
    _write_atomic(data)


def heartbeat() -> None:
    data = read()
    if data is None:
        return
    data["heartbeat"] = datetime.now(timezone.utc).isoformat()
    _write_atomic(data)


def read() -> dict | None:
    try:
        return json.loads(_DATA_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def cleanup_stale() -> bool:
    """Remove lockfile if the owning PID is no longer alive. Returns True if cleaned up."""
    data = read()
    if data is None:
        return False
    pid = data.get("pid")
    if pid is None:
        _DATA_FILE.unlink(missing_ok=True)
        return True
    try:
        os.kill(pid, 0)
        return False
    except ProcessLookupError:
        _DATA_FILE.unlink(missing_ok=True)
        return True
    except PermissionError:
        return False


def _raise_busy() -> None:
    info = read()
    if info is None:
        raise LockBusyError("rag busy: lock held but details unavailable")
    started = datetime.fromisoformat(info["started_at"])
    elapsed = int((datetime.now(timezone.utc) - started).total_seconds())
    mins, secs = divmod(elapsed, 60)
    elapsed_str = f"{mins}m{secs:02d}s" if mins else f"{secs}s"
    prog = info.get("progress") or {}
    prog_str = ""
    if prog:
        prog_str = f", progress {prog['done']}/{prog['total']} ({prog['current_document']})"
    collection = info.get("args", {}).get("collection") or info.get("args", {}).get("input", "?")
    raise LockBusyError(
        f"rag busy: {info['command']} running"
        f" (collection: {collection})"
        f" since {elapsed_str} ago, PID {info['pid']}{prog_str}"
    )


def _write_atomic(data: dict) -> None:
    tmp = _DATA_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.rename(_DATA_FILE)
