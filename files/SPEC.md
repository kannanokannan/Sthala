# Sthala Framework Specification

**Version:** 0.1.0
**Status:** Alpha
**License:** Apache 2.0
**Last updated:** 2026-05-23

---

## 1. Purpose

Sthala is a reference framework for deploying AI inference workloads on
commodity x86 hardware in sovereign, on-premise environments.

It addresses a specific gap: organisations that need AI-powered analysis
of their own data, cannot or will not send that data to cloud providers,
and do not have the budget or staff for enterprise AI infrastructure.

Sthala is not a product. It is a documented pattern — a set of decisions,
conventions, and reference implementations that anyone can follow, fork,
or extend.

---

## 2. Scope

**In scope:**
- Batch document ingestion and mining
- Retrieval-augmented generation (RAG) on local data
- Structured data analysis with LLM-generated narrative
- Airgapped and network-restricted deployments
- Single-node and small multi-node configurations
- x86 hardware: refurbished workstations, servers, prosumer builds

**Out of scope:**
- Training or fine-tuning models (see ContextOps for governance)
- Real-time streaming inference at scale
- Multi-tenant cloud deployments
- Consumer / mobile applications

---

## 3. Core Thesis

> The LLM is a component. The system is the framework around it.

Most "AI" deployment failures are not LLM failures. They are system design
failures: treating LLM as the pipeline rather than as one stage within it.

Sthala enforces a strict pipeline:

```
Ingest → Extract (LLM) → Verify (deterministic) → Compute (code) → Narrate (LLM)
```

Each stage is independently testable. Each stage has a measurable error rate.
No LLM output becomes a business number without passing through a deterministic
verification layer.

---

## 4. Design Principles

### P1 — LLM as Component
The LLM performs: fuzzy text extraction, classification, narration.
The LLM does not perform: arithmetic, aggregation, final validation.
These are performed by DuckDB, Python, or SQL — not an LLM.

### P2 — Deterministic Verify
Every LLM extraction is verified against its source before use.
Two methods, in order of preference:
1. Code verification (re-derive the value from source data)
2. Cross-model verification (second model confirms, different family)

### P3 — Egress by Consent
Three egress tiers. Every recipe must declare which tier it uses.
No data moves between tiers without explicit user action.

| Tier | What | Condition |
|------|------|-----------|
| 1 | Never leaves the box | Default |
| 2 | Anonymised aggregates | User reviews and approves each export |
| 3 | Explicit paid-API escalation | Per-call consent, PII scrubbed, audit logged |

### P4 — Immutable Base
The operating system is read-only at runtime.
Updates are atomic (A/B partition) with automatic rollback on failure.
No `apt install` at runtime. Dependencies are baked into the image.

### P5 — No Framework Lock-in
No LangChain. No LlamaIndex. No Haystack.
Orchestration is thin Python + POSIX tools.
Any step can be replaced without rewriting the pipeline.

### P6 — Hardware-Honest
Configuration adapts to available hardware.
No assumptions about GPU presence.
CPU-only mode is a first-class deployment target, not a fallback.

### P7 — Audit-First
Every inference call is logged: model, prompt hash, latency, tokens.
Every egress event is logged: what, when, destination, approval record.
Logs are append-only. Cannot be deleted via normal operation.

---

## 5. Reference Stack

| Layer | Component | Notes |
|-------|-----------|-------|
| OS base | Debian 12 minimal / Fedora CoreOS | Immutable, no GUI |
| Container runtime | Podman (rootless) | No daemon required |
| Orchestration | docker-compose / k3s (multi-node) | |
| Inference runtime | llama.cpp (CPU) / vLLM (GPU) | Auto-selected at boot |
| Default model | Llama 3.1 8B Instruct GGUF Q4_K_M | Global default |
| Embeddings | nomic-embed-text-v1.5 | Local, no API |
| Vector store | Qdrant (embedded) / LanceDB | Auto-selected by scale |
| Tabular engine | DuckDB | All numeric computation |
| Document parser | Unstructured.io / Docling | PDFs, Office, scans |
| OCR | Tesseract (default) / regional override | |
| Reverse proxy | Caddy | Auto-HTTPS, one config line |
| Remote access | Tailscale | Zero-config, optional |
| Observability | OpenTelemetry + Prometheus | GenAI semantic conventions |
| API gateway | LiteLLM | OpenAI-compatible, routes local+cloud |
| AI BOM | CycloneDX 1.7 | Auto-generated on build |

---

## 6. Hardware Tiers

All costs in USD. Refurbished pricing (secondary market, 2026).

### Tier 0 — Entry (CPU-only)
```
CPU:    Any x86_64, 4+ cores, AVX2 support
RAM:    32GB DDR4
SSD:    500GB NVMe
GPU:    None
Cost:   $300–600
Models: Phi-3 mini, Gemma 2B, Llama 3.2 3B
Use:    Batch async workloads, classification, small RAG
```

### Tier 1 — Standard (GPU-assisted)
```
CPU:    Intel i7/i9 or AMD Ryzen 7/9 (8+ cores)
RAM:    64GB DDR4
SSD:    1TB NVMe
GPU:    NVIDIA RTX 3090 (24GB VRAM) or Tesla P40 (24GB)
Cost:   $900–1,400
Models: Llama 3.1 8B, Mistral 7B, Qwen2.5 7B (Q4–Q6)
Use:    Production RAG, 20–50 concurrent users, document mining
```

### Tier 2 — Professional
```
CPU:    Dual Intel Xeon (16+ cores total)
RAM:    128GB DDR4 ECC
SSD:    2TB NVMe RAID
GPU:    RTX 3090 24GB or equivalent
Cost:   $1,800–2,500
Models: Qwen2.5 14B, Gemma 27B (Q4)
Use:    Department-level, multi-model, 50–200 users
```

