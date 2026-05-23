# Contributing to Sthala

Thank you for contributing. Sthala is a community framework — every recipe,
connector, and hardware profile added here helps another organisation run AI
on hardware they own.

---

## What You Can Contribute

| Contribution type | Where it goes | Effort |
|---|---|---|
| New recipe (new country) | `recipes/<country-code>/<name>/` | High |
| New recipe (existing country) | `recipes/<country-code>/<name>/` | Medium |
| New vertical profile | `profiles/<name>.yaml` | Low |
| Model catalog entry | `docs/models.md` | Low |
| Hardware tier correction | `docs/hardware.md` | Low |
| Bug fix in stack | `stack/<module>/` | Medium |
| Documentation | `docs/` | Low |

**Do not contribute:**
- Country-specific logic to `SPEC.md`, `profiles/`, or `stack/`
- Anything that requires internet access at runtime
- LangChain, LlamaIndex, Haystack, or other heavyweight frameworks
- Changes to `research/` (read-only source documents)

---

## Adding a New Recipe — Step by Step

### 1. Check existing recipes first
Browse `recipes/` — your use case may already be partially implemented.
If it is, contribute to the existing recipe instead of creating a new one.

### 2. Identify your country code
Use ISO 3166-1 alpha-2: `us`, `de`, `br`, `sg`, `au`, `jp`, `za`...
Global recipes (no country dependency) go in `recipes/global/`.

### 3. Branch
```bash
git checkout develop
git pull origin develop
git checkout -b recipe/<country-code>/<recipe-name>
# Example: recipe/sg/xero-accountant-copilot
```

### 4. Scaffold from template
```bash
cp -r recipes/_template recipes/<country-code>/<recipe-name>
cd recipes/<country-code>/<recipe-name>
```

### 5. Required files
Your recipe must have all of these before it can be merged:

```
recipes/<cc>/<name>/
├── README.md             ← what, who, how (keep under 1 page)
├── profile.yaml          ← extends a base profile, declares egress tier
├── pipeline/
│   ├── ingest.py         ← Stage 1: file → Document objects (no LLM)
│   ├── extract.py        ← Stage 2: Document → structured JSON (LLM)
│   ├── verify.py         ← Stage 3: JSON → verified JSON (code/cross-model)
│   ├── compute.py        ← Stage 4: verified JSON → metrics (DuckDB, NO LLM)
│   ├── narrate.py        ← Stage 5: metrics → report (LLM)
│   └── egress.py         ← Stage 6: optional, Tier 3 only
├── prompts/
│   ├── system.txt        ← system prompt for extract stage
│   └── narrate.txt       ← system prompt for narrate stage
├── docker-compose.yml    ← extends stack modules, recipe-specific overrides
├── run.sh                ← entry point: bash run.sh --data /path
└── sample-data/          ← anonymised test inputs (required for CI)
```

### 6. Profile YAML
```yaml
extends: ../../../profiles/accounting-firm.yaml   # choose closest base
country: sg                                        # ISO 3166-1 alpha-2
language: en
egress:
  tier: 1   # 1 = never leaves, 2 = anonymised+consent, 3 = API+consent
```

### 7. Pipeline rules (enforced)
```
ingest.py   → NO LLM calls
extract.py  → LLM calls allowed
verify.py   → code verification preferred, cross-model if unavailable
compute.py  → NO LLM calls (CI linter enforces this)
narrate.py  → LLM calls allowed
egress.py   → only if egress.tier = 3
```

### 8. Sample data
- Must be fully anonymised (no real names, IDs, amounts)
- Must be small enough to run in CI (<10MB)
- Must demonstrate the recipe end-to-end

### 9. Verify before PR
```bash
# Profile is valid YAML
python -c "import yaml; yaml.safe_load(open('profile.yaml'))"

# No LLM in compute stage
grep -n "llm\|chat\|completion" pipeline/compute.py && echo "FAIL" || echo "OK"

# Pipeline runs on sample data
bash run.sh --data sample-data/
test -f output/report.md && echo "report: OK"
test -f audit/run.log && echo "audit: OK"
```

### 10. Open PR to `develop`
```bash
git push -u origin recipe/<country-code>/<recipe-name>
gh pr create --base develop --title "recipe(<cc>/<name>): <one-line description>"
```

---

## Adding a Model to the Catalog

1. Verify the model has an open license (Apache 2.0 / MIT preferred)
2. Verify it fits at least Tier 1 hardware (≤ 8GB VRAM / 16GB RAM)
3. Verify public benchmarks exist
4. Add to `docs/models.md` — all fields required:
   - HuggingFace link
   - License
   - GGUF size (GB)
   - Min RAM / Min VRAM
   - GPU required (Y/N)
   - Good at / Bad at
   - Sthala role
5. PR to `develop` with commit: `docs(models): add <model-name>`

---

## Commit Style

Follow conventional commits:

```
feat(recipes/in): add tally CA copilot recipe
fix(stack/inference): correct VRAM detection for RTX 3090
docs(models): add Qwen2.5-14B to tier 2
recipe(sg/xero): add initial Xero ingest connector
chore(template): update pipeline stage stubs
```

---

## Code Style

- Python 3.11+
- No external orchestration frameworks (no LangChain, LlamaIndex, Haystack)
- Type hints on all function signatures
- Docstring on every module (purpose + stages)
- DuckDB for all aggregation — never ask LLM to compute numbers
- Every LLM call writes to `audit/run.log`

---

## Questions

Open an issue or start a discussion. Tag it with the country code if it's
recipe-specific: `[IN]`, `[US]`, `[EU]`, `[global]`.
