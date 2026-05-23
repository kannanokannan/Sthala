# Sthala — Claude Code Instructions

> Sthala is a sovereign, on-premise AI appliance reference framework
> for SMBs and institutions on commodity x86 hardware.
> Built in India. Designed for everywhere.

---

## Core Principles (read before anything)

1. **Framework is country-neutral.** SPEC.md, AGENTS.md, hardware tiers,
   model catalog — zero country-specific references. Country logic lives
   only inside `recipes/<country-code>/`.

2. **LLM is a component, not the system.** Never treat LLM as the pipeline.
   Extraction → Verification (deterministic) → Compute (DuckDB/SQL) →
   Narration (LLM). This order is enforced in every recipe.

3. **Recipes are the unit of value.** Every real-world use case is a recipe.
   A recipe is self-contained, boot-to-result, documented for a semi-technical user.

4. **Immutable research.** Files under `research/` are source documents.
   Never modify, never delete. Reference only.

5. **No LangChain.** No LlamaIndex. Thin Python orchestration only.
   Dependencies are a liability on airgapped hardware.

---

## Repo Structure

```
sthala/
├── CLAUDE.md                  ← you are here (Claude Code reads this first)
├── SPEC.md                    ← framework specification (source of truth)
├── AGENTS.md                  ← machine-readable build contract for LLM agents
├── README.md                  ← human-facing intro (no jargon)
│
├── research/                  ← READ ONLY. Source research documents.
│   ├── 2026-05-market.md
│   └── 2026-05-standards.md
│
├── docs/
│   ├── models.md              ← model catalog (global defaults + regional options)
│   ├── hardware.md            ← hardware tiers in USD
│   ├── compliance.md          ← jurisdiction mapping
│   └── egress.md              ← egress contract (ContextBoundary integration)
│
├── profiles/                  ← vertical presets (country-neutral)
│   ├── generic.yaml
│   ├── accounting-firm.yaml
│   ├── distributor.yaml
│   ├── clinic.yaml
│   └── school.yaml
│
├── stack/                     ← modular docker-compose components
│   ├── inference/
│   │   └── docker-compose.yml
│   ├── rag/
│   │   └── docker-compose.yml
│   ├── ingestion/
│   │   └── docker-compose.yml
│   └── observability/
│       └── docker-compose.yml
│
├── recipes/                   ← country-tagged use cases
│   ├── global/                ← no country dependency
│   │   └── document-mining-generic/
│   ├── in/                    ← India-specific
│   │   ├── tally-ca-copilot/
│   │   └── sales-trend-mining/
│   ├── us/                    ← United States
│   │   └── quickbooks-cpa-copilot/
│   └── eu/                    ← European Union
│       └── gdpr-document-node/
│
├── hardware/
│   └── detect.sh              ← auto-detect CPU/GPU/RAM, recommend tier
│
└── install.sh                 ← idempotent one-liner entry point
```

---

## Git Conventions

### Branch naming
```
feat/<short-description>        # new feature or recipe
fix/<short-description>         # bug fix
docs/<short-description>        # documentation only
recipe/<country>/<name>         # new recipe
refactor/<short-description>    # code restructure, no behavior change
```

### Commit format (conventional commits)
```
feat(recipes/in): add tally CA copilot recipe
fix(stack/inference): correct VRAM detection for RTX 3090
docs(models): add Qwen2.5-14B to medium tier
recipe(us/quickbooks): add initial QuickBooks connector
```

### Protected branches
- `main` — stable, tested, always boots
- `develop` — integration branch, may be unstable
- Never force-push to `main`

### PR rules
- Every recipe needs a working `README.md` inside its folder
- Every PR touching `SPEC.md` needs a version bump in the header
- `research/` is read-only — no PRs that modify it

---

## Adding a New Recipe

