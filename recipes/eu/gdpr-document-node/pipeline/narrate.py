"""Stage 5 — NARRATE (Document Mining Generic / Global). LLM allowed."""
import argparse, json, logging
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--log", required=True)
    return p.parse_args()

def narrate(metrics: dict, data_dir: Path, log: str) -> str:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    report = "# Document Mining Report\n\n_No metrics yet._\n"
    out = Path(data_dir) / "output" / "report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report)
    logger.info(f"narrate complete report={out}")
    return report

if __name__ == "__main__":
    args = parse_args()
    narrate({}, Path(args.data), args.log)
