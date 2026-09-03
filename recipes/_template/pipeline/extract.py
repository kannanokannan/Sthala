"""
Stage 2 — EXTRACT
Input:  Normalised Document objects from Stage 1
Output: Structured JSON with source citations and confidence scores
Rules:  LLM calls allowed here. Every field must include source_doc,
        source_location, and confidence.
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


def extract(data_dir: Path, profile: dict, log: str) -> list[dict]:
    """
    For each document from Stage 1, call LLM to extract structured fields.
    Returns list of extraction dicts, each with:
      {field_name, value, source_doc, source_location, confidence}
    """
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    system_prompt = _load_prompt("system.txt")
    extractions = []

    # TODO: load documents from DuckDB staging table
    documents = []

    for doc in documents:
        result = _call_llm(system_prompt, doc["content"], profile)
        result["source_doc"] = doc["source"]
        extractions.append(result)
        logger.info(
            f"extracted source={doc['source']} "
            f"confidence={result.get('confidence', 0):.2f}"
        )

    logger.info(f"extract complete extractions={len(extractions)}")
    return extractions


def _load_prompt(filename: str) -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / filename
    if prompt_path.exists():
        return prompt_path.read_text()
    return "Extract structured information from the document."


def _call_llm(system: str, content: str, profile: dict) -> dict:
    """
    Call local inference via OpenAI-compatible API.
    Returns structured dict with confidence score.
    """
    # TODO: POST to http://localhost:8080/v1/chat/completions
    return {
        "fields": {},
        "confidence": 0.0,
        "source_location": "page 1",
    }


if __name__ == "__main__":
    args = parse_args()
    import yaml
    profile = yaml.safe_load(open(args.profile))
    extract(Path(args.data), profile, args.log)
