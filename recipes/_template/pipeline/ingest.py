"""
Stage 1 — INGEST
Input:  Raw files from --data directory (PDF, Excel, CSV, images)
Output: Normalised Document objects written to DuckDB staging table
Rules:  NO LLM calls in this stage
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


def ingest(data_dir: Path, log: str) -> list[dict]:
    """
    Walk data_dir/input/, parse each file into a Document dict:
      {id, content, source, page, metadata}
    Write results to DuckDB staging table.
    Returns list of document dicts.
    """
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    input_dir = Path(data_dir) / "input"
    documents = []

    for path in input_dir.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()

        # TODO: wire up connectors per file type
        if suffix == ".pdf":
            doc = _parse_pdf(path)
        elif suffix in (".xlsx", ".csv"):
            doc = _parse_tabular(path)
        else:
            logger.warning(f"Unsupported file type: {path}")
            continue

        documents.append(doc)
        logger.info(f"ingested file={path.name} pages={doc.get('pages', 1)}")

    logger.info(f"ingest complete documents={len(documents)}")
    return documents


def _parse_pdf(path: Path) -> dict:
    # TODO: use Docling / Unstructured.io
    return {"id": str(path), "content": "", "source": str(path),
            "page": 1, "metadata": {"type": "pdf"}}


def _parse_tabular(path: Path) -> dict:
    # TODO: use DuckDB read_csv / read_xlsx
    return {"id": str(path), "content": "", "source": str(path),
            "page": 1, "metadata": {"type": "tabular"}}


if __name__ == "__main__":
    args = parse_args()
    ingest(Path(args.data), args.log)
