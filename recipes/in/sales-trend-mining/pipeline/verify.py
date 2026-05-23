"""
Stage 3 — VERIFY (Sales Trend Mining / India)
Cross-check extracted line items against DuckDB source tables.
Flag confidence < 0.7 for human review.
"""
import argparse
import logging
from pathlib import Path

CONFIDENCE_THRESHOLD = 0.7


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data",    required=True)
    p.add_argument("--log",     required=True)
    return p.parse_args()


def verify(extractions: list[dict], data_dir: Path, log: str) -> list[dict]:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    verified, flagged = [], 0
    for item in extractions:
        code_ok, conf = _code_verify(item, data_dir)
        if not code_ok:
            conf = _cross_model_verify(item)
        needs_review = conf < CONFIDENCE_THRESHOLD
        if needs_review: flagged += 1
        verified.append({**item, "verified": code_ok,
                          "confidence": conf, "needs_review": needs_review})
        logger.info(f"verify conf={conf:.2f} needs_review={needs_review}")
    logger.info(f"verify complete total={len(verified)} flagged={flagged}")
    return verified

def _code_verify(item: dict, data_dir: Path) -> tuple[bool, float]:
    # TODO: cross-check against Tally sales_fact table
    return False, 0.0

def _cross_model_verify(item: dict) -> float:
    # TODO: POST to Qwen2.5-7B verifier
    return 0.0


if __name__ == "__main__":
    args = parse_args()
    verify([], Path(args.data), args.log)
