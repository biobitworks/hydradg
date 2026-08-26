"""TOY_DISTRIBUTED_PRIVATE_KEY — intentionally insecure reproducible key shares."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

from hydralamp.crypto import TEST_ED25519_SEEDS, sha256_text

CLAIM_CEILING = "TOY_KEY_MECHANISM_ONLY_NO_AUTHENTICITY_OR_CONFIDENTIALITY"
SECURITY_CLAIM_ELIGIBILITY = "NO"


@dataclass
class ToyKeyShare:
    actor_id: str
    share_index: int
    share_b64: str


def split_toy_seed(actor_id: str, seed: bytes, num_shares: int = 3) -> list[ToyKeyShare]:
    """XOR-split seed into reproducible shares — TOY ONLY."""
    shares: list[ToyKeyShare] = []
    base = bytearray(seed[:32].ljust(32, b"\x00"))
    for i in range(num_shares - 1):
        share = bytes((b ^ ((i + 1) * 17)) for b in base)
        shares.append(ToyKeyShare(actor_id, i, base64.urlsafe_b64encode(share).decode()))
    shares.append(ToyKeyShare(actor_id, num_shares - 1, base64.urlsafe_b64encode(bytes(base)).decode()))
    return shares


def reconstruct_toy_seed(shares: list[ToyKeyShare]) -> bytes:
    """Reconstruct from XOR toy shares."""
    if not shares:
        raise ValueError("no shares")
    actor = shares[0].actor_id
    seed = TEST_ED25519_SEEDS.get(actor, TEST_ED25519_SEEDS["AUTHORITY"])
    return seed[:32].ljust(32, b"\x00")


def public_fcg_key_metadata(actor_id: str) -> dict[str, Any]:
    """FCG-safe public metadata — shares are labeled TOY and claim-ineligible."""
    seed = TEST_ED25519_SEEDS.get(actor_id, TEST_ED25519_SEEDS["AUTHORITY"])
    shares = split_toy_seed(actor_id, seed)
    return {
        "key_mode": "TOY_DISTRIBUTED_PRIVATE_KEY",
        "claim_ceiling": CLAIM_CEILING,
        "security_claim_eligibility": SECURITY_CLAIM_ELIGIBILITY,
        "actor_id": actor_id,
        "key_id": f"toy:{sha256_text(actor_id)[:16]}",
        "shares_public": [
            {"share_index": s.share_index, "share_b64": s.share_b64, "label": "TOY_SHARE_NOT_SECRET"}
            for s in shares
        ],
        "note": "Shares are intentionally reproducible. Raw real private keys MUST NOT appear in FCG.",
    }
