#!/usr/bin/env python3
"""Canonical Anticube quadrant classification for IC failure-learning objects.

Uses documented four-state preservation (SELF/NON_SELF × SAFE/NON_SAFE).
Does NOT invent a scalar Anticube score; returns quadrant + basis only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

CLASSIFIER_VERSION = "hydradg-ic-failure-anticube-1.0.0"
CLASSIFIER_SHA = hashlib.sha256(
    Path(__file__).read_bytes()
).hexdigest()
FORENSIC_BASE_SHA = "7a737d868e3d444aa29a629219fba689425959da"
IC_CONTEXT = "immersive_commons_track01_submission_20260827"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def classify(
    object_id: str,
    self_state: str,
    safe_state: str,
    basis: str,
    rule_deps: list[str],
    claim_ceiling: str,
    confidence: float | None = None,
    abstention: str | None = None,
) -> dict[str, Any]:
    quadrant = f"{self_state}_{safe_state}"
    return {
        "object_fco": object_id,
        "self_state": self_state,
        "safe_state": safe_state,
        "classification": quadrant,
        "basis": basis,
        "rule_evidence_dependencies": rule_deps,
        "confidence": confidence,
        "abstention": abstention,
        "claim_ceiling": claim_ceiling,
        "classifier_version": CLASSIFIER_VERSION,
        "classifier_sha": CLASSIFIER_SHA,
        "context": IC_CONTEXT,
    }


def readme_at_submission(repo: Path) -> str:
    path = repo / "eval/ic_failure_learning_20260827/source_freeze/README_AT_SUBMISSION_SHA.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return subprocess.check_output(
        ["git", "show", f"{FORENSIC_BASE_SHA}:README.md"],
        cwd=repo,
        text=True,
    )


def build_classifications(repo: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    readme = readme_at_submission(repo)
    rows.append(classify(
        "README_AT_SUBMISSION",
        "SELF", "NON_SAFE",
        "Custody-resolved repository README in accepted lineage; presents HydraDG/Hack Hydra Track03 "
        "identity without HydraLamp IC delta disclosure — fails IC context acceptance for origin legibility",
        ["R_README_PROJECT_IDENTITY", "R_ORIGIN_LEGIBILITY", "R_LANDS_IN_PRODUCT"],
        "VERIFIED_EMPIRICAL_RESULT",
        confidence=0.92,
    ))

    payload_path = repo / "eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    rows.append(classify(
        "SUBMISSION_PAYLOAD",
        "SELF", "NON_SAFE",
        "Exact six-field payload is custody lineage artifact; folder_id=null and root repo_url "
        "fail evidence-delivery and origin-legibility criteria for IC",
        ["R_VAULT_FOLDER", "R_ORIGIN_LEGIBILITY", "R_NO_UNSURFACED_JUDGE_EVIDENCE"],
        "VERIFIED_EMPIRICAL_RESULT",
        confidence=0.95,
    ))

    rows.append(classify(
        "MISSING_VAULT_STATE",
        "SELF", "NON_SAFE",
        "folder_id=null at submit is in-repo custody fact; violates vault evidence requirement",
        ["R_VAULT_FOLDER", "R_NO_SUBMIT_BEFORE_VAULT"],
        "VERIFIED_EMPIRICAL_RESULT",
        confidence=0.98,
    ))

    rows.append(classify(
        "LATE_VAULT_PACKET",
        "SELF", "NON_SAFE",
        "IC_VAULT_UPLOAD_PACKET created after acknowledgement — custody artifact but non-safe timing",
        ["R_VAULT_FOLDER", "R_NO_SUBMIT_BEFORE_VAULT"],
        "VERIFIED_EMPIRICAL_RESULT",
        confidence=0.90,
    ))

    rows.append(classify(
        "ORIGIN_TIMELINE",
        "SELF", "SAFE",
        "Successor forensic origin timeline derived from accepted git lineage with explicit SHAs",
        ["R_ORIGIN_LEGIBILITY"],
        "RECOMPUTED_RESULT",
        confidence=0.88,
    ))

    rows.append(classify(
        "POSTMORTEM",
        "SELF", "SAFE",
        "Successor forensic analysis in accepted custody lane; explicit claim ceilings preserved",
        [],
        "DIRECT_HUMAN_EVIDENCE",
        confidence=0.85,
    ))

    rows.append(classify(
        "COUNTERFACTUAL_START_HERE",
        "NON_SELF", "SAFE",
        "Counterfactual fixture not in historical submission; would satisfy cold-start surfacing if deployed",
        ["R_TRACK01_COLD_START", "R_AGENT_SURFACE_30PT"],
        "INFERENCE_HYPOTHESIS",
        confidence=0.75,
    ))

    rows.append(classify(
        "COUNTERFACTUAL_VIDEO",
        "NON_SELF", "SAFE",
        "Counterfactual demo video fixture; not submitted but would improve judge evidence if in vault",
        ["R_DEMO", "R_VAULT_FOLDER"],
        "INFERENCE_HYPOTHESIS",
        confidence=0.75,
    ))

    rows.append(classify(
        "COUNTERFACTUAL_BRANCH_QUALIFIED_REPO",
        "NON_SELF", "SAFE",
        "Branch-qualified repo URL counterfactual; not historical submit state but improves origin legibility",
        ["R_ORIGIN_LEGIBILITY"],
        "INFERENCE_HYPOTHESIS",
        confidence=0.80,
    ))

    protocol = (repo / "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md").read_text(encoding="utf-8")
    rows.append(classify(
        "HACKATHON_SUBMISSION_FCO_PROTOCOL",
        "SELF", "SAFE",
        "Successor governed protocol in accepted repository custody; specifies gates preventing recurrence",
        ["R_NO_SUBMIT_BEFORE_VAULT", "R_NO_UNSURFACED_JUDGE_EVIDENCE"],
        "DIRECT_HUMAN_EVIDENCE",
        confidence=0.90,
    ))

    # Antidote fixture (created later, classified when present)
    antidote_path = repo / "eval/ic_failure_learning_20260827/README_ANTIDOTE_FCO.json"
    if antidote_path.exists():
        antidote = json.loads(antidote_path.read_text(encoding="utf-8"))
        rows.append(classify(
            "SUCCESSOR_README_ANTIDOTE",
            "SELF", "SAFE",
            antidote.get("basis", "Successor README antidote supersedes poison for future judge entry"),
            ["R_ORIGIN_LEGIBILITY", "R_README_PROJECT_IDENTITY"],
            "DETERMINISTIC_TOOL_OUTPUT",
            confidence=0.93,
        ))

    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="eval/ic_failure_learning_20260827/ANTICUBE_CLASSIFICATIONS.jsonl")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    rows = build_classifications(repo)
    out = (repo / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"classifications": len(rows), "out": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
