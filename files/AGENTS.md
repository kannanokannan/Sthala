# Sthala — Agent Build Contract

**Version:** 0.1.0
**For:** Claude Code, Cursor, Aider, Devin, or any LLM coding agent
**Read CLAUDE.md first.** This file assumes you have.

---

## Purpose

This file tells an LLM coding agent how to build, extend, and maintain
the Sthala framework. It is written for machine consumption.

If a human is reading this: this file drives automated builds.
For human documentation, read README.md and SPEC.md.

---

## Decision Tree — What to Build

```
User says → What to do
─────────────────────────────────────────────────────────────────
"Set up Sthala" or "boot a box"
  → Run: install.sh --config <profile>
  → If no profile specified: ask Q1, Q2, Q3 below
  → Then run: hardware/detect.sh to confirm tier

"Add a recipe" or "create a recipe for <use case>"
  → Ask: Q1 (country), Q4 (use case detail), Q5 (data sources)
  → Create: recipes/<country-code>/<recipe-name>/
  → Use template: recipes/_template/

"Update the model" or "use a different model"
  → Edit: profile.yaml → models.inference.user_override
  → Validate: VRAM against hardware/detect.sh output
  → Warn if insufficient, do not block

"Add a new country"
  → Create: recipes/<iso-country-code>/
  → Create: recipes/<iso-country-code>/README.md (country context)
  → Do not touch: SPEC.md, profiles/, stack/

"Run a recipe"
  → cd recipes/<country>/<name>
  → bash run.sh --data <path>
  → Monitor: http://localhost:3000 (Grafana)

"Update the framework"
  → Edit: SPEC.md (version bump required)
  → Update: CLAUDE.md if structure changes
  → Update: this file if decision tree changes
  → PR to develop, never direct to main
```

---

## Required Inputs (ask before building)

When user intent is unclear, ask these — one at a time, not all at once:

```
Q1: What country is this deployment in?
    (ISO 3166-1 code preferred: us, de, in, br, sg, au...)
    → Determines: recipes/<country>/ path, compliance posture

Q2: What hardware is available?
    (Options: CPU-only / has GPU / unknown)
    → If unknown: run hardware/detect.sh first
    → Determines: model tier, runtime (llama.cpp vs vLLM)

Q3: What vertical does this serve?
    (Options: accounting-firm / distributor / clinic / school / generic)
    → Determines: base profile to extend

Q4: What is the specific use case?
    (Example: "trend analysis on 5 years of sales invoices")
    → Determines: recipe name and pipeline configuration

Q5: What are the data sources?
    (Example: "Tally exports, Excel files, scanned PDFs")
    → Determines: ingest connectors and OCR configuration
```

---

## Build Sequence — New Recipe

Follow this exact order. Do not skip steps.

```
Step 1: SCAFFOLD
  mkdir -p recipes/<country>/<recipe-name>
  cp -r recipes/_template/* recipes/<country>/<recipe-name>/
  cd recipes/<country>/<recipe-name>

Step 2: CONFIGURE PROFILE
  Edit profile.yaml:
    - Set extends: to base profile (e.g., ../../profiles/accounting-firm.yaml)
    - Set country: <iso-code>
    - Set egress.tier: (1, 2, or 3)
    - Set models.inference.user_override: null (unless regional override needed)

Step 3: CONFIGURE INGEST
  Edit pipeline/ingest.py:
    - Add connectors for Q5 data sources
    - Each connector outputs: List[Document]
    - Document schema: {id, content, source, page, metadata}

Step 4: CONFIGURE EXTRACT
  Edit pipeline/extract.py:
    - Define extraction schema as Pydantic model
    - Each field includes: source_doc, source_location, confidence
    - Confidence threshold: 0.7 (configurable in profile.yaml)

Step 5: CONFIGURE VERIFY
  Edit pipeline/verify.py:
    - Implement code verification where possible
    - Fall back to cross-model only when code verification unavailable
    - Flag confidence < 0.7 to human_review queue

Step 6: CONFIGURE COMPUTE
  Edit pipeline/compute.py:
    - DuckDB for all aggregation
    - No LLM calls in this file — enforced by linter
    - Output: computed metrics as typed dict

Step 7: CONFIGURE NARRATE
  Edit pipeline/narrate.py:
    - LLM receives: computed metrics + verified facts only
    - System prompt: loaded from prompts/<recipe-name>/system.txt
    - Output: markdown report

Step 8: DOCKER COMPOSE
  Edit docker-compose.yml:
    - Extend ../../stack/inference/docker-compose.yml
    - Add recipe-specific services only
    - Mount data volume at /data (read-only)

Step 9: WRITE README
  Edit README.md:
    - What it does (2 sentences)
    - Who it is for (1 sentence)
    - Prerequisites (hardware tier, data format)
    - How to run (3 commands max)
    - Sample output (screenshot or text)

Step 10: TEST
  bash run.sh --data sample-data/
  Confirm: output/report.md exists and is non-empty
  Confirm: audit/run.log exists and has entries
  Confirm: no data in output/ contains raw PII if egress.tier > 1
```

