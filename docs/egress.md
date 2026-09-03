# Sthala Egress Contract

This document defines the three egress tiers, what is permitted at each tier,
and how to declare and enforce the tier in a recipe.

Sthala's egress model is based on **ContextBoundary** contracts:
https://github.com/kannanokannan/ContextBoundary

---

## The Three Tiers

### Tier 1 — Sovereign (Never Leaves)

All data stays on-premise. No network egress for AI processing.

**Permitted:**
- Raw documents, PII, per-transaction data
- Proprietary pricing, client names, financial records
- Any data the user has not explicitly approved for egress

**Blocked:**
- Any outbound HTTP call for AI inference
- Any cloud API (OpenAI, Anthropic, Google, Azure, etc.)

**When to use:** Default for all recipes. GDPR Article 44 compliance.
Healthcare data. Government data. Competitive / confidential business data.

---

### Tier 2 — Anonymised Aggregates (With Consent)

Aggregated, anonymised data may be sent externally — with explicit operator
approval at each egress event.

**Permitted (after consent gate):**
- Monthly/quarterly revenue totals (no party names)
- Trend percentages (YoY, QoQ)
- Anomaly flags without entity identifiers
- Statistical summaries

**Blocked:**
- Any raw per-record data
- Party names, GSTINs, employee IDs, patient IDs
- Individual transaction amounts

**Consent gate:** Operator sees a preview of exactly what will be sent
before any data leaves. Must click Approve. Audit log entry created.

**When to use:** Narrative polish via Claude API. Industry benchmarking.
Aggregate reporting to regulators (where permitted).

---

### Tier 3 — Paid API Escalation (Explicit Config + Consent)

Full API escalation to a cloud LLM provider. Must be explicitly enabled
in recipe `profile.yaml` AND approved by operator at runtime.

**Permitted (after config + consent):**
- Anonymised aggregates (same as Tier 2 constraints apply)
- Executive narrative generation via Claude / GPT-4
- Complex reasoning tasks not feasible on local hardware

**Required before Tier 3 egress:**
1. `egress.tier: 3` declared in `profile.yaml`
2. PII scrub confirmed (pipeline asserts `pii_detected: false`)
3. Egress preview shown to operator
4. Operator clicks Approve
5. Audit log entry with `human_approved: true`

**When to use:** Optional executive narrative polish. Never for raw data.

---

## Recipe Declaration

Every recipe's `profile.yaml` must declare its egress tier:

```yaml
egress:
  tier: 1   # or 2 or 3
```

If `tier` is omitted, the pipeline defaults to `1` (most restrictive).

---

## Egress Gate Implementation

The egress gate is enforced in `stack/ingestion/` before any data reaches
the narration stage:

```python
# Pseudocode — actual implementation in stack/ingest/egress_gate.py
def check_egress(data: dict, tier: int) -> dict:
    if tier == 1:
        raise EgressBlocked("Tier 1: no egress permitted")

    scrubbed = pii_scrub(data)          # deterministic, not LLM
    assert not contains_pii(scrubbed)   # hard assertion

    if tier >= 2:
        preview = render_preview(scrubbed)
        approved = operator_consent(preview)  # blocks until human action
        if not approved:
            raise EgressBlocked("Operator declined egress")
        audit_log(scrubbed, tier, approved=True)

    return scrubbed
```

---

## ContextBoundary Integration

Sthala's egress tiers map to ContextBoundary boundary contracts:

| Sthala tier | ContextBoundary zone |
|---|---|
| Tier 1 | Customer Sovereign (never crosses boundary) |
| Tier 2 | Managed transit — anonymised, consented |
| Tier 3 | LLM Vendor zone — explicit escalation |

See: https://github.com/kannanokannan/ContextBoundary
