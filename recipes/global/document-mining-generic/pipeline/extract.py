"""Stage 2 — EXTRACT (Document Mining Generic / Global). LLM allowed."""
import argparse, logging
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--log", required=True)
    return p.parse_args()

def extract(data_dir: Path, profile: dict, log: str) -> list[dict]:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    # TODO: load documents, call LLM for structured extraction
    extractions: list[dict] = []
    logger.info(f"extract complete extractions={len(extractions)}")
    return extractions

if __name__ == "__main__":
    args = parse_args()
    import yaml
    extract(Path(args.data), yaml.safe_load(open(args.profile)), args.log)
