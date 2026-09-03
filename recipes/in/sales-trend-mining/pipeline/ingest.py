"""
Stage 1 — INGEST (Sales Trend Mining / India)
Input:  Tally exports, Excel files, PDF invoices, WhatsApp Business exports
Output: Normalised sales_fact table in DuckDB
Rules:  NO LLM calls. Normalise product/party names using fuzzy code match.
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


def ingest(data_dir: Path, log: str) -> dict:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    input_dir = Path(data_dir) / "input"
    counts = {"tally": 0, "excel": 0, "pdf": 0, "whatsapp": 0}

    for f in input_dir.glob("tally/**/*"):
        if f.suffix in (".xml", ".900"):
            _ingest_tally(f, logger); counts["tally"] += 1

    for f in list(input_dir.glob("**/*.xlsx")) + list(input_dir.glob("**/*.csv")):
        _ingest_excel(f, logger); counts["excel"] += 1

    for f in input_dir.glob("invoices/**/*"):
        if f.suffix in (".pdf", ".jpg", ".png"):
            _queue_ocr(f, logger); counts["pdf"] += 1

    for f in input_dir.glob("whatsapp/**/*.txt"):
        _ingest_whatsapp(f, logger); counts["whatsapp"] += 1

    logger.info(f"ingest complete counts={counts}")
    return counts


def _ingest_tally(path: Path, logger: logging.Logger) -> None:
    # TODO: parse Tally sales vouchers into DuckDB sales_fact table
    logger.info(f"tally: {path.name}")

def _ingest_excel(path: Path, logger: logging.Logger) -> None:
    # TODO: duckdb read_xlsx/read_csv → sales_fact
    logger.info(f"excel: {path.name}")

def _queue_ocr(path: Path, logger: logging.Logger) -> None:
    # TODO: add to ocr_queue in DuckDB
    logger.info(f"ocr queue: {path.name}")

def _ingest_whatsapp(path: Path, logger: logging.Logger) -> None:
    # TODO: parse WhatsApp Business chat export for order lines
    logger.info(f"whatsapp: {path.name}")


if __name__ == "__main__":
    args = parse_args()
    ingest(Path(args.data), args.log)
