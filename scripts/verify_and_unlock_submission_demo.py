#!/usr/bin/env python3
"""Verify Immersive Commons submission seal and decrypt public-safe demo capsule."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hydralamp.crypto import canonical_json, decrypt_payload, sha256_bytes, verify_signature  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey  # noqa: E402
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat  # noqa: E402

SEAL_DIR = REPO / "eval" / "immersive_commons_submission_20260827" / "seal"


def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def load_unlock_private_key() -> X25519PrivateKey:
    text = (SEAL_DIR / "HYDRALAMP_PUBLICLY_DISCLOSED_DEMO_UNLOCK_KEY.txt").read_text()
    for line in text.splitlines():
        if line.startswith("private_key_b64url:"):
            raw = b64url_decode(line.split(":", 1)[1].strip())
            return X25519PrivateKey.from_private_bytes(raw)
    raise SystemExit("DEMO unlock private key not found in disclosure file")


def main() -> int:
    payload_path = SEAL_DIR / "IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json"
    payload_bytes = payload_path.read_bytes()
    payload_sha = sha256_bytes(payload_bytes)
    manifest = json.loads((SEAL_DIR / "SUBMISSION_SEAL_MANIFEST.json").read_text())
    sig_doc = json.loads((SEAL_DIR / "SUBMISSION_SEAL_SIGNATURE.json").read_text())

    print("=== SEALED SUBMISSION ===")
    print(f"Artifact: {manifest.get('project')} — Agent Natives Builders Hackathon")
    print(f"SHA-256: {payload_sha}")
    print(f"Git SHA: {manifest.get('HydraDG_git_sha')}")
    print(f"BYTE_IDENTITY={'PASS' if payload_sha == manifest['submission_payload_sha256'] else 'FAIL'}")

    if sig_doc.get("signature_state") == "SIGNED" and sig_doc.get("signature"):
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(sig_doc["public_key"]))
        ok = verify_signature(pub, payload_bytes, bytes.fromhex(sig_doc["signature"]))
        print(f"SIGNATURE_VERIFY={'PASS' if ok else 'FAIL'}")
    else:
        print("SIGNATURE: NOT SIGNED")
        print("SIGNATURE_VERIFY=NOT_ATTEMPTED")

    demo_manifest = json.loads((SEAL_DIR / "HYDRALAMP_PUBLIC_UNLOCK_DEMO_MANIFEST.json").read_text())
    enc_path = SEAL_DIR / demo_manifest["ciphertext_path"]
    enc_bytes = enc_path.read_bytes()
    ciphertext_sha = sha256_bytes(enc_bytes)
    print(f"\nENCRYPTED DEMO CAPSULE SHA-256: {ciphertext_sha}")
    print(f"CIPHERTEXT_SHA256_VERIFY={'PASS' if ciphertext_sha == demo_manifest['ciphertext_sha256'] else 'FAIL'}")
    print(f"DEMO PUBLIC KEY FINGERPRINT: {demo_manifest['public_encryption_key_fingerprint']}")

    envelope = json.loads(enc_path.read_text())
    aad = b"hydralamp-public-unlock-demo-v1"
    recipient_private = load_unlock_private_key()
    sender_public_b64 = envelope.get("sender_public_b64")
    if not sender_public_b64:
        # Re-derive sender from fixed demo seed used at build time
        from hydralamp.crypto import generate_x25519_keypair  # noqa: E402

        sender_public = generate_x25519_keypair(b"DEMO-IC-SUBMISSION-EPHEMERAL!!").public_key
    else:
        sender_public = X25519PublicKey.from_public_bytes(b64url_decode(sender_public_b64))

    plaintext = decrypt_payload(recipient_private, sender_public, envelope, aad)
    if plaintext is None:
        print("DECRYPTION=FAIL")
        return 1

    expected_sha = demo_manifest["plaintext_sha256"]
    actual_sha = sha256_bytes(plaintext)
    print(f"PLAINTEXT_SHA256_VERIFY={'PASS' if actual_sha == expected_sha else 'FAIL'}")
    print(f"DECRYPTION={'PASS' if actual_sha == expected_sha else 'FAIL'}")
    print("\nDecrypted public-safe capsule:")
    print(canonical_json(json.loads(plaintext.decode())))
    return 0 if actual_sha == expected_sha else 1


if __name__ == "__main__":
    raise SystemExit(main())
