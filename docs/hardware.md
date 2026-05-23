# Sthala Hardware Tiers

Hardware is classified into four tiers. All prices are approximate USD (2026).
The framework runs on all tiers — GPU accelerates, CPU is baseline.

---

## Tier 1 — CPU Only (Entry)

**Target:** Small office, school, clinic, proof-of-concept

| Component | Specification | Approx. Cost |
|---|---|---|
| CPU | Intel Core i7-12700 / AMD Ryzen 7 5800X or better | $250–350 |
| RAM | 32GB DDR4 (2× 16GB) | $60–80 |
| Storage | 1TB NVMe SSD | $80–100 |
| PSU | 450W 80+ Bronze | $50 |
| Case + Cooling | Mid-tower, air cooling | $80–120 |
| **Total** | | **~$520–650** |

**Model defaults (Tier 1):**
- Primary: Phi-3-mini Q4 (~2GB VRAM) or Llama-3.1-8B Q4 (CPU)
- Verifier: Qwen2.5-1.5B Q4
- Throughput: 3–8 tok/s (batch overnight recommended)

---

## Tier 2 — Mid GPU (Recommended)

**Target:** CA firm (10–50 clients), distributor, mid-size school

| Component | Specification | Approx. Cost |
|---|---|---|
| CPU | Intel Core i9-13900K / AMD Ryzen 9 7900X | $400–500 |
| RAM | 64GB DDR5 (2× 32GB) | $130–160 |
| GPU | NVIDIA RTX 3090 (24GB VRAM) | $800–1000 |
| Storage | 2TB NVMe SSD | $150–180 |
| PSU | 850W 80+ Gold | $120 |
| Case + Cooling | Mid-tower, 360mm AIO | $150–200 |
| **Total** | | **~$1750–2160** |

**Model defaults (Tier 2):**
- Primary: Sarvam-30B Q6_K (India) / Llama-3.1-8B Q4 (global)
- Verifier: Qwen2.5-7B Q4_K_M
- Throughput: 15–40 tok/s

---

## Tier 3 — High GPU (Performance)

**Target:** Large CA firm (100+ clients), hospital, university

| Component | Specification | Approx. Cost |
|---|---|---|
| CPU | AMD Threadripper 7960X / Intel Xeon W | $1400–2000 |
| RAM | 128GB DDR5 ECC | $400–600 |
| GPU | NVIDIA RTX 4090 (24GB VRAM) | $1600–1800 |
| Storage | 4TB NVMe SSD (RAID 1 recommended) | $400–500 |
| PSU | 1200W 80+ Platinum | $200 |
| Server Case | 4U rackmount | $300–500 |
| **Total** | | **~$4300–5600** |

**Model defaults (Tier 3):**
- Primary: Sarvam-30B Q6_K or Qwen2.5-14B Q6_K
- Verifier: Qwen2.5-7B Q4_K_M
- Throughput: 50–100 tok/s

---

## Tier 4 — Dual GPU (Enterprise)

**Target:** Government, large hospital network, multi-branch firm

| Component | Specification | Approx. Cost |
|---|---|---|
| CPU | AMD Threadripper Pro 7985WX | $4000–5000 |
| RAM | 256GB DDR5 ECC | $1200–1600 |
| GPU | 2× NVIDIA RTX 4090 (2× 24GB VRAM) | $3200–3600 |
| Storage | 8TB NVMe (RAID 10) | $1200–1600 |
| PSU | 1600W redundant | $500 |
| Workstation case | Tower workstation | $500–800 |
| **Total** | | **~$10600–12600** |

**Model defaults (Tier 4):**
- Primary: Qwen2.5-32B Q6_K or custom fine-tune
- Throughput: 120–200 tok/s

---

## Hardware Detection

Run the auto-detect script to get a tier recommendation:

```bash
bash hardware/detect.sh
```

Output example:
```
[sthala-detect] CPU: AMD Ryzen 9 7900X (12 cores)
[sthala-detect] RAM: 64GB
[sthala-detect] GPU: NVIDIA RTX 3090 (24GB VRAM)
[sthala-detect] → Recommended tier: 2
[sthala-detect] → Suggested profile: --profile accounting-firm
[sthala-detect] → Suggested model:   Sarvam-30B Q6_K
```

---

## Notes

- All tiers run without internet at inference time
- `install.sh` requires internet for initial model download
- GPU is optional — Tier 1 CPU-only mode is fully supported
- ECC RAM recommended for Tier 3+ (data integrity on long batch jobs)
- Tailscale provides zero-config remote access without opening firewall ports
