<p align="center">
  <h1 align="center">Sthala</h1>
  <p align="center"><strong>Your AI's place.</strong></p>
  <p align="center">
    A sovereign, on-premise AI appliance reference framework<br/>
    for SMBs and institutions on commodity x86 hardware.<br/>
    <em>Built in India. Designed for everywhere.</em>
  </p>
  <p align="center">
    <a href="SPEC.md">Specification</a> ·
    <a href="AGENTS.md">Build Contract</a> ·
    <a href="docs/models.md">Model Catalog</a> ·
    <a href="docs/hardware.md">Hardware Tiers</a> ·
    <a href="recipes/">Recipes</a>
  </p>
</p>

---

## What Sthala Is

Sthala is a reference framework — not a product, not a SaaS — for deploying
AI workloads on hardware you own, in a location you control, under rules you set.

It is designed for the 80% of organisations that cannot or will not send
sensitive data to cloud AI providers: accounting firms, distributors, clinics,
schools, manufacturers, and anyone subject to data residency requirements.

---

## What You Get

```
Boot a commodity PC → drop your data → get AI-powered analysis
Nothing leaves your box unless you explicitly approve it
```

- **Immutable Linux base** — no drift, atomic updates, boots in under 15 seconds
- **Llama 3.1 8B default** (global) · regional model override per country
- **Multi-model verifier pipeline** — LLM extracts → code computes → LLM narrates
- **Egress consent gateway** — you see what leaves, you approve every send
- **Vertical recipes** — accounting firm, distributor, school, clinic

---

## How It Works

```
Your Data                  Sthala Box                    Optional
─────────                  ──────────                    ────────
PDFs          →   Ingest → Extract → Verify → Compute →  Anonymised
Excel files       (local)   (LLM)   (code)   (DuckDB)    summary →
Invoices                                        ↓         Paid API
Scanned docs                              Narrate (LLM)   (with your
                                               ↓          consent)
                                          Report / API
```

The LLM is a component. The numbers come from code. The insight comes from both.

---

## Hardware Tiers

| Tier | Spec | Approx. Cost (USD) | Use Case |
|------|------|--------------------|----------|
| Entry | Refurb workstation, 32GB RAM, CPU-only | $400–700 | Batch, async, small models |
| Standard | Refurb server, 64GB RAM, RTX 3090 24GB | $900–1,400 | 7B–14B models, 50 users |
| Professional | Dual-Xeon, 128GB RAM, RTX 3090 | $1,800–2,500 | 30B models, departments |
| Scale | Dual-Xeon Gold, 256GB RAM, dual GPU | $4,000–6,000 | Multi-model, multi-tenant |

Run `bash hardware/detect.sh` — Sthala reads your hardware and recommends the right profile.

---

## Recipes

Recipes are self-contained, country-tagged use cases. Pick one. It runs end-to-end.

```
recipes/
├── global/
│   └── document-mining-generic/      ← start here
├── in/                               ← India
│   ├── tally-ca-copilot/
│   └── sales-trend-mining/
├── us/                               ← United States
│   └── quickbooks-cpa-copilot/
└── eu/                               ← European Union
    └── gdpr-document-node/
```

Adding a new recipe for your country? See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-org/sthala
cd sthala

# 2. Detect your hardware
bash hardware/detect.sh

# 3. Pick a profile and run
cp profiles/generic.yaml my-config.yaml
# edit my-config.yaml → set your data path and model preference

# 4. Boot the stack
bash install.sh --config my-config.yaml

# 5. Drop your data and run a recipe
cd recipes/global/document-mining-generic
bash run.sh --data /path/to/your/data
```

Stack is live at `http://localhost:8080`.
API endpoint at `http://localhost:11434` (OpenAI-compatible).

---

## Design Principles

1. **LLM as component** — not the pipeline. LLM does fuzzy work; code does math.
2. **Deterministic verify** — every LLM output is verified before it becomes a number.
3. **Egress by consent** — three tiers: never leaves / anonymised aggregate / explicit API call.
4. **Immutable base** — the OS does not drift. Updates are atomic, rollback is one command.
5. **No framework lock-in** — no LangChain, no LlamaIndex. Thin Python + well-known tools.
6. **Hardware-honest** — configuration adapts to what you have, not what you should buy.
7. **Audit-first** — every inference call is logged. Every egress event is recorded.

---

## Standards Alignment

Sthala is designed to satisfy baseline requirements of:

- ISO/IEC 42001 (AI management systems)
- NIST AI RMF 1.0
- EU AI Act (non-high-risk deployment profile)
- CycloneDX 1.7 AI Bill of Materials (auto-generated on build)
- OpenTelemetry GenAI semantic conventions

Country-specific compliance (GDPR, DPDP, LGPD, CCPA) is handled per recipe.
See [docs/compliance.md](docs/compliance.md).

---

## Related Projects

| Project | Role |
|---------|------|
| [ContextOps](https://github.com/your-org/contextops) | Governance framework — how to manage AI context |
| [ContextBoundary](https://github.com/your-org/contextboundary) | Egress spec — where AI context can flow |
| **Sthala** | Execution layer — where AI actually runs |

---

## Status

**v0.1 — Framework Alpha**

- [x] SPEC.md v0.1
- [x] AGENTS.md v0.1
- [x] CLAUDE.md (Claude Code instructions)
- [x] Hardware detection
- [ ] generic recipe (in progress)
- [ ] `in/tally-ca-copilot` (in progress)
- [ ] `us/quickbooks-cpa-copilot` (planned)
- [ ] `eu/gdpr-document-node` (planned)

---

## License

Apache 2.0 — use it, fork it, ship it. Attribution appreciated.

---

<p align="center">
  <sub>Sthala (स्थल) — a place, a site, a ground. Your AI's place.</sub>
</p>
