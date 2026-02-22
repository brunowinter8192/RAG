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

# Start llama.cpp embedding server if not running
if ! curl -s http://localhost:8081/health >/dev/null 2>&1; then
    echo "Starting llama.cpp embedding server..." >&2
    mkdir -p "$SCRIPT_DIR/logs"
    "$SCRIPT_DIR/llama.cpp/build/bin/llama-server" \
        -m "$SCRIPT_DIR/models/Qwen3-Embedding-8B-Q8_0.gguf" \
        --embedding --host 0.0.0.0 --port 8081 \
        -ngl 99 -ub 4096 -b 4096 \
        > "$SCRIPT_DIR/logs/llama-server.log" 2>&1 &
    for i in $(seq 1 30); do
        curl -s http://localhost:8081/health >/dev/null 2>&1 && break
        sleep 1
    done
fi

exec "$VENV_DIR/bin/fastmcp" run "$SCRIPT_DIR/server.py"
