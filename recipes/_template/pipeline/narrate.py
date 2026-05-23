"""
Stage 5 — NARRATE
Input:  Computed metrics from Stage 4 + verified facts from Stage 3
Output: Human-readable markdown report saved to output/report.md
Rules:  LLM receives ONLY verified, computed inputs.
        It interprets and narrates. It does not recalculate.
        Raw PII never enters the prompt.
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
    """
    Call LLM with computed metrics to generate executive narrative.
    Saves report to data_dir/output/report.md.
    Returns report text.
    """
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    system_prompt = _load_prompt("narrate.txt")
    user_content   = json.dumps(metrics, indent=2)

    report = _call_llm(system_prompt, user_content)

    out_path = Path(data_dir) / "output" / "report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)

    logger.info(f"narrate complete report={out_path} chars={len(report)}")
    return report


def _load_prompt(filename: str) -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / filename
    if prompt_path.exists():
        return prompt_path.read_text()
    return "You are a business analyst. Narrate the following metrics clearly and concisely."


def _call_llm(system: str, user: str) -> str:
    """
    Call local inference via OpenAI-compatible API.
    Returns generated markdown report text.
    """
    # TODO: POST to http://localhost:8080/v1/chat/completions
    return f"# Report\n\nMetrics received:\n\n```json\n{user}\n```\n"


if __name__ == "__main__":
    args = parse_args()
    narrate({}, Path(args.data), args.log)
