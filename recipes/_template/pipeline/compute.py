"""
Stage 4 — COMPUTE
Input:  Verified JSON from Stage 3
Output: Computed metrics and aggregates as typed dict
Rules:  NO LLM CALLS IN THIS FILE. All computation via DuckDB / Python.
        The CI linter enforces this — any 'llm', 'chat', or 'completion'
        string in this file will fail the build.
"""
import argparse
import logging
from pathlib import Path

try:
    import duckdb
except ImportError:
    duckdb = None  # type: ignore


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data",    required=True)
    p.add_argument("--log",     required=True)
    return p.parse_args()


def compute(verified: list[dict], data_dir: Path, log: str) -> dict:
    """
    Run all aggregation using DuckDB.
    Returns a dict of computed metrics to pass to narrate.py.
    NO LLM CALLS HERE.
    """
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    db_path = Path(data_dir) / "sthala.duckdb"
    metrics = {}

    if duckdb is None:
        logger.error("duckdb not installed — cannot compute")
        return metrics

    conn = duckdb.connect(str(db_path))

    # TODO: load verified data into DuckDB table
    # TODO: run aggregation queries
    # Example:
    # conn.execute("CREATE TABLE IF NOT EXISTS facts AS SELECT * FROM ...")
    # result = conn.execute("SELECT SUM(amount) FROM facts").fetchone()
    # metrics["total"] = result[0]

    conn.close()
    logger.info(f"compute complete metrics={list(metrics.keys())}")
    return metrics


if __name__ == "__main__":
    args = parse_args()
    compute([], Path(args.data), args.log)
