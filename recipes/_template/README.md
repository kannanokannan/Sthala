# Recipe: <Name>

**Profile:** `<base-profile>`
**Country:** `<iso-code>` or `global`
**Status:** Stub / WIP / Stable
**Hardware:** Tier N minimum

---

## What It Does

_2 sentences. What problem does this recipe solve?_

## Who It Is For

_1 sentence. Who is the operator?_

---

## Prerequisites

- Hardware: Tier N minimum (see `docs/hardware.md`)
- Data format: _list formats_
- Software: Docker / Podman

---

## How to Run

```bash
# 1. Drop your data
cp your-data/* /var/sthala/data/input/

# 2. Run the recipe
cd recipes/<cc>/<name>
bash run.sh --data /var/sthala/data

# 3. Collect output
ls /var/sthala/data/output/
```

---

## Pipeline

```
<Data Source>
     │
     ▼
┌─────────────────┐
│  ingest.py      │  ← normalise to Document objects
└────────┬────────┘
         ▼
┌─────────────────┐
│  extract.py     │  ← LLM: unstructured → structured JSON
└────────┬────────┘
         ▼
┌─────────────────┐
│  verify.py      │  ← code/cross-model confidence check
└────────┬────────┘
         ▼
┌─────────────────┐
│  compute.py     │  ← DuckDB: all aggregation (no LLM)
└────────┬────────┘
         ▼
┌─────────────────┐
│  narrate.py     │  ← LLM: generate report from metrics
└────────┬────────┘
         ▼
┌─────────────────┐
│  output/        │  ← report.md + report.pdf
└─────────────────┘
```

---

## Sample Output

```
_paste anonymised sample output here_
```

---

## Verification

```bash
bash run.sh --data sample-data/
test -f output/report.md && echo "report: OK"
test -f audit/run.log  && echo "audit:  OK"
grep -c "stage" audit/run.log
```
