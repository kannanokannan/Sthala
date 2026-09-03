"""Stage 1 — INGEST (Document Mining Generic / Global). NO LLM."""
import argparse, logging
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--log", required=True)
    return p.parse_args()

def ingest(data_dir: Path, log: str) -> int:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    input_dir = Path(data_dir) / "input"
    count = 0
    for f in input_dir.rglob("*"):
        if f.is_file() and f.suffix in (".pdf",".docx",".txt",".xlsx",".csv",".jpg",".png"):
            logger.info(f"ingest: {f.name}")
            count += 1
    logger.info(f"ingest complete count={count}")
    return count

if __name__ == "__main__":
    args = parse_args()
    ingest(Path(args.data), args.log)
