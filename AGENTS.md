# AGENTS.md — Sthala Build Contract

This file is the machine-readable build contract for AI coding agents deploying or extending Sthala. It contains decision trees, parameter discovery, verification steps, and failure recovery.

Read CLAUDE.md for reasoning. This file is for execution.

---

## Entry Point

When a user asks you to "deploy Sthala" or "set up Sthala" or "install Sthala":

1. Run parameter discovery (Section 1)
2. Detect hardware (Section 2)
3. Select profile (Section 3)
4. Execute build (Section 4)
5. Verify deployment (Section 5)
6. Confirm to user (Section 6)

---

## Section 1 — Parameter Discovery

Ask the user for the following. Maximum 5 questions, in order. Stop when you have enough to proceed.

```
REQUIRED (ask if not provided):
  Q1: "What will you primarily use this for?"
      Options:
        a) CA firm / accounting / Tally data → profile: ca-firm
        b) Distributor / sales trend analysis → profile: distributor
        c) School / university admin → profile: school
        d) General document mining → profile: generic
        e) Something else → ask Q1b

  Q1b (if e): "Describe your use case in one sentence."
      → Use profile: generic, note use case in config comment

  Q2: "How much RAM does the target machine have?"
      Options: 16GB / 32GB / 64GB / 128GB / 256GB+ / I don't know
      → I don't know: run hardware/detect.sh first

  Q3: "Does the machine have a dedicated GPU?"
      Options: Yes (NVIDIA) / Yes (AMD) / No GPU / I don't know
      → I don't know: run hardware/detect.sh first

  Q4: "Do you need to process documents in Tamil, Hindi, or other Indian languages?"
      Options: Yes / No / Both English and Indic
      → Yes/Both: set ocr.indic_enabled: true in profile

  Q5: "Should the system ever send anonymised summaries to Claude/GPT for better narrative?"
      Options: No (fully airgapped) / Yes (with my approval each time)
      → No: set egress.tier_3_enabled: false
      → Yes: set egress.tier_3_enabled: true, prompt for API key later
```

---

## Section 2 — Hardware Detection

Run: `bash hardware/detect.sh`

Expected output format:
```json
{
  "cpu": {"model": "...", "cores": 8, "avx512": true},
  "ram_gb": 64,
  "gpu": {"vendor": "nvidia", "model": "RTX 3090", "vram_gb": 24},
  "disk_free_gb": 1800,
  "os": "debian-12",
  "tier": 2
}
```

Decision based on tier:
- Tier 1 (no GPU, <64GB RAM): inference_backend = llama.cpp, default model = Phi-3 mini or Qwen2.5-1.5B
- Tier 2 (GPU 16-24GB): inference_backend = vLLM, default model = Sarvam-30B Q6_K
- Tier 3+ (GPU >24GB or multi-GPU): inference_backend = vLLM, default model = Sarvam-30B full

If detect.sh fails:
- Ask user for RAM and GPU manually (Q2, Q3 above)
- Set inference_backend based on answer
- Warn: "Hardware detection failed. Manual configuration applied."

---

## Section 3 — Profile Selection

Map Q1 answer to profile file:

```
accounting-firm → profiles/accounting-firm.yaml
distributor → profiles/distributor.yaml
school      → profiles/school.yaml
generic     → profiles/generic.yaml
```

Apply hardware tier override to profile:
```python
profile['hardware']['detected_tier'] = tier_from_detect
if tier == 1:
    profile['models']['primary']['override'] = 'Qwen/Qwen2.5-1.5B-Instruct-GGUF'
    profile['models']['primary']['inference_backend'] = 'llama.cpp'
```

Apply language override:
```python
if indic_required:
    profile['ingestion']['ocr']['backend'] = 'bhashini_parseq'
    profile['models']['primary']['recommended'] = 'bartowski/Sarvam-30B-A3B-Instruct-GGUF'
```

Apply egress override:
```python
profile['egress']['tier_3_enabled'] = user_answer_q5 == 'yes'
```

---

## Section 4 — Build Execution

