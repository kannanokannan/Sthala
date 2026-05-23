"""
Stage 2 — EXTRACT (Sales Trend Mining / India)
Input:  OCR queue from ingest; WhatsApp order messages
Output: Structured line-item JSON with source citations
Rules:  LLM for unstructured invoice/WhatsApp text only.
        Structured Tally/Excel data does NOT go through LLM extraction.
"""
import argparse
import logging
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data",    required=True)
    p.add_argument("--log",     required=True)
    return p.parse_args()


def extract(data_dir: Path, profile: dict, log: str) -> list[dict]:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    system_prompt = _load_prompt("system.txt")
    extractions = []
    # TODO: load OCR queue + WhatsApp entries from DuckDB
    logger.info(f"extract complete extractions={len(extractions)}")
    return extractions


def _load_prompt(filename: str) -> str:
    p = Path(__file__).parent.parent / "prompts" / filename
    return p.read_text() if p.exists() else "Extract sales line items as JSON."

def _call_llm(system: str, content: str, profile: dict) -> dict:
    # TODO: POST to http://localhost:8080/v1/chat/completions
    return {"fields": {}, "confidence": 0.0, "source_location": ""}


if __name__ == "__main__":
    args = parse_args()
    import yaml
    profile = yaml.safe_load(open(args.profile))
    extract(Path(args.data), profile, args.log)
