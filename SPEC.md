# Sthala Framework Specification

**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-05-23
**Author:** Kannan Okannan

---

## 1. Purpose

Sthala defines a reference architecture for deploying sovereign, on-premise AI workloads on commodity and refurbished x86 hardware. It targets organisations where:

- Data cannot leave the premises (compliance, sovereignty, trust)
- Cloud AI costs are prohibitive
- IT staff is minimal or absent
- Batch processing tolerance is acceptable (hours to days)
- Hardware budget is ₹1L–₹6.5L (€1,200–€8,000)

Sthala is a **framework** (documented pattern + reference implementation), not a product. It is designed to be consumed by humans and AI coding agents equally.

---

## 2. Scope

**In scope:**
- On-premise x86 deployment (bare metal, not VM-primary)
- Batch inference workloads (document mining, RAG, trend analysis)
- CPU-only and single-consumer-GPU configurations
- Indic language workloads (Tamil, Hindi, Telugu, Kannada, Bengali, Marathi)
- Hybrid egress pattern (local-first, optional paid API for narrative)

**Out of scope:**
- Kubernetes at scale (k3s optional, not required)
- Training or fine-tuning (inference only)
- Real-time / sub-second latency requirements
- Mobile or browser deployments
- Proprietary hardware (custom ASICs, vendor-locked NPUs)

---

## 3. Design Principles

### 3.1 LLM-as-ML-Component
The LLM is one component in a deterministic pipeline, not the pipeline itself.

```
Document → [Parser] → [LLM: Extract structured JSON] →
[Verifier LLM: cross-check citations] →
[DuckDB: compute all numbers] →
[LLM: narrate verified result] → Output
```

The LLM handles fuzzy text→structure conversion. Code handles all computation, aggregation, and arithmetic. This is non-negotiable.

### 3.2 Deterministic Compute, Fuzzy Understanding
- LLMs extract, classify, and narrate
- SQL/Python compute every number
- No LLM is ever the final arbiter of a numeric claim

### 3.3 Egress-by-Consent
Derived from ContextBoundary egress contract model:

| Tier | Data | Egress |
|---|---|---|
| I | Raw documents, PII, per-transaction | Never leaves |
| II | Anonymised aggregates | Customer-approved per-send, previewed |
| III | Structured question + context | Explicit per-call to paid API (Claude/GPT) |

### 3.4 Commodity Hardware First
If a workload requires hardware costing more than ₹6.5L, it is out of Sthala's scope. Design for refurb Xeon + single consumer GPU.

### 3.5 Vertical Recipes Over Generic Stacks
A CA firm using Tally is not a chatbot. A pharma distributor mining invoices is not an LLM playground. Each vertical gets a specific recipe, not a generic "ask questions to your data" pattern.

### 3.6 16-Factor App for AI
Sthala follows Google's 2024 16-Factor App extension for generative AI, adding: conversational memory management, non-determinism handling, and AI security posture.

### 3.7 Boot-to-Purpose
The system boots directly into its AI function. No general-purpose escape hatch. No exposed package manager. No root shell by default. Managed via web console or CLI over network.

---

## 4. Reference Stack

### 4.1 Operating System Layer

| Component | Choice | Rationale |
|---|---|---|
| Base | Debian 12 minimal | Stable, widely understood, small base |
| Immutability | OSTree / Fedora CoreOS | Atomic updates, A/B partitions, no drift |
| Init | systemd | Standard, service dependency management |
| Container runtime | Podman (rootless) | No daemon, SELinux-compatible, rootless |
| Orchestration (optional) | k3s | Single-binary, <50MB, multi-node if needed |
| First-boot config | cloud-init | Standard, vendor-neutral |

### 4.2 Inference Layer

| Component | Choice | Rationale |
|---|---|---|
| Default model | Sarvam-30B Q6_K (GGUF) | Apache 2.0, MoE 2.4B active, Indic-optimised |
| Verifier model | Qwen2.5-7B Q4 | Different family = uncorrelated errors |
| Inference server | vLLM (GPU) / llama.cpp (CPU) | PagedAttention, OpenAI-compatible API |
| Embeddings | BGE-small-en + IndicBERT | Multilingual, CPU-efficient |
| API gateway | LiteLLM | OpenAI-compatible, routes local + cloud |

