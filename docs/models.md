# Sthala Model Catalog

Curated models for Sthala deployments. All models are open license (Apache 2.0 or MIT unless noted). Tested against the hardware tiers in SPEC.md.

**To use a custom model:** set `user_override` in your profile YAML. Sthala will warn on hardware incompatibility but will not block.

Browse more: [HuggingFace GGUF models (trending)](https://huggingface.co/models?library=gguf&sort=trending)

---

## Global Default Model

### Llama 3.1 8B

| Property | Value |
|---|---|
| HuggingFace | [meta-llama/Llama-3.1-8B-Instruct-GGUF](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct-GGUF) |
| License | Llama 3.1 Community (commercial use allowed >700M MAU restriction) |
| GGUF size | Q4_K_M: ~5GB |
| Min RAM | 12GB / 8GB VRAM |
| Good at | English RAG, code, structured extraction |
| Bad at | Indic languages (limited tokenizer) |
| Sthala role | Global default primary model for Tier 1 deployments |

---

## Regional Specialist Models

### Sarvam-30B (Indic Recommended)

| Property | Value |
|---|---|
| HuggingFace | [bartowski/Sarvam-30B-A3B-Instruct-GGUF](https://huggingface.co/bartowski/Sarvam-30B-A3B-Instruct-GGUF) |
| License | Apache 2.0 |
| Architecture | MoE (32B total, 2.4B active per pass) |
| GGUF size | Q6_K: ~19GB |
| Min RAM | 32GB (CPU), 24GB VRAM (GPU) |
| GPU required | No (GPU strongly recommended) |
| Indic tokenizer | Yes — Tamil, Hindi, Telugu, Kannada, Marathi, Bengali |
| Tokenizer fertility | ~2.27 (vs Gemma 3.07) — 2–4× compute saving on Indic text |
| Agentic tool-calling | Yes |
| Good at | Indic document extraction, Indian SMB context, multilingual RAG, structured output |
| Bad at | Long mathematical reasoning chains, very recent events |
| Sthala role | Regional override for Indic document extraction and narration |

---

## Verifier Models (cross-check layer)

### Qwen2.5-7B

| Property | Value |
|---|---|
| HuggingFace | [Qwen/Qwen2.5-7B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF) |
| License | Apache 2.0 |
| GGUF size | Q4_K_M: ~4.5GB |
| Min RAM | 8GB |
| GPU required | No |
| Good at | Citation verification, claim cross-check, structured JSON output |
| Bad at | Long context (>16K tokens) |
| Sthala role | Verifier (different family from Sarvam = uncorrelated errors) |

---

## Tiny Models (Tier 0 / CPU-only)

### Phi-3 Mini (3.8B)

| Property | Value |
|---|---|
| HuggingFace | [microsoft/Phi-3-mini-4k-instruct-gguf](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) |
| License | MIT |
| GGUF size | Q4: ~2.2GB |
| Min RAM | 8GB |
| GPU required | No |
| Speed (CPU) | 8–15 tok/s on Core i7 |
| Good at | Short document classification, intent detection, routing |
| Bad at | Long documents, Indic languages |
| Sthala role | Tier 0 primary, or fast routing classifier |

### Gemma 2 2B

| Property | Value |
|---|---|
| HuggingFace | [google/gemma-2-2b-it-GGUF](https://huggingface.co/google/gemma-2-2b-it-GGUF) |
| License | Gemma Terms (non-commercial restrictions apply) |
| GGUF size | Q4: ~1.5GB |
| Min RAM | 6GB |
| GPU required | No |
| Good at | Very fast classification, PII detection, short summarisation |
| Bad at | Complex reasoning, Indic languages |
| Sthala role | Pre-filter / PII scrubber |

### Qwen2.5-1.5B

| Property | Value |
|---|---|
| HuggingFace | [Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) |
| License | Apache 2.0 |
| GGUF size | Q4: ~1GB |
| Min RAM | 4GB |
| GPU required | No |
| Good at | Routing, tagging, lightweight classification |
| Sthala role | Ultra-light classifier for Tier 1 |

---

## Small Models (Tier 1 / 16-24GB VRAM)

### Mistral 7B v0.3

| Property | Value |
|---|---|
| HuggingFace | [mistralai/Mistral-7B-Instruct-v0.3-GGUF](https://huggingface.co/MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF) |
| License | Apache 2.0 |
| GGUF size | Q4: ~4.5GB |
| Min RAM | 10GB |
| Good at | Fast English inference, function calling |
| Sthala role | Alternative to Llama 3.1 8B |

---

## Code Models

### Qwen2.5-Coder-7B

| Property | Value |
|---|---|
| HuggingFace | [Qwen/Qwen2.5-Coder-7B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF) |
| License | Apache 2.0 |
| GGUF size | Q4: ~4.5GB |
| Min RAM | 10GB |
| Good at | SQL generation, Python, JavaScript, code review |
| Sthala role | DuckDB SQL generation from natural language |

---

## Indic Specialist Models

### OpenHathi-7B

| Property | Value |
|---|---|
| HuggingFace | [sarvamai/OpenHathi-7B-Hi-v0.1-Base](https://huggingface.co/sarvamai/OpenHathi-7B-Hi-v0.1-Base) |
| License | CC-BY-4.0 |
| Good at | Hindi-first tasks, Hindi document understanding |
| Sthala role | Hindi-specialist overlay where Sarvam-30B is insufficient |

### IndicBART

| Property | Value |
|---|---|
| HuggingFace | [ai4bharat/IndicBART](https://huggingface.co/ai4bharat/IndicBART) |
| License | MIT |
| Good at | Translation between Indic languages, summarisation |
| Sthala role | Indic-to-English translation preprocessing step |

---

## Embedding Models

### nomic-embed-text-v1.5 (Default)

| Property | Value |
|---|---|
| HuggingFace | [nomic-ai/nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) |
| License | Apache 2.0 |
| Size | 274MB |
| CPU feasible | Yes |
| Good at | English + multilingual retrieval, RAG |
| Sthala role | Default embedding model |

### BGE-small-en-v1.5

| Property | Value |
|---|---|
| HuggingFace | [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) |
| License | MIT |
| Size | 134MB |
| CPU feasible | Yes — extremely fast |
| Good at | Fast English retrieval |
| Sthala role | Fast-path embedding for English-only deployments |

---

## OCR Engines

### Bhashini PARSeq (Default for Indic)

| Property | Value |
|---|---|
| Source | [AI4Bharat / Bhashini](https://bhashini.gov.in) |
| License | MIT |
| WRR (Word Recognition Rate) | 73%+ on Indic scripts |
| vs Tesseract | ~58% improvement on Tamil/Hindi/Telugu |
| Sthala role | Default OCR for Indic document recipes |

### Tesseract 5.x (Fallback)

| Property | Value |
|---|---|
| License | Apache 2.0 |
| WRR (Indic) | ~15% |
| WRR (English) | ~85% |
| Sthala role | English-only OCR fallback when Bhashini unavailable |

---

*Model catalog is community-maintained. Submit additions via PR to `docs/models.md`.*
*Always verify license compatibility with your deployment context.*
