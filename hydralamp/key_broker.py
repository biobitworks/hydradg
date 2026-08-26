"""External key broker — private keys never enter model prompts or Git."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from hydralamp.crypto import (
    Ed25519Keypair,
    X25519Keypair,
    TEST_ED25519_SEEDS,
    TEST_X25519_SEEDS,
    generate_ed25519_keypair,
    generate_x25519_keypair,
)

if TYPE_CHECKING:
    pass


@dataclass
class KeyBroker:
    """Sidecar holding private signing/decryption keys in process memory only."""

    mode: str  # TEST_VECTOR_REPLAY | REAL_CRYPTO_CANARY
    _ed25519: dict[str, Ed25519Keypair] = field(default_factory=dict)
    _x25519: dict[str, X25519Keypair] = field(default_factory=dict)

    @classmethod
    def for_mode(cls, mode: str, actor_ids: list[str]) -> "KeyBroker":
        broker = cls(mode=mode)
        for actor_id in actor_ids:
            if mode == "TEST_VECTOR_REPLAY":
                ed_seed = TEST_ED25519_SEEDS.get(actor_id, TEST_ED25519_SEEDS["AUTHORITY"])
                x_seed = TEST_X25519_SEEDS.get(actor_id, TEST_X25519_SEEDS["AUTHORITY"])
                broker._ed25519[actor_id] = generate_ed25519_keypair(ed_seed)
                broker._x25519[actor_id] = generate_x25519_keypair(x_seed)
            else:
                broker._ed25519[actor_id] = generate_ed25519_keypair()
                broker._x25519[actor_id] = generate_x25519_keypair()
        broker._ed25519["AUTHORITY"] = (
            generate_ed25519_keypair(TEST_ED25519_SEEDS["AUTHORITY"])
            if mode == "TEST_VECTOR_REPLAY"
            else generate_ed25519_keypair()
        )
        broker._x25519["AUTHORITY"] = (
            generate_x25519_keypair(TEST_X25519_SEEDS["AUTHORITY"])
            if mode == "TEST_VECTOR_REPLAY"
            else generate_x25519_keypair()
        )
        return broker

    def ed25519(self, actor_id: str) -> Ed25519Keypair:
        if actor_id not in self._ed25519:
            raise KeyError(f"No Ed25519 key for {actor_id}")
        return self._ed25519[actor_id]

    def x25519(self, actor_id: str) -> X25519Keypair:
        if actor_id not in self._x25519:
            raise KeyError(f"No X25519 key for {actor_id}")
        return self._x25519[actor_id]

    def public_keys_manifest(self) -> dict[str, dict[str, str]]:
        """Export public keys only — safe for world-leak bundle."""
        manifest: dict[str, dict[str, str]] = {}
        for actor_id in self._ed25519:
            manifest[actor_id] = {
                "ed25519_public_b64": self._ed25519[actor_id].public_key_b64,
                "x25519_public_b64": self._x25519[actor_id].public_key_b64,
            }
        return manifest
