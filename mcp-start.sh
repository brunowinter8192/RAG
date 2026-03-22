#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Bootstrap venv if missing
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
fi

# Start PostgreSQL if not running
if ! pg_isready -h localhost -p 5433 -q 2>/dev/null; then
    echo "Starting PostgreSQL..." >&2
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" up -d postgres
    sleep 3
fi

# GPU servers (embedding, reranker, splade) auto-start on demand via server_manager.py.
# MCP server works without them for list/read operations.

export POSTGRES_PORT="${POSTGRES_PORT:-5433}"
exec "$VENV_DIR/bin/fastmcp" run "$SCRIPT_DIR/server.py"
