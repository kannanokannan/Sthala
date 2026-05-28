# Sthala

**Your AI's place.**

Most AI deployments let LLMs touch everything — computation, decisions, execution. That's the failure mode. Sthala is built on one hard constraint: LLMs narrate, code executes. Always. Enforced at build time.

An open-source reference framework for sovereign, on-premise AI on commodity x86 hardware. Airgapped by default. Built for SMBs, CA firms, clinics, schools — any organisation where data must not leave the building.

> *"Sthala" (स्थल / ஸ்தலம்) — place, site, ground. Where your AI actually runs.*

---

## Why Sthala

- **Cloud AI is expensive** — 3-year TCO cloud vs Sthala appliance: ~6× savings
- **Compliance is tightening** — EU AI Act (Aug 2026), India DPDP Act (Stage 2: Nov 2026), MCA backup mandates
- **LLMs are commodities** — the moat is the pipeline, not the model
- **Refurb hardware works** — a ₹1.5L box serves 50–200 concurrent SMB users on 7B–34B models

Sthala is **not** a product. It is a documented pattern. Read it, fork it, deploy it, adapt it.

---

## Family

| Project | Role |
|---|---|
| [ContextOps](https://github.com/kannanokannan/ContextOps) | How to govern AI context |
| [ContextBoundary](https://github.com/kannanokannan/ContextBoundary) | Where AI context can flow |
| **Sthala** | Where AI actually runs |

---

## What You Get

```
Boot a commodity PC → drop your data → get AI-powered analysis
Nothing leaves your box unless you explicitly approve it
```

- Immutable Linux base (no drift, atomic updates)
- Sarvam-30B default (Apache 2.0, Indic-optimised, 24GB VRAM Q6_K)
- Multi-model verifier pipeline (LLM extracts → code computes → LLM narrates)
- Egress consent gateway (you see what leaves, you approve every send)
- Vertical recipes: CA firm, distributor, school, clinic

---

## Quick Start

```bash
curl -fsSL https://raw.githubusercontent.com/kannanokannan/sthala/main/install.sh | bash
```

Or with a profile:

```bash
curl -fsSL .../install.sh | bash -s -- --profile ca-firm
```

---

## Repository Structure

```
sthala/
├── SPEC.md                    ← Framework specification
├── AGENTS.md                  ← Machine-readable build contract for AI coding agents
├── CLAUDE.md                  ← Context file for Claude / AI assistants
├── install.sh                 ← Idempotent bootstrap script
├── profiles/                  ← Vertical presets
│   ├── generic.yaml
│   ├── ca-firm.yaml
│   ├── distributor.yaml
│   └── school.yaml
├── hardware/
│   └── detect.sh              ← Auto-detect CPU/GPU/RAM, recommend tier
├── stack/
│   └── docker-compose.yml     ← Full service stack
├── models/
│   └── models.md              ← Curated model catalog with HuggingFace links
├── recipes/
│   ├── tally-ca-copilot/      ← CA firm + Tally integration recipe
│   └── sales-trend-mining/    ← Distributor trend analysis recipe
├── research/
│   ├── 2026-05-market.md      ← India SMB AI market research
│   └── 2026-05-standards.md   ← Standards & academic landscape
└── docs/
    └── architecture.md        ← Architecture deep-dive
```

---

## Design Principles

1. **LLM-as-component, not LLM-as-magic** — LLM extracts, code computes, LLM narrates
2. **Deterministic compute, fuzzy understanding** — numbers never come from an LLM
3. **Egress-by-consent** — nothing leaves without explicit human approval
4. **Commodity hardware first** — if it needs a $30K GPU, it's out of scope
5. **Vertical recipes over generic stacks** — a CA firm is not a chatbot

---

## Standards Alignment

- NIST AI RMF 1.0 + GenAI Profile
- ISO/IEC 42001 (AI management systems)
- EU AI Act (non-high-risk tier by default)
- India DPDP Act 2023 compliance posture
- 16-Factor App for AI (Google, 2024)
- OpenTelemetry GenAI semantic conventions
- CycloneDX 1.7 AI BOM auto-generated

---

## License

Apache 2.0 — use it, fork it, ship it, build on it.

---

## Author

[Kannan Okannan](https://github.com/kannanokannan) — Chennai, India

*Part of the ContextOps / ContextBoundary / Sthala open-source family.*

---

## Part of the Stack

This project is one of three sibling open-source projects under [github.com/kannanokannan](https://github.com/kannanokannan).

| Project | Question | Repo |
|---------|----------|------|
| ContextOps | How does an org govern its AI context? | [github.com/kannanokannan/ContextOps](https://github.com/kannanokannan/ContextOps) |
| ContextBoundary | Where is data allowed to go? | [github.com/kannanokannan/ContextBoundary](https://github.com/kannanokannan/ContextBoundary) |
| Sthala | Where does the AI actually run? | [github.com/kannanokannan/Sthala](https://github.com/kannanokannan/Sthala) |

Canonical terminology and cross-project decisions: [context-stack](https://github.com/kannanokannan/context-stack)
