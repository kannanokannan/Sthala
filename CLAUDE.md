# CLAUDE.md — Sthala AI Agent Context File

This file provides complete context for AI coding agents (Claude Code, Cursor, Aider, Devin, GitHub Copilot) working with the Sthala repository. Read this first, read SPEC.md second, then proceed.

---

## Canonical Reference

Before introducing any new term: check https://github.com/kannanokannan/context-stack/blob/main/GLOSSARY.md

Before making any cross-project decision: check https://github.com/kannanokannan/context-stack/blob/main/DECISIONS.md

Terminology defined in GLOSSARY.md overrides any local usage in this repo.

---

## What Sthala Is

Sthala is a **reference framework** for deploying sovereign on-premise AI on commodity x86 hardware. It is not a product, not a SaaS, not a cloud service. It is a documented pattern + reference implementation that organisations deploy on their own hardware.

Target users: SMBs, CA firms, distributors, schools, clinics in India and globally, where data cannot leave the premises.

**The core promise:** Boot a commodity PC → point at your data → get AI-powered analysis. Nothing leaves the box without explicit human approval.

---

## Repository Mental Model

```
SPEC.md           ← The law. Architecture decisions live here.
AGENTS.md         ← How YOU (the AI agent) should build in this repo.
profiles/         ← User-facing configuration. One YAML per vertical.
stack/            ← The runtime. Docker Compose. Don't over-engineer.
models/models.md  ← Curated model catalog. Links, not code.
recipes/          ← End-to-end vertical implementations.
hardware/         ← Auto-detection and recommendation scripts.
research/         ← Background research. Read for context, not for code.
docs/             ← Extended documentation.
```

---

## Design Rules (Non-Negotiable)

1. **LLM never computes numbers.** LLM extracts → code (DuckDB/Python) computes → LLM narrates. If you find code asking an LLM to add or average, fix it.

2. **Two model families minimum for verification.** Sarvam-30B as primary. Qwen2.5-7B as verifier. Different training data = uncorrelated failure modes.

3. **Nothing egresses without consent.** Every external API call must go through the egress gate defined in `stack/egress-gate/`. Raw documents, PII, and per-transaction data never leave. See SPEC.md Section 8.

4. **No LangChain.** Thin Python orchestration only. If you're about to import LangChain, stop. Write the pipeline step directly.

5. **No GPU assumption.** CPU-only must work (slowly). GPU accelerates. Hardware detect script sets the runtime flag.

6. **Indic-first.** Sarvam-30B is the default model because it is optimised for Tamil, Hindi, Telugu, and other Indic scripts. BGE + IndicBERT for embeddings. Bhashini PARSeq for OCR on Indic scripts.

7. **Profiles drive everything.** User-facing configuration lives in `profiles/*.yaml`. Stack services read from the active profile. Never hardcode a model name, path, or port in service code.

8. **OpenAI-compatible API surface.** All inference goes through LiteLLM. External tools using OpenAI SDK should work without modification.

---

## Key Technology Choices

| Layer | Choice | Why |
|---|---|---|
| Default LLM | Sarvam-30B Q6_K GGUF | Apache 2.0, MoE 2.4B active, fits 24GB VRAM, Indic-native |
| Verifier LLM | Qwen2.5-7B Q4 | Different family, uncorrelated errors, lightweight |
| Inference (GPU) | vLLM | PagedAttention, continuous batching, OpenAI API compatible |
| Inference (CPU) | llama.cpp | AVX-512 optimised, Q4 quantisation, CPU-efficient |
| Embeddings | nomic-embed-text / BGE-small | CPU-feasible, strong retrieval quality |
| Vector DB | Qdrant (embedded) | No external server, local-first |
| Tabular | DuckDB | Embedded, handles Excel/Parquet/CSV/JSON natively |
| OCR | Bhashini PARSeq | 73%+ WRR on Indic vs Tesseract 15% |
| Document parse | Docling | Multi-format, table extraction, structured output |
| Job queue | Python RQ + Redis | Lightweight batch scheduling |
| Gateway | LiteLLM | Routes local and cloud, OpenAI-compatible |
| Proxy | Caddy | Auto-HTTPS, simple config |
| Remote access | Tailscale | Zero-config, no open ports |
| Containers | Podman (rootless) | No daemon, SELinux-safe |
| OS | Debian 12 minimal | Stable, small, widely understood |
| Observability | OpenTelemetry + Prometheus | GenAI semantic conventions |