### Step 4.1 — Prerequisites check
```bash
# Check Docker/Podman
which podman || which docker || { echo "ERROR: No container runtime found"; exit 1; }

# Check disk space (minimum 200GB free)
df -h / | awk 'NR==2 {print $4}' 

# Check ports available
for port in 80 443 8080 6333 7474; do
  ss -tlnp | grep ":$port " && echo "WARNING: port $port in use"
done
```

### Step 4.2 — Download models
```bash
# Pull models via Ollama or direct GGUF download
ollama pull sarvam/sarvam-30b-a3b-instruct  # if Ollama available
# OR
huggingface-cli download bartowski/Sarvam-30B-A3B-Instruct-GGUF \
  --include "Sarvam-30B-A3B-Instruct-Q6_K.gguf" \
  --local-dir ./models/
```

### Step 4.3 — Launch stack
```bash
# Set active profile
export STHALA_PROFILE=<selected_profile>
export STHALA_TIER=<detected_tier>

# Launch
podman-compose -f stack/docker-compose.yml up -d
# OR
docker compose -f stack/docker-compose.yml up -d
```

### Step 4.4 — Wait for readiness
```bash
# Poll inference endpoint (max 5 min)
for i in $(seq 1 30); do
  curl -s http://localhost:8080/health && break
  sleep 10
done
```

---

## Section 5 — Verification

Run after every deployment:

```bash
# 5.1 Inference test
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"sarvam","messages":[{"role":"user","content":"Reply OK"}],"max_tokens":5}' \
  | jq '.choices[0].message.content'
# Expected: "OK"

# 5.2 Embeddings test
curl -s http://localhost:8080/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic","input":"test"}' \
  | jq '.data[0].embedding | length'
# Expected: number > 0

# 5.3 Vector store test
curl -s http://localhost:6333/healthz
# Expected: {"status":"ok"}

# 5.4 DuckDB test
python3 -c "import duckdb; print(duckdb.sql('SELECT 42').fetchone()[0])"
# Expected: 42

# 5.5 Egress gate test (if tier_3 enabled)
curl -s http://localhost:8090/egress/status
# Expected: {"enabled":true,"pending_approval":0}
```

---

## Section 6 — User Confirmation

After successful verification, report to user:

```
✓ Sthala deployed successfully

Profile:      <profile_name>
Hardware:     Tier <N> (<tier description>)
Model:        <primary_model_name>
Verifier:     <verifier_model_name>
OCR:          <ocr_backend>
Egress:       <Fully airgapped | Tier 2+3 enabled>

Access:
  Web console:  http://localhost:8080
  API:          http://localhost:8080/v1 (OpenAI-compatible)
  Remote:       Install Tailscale, then https://sthala.ts.net

Next steps:
  - Drop your data files into: ./data/input/
  - Run your recipe: bash recipes/<recipe_name>/run.sh
  - View job status: http://localhost:8080/jobs
```

---

## Failure Recovery

| Failure | Recovery |
|---|---|
| Model download fails | Try `--resume-download`, check disk space, try smaller model |
| Port conflict | Check `ss -tlnp`, stop conflicting service, retry |
| GPU not detected | Set `STHALA_TIER=1`, use llama.cpp, CPU-only mode |
| Inference timeout | Reduce model size (Q4 instead of Q6_K), check RAM |
| Podman not found | Install with `apt install podman` or `dnf install podman` |
| DuckDB import error | Check file encoding (UTF-8 required), check column headers |
| OCR poor quality | Switch to `bhashini_parseq` for Indic, increase DPI for scans |

---

## Extension Contract

When adding a new recipe:
1. MUST have a working `run.sh` that executes end-to-end
2. MUST have a `verify.sh` with at least 3 assertions
3. MUST not introduce cloud dependencies in the default path
4. MUST document all data format assumptions
5. MUST include sample sanitised input in `sample-data/`

When adding a new service to docker-compose:
1. MUST expose OpenTelemetry metrics on `/metrics`
2. MUST have a `/health` or `/healthz` endpoint
3. MUST read config from environment variables (not hardcoded)
4. MUST be optional (profile-driven, not always-on)
