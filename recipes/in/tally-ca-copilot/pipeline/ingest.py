"""
Stage 1 — INGEST (Tally CA Copilot / India)
Input:  TallyPrime ODBC / XML exports, Excel, GST JSONs, scanned PDFs
Output: Normalised Document objects in DuckDB staging tables
Rules:  NO LLM calls. Paginate Tally pulls in ≤500 voucher batches.
"""
import argparse
import logging
from pathlib import Path

TALLY_BATCH_SIZE = 500  # never pull more — Tally has a known memory leak


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
    counts = {"tally": 0, "excel": 0, "pdf": 0, "gst": 0}

    # Tally XML / .900 exports
    for f in input_dir.glob("tally/**/*"):
        if f.suffix in (".xml", ".900", ".1800"):
            _ingest_tally_xml(f, logger)
            counts["tally"] += 1

    # Excel / CSV
    for f in input_dir.glob("**/*.xlsx"):
        _ingest_excel(f, logger)
        counts["excel"] += 1
    for f in input_dir.glob("**/*.csv"):
        _ingest_excel(f, logger)
        counts["excel"] += 1

    # Scanned invoices / PDFs → OCR handled in extract stage
    for f in input_dir.glob("invoices/**/*"):
        if f.suffix in (".pdf", ".jpg", ".png", ".tiff"):
            _queue_for_ocr(f, logger)
            counts["pdf"] += 1

    # GST JSON exports
    for f in input_dir.glob("gst/**/*.json"):
        _ingest_gst_json(f, logger)
        counts["gst"] += 1

    logger.info(f"ingest complete counts={counts}")
    return counts


def _ingest_tally_xml(path: Path, logger: logging.Logger) -> None:
    """Parse TallyPrime XML export into DuckDB voucher/ledger tables."""
    # TODO: implement XML parser + DuckDB write
    logger.info(f"tally xml: {path.name}")


def _ingest_excel(path: Path, logger: logging.Logger) -> None:
    """Load Excel/CSV into DuckDB using read_xlsx / read_csv."""
    # TODO: duckdb.execute(f"CREATE TABLE ... AS SELECT * FROM read_xlsx('{path}')")
    logger.info(f"excel: {path.name}")


def _queue_for_ocr(path: Path, logger: logging.Logger) -> None:
    """Register PDF/image for OCR processing in extract stage."""
    # TODO: write path to ocr_queue table in DuckDB
    logger.info(f"ocr queue: {path.name}")


def _ingest_gst_json(path: Path, logger: logging.Logger) -> None:
    """Parse GSTR-1 / GSTR-3B / GSTR-2A JSON into DuckDB gst_returns table."""
    # TODO: implement JSON parser
    logger.info(f"gst json: {path.name}")


if __name__ == "__main__":
    args = parse_args()
    ingest(Path(args.data), args.log)