---

## Verification Steps (run after every build)

```bash
# 1. Hardware detection works
bash hardware/detect.sh

# 2. Profile YAML is valid
python -c "import yaml; yaml.safe_load(open('profile.yaml'))"

# 3. Stack boots
docker compose up -d
sleep 10
curl -sf http://localhost:11434/api/tags > /dev/null && echo "inference: OK"
curl -sf http://localhost:6333/healthz > /dev/null && echo "vector: OK"

# 4. No LLM calls in compute.py (enforced)
grep -n "llm\|chat\|completion" pipeline/compute.py && echo "VIOLATION: LLM in compute stage" && exit 1

# 5. Egress tier declared
grep -q "egress:" profile.yaml || (echo "MISSING: egress tier" && exit 1)

# 6. AI BOM generated
docker compose run --rm sthala-build generate-aibom
test -f output/sbom.cdx.json && echo "AI BOM: OK"
```

---

## Failure Recovery

```
Failure: model does not fit in VRAM
  → hardware/detect.sh --recommend
  → Lower quantisation: Q6_K → Q4_K_M → Q3_K_S
  → Or: switch to CPU mode (llama.cpp --n-gpu-layers 0)

Failure: docker compose fails to start
  → Check: docker logs sthala-inference
  → Common: port conflict on 11434 (Ollama running elsewhere)
  → Fix: change port in docker-compose.yml or stop conflicting service

Failure: extract confidence below threshold
  → Check: sample-data/ for representative documents
  → Tune: confidence_threshold in profile.yaml (default 0.7)
  → Add: few-shot examples to prompts/<recipe>/extract_examples.json

Failure: DuckDB out of memory on large dataset
  → Use: DuckDB LIMIT + OFFSET pagination in compute.py
  → Or: process in chunks (default chunk_size: 10000 rows)

Failure: install.sh fails on fresh machine
  → Check: bash version >= 5.0
  → Check: internet access for initial model pull (or pre-seed /models/)
  → Check: docker or podman installed and running
```

---

## File Conventions

```
File                    Purpose
────────────────────    ───────────────────────────────────────
profile.yaml            Recipe configuration (edit this)
pipeline/ingest.py      Stage 1: file → Document objects
pipeline/extract.py     Stage 2: Document → structured JSON (LLM)
pipeline/verify.py      Stage 3: JSON → verified JSON (code/cross-model)
pipeline/compute.py     Stage 4: verified JSON → metrics (DuckDB, NO LLM)
pipeline/narrate.py     Stage 5: metrics → report (LLM)
pipeline/egress.py      Stage 6: report → external (optional, Tier 3 only)
prompts/                LLM prompt templates (system + user)
sample-data/            Anonymised example inputs
output/                 Generated reports (gitignored)
audit/                  Inference and egress logs (gitignored)
docker-compose.yml      Stack definition for this recipe
run.sh                  Entry point: run the full pipeline
README.md               Human documentation for this recipe
```

---

## Hard Rules (never violate)

```
NEVER: Modify research/ directory
NEVER: Put country-specific logic in SPEC.md, profiles/, or stack/
NEVER: Call LLM in pipeline/compute.py
NEVER: Send Tier-1 data to external API without user console approval
NEVER: Hardcode model names outside docs/models.md or profile.yaml
NEVER: Use LangChain, LlamaIndex, or Haystack
NEVER: Push directly to main branch
NEVER: Skip the VERIFY stage in any recipe
ALWAYS: Log every inference call to audit/run.log
ALWAYS: Include source_doc and source_location in every extraction
ALWAYS: Declare egress.tier in profile.yaml
ALWAYS: Run verification steps before marking recipe complete
```

---

## Sthala Agent Version

AGENTS.md version: 0.1.0
Compatible SPEC.md: 0.1.x
