"""
Stage 4 — COMPUTE (Tally CA Copilot / India)
Input:  Verified JSON from Stage 3 + DuckDB Tally tables from Stage 1
Output: Computed metrics dict (GST trends, AR/AP aging, anomaly flags)
Rules:  NO LLM CALLS. All aggregation via DuckDB SQL.
        Every rupee amount, percentage, and count comes from this stage.
"""
import argparse
import logging
from pathlib import Path

try:
    import duckdb
except ImportError:
    duckdb = None  # type: ignore


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data",    required=True)
    p.add_argument("--log",     required=True)
    return p.parse_args()


def compute(data_dir: Path, log: str) -> dict:
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    db_path = Path(data_dir) / "sthala.duckdb"
    metrics: dict = {}

    if duckdb is None:
        logger.error("duckdb not installed")
        return metrics

    conn = duckdb.connect(str(db_path))

    # GST monthly trend
    metrics["gst_monthly"] = conn.execute("""
        SELECT
            strftime(voucher_date, '%Y-%m') AS month,
            SUM(output_tax)   AS output_tax,
            SUM(input_credit) AS input_credit,
            SUM(output_tax) - SUM(input_credit) AS net_liability
        FROM gst_returns
        GROUP BY month
        ORDER BY month
    """).fetchdf().to_dict(orient="records")

    # AR aging
    metrics["ar_aging"] = conn.execute("""
        SELECT
            CASE
                WHEN DATEDIFF('day', due_date, CURRENT_DATE) <= 30  THEN '0-30'
                WHEN DATEDIFF('day', due_date, CURRENT_DATE) <= 60  THEN '31-60'
                WHEN DATEDIFF('day', due_date, CURRENT_DATE) <= 90  THEN '61-90'
                ELSE '90+'
            END AS bucket,
            SUM(outstanding_amount) AS amount,
            COUNT(*) AS invoice_count
        FROM ar_ledger
        WHERE outstanding_amount > 0
        GROUP BY bucket
    """).fetchdf().to_dict(orient="records")

    # YoY revenue comparison
    metrics["yoy_revenue"] = conn.execute("""
        SELECT
            strftime(voucher_date, '%Y') AS year,
            SUM(amount) AS total_revenue
        FROM vouchers
        WHERE voucher_type = 'Sales'
        GROUP BY year
        ORDER BY year
    """).fetchdf().to_dict(orient="records")

    conn.close()
    logger.info(f"compute complete metrics={list(metrics.keys())}")
    return metrics


if __name__ == "__main__":
    args = parse_args()
    compute(Path(args.data), args.log)
