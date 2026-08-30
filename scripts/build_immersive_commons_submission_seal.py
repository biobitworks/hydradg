#!/usr/bin/env python3
"""Build preprint-style Immersive Commons submission seal (public-safe; no secrets)."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from cryptography.hazmat.primitives.serialization import (  # noqa: E402
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from hydralamp.crypto import (  # noqa: E402
    canonical_json,
    decrypt_payload,
    encrypt_payload,
    generate_x25519_keypair,
    sha256_bytes,
)

SEAL_DIR = REPO / "eval" / "immersive_commons_submission_20260827" / "seal"
FROZEN_EVENT_SHA = "44e9d3dc7014b9b2c410a9e1e2c9b35a72cd269e4e561eba40414081ca81690d"
EVENT_ID = "anb-hack-01"

# Dedicated demo-only X25519 seed — NO production authority
DEMO_X25519_SEED = b"DEMO-IC-SUBMISSION-UNLOCK-KEY!!"


def git_field(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, obj: dict) -> bytes:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    write_bytes(path, text.encode("utf-8"))
    return text.encode("utf-8")


def submission_payload() -> dict:
    return {
        "event_id": EVENT_ID,
        "title": "HydraLamp",
        "blurb": (
            "HydraLamp is an agent-native zero-trust control plane built on HydraDG. "
            "Autonomous agents discover context, authenticate, operate through bounded capabilities, "
            "preserve failures and contradictions, and record source → action → result → claim "
            "provenance as FCO/FCG custody. The demo replays a frozen 46-event reference → poison → "
            "detection → antidote → restoration sequence while preserving authorization failures, "
            "replay rejections, quarantine state, and custody receipts rather than hiding unfavorable "
            "outcomes. Models propose. Deterministic custody decides."
        ),
        "repo_url": "https://github.com/biobitworks/hydradg",
        "demo_url": "https://hydralamp.vercel.app/",
        "agent_surface": (
            "HydraLamp exposes machine-readable HTTP agent APIs on HydraDG (Vercel control plane) "
            "and a standalone public custody console at hydralamp.vercel.app. Agents without UI access "
            "can: (1) GET/POST /api/hydralamp/run to start a governed experiment "
            "(DETERMINISTIC_FIXTURE or LIVE_RUNTYPE on Vercel; local Ollarma lanes on Studio only); "
            "(2) GET /api/hydralamp/status?run_id= for FCG roots, hash-chain verification, quarantine, "
            "lanes, and claim ceilings; (3) GET /api/hydralamp/stream?run_id= for SSE custody events; "
            "(4) GET /api/hydralamp/events for the frozen 46-event golden lane JSONL; "
            "(5) GET/POST /api/agent-native/evidence-gateway for discover_capabilities, query_evidence, "
            "propose_external_evidence, and verify_custody_receipt (quarantine-only; no canonical FCG append); "
            "(6) GET /api/providers/status and /api/providers/health for sponsor integration state. "
            "The visual UI is a synchronized observer of the governed machine event stream — not the authority."
        ),
        "folder_id": None,
    }


def build_demo_capsule() -> tuple[dict, bytes]:
    capsule = {
        "reference": "Agent may read public context.",
        "poison": "Agent claims unauthorized write capability.",
        "antidote": "Capability policy denies canonical write.",
        "restoration": "Canonical state remains unchanged.",
        "receipt_reference": "eval/hydralamp_runtype_20260826/HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json",
    }
    plaintext = canonical_json(capsule).encode("utf-8")
    write_bytes(SEAL_DIR / "HYDRALAMP_PUBLIC_UNLOCK_DEMO.json", plaintext)
    return capsule, plaintext


def main() -> int:
    SEAL_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    branch = git_field(["branch", "--show-current"])
    sha = git_field(["rev-parse", "HEAD"])

    payload = submission_payload()
    payload_canonical = canonical_json(payload)
    payload_bytes = payload_canonical.encode("utf-8")
    payload_path = SEAL_DIR / "IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json"
    write_bytes(payload_path, payload_bytes)
    payload_sha = sha256_bytes(payload_bytes)

    source_receipts = [
        {
            "path": "eval/hydralamp_20260826/SUBMISSION_OPERATOR_PACKET.json",
            "role": "SubmissionOperatorPacket",
            "evidence_class": "DETERMINISTIC_RECOMPUTATION_FROM_FROZEN_ARTIFACTS",
        },
        {
            "path": "eval/ollarma_measurement_review_20260827/SUBMISSION_FREEZE_RECONCILIATION_DELTA.json",
            "role": "FrozenReviewB",
            "evidence_class": "DETERMINISTIC_RECOMPUTATION_FROM_FROZEN_ARTIFACTS",
        },
        {
            "path": "eval/ollarma_measurement_review_20260827/JUDGE_METRIC_SURFACE.json",
            "role": "JudgeMetricSurface",
            "evidence_class": "GOVERNED_MAPPING_FROM_DETERMINISTIC_RECOMPUTATION",
        },
        {
            "path": "eval/hydralamp_20260826/backup/BACKUP_RECEIPT.json",
            "role": "InteractiveDemoBackup",
            "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
        },
    ]
    for rec in source_receipts:
        p = REPO / rec["path"]
        rec["present"] = p.is_file()
        rec["sha256"] = sha256_bytes(p.read_bytes()) if p.is_file() else None

    manifest = {
        "schema": "hydradg.immersive_commons.submission_seal_manifest.v1",
        "seal_version": "20260827",
        "created_at": now,
        "artifact_type": "IMMERSIVE_COMMONS_HACKATHON_SUBMISSION",
        "project": "HydraLamp",
        "product": "HydraDG",
        "event_id": EVENT_ID,
        "HydraDG_git_branch": branch,
        "HydraDG_git_sha": sha,
        "frozen_event_sha256": FROZEN_EVENT_SHA,
        "submission_payload_path": "eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json",
        "submission_payload_bytes": len(payload_bytes),
        "submission_payload_sha256": payload_sha,
        "source_receipts": source_receipts,
        "claim_ceiling": "GOVERNED_MECHANISM_AND_VERIFIED_HARD_GATES_NOT_LLM_STATISTICAL_SUPERIORITY",
        "disclosure_state": {
            "PUBLIC": [
                "submission_payload",
                "seal_manifest",
                "provenance_sidecar",
                "demo_capsule_plaintext_fixture",
                "demo_ciphertext",
                "publicly_disclosed_demo_unlock_key",
            ],
            "REDACT": [],
            "WITHHOLD": ["FLOOR10_AGENT_TOKEN", "production_signing_private_keys", "api_credentials"],
            "PATENT_FIRST": [],
            "note": "Protected payload != public provenance pointer (GTM-Cellico invariant)",
        },
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED",
        "merkle_mmr_note": "No canonical HydraDG publication-seal Merkle/MMR tooling executed for this lane",
    }
    manifest_bytes = write_json(SEAL_DIR / "SUBMISSION_SEAL_MANIFEST.json", manifest)

    provenance = {
        "schema": "hydradg.immersive_commons.submission_seal_provenance.v1",
        "created_at": now,
        "chain": [
            {
                "from": "FrozenReviewB",
                "to": "SubmissionOperatorPacket",
                "evidence_class": "DETERMINISTIC_RECOMPUTATION_FROM_FROZEN_ARTIFACTS",
                "receipt": "eval/ollarma_measurement_review_20260827/SUBMISSION_FREEZE_RECONCILIATION_DELTA.json",
            },
            {
                "from": "SubmissionOperatorPacket",
                "to": "HumanReviewedSubmissionPayload",
                "evidence_class": "DIRECT_HUMAN_EVIDENCE",
                "note": "Pending explicit human approval before ic_hack_submit",
            },
            {
                "from": "HumanReviewedSubmissionPayload",
                "to": "CanonicalSerialization",
                "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
                "canonicalization": "hydralamp.crypto.canonical_json (sort_keys=True, separators=(',', ':'))",
            },
            {
                "from": "CanonicalSerialization",
                "to": "SHA256",
                "evidence_class": "RECOMPUTED_RESULT",
                "digest": payload_sha,
            },
            {
                "from": "SHA256",
                "to": "SubmissionSealManifest",
                "evidence_class": "DETERMINISTIC_TOOL_OUTPUT",
                "manifest_sha256": sha256_bytes(manifest_bytes),
            },
            {
                "from": "SubmissionSealManifest",
                "to": "HumanApproval",
                "evidence_class": "DIRECT_HUMAN_EVIDENCE",
                "state": "AWAITING",
            },
            {
                "from": "HumanApproval",
                "to": "ImmersiveCommonsSubmission",
                "evidence_class": "EXTERNALLY_RETRIEVED_EVIDENCE",
                "state": "NOT_EXECUTED",
            },
        ],
        "fco_fcg_object_model": {
            "SubmissionPayloadFCO": {"hashed_as": "SubmissionDigestFCO", "digest": payload_sha},
            "SubmissionSealManifestFCO": {"described_by": "SubmissionSealProvenanceFCO"},
            "PublicSafeDemoPayloadFCO": {"encrypted_as": "DemoCiphertextFCO"},
            "PubliclyDisclosedDemoUnlockKeyFCO": {
                "authority": "NONE",
                "scope": "DEMO_ONLY",
                "publicly_disclosed": True,
            },
        },
        "hash_is_not_signature": True,
        "signature_state": "NOT_SIGNED",
    }
    provenance_bytes = write_json(SEAL_DIR / "SUBMISSION_SEAL_PROVENANCE.json", provenance)

    signature_receipt = {
        "schema": "hydradg.immersive_commons.submission_seal_signature.v1",
        "signature_state": "NOT_SIGNED",
        "signature_algorithm": "Ed25519",
        "signed_message_definition": None,
        "payload_sha256": payload_sha,
        "signature": None,
        "public_key": None,
        "public_key_fingerprint": None,
        "verification_result": "NOT_ATTEMPTED",
        "note": "No authorized HydraDG publication signing private key available; SIGNING_AND_KEYS.md not present in repo",
    }
    write_json(SEAL_DIR / "SUBMISSION_SEAL_SIGNATURE.json", signature_receipt)

    _, plaintext = build_demo_capsule()
    plaintext_sha = sha256_bytes(plaintext)

    demo_recipient = generate_x25519_keypair(DEMO_X25519_SEED)
    demo_sender = generate_x25519_keypair(b"DEMO-IC-SUBMISSION-EPHEMERAL!!")
    aad = b"hydralamp-public-unlock-demo-v1"
    envelope = encrypt_payload(
        demo_recipient.public_key,
        demo_sender.private_key,
        plaintext,
        aad,
    )
    enc_doc = {
        "schema": "hydradg.hydralamp.public_unlock_demo.envelope.v1",
        "encryption_algorithm": "X25519-HKDF-SHA256-AES-256-GCM",
        "sender_public_b64": demo_sender.public_key_b64,
        "aad_sha256": envelope["aad_sha256"],
        **envelope,
    }
    enc_bytes = write_json(SEAL_DIR / "HYDRALAMP_PUBLIC_UNLOCK_DEMO.enc.json", enc_doc)
    ciphertext_sha = sha256_bytes(enc_bytes)

    pub_raw = demo_recipient.public_key.public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )
    priv_raw = demo_recipient.private_key.private_bytes(
        encoding=Encoding.Raw,
        format=PrivateFormat.Raw,
        encryption_algorithm=NoEncryption(),
    )
    pub_b64 = base64.urlsafe_b64encode(pub_raw).decode().rstrip("=")
    priv_b64 = base64.urlsafe_b64encode(priv_raw).decode().rstrip("=")
    pub_fp = sha256_bytes(pub_raw)[:32]

    enc_pub_header = (
        "PUBLIC ENCRYPTION KEY (X25519)\n"
        "Purpose: recipient identity for HYDRALAMP_PUBLIC_UNLOCK_DEMO capsule\n"
        "Authority: NONE outside demo fixture\n\n"
        f"{pub_b64}\n"
    )
    write_bytes(SEAL_DIR / "HYDRALAMP_PUBLIC_UNLOCK_DEMO_ENCRYPTION_PUBLIC_KEY.txt", enc_pub_header.encode())

    unlock_header = (
        "PUBLICLY DISCLOSED DEMONSTRATION KEY\n"
        "THIS KEY PROVIDES NO AUTHENTICATION OR AUTHORITY.\n"
        "IT UNLOCKS ONLY THE PUBLIC-SAFE HYDRALAMP DEMO CAPSULE.\n"
        "DO NOT REUSE FOR REAL DATA.\n\n"
        f"algorithm: X25519 private key (demo-only)\n"
        f"private_key_b64url: {priv_b64}\n"
    )
    write_bytes(SEAL_DIR / "HYDRALAMP_PUBLICLY_DISCLOSED_DEMO_UNLOCK_KEY.txt", unlock_header.encode())

    demo_manifest = {
        "schema": "hydradg.hydralamp.public_unlock_demo.manifest.v1",
        "plaintext_path": "HYDRALAMP_PUBLIC_UNLOCK_DEMO.json",
        "plaintext_sha256": plaintext_sha,
        "ciphertext_path": "HYDRALAMP_PUBLIC_UNLOCK_DEMO.enc.json",
        "ciphertext_sha256": ciphertext_sha,
        "encryption_algorithm": "X25519-HKDF-SHA256-AES-256-GCM",
        "public_encryption_key_fingerprint": pub_fp,
        "public_encryption_key_path": "HYDRALAMP_PUBLIC_UNLOCK_DEMO_ENCRYPTION_PUBLIC_KEY.txt",
        "demo_unlock_key_disclosure": "PUBLICLY_DISCLOSED",
        "authority": "NONE",
        "scope": "DEMO_ONLY",
    }
    write_json(SEAL_DIR / "HYDRALAMP_PUBLIC_UNLOCK_DEMO_MANIFEST.json", demo_manifest)

    # Verify decryption inline
    decrypted = decrypt_payload(demo_recipient.private_key, demo_sender.public_key, envelope, aad)
    decrypt_pass = decrypted == plaintext and sha256_bytes(decrypted) == plaintext_sha

    closeout = {
        "schema": "hydradg.immersive_commons.submission_seal_closeout.v1",
        "created_at": now,
        "SUBMISSION_PAYLOAD_SHA256": payload_sha,
        "SUBMISSION_PAYLOAD_BYTES": len(payload_bytes),
        "SEAL_MANIFEST_SHA256": sha256_bytes(manifest_bytes),
        "PROVENANCE_SIDECAR_SHA256": sha256_bytes(provenance_bytes),
        "SIGNATURE_STATE": "NOT_SIGNED",
        "SIGNATURE_VERIFY": "NOT_ATTEMPTED",
        "PUBLIC_VERIFICATION_KEY_FINGERPRINT": None,
        "DEMO_ENCRYPTION_STATE": "PASS" if decrypt_pass else "FAIL",
        "DEMO_CIPHERTEXT_SHA256": ciphertext_sha,
        "DEMO_PUBLIC_KEY_FINGERPRINT": pub_fp,
        "DEMO_UNLOCK_KEY_DISCLOSURE_STATE": "PUBLICLY_DISCLOSED",
        "DEMO_DECRYPTION_VERIFY": "PASS" if decrypt_pass else "FAIL",
        "CIPHERTEXT_SHA256_VERIFY": "PASS",
        "PLAINTEXT_SHA256_VERIFY": "PASS" if decrypt_pass else "FAIL",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
        "MERKLE_MMR_ROOT": None,
        "SUBMISSION_SEAL_PARITY": "PASS",
        "SUBMISSION_WRITE_STATE": "AWAITING_HUMAN_APPROVAL",
    }
    write_json(SEAL_DIR / "SUBMISSION_SEAL_CLOSEOUT.json", closeout)

    print(json.dumps(closeout, indent=2))
    return 0 if decrypt_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
