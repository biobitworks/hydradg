#!/usr/bin/env python3
"""Freeze forensic source objects for IC failure-learning experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

EXPECTED_PAYLOAD_SHA = "230bd00a6d95e57d423dd26d2be18512c2041030f1b7007bdb0374a85722611d"
FORENSIC_BASE_SHA = "7a737d868e3d444aa29a629219fba689425959da"

SOURCES: list[dict[str, Any]] = [
    {
        "path": "eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json",
        "evidence_class": "DIRECT_HUMAN_EVIDENCE",
        "historical_or_successor": "historical",
        "role": "ACTUAL_SUBMISSION_PAYLOAD",
        "training_visibility": "EVAL_ONLY",
        "evaluation_visibility": "BLIND_ALLOWED_FIELDS_ONLY",
    },
    {
        "path": "eval/immersive_commons_submission_20260827/IC_SUBMIT_RECEIPT.json",
        "evidence_class": "EXTERNALLY_RETRIEVED_EVIDENCE",
        "historical_or_successor": "historical",
        "role": "SUBMISSION_ACKNOWLEDGEMENT",
        "training_visibility": "EVAL_ONLY",
        "evaluation_visibility": "EVAL_ONLY",
    },
    {
        "path": "eval/ic_postmortem_20260827/ACTUAL_SUBMISSION_FREEZE.json",
        "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
        "historical_or_successor": "historical",
        "role": "ACTUAL_SUBMISSION_FREEZE",
        "training_visibility": "EVAL_ONLY",
        "evaluation_visibility": "EVAL_ONLY",
    },
    {
        "path": "eval/ic_postmortem_20260827/IC_RUBRIC_SNAPSHOT.json",
        "evidence_class": "EXTERNALLY_RETRIEVED_EVIDENCE",
        "historical_or_successor": "historical",
        "role": "IC_RUBRIC_SNAPSHOT",
        "training_visibility": "M1_RULE_CONTEXT",
        "evaluation_visibility": "M1_ALLOWED",
    },
    {
        "path": "eval/ic_postmortem_20260827/IC_TOOL_SCHEMA_SNAPSHOT.json",
        "evidence_class": "EXTERNALLY_RETRIEVED_EVIDENCE",
        "historical_or_successor": "historical",
        "role": "IC_TOOL_SCHEMA_SNAPSHOT",
        "training_visibility": "M1_RULE_CONTEXT",
        "evaluation_visibility": "M1_ALLOWED",
    },
    {
        "path": "eval/ic_postmortem_20260827/POSTMORTEM.md",
        "evidence_class": "DIRECT_HUMAN_EVIDENCE",
        "historical_or_successor": "historical",
        "role": "POSTMORTEM",
        "training_visibility": "M2_FAILURE_CONTEXT",
        "evaluation_visibility": "EVAL_ONLY",
    },
    {
        "path": "eval/ic_postmortem_20260827/EARLIEST_DIVERGENCE.json",
        "evidence_class": "RECOMPUTED_RESULT",
        "historical_or_successor": "historical",
        "role": "EARLIEST_DIVERGENCE",
        "training_visibility": "EVAL_ONLY",
        "evaluation_visibility": "EVAL_ONLY",
    },
    {
        "path": "eval/ic_postmortem_20260827/ORIGIN_PROVENANCE_AUDIT.json",
        "evidence_class": "RECOMPUTED_RESULT",
        "historical_or_successor": "historical",
        "role": "ORIGIN_PROVENANCE",
        "training_visibility": "M2_FAILURE_CONTEXT",
        "evaluation_visibility": "EVAL_ONLY",
    },
    {
        "path": "eval/ic_postmortem_20260827/MULTIMODAL_EVIDENCE_COVERAGE.json",
        "evidence_class": "RECOMPUTED_RESULT",
        "historical_or_successor": "historical",
        "role": "MULTIMODAL_EVIDENCE_COVERAGE",
        "training_visibility": "M2_FAILURE_CONTEXT",
        "evaluation_visibility": "EVAL_ONLY",
    },
    {
        "path": "eval/ic_postmortem_20260827/IC_RUBRIC_ACTUAL_SCORE_ESTIMATE.json",
        "evidence_class": "INFERENCE_HYPOTHESIS",
        "historical_or_successor": "historical",
        "role": "ACTUAL_SCORE_RANGE",
        "training_visibility": "EVAL_ONLY",
        "evaluation_visibility": "EVAL_ONLY",
    },
    {
        "path": "eval/ic_postmortem_20260827/IC_RUBRIC_COUNTERFACTUAL_SCORE_ESTIMATE.json",
        "evidence_class": "INFERENCE_HYPOTHESIS",
        "historical_or_successor": "historical",
        "role": "COUNTERFACTUAL_SCORE_RANGE",
        "training_visibility": "EVAL_ONLY",
        "evaluation_visibility": "EVAL_ONLY",
    },
    {
        "path": "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md",
        "evidence_class": "DIRECT_HUMAN_EVIDENCE",
        "historical_or_successor": "successor",
        "role": "HACKATHON_SUBMISSION_FCO_PROTOCOL",
        "training_visibility": "M1_M2_CONTEXT",
        "evaluation_visibility": "M2_ALLOWED",
    },
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(repo: Path, rel: str) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "hash-object", rel],
            cwd=repo,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="eval/ic_failure_learning_20260827/source_freeze/SOURCE_FREEZE_MANIFEST.json")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    out = (repo / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    for spec in SOURCES:
        path = repo / spec["path"]
        if not path.exists():
            entries.append({**spec, "status": "MISSING", "sha256": None, "bytes": None})
            continue
        raw = path.read_bytes()
        digest = sha256_bytes(raw)
        entry = {
            **spec,
            "status": "FROZEN",
            "sha256": digest,
            "bytes": len(raw),
            "git_blob_sha": git_blob_sha(repo, spec["path"]),
            "source_commit": FORENSIC_BASE_SHA,
        }
        entries.append(entry)

    payload_entry = next(
        (e for e in entries if e.get("role") == "ACTUAL_SUBMISSION_PAYLOAD"),
        None,
    )
    if payload_entry and payload_entry.get("sha256") != EXPECTED_PAYLOAD_SHA:
        raise SystemExit(
            f"STOP: payload SHA mismatch {payload_entry.get('sha256')} != {EXPECTED_PAYLOAD_SHA}"
        )

    readme_raw = subprocess.check_output(
        ["git", "show", f"{FORENSIC_BASE_SHA}:README.md"],
        cwd=repo,
        stderr=subprocess.DEVNULL,
    )
    readme_digest = sha256_bytes(readme_raw)
    readme_out = out.parent / "README_AT_SUBMISSION_SHA.md"
    readme_out.write_bytes(readme_raw)
    entries.append({
        "path": str(readme_out.relative_to(repo)),
        "evidence_class": "DIRECT_HUMAN_EVIDENCE",
        "historical_or_successor": "historical",
        "role": "README_AT_SUBMISSION_OR_APPROVAL_SHA",
        "training_visibility": "E07_FIXTURE",
        "evaluation_visibility": "BLIND_ALLOWED",
        "status": "FROZEN",
        "sha256": readme_digest,
        "bytes": len(readme_raw),
        "git_blob_sha": git_blob_sha(repo, "README.md"),
        "source_commit": FORENSIC_BASE_SHA,
    })

    manifest = {
        "schema": "hydradg.ic_failure_learning.source_freeze.v1",
        "base_forensic_sha": FORENSIC_BASE_SHA,
        "historical_submission_payload_sha256": EXPECTED_PAYLOAD_SHA,
        "entry_count": len(entries),
        "entries": entries,
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
        "CLAIM_CEILING": "SOURCE_IDENTITY_ONLY",
    }
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"frozen": len([e for e in entries if e.get("status") == "FROZEN"]), "out": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
