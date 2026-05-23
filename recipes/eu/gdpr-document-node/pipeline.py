"""
GDPR Document Node (EU) — thin orchestration pipeline stub.

Stages:
  ingest    → file_drop (PDF, DOCX, email exports)
  pii       → local NER — detect personal data categories
  classify  → LLM document type + legal basis classification
  dsar      → DuckDB — match all records for a data subject
  redact    → deterministic PII scrub (not LLM)
  respond   → LLM DSAR response draft (no PII in prompt)
  audit     → immutable audit log entry

Run:
  python pipeline.py --profile profile.yaml --data /var/sthala/data
"""

import argparse
import yaml


def load_profile(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run(profile: dict, data_dir: str) -> None:
    print(f"[sthala] Starting GDPR document node — country={profile['country']}")
    stages = ["ingest", "pii", "classify", "dsar", "redact", "respond", "audit"]
    for stage in stages:
        print(f"  → {stage} (stub)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="profile.yaml")
    parser.add_argument("--data", default="/var/sthala/data")
    args = parser.parse_args()
    profile = load_profile(args.profile)
    run(profile, args.data)
