#!/bin/bash
cd "$(dirname "$0")/.."
./venv/bin/python -m uvicorn src.rag.splade_server:app --host 0.0.0.0 --port 8083
