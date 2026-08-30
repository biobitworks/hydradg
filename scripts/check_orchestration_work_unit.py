#!/usr/bin/env python3
"""Fail-closed structural checker for HydraDG orchestration work units.

This validates the meta-orchestration envelope. It does not establish scientific
correctness, FCO/FCG validity, cryptographic signature validity, or Merkle/MMR
commitment by itself.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = (
    "schema", "work_unit_id", "phase", "actor", "role_lane", "role_ceiling",
    "writeback_disposition", "repo", "branch", "base_git_sha", "expected_host",
    "capability_snapshot_sha256", "input_packet_sha256", "lease",
    "expected_outputs", "verification_gates", "stop_conditions", "claim_ceiling",
    "fco_state", "fcg_state", "signature_state", "merkle_mmr_state",
)
PHASES = {"OFFER", "ACCEPT", "CHECKPOINT", "CLOSEOUT"}
SIG_STATES = {"NOT_SIGNED", "PENDING_EXTERNAL_PRIVATE_KEY_OPERATION", "SIGNED_VERIFIED"}


def fail(msg: str) -> None:
    raise ValueError(msg)


def check(path: Path) -> None:
    doc = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in doc]
    if missing:
        fail(f"missing required fields: {', '.join(missing)}")
    if doc["schema"] != "hydradg.orchestration_work_unit.v1":
        fail("unsupported schema")
    if doc["phase"] not in PHASES:
        fail(f"invalid phase: {doc['phase']}")
    if not HEX40.fullmatch(str(doc["base_git_sha"])):
        fail("base_git_sha must be full 40-hex Git commit")
    for key in ("capability_snapshot_sha256", "input_packet_sha256"):
        if not HEX64.fullmatch(str(doc[key])):
            fail(f"{key} must be 64 lowercase hex")
    for h in doc.get("parent_receipt_sha256", []):
        if not HEX64.fullmatch(str(h)):
            fail("parent_receipt_sha256 contains non-SHA256 value")
    if doc["phase"] != "OFFER":
        actual = doc.get("actual_host")
        if not actual:
            fail("actual_host required after OFFER")
        if actual != doc["expected_host"]:
            fail(f"host mismatch expected={doc['expected_host']} actual={actual}")
    actor = doc["actor"]
    if not isinstance(actor, dict) or not actor.get("actor_class") or not actor.get("runtime_identity"):
        fail("actor must include actor_class and runtime_identity")
    lease = doc["lease"]
    for key in ("lease_id", "fencing_token", "single_writer_scope", "lease_owner", "lease_state"):
        if key not in lease:
            fail(f"lease missing {key}")
    if not isinstance(lease["fencing_token"], int) or lease["fencing_token"] < 1:
        fail("fencing_token must be a positive integer")
    for key in ("expected_outputs", "verification_gates", "stop_conditions"):
        if not isinstance(doc[key], list) or not doc[key]:
            fail(f"{key} must be a non-empty list")
    sig_state = doc["signature_state"]
    if sig_state not in SIG_STATES:
        fail(f"invalid signature_state: {sig_state}")
    if sig_state == "SIGNED_VERIFIED" and not doc.get("cryptographic_signature_receipt"):
        fail("SIGNED_VERIFIED requires cryptographic_signature_receipt")
    # A legacy SIG-* label never upgrades cryptographic state.
    if doc.get("legacy_signature_label") and sig_state == "SIGNED_VERIFIED" and not doc.get("cryptographic_signature_receipt"):
        fail("legacy signature label cannot establish SIGNED_VERIFIED")
    print(f"ORCHESTRATION_WORK_UNIT=PASS path={path}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"usage: {argv[0]} <work-unit.json> [<work-unit2.json> ...]", file=sys.stderr)
        return 2
    rc = 0
    for raw in argv[1:]:
        path = Path(raw)
        try:
            check(path)
        except Exception as exc:
            rc = 1
            print(f"ORCHESTRATION_WORK_UNIT=FAIL path={path} reason={exc}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
