#!/usr/bin/env python3
import base64, hashlib, json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT=Path(__file__).resolve().parents[1]
seal=json.loads((ROOT/"toy_seal/TOY_PACKAGE_SEAL.json").read_text())
pub=Ed25519PublicKey.from_public_bytes(base64.b64decode(seal["toy_public_key_b64"]))
sig=base64.b64decode(seal["signature_b64"])
root=bytes.fromhex(seal["seal_root_sha256"])
pub.verify(sig,root)
print("TOY_SEAL_SIGNATURE=PASS")
print("AUTHENTICITY=NOT_ESTABLISHED_BY_TOY_KEY")
print("PRIVATE_KEY_DISCLOSURE=INTENTIONAL")
