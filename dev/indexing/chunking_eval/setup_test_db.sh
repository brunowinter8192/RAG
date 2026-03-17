#!/usr/bin/env bash
# Creates rag_test database for chunking evaluation experiments.
# Prod DB (rag) is never touched.
set -euo pipefail

DB_NAME="${1:-rag_test}"
POSTGRES_PORT="${POSTGRES_PORT:-5433}"
POSTGRES_USER="${POSTGRES_USER:-rag}"

echo "Creating test database: $DB_NAME"
psql -h localhost -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database $DB_NAME already exists"
psql -h localhost -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -h localhost -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS sparsevec;" 2>/dev/null || echo "sparsevec extension not available separately (included in pgvector)"

echo "Test database $DB_NAME ready."
echo "Usage: POSTGRES_DB=$DB_NAME ./venv/bin/python dev/indexing/chunking_eval/chunking_sweep.py ..."
