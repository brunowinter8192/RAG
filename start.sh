#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting PostgreSQL..."
docker compose up -d postgres

echo "Waiting for PostgreSQL..."
sleep 3

echo "Starting llama.cpp embedding server (Metal GPU)..."
./llama.cpp/build/bin/llama-server \
  -m ./models/Qwen3-Embedding-8B-Q8_0.gguf \
  --embedding \
  --host 0.0.0.0 \
  --port 8081 \
  -ngl 99 \
  -ub 4096 \
  -b 4096

# Reranker server (optional — auto-started on first rerank query by reranker.py)
# Pre-start for faster first query:
# ./llama.cpp/build/bin/llama-server \
#   -m ./models/qwen3-reranker-0.6b-q8_0.gguf \
#   --rerank --host 0.0.0.0 --port 8082 -ngl 99 &
