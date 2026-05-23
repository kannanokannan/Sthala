# Standards & Academic Landscape Research Summary

**Research Date:** May 2026
**Scope:** Existing standards, frameworks, and academic literature relevant to Sthala

---

## Standards Sthala Should Align With (Top 5)

### 1. NIST AI RMF 1.0 + GenAI Profile (2024)
- Most credible AI governance framework globally
- GenAI Profile specifically addresses LLM deployment risks
- Sthala's SPEC.md maps to: Govern, Map, Measure, Manage functions
- **Action:** Add RMF function mapping table to SPEC.md Section 7

### 2. ISO/IEC 42001:2023 (AI Management Systems)
- International standard for AI management
- Covers: policy, controls, audit, continual improvement
- Sthala satisfies core requirements by design
- **Action:** Add compliance checklist to docs/

### 3. 16-Factor App for AI (Google, 2024)
- Extension of 12-Factor App for generative AI
- Adds: conversational memory, non-determinism, AI security
- **This is Sthala's core architectural pattern — cite explicitly in SPEC.md**

### 4. OpenTelemetry GenAI Semantic Conventions (CNCF, 2024-2025)
- Standardised observability for AI/LLM workloads
- Spans, metrics, logs for inference, embeddings, RAG
- Already built into Sthala stack
- **Action:** Instrument all services per GenAI semconv

### 5. CycloneDX 1.7 AI BOM (2024)
- AI-specific extension of Software Bill of Materials
- Captures: model provenance, training data lineage, license
- Growing adoption for compliance (EU AI Act, DPDP)
- **Action:** Auto-generate AIBOM at install time

---

## Standards to Differentiate From (Top 3)

### 1. NVIDIA NIM (Vendor lock-in)
- High-quality inference, but NVIDIA hardware dependency
- Sthala: hardware-agnostic, AMD/Intel/CPU-first
- **Differentiation:** "NVIDIA NIM assumes you have the budget. Sthala assumes you don't."

### 2. LangChain / LlamaIndex (Framework bloat)
- Heavyweight abstractions, version hell, hidden complexity
- Sthala: thin Python orchestration, explicit pipelines, no magic
- **Differentiation:** "LangChain gives you an abstraction. Sthala gives you a pipeline you can read."

### 3. Hyperscaler Sovereign Cloud (AWS GovCloud, Azure Sovereign)
- "Sovereign" in marketing, data still on US/EU vendor hardware
- Sthala: data on your hardware, in your building
- **Differentiation:** "Their sovereign cloud. Your sovereign box."

---

## Relevant Academic Literature

### On-Premise LLM Deployment
- PagedAttention (vLLM, Kwon et al. 2023) — memory management for KV cache — used in Sthala stack
- FlashAttention-2 (Dao, 2023) — efficient attention for inference — built into vLLM
- Speculative decoding — 2-3× speedup for inference — optional in llama.cpp

### Model Cascading / Routing
- "FrugalGPT" (Chen et al., 2023) — cascade smaller to larger models, cost-quality tradeoff
- "Hybrid LLM" (Ding et al., 2024) — route queries by complexity — validates Sthala's tier routing
- **These directly validate the Sthala routing architecture**

### RAG Architecture
- "RAGAS" (Es et al., 2023) — RAG evaluation framework — use for recipe verification
- "Self-RAG" (Asai et al., 2023) — retrieval on demand — reference for advanced recipes

### Hallucination Mitigation
- "LLM-as-Judge" (Zheng et al., 2023) — using LLM to evaluate LLM output — validates Sthala verifier pattern
- "Chain-of-Verification" (Dhuliawala et al., 2023) — iterative self-verification — future sthalad feature

### Edge/Resource-Constrained AI
- GGUF quantization papers (Gerganov, 2023-2024) — llama.cpp format — Sthala's CPU-tier runtime
- ExLlamaV2 — alternative quantization for GPU inference
- "Efficient LLM Inference on CPUs" (Intel Labs, 2023) — AVX-512 optimisation — Sthala Tier 1 basis

---

## Name / IP Collision Check

### "Sthala"
- **Tech/AI space:** No conflicts found. Zero trademark hits in software/AI.
- **Other uses:** Indonesian hotel name, Bangalore interior design firm, Hyderabad infrastructure company
- **Verdict:** ✅ Safe to use. Register trademark in India Class 42 (software services).

### "Sovereign Stack"
- **Status:** Heavily diluted. Used by 10+ projects, two partial trademarks in EU.
- **Verdict:** ❌ Do not use as primary brand. Use as descriptive marketing only.

### "Sovereign AI"
- **Status:** Generic phrase, used by NVIDIA, G42, multiple governments.
- **Verdict:** ⚠️ Use as category description, not product name.

---

## Gaps Sthala Can Legitimately Claim to Fill

1. **SMB-scale sovereign AI deployment framework** — NIST, ISO, MLCommons all assume enterprise or hyperscaler. No standard addresses the ₹1-2L hardware, 1-2 person IT, on-prem-first SMB.

2. **Indic-language sovereign AI** — Global frameworks are English-first. No reference architecture for Tamil/Hindi SMB document workloads.

3. **Tally-native AI integration** — 7M+ Indian businesses use Tally. Zero AI frameworks address Tally ODBC integration, voucher batch limits, or TDL scripting.

4. **Refurb hardware tier guidance** — Every AI reference architecture assumes new hardware. Sthala is the only framework that explicitly targets and documents refurb Xeon + consumer GPU configurations.

5. **Batch-tolerant AI architecture** — Real-time AI gets all the attention. Overnight batch processing for document mining is a mainstream SMB need with no reference architecture.

---

## Frameworks to Monitor

- **MLflow 3.0** (2025) — adding deployment manifests, watch for SMB-targeting
- **Kubeflow 2.0** — heavy, but simplified mode emerging
- **Open Platform for Enterprise AI (OPEA)** — Intel-led, hardware-agnostic inference stack — closest to Sthala's territory, but enterprise-focused
- **HuggingFace HUGS** — hardware-agnostic serving, worth referencing in models.md
