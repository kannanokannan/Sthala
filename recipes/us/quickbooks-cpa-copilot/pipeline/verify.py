"""Stage 3 — VERIFY (Document Mining Generic / Global)."""
import argparse, logging
from pathlib import Path

CONFIDENCE_THRESHOLD = 0.7

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--log", required=True)
    return p.parse_args()

def verify(extractions: list[dict], data_dir: Path, log: str) -> list[dict]:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    verified, flagged = [], 0
    for item in extractions:
        conf = item.get("confidence", 0.0)
        needs_review = conf < CONFIDENCE_THRESHOLD
        if needs_review: flagged += 1
        verified.append({**item, "needs_review": needs_review})
    logger.info(f"verify complete total={len(verified)} flagged={flagged}")
    return verified

if __name__ == "__main__":
    args = parse_args()
    verify([], Path(args.data), args.log)
