"""
Stage 5 — NARRATE (Sales Trend Mining / India)
Input:  Computed metrics (revenue trends, seasonal index, concentration)
Output: Executive sales trend report in markdown
Rules:  LLM receives only anonymised aggregates. No party names in prompt.
"""
import argparse
import json
import logging
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data",    required=True)
    p.add_argument("--log",     required=True)
    return p.parse_args()


def narrate(metrics: dict, data_dir: Path, log: str) -> str:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    system_prompt = _load_prompt("narrate.txt")
    user_content = json.dumps(metrics, indent=2, default=str)
    report = _call_llm(system_prompt, user_content)
    out_path = Path(data_dir) / "output" / "report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    logger.info(f"narrate complete report={out_path}")
    return report

def _load_prompt(filename: str) -> str:
    p = Path(__file__).parent.parent / "prompts" / filename
    return p.read_text() if p.exists() else "Narrate the sales trend data as an executive report."

def _call_llm(system: str, user: str) -> str:
    # TODO: POST to http://localhost:8080/v1/chat/completions
    return f"# Sales Trend Report\n\n_Metrics received._\n"


if __name__ == "__main__":
    args = parse_args()
    narrate({}, Path(args.data), args.log)