### Tier 3 — Scale
```
CPU:    Dual Xeon Gold (32+ cores total)
RAM:    256GB DDR4 ECC
SSD:    4TB NVMe RAID
GPU:    2× RTX 3090 or 2× A100 40GB
Cost:   $4,000–6,000
Models: Qwen2.5 30B, Llama 70B (Q4)
Use:    Organisation-wide, multi-tenant, 200+ users
```

---

## 7. Model Selection

### Global Defaults

```yaml
inference:
  tier0_cpu:      Phi-3-mini-4k-instruct-GGUF          # < 4GB RAM
  tier1_default:  Llama-3.1-8B-Instruct-Q4_K_M.gguf    # 8GB VRAM
  tier2_default:  Qwen2.5-14B-Instruct-Q4_K_M.gguf     # 16GB VRAM
  tier3_default:  Qwen2.5-32B-Instruct-Q4_K_M.gguf     # 24GB VRAM

embeddings:
  default:        nomic-embed-text-v1.5.Q8_0.gguf

code:
  default:        Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

verifier:
  default:        same family as inference, different quantisation
```

### Regional Overrides (per recipe)

Regional model overrides are declared in `recipes/<country>/profile.yaml`.
They do not appear in the global framework. Examples:

| Country | Override model | Reason |
|---------|---------------|--------|
| `in` | Sarvam-30B | Indic language efficiency |
| `fr` | Mistral-7B | French language training |
| `de` | community-tbd | German compliance |

### User Override (always available)

Any HuggingFace GGUF model can be substituted via `profile.yaml`:
```yaml
models:
  inference:
    user_override: "org/model-name-GGUF"
```
Sthala validates VRAM fit and warns if insufficient. It does not block.

---

## 8. Pipeline Specification

Every recipe implements this pipeline. Stages are not optional.

```
Stage 1: INGEST
  Input:  Raw files (PDF, Excel, CSV, image, email)
  Output: Normalised document objects
  Tools:  Unstructured.io, Docling, pandas
  Rule:   No LLM at this stage

Stage 2: EXTRACT  
  Input:  Normalised documents
  Output: Structured JSON (fields, values, source citations)
  Tools:  LLM (primary), regex (fallback)
  Rule:   Every extraction includes source_doc and source_location

Stage 3: VERIFY
  Input:  Structured JSON from Extract
  Output: Verified JSON with confidence scores
  Tools:  Code verification preferred; cross-model if code unavailable
  Rule:   Confidence < 0.7 → flag for human review, do not use

Stage 4: COMPUTE
  Input:  Verified JSON
  Output: Computed metrics, aggregates, trends
  Tools:  DuckDB (mandatory), Python, SQL
  Rule:   No LLM in this stage. All numbers come from code.

Stage 5: NARRATE
  Input:  Computed metrics + verified facts
  Output: Human-readable report / API response
  Tools:  LLM
  Rule:   LLM receives only verified, computed inputs.
          It interprets and narrates. It does not recalculate.

Stage 6: EGRESS (optional)
  Input:  Narrated output
  Output: External API call (Tier 3 only)
  Tools:  LiteLLM → paid API
  Rule:   PII scrubbed. User previews payload. User approves. Logged.
```

---

## 9. Vertical Profiles

Profiles are country-neutral templates. Recipes extend profiles.

| Profile | Primary use | Key data sources |
|---------|-------------|-----------------|
| `generic` | Any document mining | PDFs, Excel, CSV |
| `accounting-firm` | Financial analysis, trend mining | ERP exports, invoices, ledgers |
| `distributor` | Sales trend, inventory, logistics | Sales data, PO records, delivery logs |
| `clinic` | Patient records, reporting | Structured clinical data (local only) |
| `school` | Administrative, academic records | Attendance, grades, parent comms |

---

## 10. Standards Alignment

| Standard | Alignment | Notes |
|----------|-----------|-------|
| ISO/IEC 42001 | Structural | AI management system requirements mapped to SPEC sections |
| NIST AI RMF 1.0 | Governance | Govern, Map, Measure, Manage functions addressed |
| EU AI Act | Compliance | Non-high-risk profile; transparency and logging requirements satisfied |
| CycloneDX 1.7 | Artifact | AI BOM auto-generated: model metadata, quantisation, licence |
| OpenTelemetry GenAI | Observability | Semantic conventions for LLM spans, token counts, latency |
| 16-Factor App for AI | Architecture | Extends 12-Factor with non-determinism, memory, AI security |
| Apache 2.0 | Licensing | All Sthala components; model licences declared in AI BOM |

---

## 11. Related Projects

| Project | Relationship |
|---------|-------------|
| ContextOps | Governance layer above Sthala. Defines how AI context is captured, curated, and maintained across the organisation. |
| ContextBoundary | Defines egress contract implemented in Sthala Tier 2/3. The formal spec for what data can move where. |
| HyperspaceAI | Alternative architecture (P2P swarm inference). Complementary, not competitive. |

---

## 12. What Sthala Is Not

- Not a cloud service
- Not a managed product
- Not a model provider
- Not a replacement for a data team
- Not suitable for real-time inference at hyperscaler scale
- Not responsible for the quality of your input data

---

## 13. Versioning

SPEC version follows [Semantic Versioning](https://semver.org/).

- **MAJOR** — breaking changes to pipeline contract or egress tier definitions
- **MINOR** — new profiles, new standards alignment, new hardware tiers
- **PATCH** — corrections, clarifications, documentation

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-05-23 | Initial framework definition |
