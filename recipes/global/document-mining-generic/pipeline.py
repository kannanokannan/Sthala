"""
Document Mining Generic — thin orchestration pipeline.

Stages:
  ingest  → file_drop (PDF, Excel, images)
  extract → LLM structured JSON
  verify  → citation cross-check
  embed   → Qdrant vector store
  serve   → RAG Q&A via /v1/chat

Run:
  python pipeline.py --profile profile.yaml --data /var/sthala/data
"""

import argparse
import yaml


def load_profile(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run(profile: dict, data_dir: str) -> None:
    print(f"[sthala] Starting document mining — country={profile['country']}")
    stages = ["ingest", "extract", "verify", "embed", "serve"]
    for stage in stages:
        print(f"  → {stage} (stub)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="profile.yaml")
    parser.add_argument("--data", default="/var/sthala/data")
    args = parser.parse_args()
    profile = load_profile(args.profile)
    run(profile, args.data)
