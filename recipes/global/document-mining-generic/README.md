# Recipe: Document Mining (Generic)

**Profile:** `generic`
**Country:** global (no country dependency)
**Status:** Stub — ready to extend
**Hardware:** Tier 1 minimum (CPU-only)

---

## Problem

Organisations accumulate documents (PDFs, Excel, Word, scanned images) that
contain valuable structured and unstructured information. Querying across them
manually is slow. Sending them to cloud AI is a privacy risk.

**Sthala Document Mining:** Drop files into a folder, get a queryable knowledge
base and natural-language Q&A — entirely on-premise.

---

## Data Sources

| Source | Format |
|---|---|
| Documents | .pdf, .docx, .txt |
| Spreadsheets | .xlsx, .csv |
| Images | .jpg, .png, .tiff |

---

## Pipeline

```
File Drop (/data/input)
     │
     ▼
┌─────────────────────┐
│  Document Parse     │  ← Docling (PDF/Word), DuckDB (Excel/CSV)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LLM: Extract       │  ← structured JSON from unstructured text
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Verifier Check     │  ← citation confidence > 0.7
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Qdrant: Embed+Store│  ← nomic-embed-text vectors
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  RAG Q&A Interface  │  ← OpenAI-compatible /v1/chat endpoint
└─────────────────────┘
```

---

## Hardware Requirements

| Tier | RAM | GPU | Notes |
|---|---|---|---|
| 1 (CPU) | 16GB | None | Suitable for small doc sets (<1000 pages) |
| 2 (GPU) | 32GB | 8GB VRAM | Recommended for larger corpora |

---

## Step-by-Step

```bash
# 1. Drop documents
cp your-docs/*.pdf /var/sthala/data/input/

# 2. Start the stack
cd recipes/global/document-mining-generic
docker compose up

# 3. Query
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"sthala","messages":[{"role":"user","content":"Summarise key findings"}]}'
```

---

## Verification

```bash
# Check document count ingested
curl http://localhost:6333/collections/sthala/points/count

# Test Q&A
curl http://localhost:8080/v1/chat/completions \
  -d '{"model":"sthala","messages":[{"role":"user","content":"What documents are loaded?"}]}'
```

---

## Related

- Profile: `profiles/generic.yaml`
- Extends to: any country recipe by adding `extends: ../../../profiles/generic.yaml`