### 4.3 Data Layer

| Component | Choice | Rationale |
|---|---|---|
| Tabular engine | DuckDB | Columnar, embedded, handles Excel/Parquet/CSV |
| Vector store | Qdrant (embedded mode) | No external server, local-first |
| Document parser | Docling / Unstructured.io | PDFs, scanned docs, mixed formats |
| OCR (Indic) | Bhashini PARSeq / IndicPhotoOCR | 73%+ WRR vs Tesseract 15% on Indic scripts |
| Job queue | Python RQ + Redis | Lightweight, batch-suitable |
| Object storage | MinIO (local) | S3-compatible, no cloud dependency |

### 4.4 Observability Layer

| Component | Choice | Rationale |
|---|---|---|
| Metrics | Prometheus + node_exporter | Standard, Grafana-compatible |
| Tracing | OpenTelemetry (GenAI semantic conventions) | Standards-aligned |
| AI BOM | CycloneDX 1.7 auto-generated | Compliance artifact, model provenance |
| Audit log | Structured JSON → local file | Append-only, regulatory-grade |

### 4.5 Access Layer

| Component | Choice | Rationale |
|---|---|---|
| Reverse proxy | Caddy | Auto-HTTPS, minimal config |
| Remote access | Tailscale | Zero-config VPN, no port forwarding |
| Web console | Open WebUI | Familiar, model-agnostic |
| API | OpenAI-compatible (via LiteLLM) | Drop-in for existing tooling |

---

## 5. Hardware Tiers

### Tier 1 — Baseline (CPU-only, ₹40K–₹80K)
- Intel Core i7-10th gen or AMD Ryzen 5000 series
- 32–64 GB DDR4 RAM
- 2 TB NVMe SSD
- No GPU
- Runs: Phi-3 mini, Gemma 2B, Qwen2.5-1.5B at 3–8 tok/s
- Use: single-user, batch, overnight jobs

### Tier 2 — Standard (Single GPU, ₹1.1L–₹1.5L)
- Refurb workstation: Dell Precision 7920 or similar
- Dual Xeon or Core i9
- 64–128 GB ECC RAM
- RTX 3090 (24GB VRAM) — ₹45K used
- Runs: Sarvam-30B Q6_K at 15–25 tok/s, Llama 3.1 70B Q2
- Use: SMB primary node, 10–50 concurrent users (async)

### Tier 3 — Business (Dual GPU, ₹2L–₹3L)
- Dell R740 dual-socket
- Dual Intel Xeon Gold 6148 (40 cores / 80 threads)
- 256 GB ECC DDR4
- 2× RTX 3090 or 2× A5000
- 4 TB NVMe SSD
- Runs: multiple models concurrently, model routing active
- Use: department-level, 50–200 concurrent users

### Tier 4 — Enterprise (₹4L–₹6.5L)
- Dell R740 or HPE DL380 Gen10
- 512 GB–1 TB RAM
- 4× A5000 or mix of A100 80GB (used)
- 8 TB NVMe
- Runs: full Sarvam-30B at high throughput, multi-model concurrently
- Use: hospital, university, large distributor network

---

## 6. Vertical Recipes

### 6.1 CA Firm — Tally Copilot
**Problem:** CA firms have years of Tally data, no safe way to query trends, client data cannot go to cloud.
**Stack additions:** Tally TDL/ODBC connector, DuckDB GST schema, Indic OCR for scanned vouchers
**Recipe:** `recipes/tally-ca-copilot/`

### 6.2 Distributor — Sales Trend Mining
**Problem:** Distributors have years of sales data in Tally/Excel/WhatsApp PDFs, no structured trend analysis.
**Stack additions:** Excel ingestion (DuckDB), PDF invoice parser, seasonal pattern detection
**Recipe:** `recipes/sales-trend-mining/`

### 6.3 School — Administrative Copilot
**Problem:** School offices generate paper (attendance, marks, PTM schedules, parent queries). No AI handles this without sending data to US servers.
**Stack additions:** Hindi/Tamil document OCR, parent-query bot (offline), attendance CSV ingestion
**Recipe:** `recipes/school-admin-copilot/` *(planned)*

