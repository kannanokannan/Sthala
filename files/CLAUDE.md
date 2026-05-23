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

5. **No LangChain, LlamaIndex, or Haystack.** Thin Python orchestration only.
   Dependencies are a liability on airgapped hardware.

---

## Repo Structure

```
sthala/
├── CLAUDE.md                  ← you are here (Claude Code reads this first)
├── SPEC.md                    ← framework specification (source of truth)
├── AGENTS.md                  ← machine-readable build contract for LLM agents
├── README.md                  ← human-facing intro
├── CONTRIBUTING.md            ← how to add recipes and contribute
│
├── research/                  ← READ ONLY. Source research documents.
│   ├── 2026-05-market.md
│   └── 2026-05-standards.md
│
├── docs/
│   ├── models.md              ← model catalog (global defaults + regional options)
│   ├── hardware.md            ← hardware tiers in USD
│   ├── compliance.md          ← jurisdiction mapping
│   └── egress.md              ← egress contract (ContextBoundary spec)
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
│   ├── rag/
│   ├── ingestion/
│   └── observability/
│
├── recipes/                   ← country-tagged use cases
│   ├── _template/             ← copy this for new recipes
│   ├── global/
│   │   └── document-mining-generic/
│   ├── in/                    ← India (ISO 3166-1: IN)
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
feat/<short-description>           # new feature
fix/<short-description>            # bug fix
docs/<short-description>           # documentation only
recipe/<country-code>/<name>       # new or updated recipe
refactor/<short-description>       # restructure, no behaviour change
```

### Commit format (conventional commits)
```
feat(recipes/in): add tally CA copilot recipe
fix(stack/inference): correct VRAM detection for RTX 3090
docs(models): add Qwen2.5-14B to tier 2 defaults
recipe(us/quickbooks): initial QuickBooks ingest connector
chore(claude): update repo structure in CLAUDE.md
```

### Protected branches
- `main` — stable, tested, always boots
- `develop` — integration branch
- Never force-push to `main`
- Every PR to `main` requires passing verification steps from AGENTS.md

---

## Adding a New Recipe

1. Country code: ISO 3166-1 alpha-2 (`us`, `de`, `br`, `sg`, `au`...)
2. Copy template: `cp -r recipes/_template recipes/<cc>/<recipe-name>`
3. Required files:

```
recipes/<cc>/<name>/
├── README.md          ← what, who, how (keep under 1 page)
├── profile.yaml       ← extends a base profile from /profiles/
├── pipeline/          ← the 5-stage pipeline (see AGENTS.md)
├── prompts/           ← LLM prompt templates
├── docker-compose.yml ← stack override
├── run.sh             ← entry point
└── sample-data/       ← anonymised test data
```

4. Profile YAML must declare:
```yaml
extends: ../../profiles/accounting-firm.yaml
country: us
language: en
egress:
  tier: 1
```

---

## Model Defaults

```yaml
# Global defaults — used unless recipe overrides
inference:
  cpu_only:   Phi-3-mini-4k-instruct-Q4_K_M.gguf
  tier1:      Llama-3.1-8B-Instruct-Q4_K_M.gguf
  tier2:      Qwen2.5-14B-Instruct-Q4_K_M.gguf
  tier3:      Qwen2.5-32B-Instruct-Q4_K_M.gguf

embeddings:   nomic-embed-text-v1.5.Q8_0.gguf
code:         Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

# Regional model overrides live in recipes/<country>/profile.yaml
# Not here. Not in SPEC.md. Only in country recipes.
```

---

## Pipeline Enforcement

```
DO:
  pipeline/extract.py    → LLM calls allowed
  pipeline/verify.py     → code or cross-model verification
  pipeline/narrate.py    → LLM calls allowed

DO NOT:
  pipeline/compute.py    → NO LLM calls (enforced by linter)
  pipeline/ingest.py     → NO LLM calls

Hard rule: no LLM output becomes a number without passing through compute.py
```

---

## What Claude Code Must NOT Do

- Modify anything in `research/`
- Add country-specific logic to `SPEC.md`, `profiles/`, or `stack/`
- Install pip packages globally on the host
- Create a new top-level directory without updating this file
- Use LangChain, LlamaIndex, or Haystack in any recipe
- Hardcode model names outside `docs/models.md` or `profile.yaml`
- Push directly to `main`
- Skip the VERIFY stage in any recipe pipeline
- Call LLM in `pipeline/compute.py`

---

## Quick Commands

```bash
# Detect hardware and get tier recommendation
bash hardware/detect.sh

# Install and boot with a profile
bash install.sh --config profiles/generic.yaml

# Run a specific recipe
cd recipes/global/document-mining-generic
bash run.sh --data /path/to/data

# Validate all YAML
find . -name "*.yaml" -not -path "./research/*" | xargs python -c \
  "import sys,yaml; [yaml.safe_load(open(f)) for f in sys.argv[1:]]"

# Check inference is running
curl -sf http://localhost:11434/api/tags | python -m json.tool

# Lint: check for LLM in compute stage (must return empty)
grep -rn "llm\|chat\|completion" recipes/*/pipeline/compute.py
```

---

## Version

CLAUDE.md: 0.1.0
SPEC.md:   0.1.0
Last updated: 2026-05-23
