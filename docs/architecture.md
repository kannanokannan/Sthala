# Sthala Architecture

*Extended architecture documentation. See SPEC.md for the formal specification.*

---

## Core Design Decision: LLM-as-Component

The central architectural decision in Sthala is treating the LLM as one component in a deterministic pipeline, not as the pipeline itself.

```
WRONG (LLM-as-magic):
  User question → LLM → Answer
  Problem: LLM computes, extracts, AND narrates. Five failure modes stacked. Untestable.

RIGHT (LLM-as-component):
  Documents → Parser → LLM (extract) → Verifier (check) → DuckDB (compute) → LLM (narrate) → Report
  Problem: Each stage has a measurable error rate. Testable. Debuggable. Swappable.
```

**Rule: An LLM in Sthala has exactly one of three roles:**
1. **Extractor** — converts unstructured text to structured JSON
2. **Verifier** — checks if an extraction matches its source
3. **Narrator** — converts verified structured data to human prose

It never computes. It never aggregates. It never adds numbers.

---

## Two-Model Verification Pattern

Sthala uses two models from different families as a verification layer.

```
Primary (Sarvam-30B): extracts structured JSON from document text
Verifier (Qwen2.5-7B): checks — does the extracted data appear in the source text?

If verifier confidence < 0.70 → row flagged as needs_review, excluded from report
If both agree → data proceeds to DuckDB compute layer
```

Why different families? Because models from the same family (e.g., Llama 8B + Llama 70B) share training data and make correlated errors. Sarvam (Indian AI) + Qwen (Alibaba) have sufficiently different training to produce uncorrelated failure modes.

**Hallucination rates by pattern (approximate):**
- Single model, no verification: ~8–15% extraction error rate on structured data
- Same-family cross-check: ~5–8% (limited improvement, correlated errors)
- Different-family cross-check: ~2–4%
- Different-family + deterministic verifier: ~0.5–1%
- DuckDB computes all numbers: ~0% numeric error (deterministic)

---

## Egress Architecture

Three-tier egress model, implemented as a consent gateway service.

```
┌──────────────────────────────────────────────────────────────┐
│                    STHALA NODE (your hardware)               │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │ Raw Data     │   │ Aggregates   │   │ Narrative      │  │
│  │ (Tier I)     │   │ (Tier II)    │   │ Layer (Tier II)│  │
│  │              │   │              │   │                │  │
│  │ vouchers     │   │ monthly rev  │   │ LLM narration  │  │
│  │ PII          │   │ % trends     │   │ from verified  │  │
│  │ raw invoices │   │ anomaly flags│   │ aggregates     │  │
│  │ GSTIN        │   │ (no PII)     │   │                │  │
│  └──────┬───────┘   └──────┬───────┘   └───────┬────────┘  │
│         │                  │                   │            │
│         │ never            │ consent gate       │           │
│         │ leaves           │ (human approves)   │           │
│         │                  │                   │            │
└─────────┼──────────────────┼───────────────────┼────────────┘
          │                  │                   │
          ✗                  ✓ (approved)         ✓ (optional)
                             │                   │
                        [Preview UI]        [Claude API]
                        User sees it         Tier III
                        User approves        (if enabled)
```

---

## Hardware Auto-Detection Flow

```
install.sh
    │
    ▼
hardware/detect.sh
    │
    ├── NVIDIA GPU detected, VRAM ≥ 24GB → Tier 2+, vLLM, Sarvam-30B Q6_K
    ├── NVIDIA GPU detected, VRAM 16-23GB → Tier 2, vLLM, Sarvam-30B Q4
    ├── AMD GPU detected → Tier 2, ROCm-vLLM (experimental), Sarvam-30B Q4
    ├── No GPU, RAM ≥ 64GB → Tier 1+, llama.cpp, Sarvam-30B Q3 (slow)
    ├── No GPU, RAM 32-63GB → Tier 1, llama.cpp, Qwen2.5-7B Q4
    └── No GPU, RAM <32GB → Tier 1 minimal, llama.cpp, Phi-3 mini Q4
```

---

## Job Queue Architecture

All ingestion and inference jobs are async. No user-facing operation blocks.

```
User drops file → MinIO stores → Redis job queued → Worker picks up
                                                         │
                                              ┌──────────┼──────────┐
                                              │          │          │
                                           Parse       Embed      Infer
                                           (sync)    (async)    (async)
                                              │          │          │
                                              └──────────┼──────────┘
                                                         │
                                                    DuckDB write
                                                         │
                                                    Job complete
                                                         │
                                                 Notify via webhook
                                                 (or poll /jobs API)
```

**Why async?** Inference on CPU-tier hardware takes minutes to hours per document. Synchronous processing would block the web console. Batch jobs run overnight without user interaction.

---

## OpenAI-Compatible API Surface

All Sthala inference goes through LiteLLM, which presents an OpenAI-compatible API.

```
External tool using OpenAI SDK
    │
    │ http://sthala-box:8080/v1
    ▼
LiteLLM Gateway
    │
    ├── model: "sarvam" → local vLLM/llama.cpp
    ├── model: "verifier" → local Qwen2.5-7B
    ├── model: "claude-sonnet-4-6" → Anthropic API (Tier III only)
    └── model: "gpt-4o" → OpenAI API (Tier III only)
```

This means any tool using the OpenAI SDK can use Sthala without modification — just change the base URL.

---

## Observability

Sthala emits OpenTelemetry traces following the GenAI semantic conventions (CNCF 2024).

Key spans per inference request:
- `gen_ai.system`: inference provider (vllm, llama.cpp)
- `gen_ai.request.model`: model name + quantization
- `gen_ai.usage.input_tokens`: prompt tokens consumed
- `gen_ai.usage.output_tokens`: completion tokens generated
- `gen_ai.response.finish_reason`: stop / length / tool_call

Metrics exported to Prometheus on `:9090`:
- `sthala_inference_duration_seconds`
- `sthala_tokens_total{direction="input|output"}`
- `sthala_job_queue_depth`
- `sthala_egress_events_total{tier="2|3"}`
- `sthala_verification_confidence_histogram`

---

## CycloneDX AI BOM Generation

At install time, Sthala auto-generates an AI Bill of Materials:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.7",
  "components": [
    {
      "type": "machine-learning-model",
      "name": "Sarvam-30B-A3B-Instruct",
      "version": "GGUF-Q6_K",
      "supplier": {"name": "Sarvam AI"},
      "licenses": [{"license": {"id": "Apache-2.0"}}],
      "modelCard": {
        "quantitativeAnalysis": {
          "performanceMetrics": []
        }
      },
      "externalReferences": [
        {"type": "distribution", "url": "https://huggingface.co/bartowski/Sarvam-30B-A3B-Instruct-GGUF"}
      ]
    }
  ]
}
```

This AIBOM is stored at `/var/sthala/data/audit/aibom.json` and updated on any model change.
