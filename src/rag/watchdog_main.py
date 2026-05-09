# INFRASTRUCTURE
# Standalone watchdog entrypoint — spawned as detached process by _ensure_watchdog_process()

# ORCHESTRATOR
if __name__ == '__main__':
    from . import server_manager
    server_manager._watchdog_loop()
