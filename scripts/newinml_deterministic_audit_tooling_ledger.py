#!/usr/bin/env python3
"""Build DETERMINISTIC_AUDIT_TOOLING_LEDGER.jsonl for NewInML custody gates."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/newinml2026_solo/license_audit/DETERMINISTIC_AUDIT_TOOLING_LEDGER.jsonl"


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip()


def tracked(path: Path) -> bool:
    r = subprocess.run(["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))], cwd=ROOT, capture_output=True)
    return r.returncode == 0


def tool_record(
    *,
    tool_id: str,
    script_path: str,
    classification: str,
    scientific_validity: str,
    inputs: list[str],
    input_roots: list[str],
    deterministic_transform: str,
    outputs: list[str],
    r1: str,
    r2: str,
    r3: str,
    failure_canaries: list[str],
    receipt_path: str | None = None,
) -> dict[str, Any]:
    p = ROOT / script_path
    return {
        "tool_id": tool_id,
        "script_path": script_path,
        "git_sha": git_sha(),
        "script_sha256": sha256_file(p) if p.is_file() else None,
        "origin_tracked": tracked(p) if p.is_file() else False,
        "inputs": inputs,
        "input_roots": input_roots,
        "deterministic_transform": deterministic_transform,
        "outputs": outputs,
        "receipt": receipt_path,
        "R1_state": r1,
        "R2_state": r2,
        "R3_state": r3,
        "known_failure_canaries": failure_canaries,
        "scientific_validity_classification": scientific_validity,
        "audit_tool_classification": classification,
        "recorded_at_utc": utc(),
    }


def main() -> int:
    records = [
        tool_record(
            tool_id="REQ-CIT-SEEDGRAPH-AUDIT",
            script_path="scripts/newinml_requirement_citation_seedgraph_audit.py",
            classification="DETERMINISTIC_WITH_IMPLEMENTATION_SPECIFIC_PROFILE",
            scientific_validity="COMPLIANCE_AND_CITATION_CUSTODY_VALID",
            inputs=["main.tex", "references.bib", "official NeurIPS style freeze"],
            input_roots=["paper/newinml2026_solo/final_v4/manuscript", "paper/newinml2026_solo/requirement_citation_audit"],
            deterministic_transform="freeze sources -> parse bib/cites -> numeric lineage -> seedgraph segments",
            outputs=["paper/newinml2026_solo/requirement_citation_audit/*"],
            r1="PASS",
            r2="PASS",
            r3="PASS",
            failure_canaries=["network_fetch_optional", "hallucinated_reference_injection"],
            receipt_path="paper/newinml2026_solo/requirement_citation_audit/AUDIT_RECEIPT.json",
        ),
        tool_record(
            tool_id="CUSTODY-AUDIT",
            script_path="scripts/custody_audit.py",
            classification="DETERMINISTIC_VERIFIED",
            scientific_validity="CUSTODY_MECHANICS_VALID_NOT_SCIENCE_CLAIM",
            inputs=["hydradg repo", "seedgraph root", "store roots"],
            input_roots=["eval/custody_audit_20260829", "/Users/byron/projects/active/seedgraph"],
            deterministic_transform="gsigmad.custody_audit.runner -> R1/R2/R3 reproducibility vectors",
            outputs=["eval/custody_audit_*/CUSTODY_AUDIT_RECEIPT.json"],
            r1="PASS",
            r2="PASS",
            r3="PASS",
            failure_canaries=["missing_seedgraph_head", "store_hash_mismatch"],
            receipt_path="eval/custody_audit_20260829/CUSTODY_AUDIT_RECEIPT.json",
        ),
        tool_record(
            tool_id="GUM-DOCTOR-V2",
            script_path="scripts/gum_doctor_v2.py",
            classification="DETERMINISTIC_WITH_IMPLEMENTATION_SPECIFIC_PROFILE",
            scientific_validity="HOST_CAPABILITY_DIAGNOSTIC_NOT_EMPIRICAL_RESULT",
            inputs=["keys.env names only", "repo paths", "CFOS roots"],
            input_roots=["eval/newinml_final_daisy_20260829/execution/lane0_gum"],
            deterministic_transform="capability snapshot + credential presence matrix (no secret bytes)",
            outputs=["eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_AFTER.json"],
            r1="PASS",
            r2="PASS",
            r3="NOT_RUN",
            failure_canaries=["missing_DAYTONA_API_KEY", "swap_pressure_high"],
            receipt_path="eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_AFTER.json",
        ),
        tool_record(
            tool_id="FINAL-V3-SUBMISSION",
            script_path="scripts/newinml_final_v3_submission.py",
            classification="DETERMINISTIC_WITH_IMPLEMENTATION_SPECIFIC_PROFILE",
            scientific_validity="SUBMISSION_PACKAGING_VALID_NOT_SCIENCE_CLAIM",
            inputs=["manuscript build artifacts", "FINAL_SUBMISSION_READINESS.json"],
            input_roots=["paper/newinml2026_solo"],
            deterministic_transform="generate reviewer bundle + readiness manifest from frozen inputs",
            outputs=["paper/newinml2026_solo/reviewer_artifact/*", "paper/newinml2026_solo/FINAL_SUBMISSION_READINESS.json"],
            r1="PASS",
            r2="PASS",
            r3="PASS",
            failure_canaries=["pdf_sha_mismatch", "anonymization_leak"],
            receipt_path="paper/newinml2026_solo/FINAL_SUBMISSION_READINESS.json",
        ),
        tool_record(
            tool_id="INVENTORY-GATE",
            script_path="scripts/newinml_final_inventory_gate.py",
            classification="DETERMINISTIC_VERIFIED",
            scientific_validity="INVENTORY_COUNTS_VALID_NOT_SCIENCE_CLAIM",
            inputs=["main.tex", "references.bib", "build/main.pdf", "NUMERIC_VALUE_LINEAGE.jsonl"],
            input_roots=["paper/newinml2026_solo/final_v4/manuscript", "paper/newinml2026_solo/final_inventory"],
            deterministic_transform="recompute figure/table/page/citation inventory without PDF mutation",
            outputs=["paper/newinml2026_solo/final_inventory/*"],
            r1="PASS",
            r2="PASS",
            r3="NOT_RUN",
            failure_canaries=["baseline_count_drift", "pdf_sha_mismatch"],
            receipt_path="paper/newinml2026_solo/final_inventory/SUBMISSION_ARTIFACT_INVENTORY.json",
        ),
        tool_record(
            tool_id="TERMINOLOGY-SEEDGRAPH-EXECUTOR",
            script_path="scripts/cursor_terminology_seedgraph_anticube_execute.py",
            classification="SCAFFOLDING_NOT_SCIENTIFICALLY_VALIDATED",
            scientific_validity="DISCOVERY_ONLY_PRIOR_ART_NOT_VERIFIED_EMPIRICAL",
            inputs=["main.tex", "Crossref API responses", "TOTAL_SOURCE_UNIVERSE"],
            input_roots=["research/terminology", "research/search", "paper/newinml2026_solo/federated_evidence"],
            deterministic_transform="terminology matrix + frozen search responses + seedgraph batch (prior-art lane DISCOVERY_ONLY)",
            outputs=["research/search/SEARCH_RUN_LEDGER.jsonl", "eval/terminology_seedgraph_anticube_20260829/STAGE-001_CLOSEOUT.json"],
            r1="PASS",
            r2="PARTIAL",
            r3="NOT_RUN",
            failure_canaries=["placeholder_prior_art_hits_REMOVED", "network_fetch_fail", "GPU_blocked"],
            receipt_path="eval/terminology_seedgraph_anticube_20260829/STAGE-001_CLOSEOUT.json",
        ),
        tool_record(
            tool_id="GITHUB-WORKFLOW-FINAL-VERIFICATION",
            script_path=".github/workflows/newinml-final-verification.yml",
            classification="DETERMINISTIC_WITH_IMPLEMENTATION_SPECIFIC_PROFILE",
            scientific_validity="CI_ATTESTATION_VALID_NOT_SCIENCE_CLAIM",
            inputs=["committed PDF", "verify_submission.py", "FINAL_SUBMISSION_READINESS.json"],
            input_roots=["paper/newinml2026_solo"],
            deterministic_transform="CI attestation over frozen submission bundle",
            outputs=["FINAL_GITHUB_ACTION_ATTESTATION.json"],
            r1="PASS",
            r2="PASS",
            r3="NOT_RUN",
            failure_canaries=["anonymization_scan_fail", "pdf_sha_mismatch"],
            receipt_path=".github/workflows/newinml-final-verification.yml",
        ),
        tool_record(
            tool_id="LICENSE-AUDIT",
            script_path="scripts/newinml_license_audit.py",
            classification="DETERMINISTIC_VERIFIED",
            scientific_validity="COMPLIANCE_EVIDENCE_NOT_LEGAL_DETERMINATION",
            inputs=["LICENSE", "OpenReview requirement atoms", "manuscript artifacts"],
            input_roots=["paper/newinml2026_solo/license_audit"],
            deterministic_transform="artifact license ledger + anticube timeline + synthetic canaries",
            outputs=["paper/newinml2026_solo/license_audit/LICENSE_AUDIT_RECEIPT.json"],
            r1="PASS",
            r2="PASS",
            r3="PASS",
            failure_canaries=["license_unknown_dependency", "secret_in_bundle"],
            receipt_path="paper/newinml2026_solo/license_audit/LICENSE_AUDIT_RECEIPT.json",
        ),
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n")
    summary = {
        "DETERMINISTIC_AUDIT_TOOLS_VERIFIED": len([r for r in records if r["audit_tool_classification"] == "DETERMINISTIC_VERIFIED"]),
        "DETERMINISTIC_AUDIT_TOOLS_SCAFFOLDING": len([r for r in records if "SCAFFOLDING" in r["audit_tool_classification"]]),
        "LOCAL_UNCOMMITTED_AUDIT_TOOLS": len([r for r in records if not r["origin_tracked"]]),
        "ledger_path": str(OUT.relative_to(ROOT)),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
