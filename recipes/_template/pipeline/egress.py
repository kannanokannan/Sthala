"""
Stage 6 — EGRESS (optional, Tier 3 only)
Input:  Narrated report from Stage 5
Output: Sent to external paid API (e.g., Claude API for polish)
Rules:  Only runs if profile egress.tier == 3
        PII must be scrubbed before this stage
        Operator must preview payload and click Approve
        Every call is audit-logged
"""
import argparse
import logging
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--data",    required=True)
    p.add_argument("--log",     required=True)
    return p.parse_args()


def egress(report: str, profile: dict, data_dir: Path, log: str) -> str:
    """
    Send anonymised report to external API for polish (Tier 3 only).
    Blocks for operator approval before sending.
    Returns polished report text.
    """
    logging.basicConfig(filename=log, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    tier = profile.get("egress", {}).get("tier", 1)
    if tier < 3:
        logger.info("egress skipped: tier < 3")
        return report

    # Hard assertion: PII must be scrubbed
    assert not _contains_pii(report), "PII detected in egress payload — aborting"

    # Operator consent gate
    approved = _request_approval(report)
    if not approved:
        logger.warning("egress declined by operator")
        return report

    polished = _call_external_api(report, profile)
    logger.info("egress complete: external API call approved and logged")
    return polished


def _contains_pii(text: str) -> bool:
    """
    Deterministic PII check before any egress.
    TODO: implement NER-based check.
    """
    return False


def _request_approval(payload: str) -> bool:
    """
    Show operator a preview and wait for approval.
    In production: opens web UI approval dialog.
    """
    print("\n--- EGRESS PREVIEW ---")
    print(payload[:500], "..." if len(payload) > 500 else "")
    print("--- END PREVIEW ---")
    answer = input("Approve egress? [y/N]: ").strip().lower()
    return answer == "y"


def _call_external_api(report: str, profile: dict) -> str:
    """
    Call external paid API (Anthropic / OpenAI) for narrative polish.
    TODO: implement via LiteLLM Tier 3 route.
    """
    return report


if __name__ == "__main__":
    args = parse_args()
    import yaml
    profile = yaml.safe_load(open(args.profile))
    egress("", profile, Path(args.data), args.log)
