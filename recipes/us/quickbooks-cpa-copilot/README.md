# Recipe: QuickBooks CPA Copilot (US)

**Profile:** `accounting-firm`
**Country:** us
**Status:** Stub — community contributions welcome
**Hardware:** Tier 1 minimum, Tier 2 recommended

---

## Problem

US CPA firms manage client books in QuickBooks Online and Desktop. Trend
analysis, tax preparation, and anomaly detection are manual and slow. Cloud AI
creates data residency and confidentiality risk.

**Sthala QuickBooks CPA Copilot:** On-premise analysis of QuickBooks data —
AR/AP aging, revenue trends, anomaly flags, and narrative reports without
client data leaving the firm's network.

---

## Data Sources

| Source | Format | Notes |
|---|---|---|
| QuickBooks Desktop | IIF / CSV export | Transactions, COA, customers, vendors |
| QuickBooks Online | JSON via QBO API (local proxy) | Sandboxed — no cloud egress |
| PDF documents | .pdf | Invoices, contracts, statements |

---

## Pipeline

```
QuickBooks Export / QBO Local Proxy
     │
     ▼
┌─────────────────────┐
│  DuckDB Raw Tables  │  ← transactions, COA, parties
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LLM: Extract       │  ← unstructured docs → structured JSON
└────────┬────────────┘     (Llama-3.1-8B default for US/English)
         │
         ▼
┌─────────────────────┐
│  Verifier Check     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  DuckDB: ALL COMPUTE│  ← P&L, balance sheet ratios, AR/AP aging
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Egress Gate        │  ← aggregates only; no client PII
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LLM: Narrate       │  ← executive summary from verified aggregates
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  PDF Report         │
└─────────────────────┘
```

---

## Hardware Requirements

| Tier | RAM | GPU | Notes |
|---|---|---|---|
| 1 (CPU) | 32GB | None | English-only; Llama-3.1-8B Q4 |
| 2 (GPU) | 64GB | 16GB VRAM | Faster throughput |

---

## Compliance Notes

- AICPA SOC 2 Type II alignment: data never leaves on-premise network
- IRS data retention: raw data stays in DuckDB on local disk
- Country-specific rules: `recipes/us/` only — not in core framework

---

## Status

This is a **community stub**. To contribute:
1. Fork the repo
2. Branch: `recipe/us/quickbooks`
3. Implement `pipeline.py` stages
4. Submit PR to `develop`

---

## Related

- Profile: `profiles/accounting-firm.yaml`
- Similar recipe: `recipes/in/tally-ca-copilot/`
