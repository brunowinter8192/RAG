# INFRASTRUCTURE
# Coordinator: re-exports full public surface so all callers are unchanged.
# Defines ensure_ready (composes lifecycle + watchdog) and status (aggregate view).
# All server logic lives in server_utils / server_lifecycle / watchdog / server_cli.

from .server_utils import (
    SERVERS, _CLASS_MAP, _MODE_TO_CLASS, _PRESET_NAMES,
    TIMESTAMP_DIR, WATCHDOG_PID_FILE, IDLE_TIMEOUT, WATCHDOG_INTERVAL,
    RAG_ROOT, LLAMA_SERVER_PATH, LOG_DIR,
    find_pid_on_port, find_all_pids_on_port, pgrep_llama_server,
    _pid_alive, _check_health_port, _allocate_port, _resolve_port,
    _stop_by_state, _write_state_file, _unlink_state_file, _touch_state_file,
)
from .server_lifecycle import (
    start, stop, restart, start_arbitrary,
    _resolve_class_to_default, start_all, stop_all,
    find_server_url, check_health, status,
    _build_llama_cmd, _build_uvicorn_cmd,
)
from .watchdog import _ensure_watchdog_process, _watchdog_loop
from .server_cli import cli_server


# ORCHESTRATOR

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
        cls = _MODE_TO_CLASS.get(SERVERS[name]["mode"], SERVERS[name]["mode"])
        if any(check_health(v) for v in _CLASS_MAP.get(cls, [name])):
            continue
        start(name)

    _ensure_watchdog_process()
