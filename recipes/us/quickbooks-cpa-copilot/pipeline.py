"""
QuickBooks CPA Copilot (US) — thin orchestration pipeline stub.

Stages:
  ingest   → quickbooks IIF/CSV or QBO local proxy
  extract  → LLM structured JSON (Llama-3.1-8B for English)
  verify   → citation cross-check
  compute  → DuckDB (P&L, AR/AP, ratios)
  anomaly  → Python / statsmodels
  narrate  → LLM narrative
  report   → PDF

Run:
  python pipeline.py --profile profile.yaml --data /var/sthala/data
"""

import argparse
import yaml


def load_profile(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run(profile: dict, data_dir: str) -> None:
    print(f"[sthala] Starting QuickBooks CPA copilot — country={profile['country']}")
    stages = ["ingest", "extract", "verify", "compute", "anomaly", "narrate", "report"]
    for stage in stages:
        print(f"  → {stage} (stub)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="profile.yaml")
    parser.add_argument("--data", default="/var/sthala/data")
    args = parser.parse_args()
    profile = load_profile(args.profile)
    run(profile, args.data)
