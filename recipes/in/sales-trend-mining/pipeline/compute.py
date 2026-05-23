"""
Stage 4 — COMPUTE (Sales Trend Mining / India)
Input:  Verified sales_fact table in DuckDB
Output: Metrics dict — revenue trends, seasonal index, SKU velocity, anomalies
Rules:  NO LLM CALLS. All SQL via DuckDB.
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
        logger.error("duckdb not installed"); return metrics

    conn = duckdb.connect(str(db_path))

    # Monthly revenue trend
    metrics["monthly_revenue"] = conn.execute("""
        SELECT strftime(voucher_date, '%Y-%m') AS month,
               SUM(amount) AS revenue,
               COUNT(DISTINCT party) AS active_customers
        FROM sales_fact GROUP BY month ORDER BY month
    """).fetchdf().to_dict(orient="records")

    # Seasonal demand index (normalised, annual average = 100)
    metrics["seasonal_index"] = conn.execute("""
        WITH monthly AS (
            SELECT strftime(voucher_date, '%m') AS month_num,
                   SUM(quantity) AS total_qty
            FROM sales_fact GROUP BY month_num
        ), avg_m AS (SELECT AVG(total_qty) AS avg_qty FROM monthly)
        SELECT month_num,
               ROUND(total_qty / avg_qty * 100, 1) AS seasonal_index
        FROM monthly CROSS JOIN avg_m ORDER BY month_num
    """).fetchdf().to_dict(orient="records")

    # Customer concentration (top 10 as % of revenue)
    metrics["customer_concentration"] = conn.execute("""
        SELECT party,
               SUM(amount) AS revenue,
               ROUND(SUM(amount)*100.0/SUM(SUM(amount)) OVER(), 1) AS pct_total
        FROM sales_fact GROUP BY party ORDER BY revenue DESC LIMIT 10
    """).fetchdf().to_dict(orient="records")

    # Slow-moving SKUs
    metrics["slow_skus"] = conn.execute("""
        SELECT stock_item, SUM(quantity) AS total_sold,
               COUNT(DISTINCT strftime(voucher_date,'%Y-%m')) AS months_active
        FROM sales_fact GROUP BY stock_item HAVING months_active < 3
        ORDER BY total_sold
    """).fetchdf().to_dict(orient="records")

    conn.close()
    logger.info(f"compute complete metrics={list(metrics.keys())}")
    return metrics


if __name__ == "__main__":
    args = parse_args()
    compute(Path(args.data), args.log)
