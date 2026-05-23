"""
Tally CA Copilot — thin orchestration pipeline.

Stages:
  ingest   → tally_odbc / file_drop
  extract  → LLM structured JSON (Sarvam-30B)
  verify   → citation cross-check (Qwen2.5-7B)
  compute  → DuckDB (all numeric work)
  anomaly  → Python / scipy
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
    print(f"[sthala] Starting CA copilot pipeline — country={profile['country']}")
    # TODO: wire up each stage
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
