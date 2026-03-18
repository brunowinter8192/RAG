"""SPLADE server nnz monitor — tracks sparse vector density over time.

Periodically sends a fixed reference text to the running SPLADE server and logs
the non-zero element count (nnz). Goal: isolate the trigger for nnz explosion
(time-based? request-count-based? memory-pressure-based?).

Writes results to CSV for later analysis.

Usage:
    # Monitor every 2 minutes (default), write to CSV
    ./venv/bin/python dev/indexing/splade_truncation/monitor.py

    # Custom interval (seconds) and output path
    ./venv/bin/python dev/indexing/splade_truncation/monitor.py --interval 60 --output /tmp/splade_monitor.csv

    # Single probe (no loop)
    ./venv/bin/python dev/indexing/splade_truncation/monitor.py --once
"""
import argparse
import csv
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

SPLADE_URL = os.getenv("SPLADE_URL", "http://localhost:8083/v1/sparse-embeddings")

# Fixed reference text — should produce ~100-200 nnz under normal conditions
REFERENCE_TEXT = (
    "Information retrieval systems use sparse and dense representations to match "
    "queries with relevant documents. SPLADE models produce sparse lexical vectors "
    "by applying log-saturation to masked language model logits, resulting in "
    "interpretable term-level importance weights."
)

DEFAULT_OUTPUT = Path(__file__).parent / "monitor_results.csv"
CSV_FIELDS = [
    "timestamp", "nnz", "top5_values", "top5_tokens",
    "system_memory_pct", "process_rss_mb", "splade_pid",
    "elapsed_minutes", "probe_count",
]


def find_splade_pid() -> int | None:
    """Find the SPLADE server process PID via pgrep."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "splade_server"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                pid = int(line.strip())
                # Exclude our own process
                if pid != os.getpid():
                    return pid
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return None


def get_process_rss_mb(pid: int) -> float:
    """Get RSS of a process in MB via ps."""
    try:
        result = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(pid)],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return round(int(result.stdout.strip()) / 1024, 1)
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return 0.0


def get_system_memory_pct() -> float:
    """Get system memory usage percentage via vm_stat."""
    try:
        result = subprocess.run(
            ["vm_stat"], capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return 0.0
        lines = result.stdout.strip().split("\n")
        stats = {}
        for line in lines[1:]:
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip().rstrip(".")
                try:
                    stats[key] = int(val)
                except ValueError:
                    continue
        free = stats.get("Pages free", 0)
        active = stats.get("Pages active", 0)
        inactive = stats.get("Pages inactive", 0)
        speculative = stats.get("Pages speculative", 0)
        wired = stats.get("Pages wired down", 0)
        total = free + active + inactive + speculative + wired
        if total == 0:
            return 0.0
        used = active + wired
        return round(used / total * 100, 1)
    except subprocess.TimeoutExpired:
        return 0.0


def probe_splade() -> dict:
    """Send reference text to SPLADE server and return nnz stats."""
    response = httpx.post(
        SPLADE_URL,
        json={"input": [REFERENCE_TEXT], "model": "splade"},
        timeout=30.0,
    )
    response.raise_for_status()
    sparse = response.json()["data"][0]["sparse_vector"]

    indices = sparse["indices"]
    values = sparse["values"]
    nnz = len(indices)

    # Top 5 by absolute value
    paired = sorted(zip(values, indices), key=lambda x: abs(x[0]), reverse=True)
    top5_values = [round(v, 4) for v, _ in paired[:5]]
    top5_tokens = [idx for _, idx in paired[:5]]

    return {
        "nnz": nnz,
        "top5_values": top5_values,
        "top5_tokens": top5_tokens,
    }


def collect_system_stats() -> dict:
    """Collect system memory and SPLADE process stats."""
    splade_pid = find_splade_pid()
    process_rss = get_process_rss_mb(splade_pid) if splade_pid else 0.0
    system_mem = get_system_memory_pct()

    return {
        "system_memory_pct": system_mem,
        "process_rss_mb": process_rss,
        "splade_pid": splade_pid or "",
    }


def run_probe(probe_count: int, start_time: float) -> dict:
    """Run a single probe and return all fields."""
    splade_stats = probe_splade()
    system_stats = collect_system_stats()
    elapsed = round((time.time() - start_time) / 60, 1)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "nnz": splade_stats["nnz"],
        "top5_values": splade_stats["top5_values"],
        "top5_tokens": splade_stats["top5_tokens"],
        "system_memory_pct": system_stats["system_memory_pct"],
        "process_rss_mb": system_stats["process_rss_mb"],
        "splade_pid": system_stats["splade_pid"],
        "elapsed_minutes": elapsed,
        "probe_count": probe_count,
    }


def print_probe(row: dict, is_header: bool = False) -> None:
    """Print probe result to stdout."""
    if is_header:
        print(f"{'Time':<20} {'NNZ':>6} {'RSS_MB':>8} {'SysMem%':>8} {'Elapsed':>8} {'Top5 Values'}")
        print("-" * 80)
    print(
        f"{row['timestamp']:<20} {row['nnz']:>6} "
        f"{row['process_rss_mb']:>8} {row['system_memory_pct']:>7}% "
        f"{row['elapsed_minutes']:>7}m {row['top5_values']}"
    )


def monitor(interval: int, output: Path, once: bool) -> None:
    """Main monitoring loop."""
    file_exists = output.exists()
    probe_count = 0
    start_time = time.time()

    # Baseline probe
    try:
        row = run_probe(probe_count, start_time)
    except httpx.ConnectError:
        print(f"ERROR: SPLADE server not reachable at {SPLADE_URL}")
        print("Start with: ./venv/bin/python workflow.py server start splade")
        sys.exit(1)

    print_probe(row, is_header=True)

    with open(output, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    if once:
        print(f"\nBaseline: {row['nnz']} nnz (single probe)")
        return

    print(f"\nMonitoring every {interval}s → {output}")
    print("Press Ctrl+C to stop.\n")

    while True:
        time.sleep(interval)
        probe_count += 1
        try:
            row = run_probe(probe_count, start_time)
            print_probe(row)

            with open(output, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                writer.writerow(row)

        except httpx.ConnectError:
            print(f"{datetime.now().isoformat(timespec='seconds')} — SPLADE server unreachable (restart?)")
        except KeyboardInterrupt:
            break

    print(f"\nMonitoring stopped. Results: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor SPLADE server nnz over time")
    parser.add_argument("--interval", type=int, default=120, help="Probe interval in seconds (default: 120)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="CSV output path")
    parser.add_argument("--once", action="store_true", help="Single probe, no loop")
    args = parser.parse_args()

    try:
        monitor(args.interval, args.output, args.once)
    except KeyboardInterrupt:
        print("\nStopped.")
