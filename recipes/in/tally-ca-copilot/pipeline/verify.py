"""
Stage 3 — VERIFY (Tally CA Copilot / India)
Input:  Structured JSON from extract stage
Output: Verified JSON; rows with confidence < 0.7 flagged for human review
Rules:  Code verification first (cross-check against DuckDB Tally tables).
        Cross-model (Qwen2.5-7B) only when source data unavailable.
        GST reconciliation is always code — never cross-model.
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
        # Try code verification against Tally DuckDB tables first
        code_ok, conf = _code_verify_against_tally(item, data_dir)

        if not code_ok:
            conf = _cross_model_verify(item)

        needs_review = conf < CONFIDENCE_THRESHOLD
        if needs_review:
            flagged += 1

        verified.append({**item, "verified": code_ok,
                          "confidence": conf, "needs_review": needs_review})
        logger.info(
            f"verify doc={item.get('source_doc', '?')} "
            f"conf={conf:.2f} needs_review={needs_review}"
        )

    logger.info(f"verify complete total={len(verified)} flagged={flagged}")
    return verified


def _code_verify_against_tally(item: dict, data_dir: Path) -> tuple[bool, float]:
    """
    Cross-check extracted invoice fields against DuckDB Tally voucher tables.
    Returns (match_found, confidence).
    """
    # TODO: duckdb query to match extracted GSTIN + amount + date
    return False, 0.0


def _cross_model_verify(item: dict) -> float:
    """Ask Qwen2.5-7B to confirm extraction matches source text. Returns confidence."""
    # TODO: POST to verifier endpoint
    return 0.0


if __name__ == "__main__":
    args = parse_args()
    verify([], Path(args.data), args.log)
