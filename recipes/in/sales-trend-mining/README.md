# Recipe: Sales Trend Mining

**Profile:** `distributor`
**Status:** Work in Progress (v0.1)
**Hardware:** Tier 1 minimum, Tier 2 recommended

---

## Problem

Distributors and wholesale traders accumulate years of sales data in Tally, Excel, and WhatsApp-based orders. Trend analysis is done manually in Excel — slow, error-prone, and limited in depth. Sending data to cloud AI is a trust and competitive risk.

**Sthala Sales Trend Mining:** Runs on your box overnight. Ingests Tally, Excel, PDF invoices, and WhatsApp orders. Produces a seasonal trend report, anomaly flags, and natural-language commentary — all without data leaving the premises.

---

## Data Sources

| Source | Format | Notes |
|---|---|---|
| TallyPrime | ODBC / XML export | Sales vouchers, stock items, party ledgers |
| Excel / CSV | .xlsx / .csv | Manual export supplements |
| PDF invoices | .pdf | Supplier invoices, delivery challans |
| WhatsApp Business | .txt export | Order messages with product + quantity |

---

## Pipeline

```
Data Sources
(Tally + Excel + PDF + WhatsApp)
         │
         ▼
┌─────────────────────┐
│  Multi-Source Ingest│  ← normalize product names, party names
└────────┬────────────┘    (LLM fuzzy match only — not compute)
         │
         ▼
┌─────────────────────┐
│  DuckDB Master Table│  ← date, product, qty, amount, party,
│  (sales_fact)       │     source_doc, source_ref
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LLM Extract        │  ← unstructured invoice text → line items
│  (PDF/WhatsApp)     │     Sarvam-30B outputs JSON
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Verifier Check     │  ← Qwen cross-checks extraction
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  DuckDB Analytics   │  ← all computation here (never LLM)
│                     │
│  • Monthly revenue  │
│  • Seasonal index   │
│  • SKU velocity     │
│  • Customer conc.   │
│  • YoY comparison   │
│  • Payment trends   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Anomaly Detection  │  ← Python statsmodels
│                     │     demand spikes, slow SKUs,
│                     │     payment delays, concentration risk
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Egress Gate        │  ← anonymised aggregates only
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LLM Narrative      │  ← "Revenue grew 23% in Q3, driven by..."
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  PDF + Excel Report │
└─────────────────────┘
```

---

## Key DuckDB Queries

```sql
-- Monthly revenue trend
SELECT
    strftime(voucher_date, '%Y-%m') AS month,
    SUM(amount) AS revenue,
    COUNT(DISTINCT party) AS active_customers
FROM sales_fact
GROUP BY month
ORDER BY month;

-- Seasonal demand index (normalize to annual average = 100)
WITH monthly AS (
    SELECT
        strftime(voucher_date, '%m') AS month_num,
        SUM(quantity) AS total_qty
    FROM sales_fact
    GROUP BY month_num
),
avg_monthly AS (SELECT AVG(total_qty) AS avg_qty FROM monthly)
SELECT
    month_num,
    ROUND(total_qty / avg_qty * 100, 1) AS seasonal_index
FROM monthly CROSS JOIN avg_monthly
ORDER BY month_num;

-- Customer concentration (top-10 as % of revenue)
SELECT
    party,
    SUM(amount) AS revenue,
    ROUND(SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 1) AS pct_of_total
FROM sales_fact
GROUP BY party
ORDER BY revenue DESC
LIMIT 10;

-- SKU velocity (identify slow movers)
SELECT
    stock_item,
    SUM(quantity) AS total_sold,
    COUNT(DISTINCT strftime(voucher_date, '%Y-%m')) AS months_active,
    ROUND(SUM(quantity) * 1.0 / COUNT(DISTINCT strftime(voucher_date, '%Y-%m')), 1) AS avg_monthly_velocity
FROM sales_fact
GROUP BY stock_item
HAVING months_active < 3
ORDER BY total_sold;
```

---

## Step-by-Step Instructions

### Step 1 — Prepare data
```bash
# Tally export or ODBC (same as ca-firm recipe)
cp sales-data.xlsx /var/sthala/data/input/distributor/
cp invoices/*.pdf /var/sthala/data/input/invoices/
cp whatsapp-export.txt /var/sthala/data/input/whatsapp/
```

### Step 2 — Run
```bash
bash recipes/sales-trend-mining/run.sh
```

### Step 3 — Review & collect
```bash
ls /var/sthala/data/output/
# → distributor-trend-report-2026-05-23.pdf
# → distributor-trend-data-2026-05-23.xlsx
```

---

## Verification

```bash
bash recipes/sales-trend-mining/verify.sh

# ✓ sales_fact table populated
# ✓ Monthly trend query returns 12+ months
# ✓ Seasonal index computed (all months present)
# ✓ Anomaly detection ran (flagged or clean)
# ✓ Report PDF generated with charts
```

---

## Expected Output Sample

```
Sales Trend Report — FY 2024-25

Revenue: ₹4.82 Cr (FY2024-25) vs ₹3.91 Cr (FY2023-24) → +23.3% YoY

Seasonal Pattern:
  Peak:    Oct–Nov (Diwali) — 1.42× annual average
  Trough:  Jun–Jul (monsoon) — 0.61× annual average
  Insight: Revenue predictable within ±8% using seasonal model

Top 3 SKUs (67% of revenue):
  1. [PRODUCT-A]: ₹1.24 Cr, stable velocity
  2. [PRODUCT-B]: ₹0.98 Cr, +34% YoY — investigate capacity
  3. [PRODUCT-C]: ₹0.89 Cr, declining (-12% YoY) — review pricing

Customer Concentration:
  Top-10 customers: 58% of revenue
  ⚠ Single customer [REDACTED]: 19% of revenue — concentration risk

Anomalies Flagged:
  • Nov-2024: Revenue spike +82% vs seasonal model (investigate)
  • Feb-2025: 3 invoices with delayed payment >90 days
  • [PRODUCT-D]: Zero sales for 4 consecutive months — possible discontinuation

[Source: Tally vouchers V1001–V6743, 14 PDF invoices via OCR]
```

---

## Related

- Profile: `profiles/distributor.yaml`
- Model: Sarvam-30B (extraction) + Qwen2.5-7B (verification)
- Compute engine: DuckDB (all analytics)