1. Identify country code (ISO 3166-1 alpha-2: `us`, `de`, `br`, `sg`...)
2. Create folder: `recipes/<country-code>/<recipe-name>/`
3. Required files inside:
```
recipes/<cc>/<name>/
├── README.md          ← what it does, who it's for, how to run
├── profile.yaml       ← extends a profile from /profiles/
├── pipeline.py        ← thin orchestration script
├── docker-compose.yml ← stack override for this recipe
└── sample-data/       ← anonymized sample input (optional but preferred)
```
4. Profile YAML must reference a base profile:
```yaml
extends: ../../profiles/accounting-firm.yaml
country: us
erp: quickbooks
language: en
```
5. Never put country-specific logic inside `stack/` or `profiles/`.

---

## Model Defaults

Always use these unless recipe explicitly overrides:

```yaml
inference:
  default: meta-llama/Llama-3.1-8B-Instruct-GGUF    # global default
  multilingual: Qwen/Qwen2.5-7B-Instruct-GGUF        # non-English docs
  code: Qwen/Qwen2.5-Coder-7B-Instruct-GGUF          # code/SQL tasks

embeddings:
  default: nomic-ai/nomic-embed-text-v1.5-GGUF

verifier:
  default: same as inference.default                  # cross-check model

regional_overrides:
  in: sarvamai/sarvam-2b-v0.2                         # India / Indic
  fr: mistralai/Mistral-7B-Instruct-v0.3
```

Model selection logic (hardware-aware):
- VRAM < 8GB  → Phi-3-mini or Gemma-2B (CPU fallback)
- VRAM 8-16GB → Llama-3.1-8B or Mistral-7B
- VRAM 16-24GB → Qwen2.5-14B or Gemma-27B
- No GPU → llama.cpp CPU mode, batch only

---

## Pipeline Rules (enforced in all recipes)

```
DO:
  LLM extracts → code verifies → DuckDB computes → LLM narrates

DO NOT:
  LLM extracts AND computes AND narrates in one call
  LLM as final arbiter of any number
  Skip the deterministic verification step
  Route PII through paid API without consent gate
```

---

## Egress Rules

Three tiers — every recipe must declare which tier it uses:

```yaml
egress:
  tier: 1  # 1=never leaves, 2=anonymized aggregates with consent, 3=paid API escalation
```

Tier 3 requires:
- Explicit user consent in config
- PII scrub before egress
- Egress preview shown to user before send
- Audit log entry per call

---

## Compliance Posture

Framework aligns with these by design (see `docs/compliance.md`):
- ISO/IEC 42001 (AI management systems)
- NIST AI RMF 1.0
- EU AI Act (non-high-risk deployment)
- CycloneDX 1.7 AIBOM (auto-generated on build)
- OpenTelemetry GenAI semantic conventions (observability)

Country-specific compliance lives in `recipes/<country>/`.

---

## What Claude Code Should NOT Do

- Modify anything in `research/`
- Add country-specific logic to `SPEC.md`, `profiles/`, or `stack/`
- Install pip packages globally (always `--break-system-packages` or venv)
- Create a new top-level directory without updating this file
- Use LangChain, LlamaIndex, or Haystack in any recipe
- Hardcode model names outside of `docs/models.md` or `profile.yaml`
- Push directly to `main` — always branch + PR

---

## Quick Commands for Claude Code

```bash
# Boot a recipe locally
cd recipes/global/document-mining-generic
docker compose up

# Run hardware detection
bash hardware/detect.sh

# Validate a profile YAML
python -c "import yaml; yaml.safe_load(open('profiles/generic.yaml'))"

# Check stack health after boot
curl -s http://localhost:11434/api/tags | python -m json.tool

# Lint all YAML files
find . -name "*.yaml" | xargs python -c "import sys,yaml; [yaml.safe_load(open(f)) for f in sys.argv[1:]]"
```

---

## Version

CLAUDE.md version: 0.1.0
SPEC.md version: see SPEC.md header
Last updated: 2026-05-23