### 6.4 Clinic — Patient Records Summariser
**Problem:** Clinic records in paper/scanned PDFs, doctor needs quick summaries, DPDP forbids cloud.
**Stack additions:** Medical Indic vocabulary, structured extraction, DPDP consent logging
**Recipe:** `recipes/clinic-records/` *(planned)*

---

## 7. Standards Alignment

### 7.1 NIST AI RMF 1.0 + GenAI Profile
- **Govern:** Sthala's CLAUDE.md + SPEC.md define AI system provenance and scope
- **Map:** Vertical recipes define context, deployment, and risk tier
- **Measure:** OpenTelemetry + CycloneDX AIBOM provide measurement artifacts
- **Manage:** Egress consent gateway + audit log provide ongoing management

### 7.2 ISO/IEC 42001
- AI management system elements covered: policy (SPEC.md), controls (egress gateway), audit (structured log)

### 7.3 EU AI Act
- Sthala appliances default to **non-high-risk** classification
- High-risk verticals (medical, legal) must implement additional controls per `docs/eu-ai-act-checklist.md` *(planned)*

### 7.4 India DPDP Act 2023
- Data stays on-premise by design (Tier I default)
- Consent mechanism built into egress gateway
- Audit log satisfies accountability principle
- No cross-border transfer without explicit Tier III escalation + consent

### 7.5 MCA Companies Rules 2022
- Daily backup mandate satisfied by local MinIO + scheduled DuckDB snapshots
- Backup stays on Indian soil by design

---

## 8. Egress Contract

Derived from ContextBoundary v0.1. Three-tier model:

```yaml
egress_policy:
  tier_1:
    label: "Never leaves"
    includes:
      - raw_documents
      - pii_fields
      - per_transaction_data
      - customer_names
      - account_numbers
    enforcement: firewall_rule + audit_log

  tier_2:
    label: "Customer-approved aggregates"
    includes:
      - monthly_aggregates
      - trend_percentages
      - anomaly_flags_without_entity_names
    requires:
      - human_preview_before_send
      - explicit_approval_in_ui
      - audit_log_entry

  tier_3:
    label: "Paid API escalation"
    includes:
      - anonymised_question_plus_context
      - structured_json_no_pii
    requires:
      - explicit_per_call_approval
      - audit_log_entry
      - api_cost_display_before_send
    targets:
      - claude-sonnet-4-6
      - gpt-4o
```

---

## 9. Relationship to ContextOps / ContextBoundary

| Framework | Governs |
|---|---|
| ContextOps | How AI context is captured, curated, supplied, and renewed across an organisation |
| ContextBoundary | Where AI context can flow — defines egress contracts and privacy tiers |
| Sthala | Where AI physically runs — the execution substrate that implements ContextBoundary contracts |

Sthala is the runtime layer. It does not define policy (ContextOps) or contracts (ContextBoundary). It enforces them.

---

## 10. Model Philosophy

Sthala curates models, not trains them. Default choices are: open license (Apache 2.0 / MIT), CPU/single-GPU feasible, Indic-language capable, publicly benchmarked.

See `models/models.md` for full catalog.

Default model: **Sarvam-30B** (MoE, 2.4B active params, Apache 2.0, fits 24GB VRAM at Q6_K).

Users may override any model via `profile.yaml`. HuggingFace links are provided. Sthala warns on hardware incompatibility but does not block.

---

## 11. Versioning

Sthala follows semantic versioning.
- **SPEC version** = framework specification version
- **Stack version** = reference docker-compose version
- **Recipe version** = per-recipe versioning

SPEC changes require a CHANGELOG entry and migration notes.

---

## 12. Contributing

- New vertical recipes via PR to `recipes/`
- Model additions via PR to `models/models.md`
- Standards updates via PR to `SPEC.md` with citation
- Hardware tier updates via PR with benchmark evidence

See `CONTRIBUTING.md` *(planned)*.

---

*Sthala is part of the ContextOps / ContextBoundary / Sthala open-source family.*
*Apache 2.0 — build on it freely.*
