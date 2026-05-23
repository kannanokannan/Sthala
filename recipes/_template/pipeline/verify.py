"""
Stage 3 — VERIFY
Input:  Structured JSON from Stage 2 (extract)
Output: Verified JSON with confidence scores; low-confidence rows flagged
Rules:  Prefer code verification. Use cross-model only when code
        verification is not possible. Confidence < 0.7 → human_review queue.
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
    """
    For each extraction:
      1. Attempt code verification (re-derive from source data)
      2. If unavailable, cross-model check with verifier LLM
      3. Flag confidence < CONFIDENCE_THRESHOLD for human review
    Returns list of verified dicts with added 'verified' and 'needs_review' fields.
    """
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    verified = []
    flagged = 0

    for item in extractions:
        conf = item.get("confidence", 0.0)

        # Prefer deterministic code check
        code_ok = _code_verify(item, data_dir)

        if not code_ok:
            # Fall back to cross-model verification
            conf = _cross_model_verify(item)

        needs_review = conf < CONFIDENCE_THRESHOLD
        if needs_review:
            flagged += 1

        verified.append({**item, "verified": code_ok, "needs_review": needs_review})
        logger.info(
            f"verify source={item.get('source_doc', '?')} "
            f"confidence={conf:.2f} needs_review={needs_review}"
        )

    logger.info(
        f"verify complete total={len(verified)} flagged={flagged}"
    )
    return verified


def _code_verify(item: dict, data_dir: Path) -> bool:
    """
    Re-derive extracted values from source data deterministically.
    Return True if values match within tolerance.
    """
    # TODO: implement per-recipe
    return False


def _cross_model_verify(item: dict) -> float:
    """
    Ask verifier LLM to confirm the extraction matches the source text.
    Returns confidence score 0.0–1.0.
    """
    # TODO: POST to verifier model endpoint
    return 0.0


if __name__ == "__main__":
    args = parse_args()
    verify([], Path(args.data), args.log)
