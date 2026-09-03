# Recipe: Tally CA Copilot

**Profile:** `ca-firm`
**Status:** Work in Progress (v0.1)
**Hardware:** Tier 1 minimum (CPU), Tier 2 recommended (GPU)

---

## Problem

Chartered Accountant firms manage years of client financial data in TallyPrime. The data is structured but trapped — no safe way to query trends across clients, spot anomalies, or generate narratives. Sending this data to cloud LLMs is a compliance and trust violation. Manual Excel analysis is slow and error-prone.

**Sthala CA Copilot:** Runs on your hardware, never sends raw data out, mines years of Tally data, and produces auditor-grade trend reports.

---

## Data Sources

| Source | Format | Notes |
|---|---|---|
| TallyPrime | ODBC / TDL XML / .900 export | Primary source. Paginate in ≤500 voucher batches. |
| Excel exports | .xlsx / .csv | Manual exports, supplementary data |
| Scanned invoices | .pdf / .jpg / .png | OCR via Bhashini PARSeq for Indic scripts |
| GST portal exports | .json | GSTR-1, GSTR-3B, GSTR-2A JSON downloads |

---

## Pipeline

```
TallyPrime (ODBC)
     │
     ▼
┌─────────────────────┐
│  Incremental Pull   │  ← batch 500 vouchers, avoid Tally crash
│  (tally_odbc.py)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  DuckDB Raw Tables  │  ← vouchers, ledgers, parties, stock
└────────┬────────────┘
         │
         ├──── Scanned PDFs ──→ [Bhashini PARSeq OCR] ──→ text
         │
         ▼
┌─────────────────────┐
│  LLM: Extract       │  ← Sarvam-30B extracts structured JSON
│  (from unstructured │     from invoice text / voucher notes
│   doc text only)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Verifier LLM       │  ← Qwen2.5-7B cross-checks: does
│  (citation check)   │     extracted data match source text?
└────────┬────────────┘
         │    ← reject < 70% confidence → flag for human
         ▼
┌─────────────────────┐
│  DuckDB: ALL COMPUTE│  ← Totals, averages, trends, YoY,
│  (never LLM)        │     GST reconciliation, AR/AP aging
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Anomaly Detection  │  ← Python/scipy on computed aggregates
│  (Python, not LLM)  │     flags duplicates, spikes, GST mismatch
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Egress Gate        │  ← Only anonymised aggregates may proceed
│  (consent check)    │     to narration. No PII, no raw data.
└────────┬────────────┘
         │   [human approves what leaves raw layer]
         ▼
┌─────────────────────┐
│  LLM: Narrate       │  ← Sarvam-30B generates executive narrative
│  (from verified     │     from structured JSON only
│   aggregates only)  │
└────────┬────────────┘
         │   [Optional: send to Claude API for polish]
         ▼
┌─────────────────────┐
│  Report Generator   │  ← PDF + Excel with source citations
└─────────────────────┘
```

---

## Critical Engineering Notes

### Tally ODBC Integration
- **Never pull more than 500 vouchers per query** — TallyPrime has a known memory leak on bulk ODBC pulls that crashes the host
- Use incremental pulls: store `last_voucher_date` in DuckDB, fetch only delta
- TDL (Tally Definition Language) is preferred over ODBC for complex reports
- BUSY Accounting SQL connector is a drop-in alternative

```python
# connectors/tally_odbc.py — incremental pull pattern
def fetch_vouchers(conn, last_date: str, batch_size: int = 500):
    offset = 0
    while True:
        rows = conn.execute(f"""
            SELECT * FROM Vouchers
            WHERE VoucherDate > '{last_date}'
            ORDER BY VoucherDate
            LIMIT {batch_size} OFFSET {offset}
        """).fetchall()
        if not rows:
            break
        yield rows
        offset += batch_size
```

### GST Reconciliation
- GSTR-2A (auto-populated from supplier) vs Books: reconcile in DuckDB, flag mismatches
- Never ask LLM to reconcile — it's pure SQL joins on GSTIN + invoice number + amount

