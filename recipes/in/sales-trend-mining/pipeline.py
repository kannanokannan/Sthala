"""
Sales Trend Mining — thin orchestration pipeline.

Stages:
  ingest   → tally_odbc / excel / pdf / whatsapp
  extract  → LLM line-item extraction (Sarvam-30B)
  verify   → Qwen2.5-7B cross-check
  compute  → DuckDB (all analytics)
  anomaly  → Python / statsmodels
  narrate  → LLM narrative from aggregates
  report   → PDF + Excel

Run:
  python pipeline.py --profile profile.yaml --data /var/sthala/data
"""

import argparse
import yaml


def load_profile(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run(profile: dict, data_dir: str) -> None:
    print(f"[sthala] Starting sales trend mining — country={profile['country']}")
    stages = [
        "ingest",
        "extract",
        "verify",
        "compute",
        "anomaly",
        "narrate",
        "report",
    ]
    for stage in stages:
        print(f"  → {stage} (stub)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="profile.yaml")
    parser.add_argument("--data", default="/var/sthala/data")
    args = parser.parse_args()
    profile = load_profile(args.profile)
    run(profile, args.data)
