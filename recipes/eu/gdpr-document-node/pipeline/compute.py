"""Stage 4 — COMPUTE (Document Mining Generic / Global). NO LLM CALLS."""
import argparse, logging
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--log", required=True)
    return p.parse_args()

def compute(data_dir: Path, log: str) -> dict:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    metrics: dict = {}
    # TODO: DuckDB aggregation queries
    logger.info(f"compute complete metrics={list(metrics.keys())}")
    return metrics

if __name__ == "__main__":
    args = parse_args()
    compute(Path(args.data), args.log)