### Hallucination Prevention
- **Hard rule:** All rupee amounts, percentages, counts come from DuckDB. LLM only narrates.
- Every numeric claim in the report cites its DuckDB query + source voucher reference
- If verifier confidence < 70%, row is marked `needs_review: true` and excluded from report

---

## Hardware Requirements

| Tier | RAM | GPU | Estimated runtime (1 year Tally data) |
|---|---|---|---|
| 1 (CPU-only) | 32GB | None | 6–12 hours |
| 2 (RTX 3090) | 64GB | 24GB VRAM | 45–90 minutes |
| 3 (Dual GPU) | 128GB | 2× 24GB | 15–30 minutes |

---

## Step-by-Step Instructions

### Step 1 — Prepare your Tally data
```bash
# Option A: Enable ODBC in TallyPrime
# Settings → Connectivity → Enable ODBC Server (port 9000)

# Option B: Export from Tally
# Gateway → Export → Data → XML format → save to /data/input/tally/
```

### Step 2 — Drop files
```bash
cp your-tally-export.xml /var/sthala/data/input/tally/
cp your-gst-exports/*.json /var/sthala/data/input/gst/
cp your-invoices/*.pdf /var/sthala/data/input/invoices/
```

### Step 3 — Run the recipe
```bash
bash recipes/in/tally-ca-copilot/run.sh
```

### Step 4 — Monitor
```bash
# Watch job progress
curl http://localhost:8080/jobs

# Tail logs
docker logs -f sthala-ingest
```

### Step 5 — Review and approve egress
- Open http://localhost:8080
- Navigate to "Pending Reports"
- Review what will be sent for narration (anonymised aggregates only)
- Approve or edit before final report generation

### Step 6 — Collect output
```bash
ls /var/sthala/data/output/
# → ca-firm-trend-report-2026-05-23.pdf
# → ca-firm-trend-data-2026-05-23.xlsx
```

---

## Verification

```bash
bash recipes/in/tally-ca-copilot/verify.sh

# Expected output:
# ✓ DuckDB tables populated (vouchers, ledgers, parties)
# ✓ OCR pipeline functional (Bhashini PARSeq)
# ✓ LLM extraction returning structured JSON
# ✓ Verifier confidence > 0.70 on sample
# ✓ Egress gate blocking raw PII
# ✓ Report generated with source citations
```

---

## Expected Output Sample

```
GST Trend Analysis — Client: [REDACTED] — FY 2024-25

Q1 (Apr–Jun): ₹12.4L output tax, 94.2% reconciled with GSTR-2A
Q2 (Jul–Sep): ₹18.1L output tax (+46% QoQ) — spike correlates
              with seasonal demand (Diwali advance orders)
              ⚠ 3 invoices flagged: GSTIN mismatch with GSTR-2A
Q3 (Oct–Dec): ₹15.3L output tax (-15% QoQ, +23% YoY)
Q4 (Jan–Mar): ₹11.8L output tax — typical Q4 normalization

AR Aging Summary (as at 31-Mar-2025):
  0–30 days:  ₹34.2L (67%)
  31–60 days: ₹11.4L (22%)
  61–90 days: ₹4.1L  (8%)
  90+ days:   ₹1.5L  (3%) ← 2 parties flagged for follow-up

[Source: Tally vouchers V0001–V4821, GST portal GSTR-3B Apr24–Mar25]
```

---

## Known Limitations

- Tally ODBC requires TallyPrime running on same LAN
- Handwritten invoices require higher DPI scan (300 DPI minimum)
- Multi-GSTIN firms need manual party mapping in first run
- Report generation takes 2–5 minutes per year of data

---

## Related

- Profile: `profiles/accounting-firm.yaml`
- Connector: `connectors/tally_odbc.py` *(coming)*
- Template: `templates/ca-firm-report.html` *(coming)*
