#!/usr/bin/env python3
"""Fail-closed structural linter for HydraDG agent/model handoff receipts.

This checker validates the baseline custody contract without requiring third-party
packages. It does NOT prove that hashes, FCG roots, signatures, or readbacks are
truthful; those claims require independent recomputation/verification.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SHA_STATES = {
    "GENESIS",
    "NOT_AVAILABLE",
    "NOT_APPLICABLE",
    "NOT_APPENDED",
    "NOT_PROJECT_COMMITTED",
    "PENDING_ORIGINAL_TURN_CAPTURE",
    "PENDING_EXTERNAL_PRIVATE_KEY_OPERATION",
}
ACTORS = {
    "HUMAN",
    "CHATGPT",
    "ANTIGRAVITY",
    "CLAUDE",
    "WATCHTOWER",
    "OLLARMA",
    "OLLAMA_MODEL",
    "DETERMINISTIC_TOOL",
    "HYDRADB",
    "GIT_GITHUB",
    "OTHER_AGENT",
}
SIGNATURE_STATES = {
    "NOT_SIGNED",
    "PENDING_EXTERNAL_PRIVATE_KEY_OPERATION",
    "SIGNED",
    "SIGNATURE_VERIFIED",
    "SIGNATURE_FAILED",
}
REQUIRED = {
    "schema",
    "handoff_id",
    "timestamp_utc",
    "actor_class",
    "actor_id",
    "execution_host",
    "repo",
    "branch",
    "git_commit",
    "parent_handoff_sha256",
    "input_dependencies",
    "evidence_class",
    "transformation_class",
    "claim_ceiling",
    "signature",
    "merkle_mmr",
}


def is_sha_or_state(value) -> bool:
    return value is None or value in SHA_STATES or (isinstance(value, str) and bool(SHA256_RE.fullmatch(value)))


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"invalid JSON: {exc}"]

    missing = sorted(REQUIRED - set(obj))
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))

    if obj.get("schema") != "hydradg.agent_model_handoff.v1":
        errors.append("schema must be hydradg.agent_model_handoff.v1")

    if obj.get("actor_class") not in ACTORS:
        errors.append(f"invalid actor_class: {obj.get('actor_class')!r}")

    if not is_sha_or_state(obj.get("parent_handoff_sha256")):
        errors.append("parent_handoff_sha256 is neither lowercase SHA-256 nor an allowed explicit state")

    deps = obj.get("input_dependencies")
    if not isinstance(deps, list):
        errors.append("input_dependencies must be a list")
    else:
        for i, dep in enumerate(deps):
            if not isinstance(dep, dict):
                errors.append(f"input_dependencies[{i}] must be an object")
                continue
            for field in ("id", "sha256", "evidence_class"):
                if field not in dep:
                    errors.append(f"input_dependencies[{i}] missing {field}")
            if "sha256" in dep and not is_sha_or_state(dep.get("sha256")):
                errors.append(f"input_dependencies[{i}].sha256 invalid")

    for field in ("prompt_sha256", "request_sha256", "output_sha256", "hardware_identity_sha256"):
        if field in obj and not is_sha_or_state(obj.get(field)):
            errors.append(f"{field} invalid")

    sig = obj.get("signature")
    if not isinstance(sig, dict):
        errors.append("signature must be an object")
    else:
        state = sig.get("state")
        if state not in SIGNATURE_STATES:
            errors.append(f"invalid signature.state: {state!r}")
        if state in {"SIGNED", "SIGNATURE_VERIFIED"}:
            for field in ("algorithm", "public_key_id", "signed_scope", "signature_path"):
                if not sig.get(field):
                    errors.append(f"signature.state={state} requires signature.{field}")
        if state == "SIGNATURE_VERIFIED" and not is_sha_or_state(sig.get("verification_receipt_sha256")):
            errors.append("SIGNATURE_VERIFIED requires a valid verification_receipt_sha256")
        if state == "SIGNATURE_VERIFIED" and sig.get("verification_receipt_sha256") in {None, "NOT_AVAILABLE", "NOT_APPLICABLE"}:
            errors.append("SIGNATURE_VERIFIED cannot use a missing/not-applicable verification receipt")

    mmr = obj.get("merkle_mmr")
    if not isinstance(mmr, dict) or not mmr.get("state"):
        errors.append("merkle_mmr must contain an explicit state")
    elif "COMMITTED" in str(mmr.get("state")).upper():
        root = mmr.get("root")
        receipt = mmr.get("receipt_sha256")
        if not (isinstance(root, str) and SHA256_RE.fullmatch(root)):
            errors.append("committed Merkle/MMR state requires a lowercase SHA-256 root")
        if not (isinstance(receipt, str) and SHA256_RE.fullmatch(receipt)):
            errors.append("committed Merkle/MMR state requires a lowercase SHA-256 receipt hash")

    actor = obj.get("actor_class")
    model = obj.get("model")
    if actor == "OLLAMA_MODEL":
        if not isinstance(model, dict):
            errors.append("OLLAMA_MODEL receipt requires model object")
        else:
            for field in ("bridge", "requested_name", "approved_name", "runtime_name", "runtime_digest"):
                if not model.get(field):
                    errors.append(f"OLLAMA_MODEL receipt requires model.{field}")
            for field in ("prompt_sha256", "request_sha256", "output_sha256"):
                value = obj.get(field)
                if not (isinstance(value, str) and SHA256_RE.fullmatch(value)):
                    errors.append(f"OLLAMA_MODEL receipt requires exact lowercase SHA-256 {field}")

    for field in ("actor_id", "repo", "branch", "git_commit", "evidence_class", "transformation_class", "claim_ceiling"):
        if not obj.get(field):
            errors.append(f"{field} must be non-empty")

    return errors


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: check_agent_model_handoff_receipt.py <receipt.json> [...]", file=sys.stderr)
        return 2

    failed = False
    for name in argv:
        path = Path(name)
        errors = validate(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"PASS {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
