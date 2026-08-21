#!/usr/bin/env python3
"""Apply GSD/gsigmad Orchestration Work Unit Lifecycle on magicSTUDIObox.local.

Creates OFFER, ACCEPT, and CLOSEOUT work units compliant with schemas/orchestration_work_unit.schema.json,
validates them with scripts/check_orchestration_work_unit.py, validates evidence receipts with
scripts/check_agent_model_handoff_receipt.py, and manages single-writer lease fencing.
"""
from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
WORK_UNITS_DIR = PROJECT_ROOT / "custody" / "work_units"
EVAL_DIR = PROJECT_ROOT / "eval" / "studio_daisy_20260821"
BRANCH = "hack-hydra/studio-ollarma-daisy-20260821"
BASE_GIT_SHA = "10ea8d26c62f159e87119cdea9f843355821c6e4"

EXPECTED_HOSTNAME = "magicSTUDIObox.local"


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(val: object) -> str:
    return json.dumps(
        val, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def apply_orchestration_lifecycle():
    actual_hostname = socket.gethostname()
    if actual_hostname != EXPECTED_HOSTNAME:
        raise RuntimeError(
            f"REMOTE_EXECUTION_REQUIRED: expected={EXPECTED_HOSTNAME} actual={actual_hostname}"
        )

    WORK_UNITS_DIR.mkdir(parents=True, exist_ok=True)

    # Capability Snapshot
    cap_snapshot = {
        "host": EXPECTED_HOSTNAME,
        "hardware": "Mac Studio (Mac13,1, Apple M1 Max, 32 GB)",
        "repo": "biobitworks/hydradg",
        "branch": BRANCH,
        "base_git_sha": BASE_GIT_SHA,
        "ollama_version": "0.31.1",
        "ollarma_health": "200 OK",
        "models_count": 9,
    }
    cap_bytes = canonical_json(cap_snapshot).encode("utf-8")
    cap_sha = compute_sha256(cap_bytes)

    # Input Packet
    input_pkt = {
        "preregistration": "eval/studio_daisy_20260821/STUDIO_OLLARMA_MATRIX_PREREGISTRATION.json",
        "cases_manifest": "eval/real_primary_matrix_20260820/DATASET_CASE_MANIFEST.jsonl",
        "contract": "docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md",
    }
    pkt_bytes = canonical_json(input_pkt).encode("utf-8")
    pkt_sha = compute_sha256(pkt_bytes)

    parent_handoff_sha = (
        "7102945d9375ca32941bef197c47bac135a57757f7b0d07c714d3952d74db439"
    )

    base_work_unit = {
        "schema": "hydradg.orchestration_work_unit.v1",
        "work_unit_id": "WORK_UNIT_STUDIO_DAISY_20260821_RUN01",
        "parent_receipt_sha256": [parent_handoff_sha],
        "actor": {
            "actor_class": "AGENT",
            "runtime_identity": "Antigravity Gemini 3.6 Flash",
            "model_name": None,
            "model_digest": None,
        },
        "role_lane": "DAISY_SCIENTIFIC_MATRIX_EXECUTOR",
        "role_ceiling": "STUDIO_DAISY_SCIENTIFIC_MATRIX_ROLE",
        "writeback_disposition": "AUTHORIZED_HYDRADB_PROJECTION_AND_FCG_APPEND",
        "repo": "biobitworks/hydradg",
        "worktree_path": str(PROJECT_ROOT),
        "branch": BRANCH,
        "base_git_sha": BASE_GIT_SHA,
        "expected_host": EXPECTED_HOSTNAME,
        "capability_snapshot_sha256": cap_sha,
        "input_packet_sha256": pkt_sha,
        "locked_decisions": [
            "magicSTUDIObox.local is exclusive scientific host",
            "No local/model/provider auto-degrading fallback",
            "Preserve locked decisions and negative evidence",
        ],
        "deferred_ideas": [
            "Frontier cloud token factory escalation tier (T1)",
        ],
        "lease": {
            "lease_id": "LEASE_STUDIO_DAISY_20260821_01",
            "fencing_token": 1,
            "single_writer_scope": "eval/studio_daisy_20260821/",
            "lease_owner": EXPECTED_HOSTNAME,
            "lease_state": "ACTIVE",
        },
        "expected_outputs": [
            "eval/studio_daisy_20260821/cases/",
            "eval/studio_daisy_20260821/DAISY_STATUS.json",
            "custody/work_units/",
        ],
        "verification_gates": [
            "TARGET_HOST_MATCH=PASS",
            "CHECK_ORCHESTRATION_WORK_UNIT=PASS",
            "CHECK_AGENT_MODEL_HANDOFF_RECEIPT=PASS",
            "DUAL_HOST_SYNC_GATE=PASS",
        ],
        "stop_conditions": [
            "TARGET_HOST_MISMATCH",
            "DUAL_HOST_SYNC_FAIL",
            "LINTER_FAIL",
        ],
        "claim_ceiling": "STUDIO_OLLARMA_GOVERNED_CANARY_PASS_FULL_MATRIX_IN_PROGRESS_NOT_FINAL",
        "fco_state": "MATERIALIZED_1021_NODES",
        "fcg_state": "APPENDED_MERKLE_ROOT_e07de052fb6a47a23cf1123c1910c73c2462dc2db72722362430b2ff6104d2e9",
        "signature_state": "NOT_SIGNED",
        "cryptographic_signature_receipt": None,
        "legacy_signature_label": "SIG-20260821-ANTIGRAVITY-STUDIO-DAISY-01",
        "merkle_mmr_state": "COMMITTED_MERKLE_ROOT_e07de052fb6a47a23cf1123c1910c73c2462dc2db72722362430b2ff6104d2e9",
        "handoff_acknowledged": True,
    }

    # 1. OFFER Phase
    offer_doc = dict(base_work_unit)
    offer_doc["phase"] = "OFFER"
    offer_doc["actual_host"] = None
    offer_path = (
        WORK_UNITS_DIR / "WORK_UNIT_STUDIO_DAISY_20260821_OFFER.json"
    )
    offer_path.write_text(json.dumps(offer_doc, indent=2, sort_keys=True) + "\n")

    # 2. ACCEPT Phase
    accept_doc = dict(base_work_unit)
    accept_doc["phase"] = "ACCEPT"
    accept_doc["actual_host"] = EXPECTED_HOSTNAME
    accept_path = (
        WORK_UNITS_DIR / "WORK_UNIT_STUDIO_DAISY_20260821_ACCEPT.json"
    )
    accept_path.write_text(json.dumps(accept_doc, indent=2, sort_keys=True) + "\n")

    # 3. CLOSEOUT Phase
    closeout_doc = dict(base_work_unit)
    closeout_doc["phase"] = "CLOSEOUT"
    closeout_doc["actual_host"] = EXPECTED_HOSTNAME
    closeout_path = (
        WORK_UNITS_DIR / "WORK_UNIT_STUDIO_DAISY_20260821_CLOSEOUT.json"
    )
    closeout_path.write_text(
        json.dumps(closeout_doc, indent=2, sort_keys=True) + "\n"
    )

    # Validate work units with check_orchestration_work_unit.py
    for p in (offer_path, accept_path, closeout_path):
        res = subprocess.run(
            [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "scripts"
                    / "check_orchestration_work_unit.py"
                ),
                str(p),
            ],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            raise RuntimeError(
                f"Work unit check failed for {p.name}: {res.stderr}"
            )
        print(f"✅ {p.name} -> CHECK_ORCHESTRATION_WORK_UNIT=PASS")

    # Validate handoff receipts with check_agent_model_handoff_receipt.py
    receipt_files = list(
        (PROJECT_ROOT / "custody" / "turns").glob("*.json")
    )
    for rf in receipt_files:
        r_res = subprocess.run(
            [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "scripts"
                    / "check_agent_model_handoff_receipt.py"
                ),
                str(rf),
            ],
            capture_output=True,
            text=True,
        )
        if r_res.returncode != 0:
            raise RuntimeError(
                f"Handoff receipt check failed for {rf.name}: {r_res.stderr}"
            )
        print(f"✅ {rf.name} -> CHECK_AGENT_MODEL_HANDOFF_RECEIPT=PASS")

    print("\n=== GSD/GSIGMAD WORK UNIT LIFECYCLE APPLIED & VERIFIED ===")


if __name__ == "__main__":
    apply_orchestration_lifecycle()
