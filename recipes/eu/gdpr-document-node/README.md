# Recipe: GDPR Document Node (EU)

**Profile:** `generic`
**Country:** eu
**Status:** Stub — community contributions welcome
**Hardware:** Tier 1 minimum (CPU-only)

---

## Problem

EU organisations must process documents containing personal data under strict
GDPR constraints. Standard cloud AI processing violates Article 44+ (transfers
to third countries). On-premise processing removes the transfer risk entirely.

**Sthala GDPR Document Node:** Process, classify, and respond to data subject
requests (DSARs) on-premise — no personal data leaves the EU network boundary.

---

## Data Sources

| Source | Format | Notes |
|---|---|---|
| Documents | .pdf, .docx | Contracts, emails, HR records |
| Spreadsheets | .xlsx, .csv | Customer/employee data registers |
| Email exports | .eml, .mbox | PST/MBOX with PII |

---

## Pipeline

```
Document Intake
     │
     ▼
┌─────────────────────┐
│  PII Detection      │  ← local NER (no cloud) — names, IDs, dates
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Classification     │  ← LLM: document type, data category, legal basis
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  DSAR Matching      │  ← DuckDB: find all records for data subject
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Redaction          │  ← deterministic PII scrub (not LLM)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Response Draft     │  ← LLM: formal DSAR response letter
└────────┬────────────┘     (redacted summary only — no PII in prompt)
         │
         ▼
┌─────────────────────┐
│  Audit Log          │  ← immutable log per GDPR Art. 30
└─────────────────────┘
```

---

## Hardware Requirements

| Tier | RAM | GPU | Notes |
|---|---|---|---|
| 1 (CPU) | 16GB | None | Suitable for DSAR volumes <100/month |
| 2 (GPU) | 32GB | 8GB | Recommended for larger organisations |

---

## Compliance Notes

- GDPR Article 5: purpose limitation, data minimisation enforced in pipeline
- GDPR Article 30: Records of Processing Activities (RoPA) auto-generated
- GDPR Article 44: no third-country transfers — all processing on-premise
- EU AI Act: non-high-risk classification (document management assistant)
- Country-specific rules live here in `recipes/eu/` only

---

## Status

This is a **community stub**. To contribute:
1. Fork the repo
2. Branch: `recipe/eu/gdpr-document-node`
3. Implement PII detection and DSAR matching stages
4. Submit PR to `develop`

---

## Related

- Profile: `profiles/generic.yaml`
- Compliance doc: `docs/compliance.md`
- Egress contract: `docs/egress.md`