---

## File Conventions

### profiles/*.yaml
One file per vertical. Structure:

```yaml
profile: <name>
version: "0.1"
description: "One line description"

hardware:
  min_ram_gb: 32
  gpu_required: false
  gpu_vram_gb: 0

models:
  primary:
    recommended: "bartowski/Sarvam-30B-A3B-Instruct-GGUF"
    hf_link: "https://huggingface.co/bartowski/Sarvam-30B-A3B-Instruct-GGUF"
    user_override: null
  verifier:
    recommended: "Qwen/Qwen2.5-7B-Instruct-GGUF"
    hf_link: "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF"
    user_override: null
  embedder:
    recommended: "nomic-ai/nomic-embed-text-v1.5"
    user_override: null

stack:
  services:
    - inference
    - embeddings
    - vector_db
    - tabular
    - ocr
    - job_queue
    - gateway
    - proxy

ingestion:
  sources: []  # list of ingestion connectors

egress:
  tier_2_enabled: true
  tier_3_enabled: false
  tier_3_targets: []
```

### recipes/*/README.md
Every recipe must have:
1. Problem statement (2–3 sentences)
2. Data sources (what the recipe ingests)
3. Pipeline diagram (ASCII)
4. Hardware requirements (min tier)
5. Step-by-step instructions
6. Verification commands (how to confirm it works)
7. Expected output samples (sanitised)

### models/models.md
Every model entry must have: HuggingFace link, license, size (GB), min RAM, GPU needed (Y/N), min VRAM if GPU, "good at" and "bad at" fields.

---

## Common Tasks

### Add a new vertical recipe
1. Create `recipes/<name>/` directory
2. Copy structure from `recipes/tally-ca-copilot/`
3. Create `profiles/<name>.yaml`
4. Add ingestion connector if new data source
5. Add recipe to `README.md` recipe table
6. Reference from `SPEC.md` Section 6

### Add a new model to the catalog
1. Verify: open license (Apache 2.0 / MIT preferred)
2. Verify: fits at least Tier 2 hardware
3. Verify: benchmarked publicly (MLPerf or equivalent)
4. Add to `models/models.md` with all required fields
5. Update relevant profiles if it becomes a recommended default

### Extend the stack
1. Add service definition to `stack/docker-compose.yml`
2. Add service to relevant profile `stack.services` list
3. Update `hardware/detect.sh` if service has hardware requirements
4. Document in `docs/architecture.md`
5. Add OpenTelemetry instrumentation

---

## What NOT to Do

- Do not add cloud dependencies to the default stack (cloud is Tier 3 only)
- Do not use LangChain, LlamaIndex, or heavyweight frameworks (raw Python + specific libraries only)
- Do not hardcode model names, ports, or paths in service code (read from profile)
- Do not let an LLM compute or aggregate numbers (always route through DuckDB/Python)
- Do not expose sensitive data in logs (audit log is for actions, not data)
- Do not require internet at runtime (install.sh may need internet; running box must not)
- Do not add dependencies that break CPU-only operation

---

## Current Status

**SPEC Version:** 0.1.0 (Draft)
**Active recipes:** tally-ca-copilot (WIP), sales-trend-mining (WIP)
**Stack status:** docker-compose skeleton (not yet production-tested)
**Hardware detect:** basic CPU/GPU detection (expand coverage needed)

---

## Related Projects

- **ContextOps** — `https://github.com/kannanokannan/ContextOps` — AI context governance
- **ContextBoundary** — `https://github.com/kannanokannan/ContextBoundary` — Egress contracts

Sthala is the execution layer. ContextOps defines policy. ContextBoundary defines what can flow where. The three projects are complementary, not dependent.

---

## Author & Maintainer

Kannan Okannan — Chennai, India
GitHub: @kannanokannan

*This project is intentionally built for consumption by both humans and AI coding agents. AGENTS.md provides the agent-specific build contract. CLAUDE.md (this file) provides the reasoning behind decisions.*
