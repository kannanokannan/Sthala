"""
Stage 5 — NARRATE (Tally CA Copilot / India)
Input:  Computed metrics from Stage 4 (GST trends, AR/AP aging, YoY)
Output: Auditor-grade executive narrative saved to output/report.md
Rules:  LLM receives ONLY verified, computed aggregates.
        No raw PII, no per-voucher data, no client names in prompt.
        Sarvam-30B used for Indic language narration.
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
    user_content   = json.dumps(metrics, indent=2, default=str)

    report = _call_llm(system_prompt, user_content)

    out_path = Path(data_dir) / "output" / "report.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)

    logger.info(f"narrate complete report={out_path} chars={len(report)}")
    return report


def _load_prompt(filename: str) -> str:
    p = Path(__file__).parent.parent / "prompts" / filename
    return p.read_text() if p.exists() else (
        "You are a CA firm reporting assistant. "
        "Narrate the GST trends and AR/AP data provided as an executive summary."
    )


def _call_llm(system: str, user: str) -> str:
    # TODO: POST to http://localhost:8080/v1/chat/completions
    return f"# CA Firm Trend Report\n\n_Metrics received._\n\n```json\n{user[:200]}\n```\n"


if __name__ == "__main__":
    args = parse_args()
    narrate({}, Path(args.data), args.log)
