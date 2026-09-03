"""
Stage 2 — EXTRACT (Tally CA Copilot / India)
Input:  Queued PDFs/images from ingest; unstructured voucher notes
Output: Structured JSON with source citations and confidence scores
Rules:  LLM (Sarvam-30B) for Indic document extraction.
        Bhashini PARSeq OCR before LLM on scanned images.
        Every field must carry source_doc, source_location, confidence.
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

    # TODO: load OCR queue from DuckDB
    ocr_queue = []
    for item in ocr_queue:
        text = _run_ocr(item["path"], logger)
        result = _call_llm(system_prompt, text, profile)
        result["source_doc"] = item["path"]
        extractions.append(result)
        logger.info(
            f"extracted doc={item['path']} "
            f"confidence={result.get('confidence', 0):.2f}"
        )

    logger.info(f"extract complete extractions={len(extractions)}")
    return extractions


def _run_ocr(path: str, logger: logging.Logger) -> str:
    """Run Bhashini PARSeq OCR on scanned image/PDF."""
    # TODO: call Bhashini PARSeq container at http://localhost:8100/ocr
    logger.info(f"ocr: {path}")
    return ""


def _load_prompt(filename: str) -> str:
    p = Path(__file__).parent.parent / "prompts" / filename
    return p.read_text() if p.exists() else "Extract invoice details as JSON."


def _call_llm(system: str, content: str, profile: dict) -> dict:
    # TODO: POST to http://localhost:8080/v1/chat/completions
    return {"fields": {}, "confidence": 0.0, "source_location": ""}


if __name__ == "__main__":
    args = parse_args()
    import yaml
    profile = yaml.safe_load(open(args.profile))
    extract(Path(args.data), profile, args.log)
