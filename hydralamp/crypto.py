"""HydraLamp cryptographic primitives — Ed25519, X25519/ECDH, HKDF, AES-GCM."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization

SECURITY_CLAIM_ELIGIBILITY_TEST = "NO"
SECURITY_CLAIM_ELIGIBILITY_REAL = "CONDITIONAL_ON_OBSERVED_TESTS"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class Ed25519Keypair:
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey
    public_key_b64: str
    key_id: str


@dataclass(frozen=True)
class X25519Keypair:
    private_key: X25519PrivateKey
    public_key: X25519PublicKey
    public_key_b64: str


def _b64_pubkey_ed25519(public_key: Ed25519PublicKey) -> str:
    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    import base64

    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64_pubkey_x25519(public_key: X25519PublicKey) -> str:
    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    import base64

    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def generate_ed25519_keypair(seed: bytes | None = None) -> Ed25519Keypair:
    if seed is not None:
        private_key = Ed25519PrivateKey.from_private_bytes(seed[:32].ljust(32, b"\x00"))
    else:
        private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    pub_b64 = _b64_pubkey_ed25519(public_key)
    return Ed25519Keypair(
        private_key=private_key,
        public_key=public_key,
        public_key_b64=pub_b64,
        key_id=f"ed25519:{sha256_bytes(public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))[:16]}",
    )


def generate_x25519_keypair(seed: bytes | None = None) -> X25519Keypair:
    if seed is not None:
        private_key = X25519PrivateKey.from_private_bytes(seed[:32].ljust(32, b"\x00"))
    else:
        private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return X25519Keypair(
        private_key=private_key,
        public_key=public_key,
        public_key_b64=_b64_pubkey_x25519(public_key),
    )


def sign_message(private_key: Ed25519PrivateKey, message: bytes) -> bytes:
    return private_key.sign(message)


def verify_signature(public_key: Ed25519PublicKey, message: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False


def derive_aes_key(shared_secret: bytes, salt: bytes, info: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info,
    )
    return hkdf.derive(shared_secret)


def encrypt_payload(
    recipient_public: X25519PublicKey,
    sender_private: X25519PrivateKey,
    plaintext: bytes,
    aad: bytes,
    nonce: bytes | None = None,
) -> dict[str, str]:
    shared = sender_private.exchange(recipient_public)
    salt = os.urandom(16) if nonce is None else nonce[:16]
    key = derive_aes_key(shared, salt, b"hydralamp-aes-gcm-v1")
    iv = os.urandom(12) if nonce is None else nonce[16:28]
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, plaintext, aad)
    return {
        "ciphertext_b64": __import__("base64").urlsafe_b64encode(ciphertext).decode(),
        "salt_hex": salt.hex(),
        "iv_hex": iv.hex(),
        "aad_sha256": sha256_bytes(aad),
    }


def decrypt_payload(
    recipient_private: X25519PrivateKey,
    sender_public: X25519PublicKey,
    envelope: dict[str, str],
    aad: bytes,
) -> bytes | None:
    import base64

    try:
        shared = recipient_private.exchange(sender_public)
        salt = bytes.fromhex(envelope["salt_hex"])
        iv = bytes.fromhex(envelope["iv_hex"])
        key = derive_aes_key(shared, salt, b"hydralamp-aes-gcm-v1")
        ciphertext = base64.urlsafe_b64decode(envelope["ciphertext_b64"])
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(iv, ciphertext, aad)
    except Exception:
        return None


# TEST-ONLY deterministic keys — SECURITY_CLAIM_ELIGIBILITY=NO
TEST_ED25519_SEEDS: dict[str, bytes] = {
    "HUMAN_CONTROLLER": b"TEST-ONLY-HUMAN-CONTROLLER-KEY!!",
    "RESEARCH_AGENT": b"TEST-ONLY-RESEARCH-AGENT-KEY!!",
    "VERIFIER_AGENT": b"TEST-ONLY-VERIFIER-AGENT-KEY!!",
    "REPAIR_AGENT": b"TEST-ONLY-REPAIR-AGENT-KEY!!",
    "POISON_AGENT": b"TEST-ONLY-POISON-AGENT-KEY!!",
    "AUTHORITY": b"TEST-ONLY-AUTHORITY-KEY-SEED!!!!",
}

TEST_X25519_SEEDS: dict[str, bytes] = {
    "HUMAN_CONTROLLER": b"TEST-X25519-HUMAN-CONTROLLER!!",
    "RESEARCH_AGENT": b"TEST-X25519-RESEARCH-AGENT!!",
    "VERIFIER_AGENT": b"TEST-X25519-VERIFIER-AGENT!!",
    "REPAIR_AGENT": b"TEST-X25519-REPAIR-AGENT!!",
    "POISON_AGENT": b"TEST-X25519-POISON-AGENT-KEY!!",
    "AUTHORITY": b"TEST-X25519-AUTHORITY-KEY!!!!",
}

TEST_NONCE = bytes.fromhex("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
