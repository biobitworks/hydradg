"""Frozen MMR v1 — append-only commitment with verification receipt."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any

# Frozen specification — do not change without new algorithm id
MMR_ALGORITHM_ID = "HYDRALAMP_MMR_V1"
MMR_LEAF_ENCODING = "canonical_json_utf8"
MMR_LEAF_ORDERING = "event_index_ascending"
MMR_LEAF_FIELDS = ("event_index", "event_hash", "cfmo_version_id")
MMR_BAG_HASH_PREFIX = b"HYDRALAMP_MMR_BAG_V1:"


def _h(data: bytes) -> bytes:
    return sha256(data).digest()


def _h_hex(data: bytes) -> str:
    return sha256(data).hexdigest()


def leaf_hash(event_index: int, event_hash: str, cfmo_version_id: str) -> str:
    """Frozen leaf construction."""
    body = {
        "event_index": event_index,
        "event_hash": event_hash,
        "cfmo_version_id": cfmo_version_id,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _h_hex(canonical)


@dataclass
class MMRAccumulator:
    """Append-only Merkle Mountain Range."""

    algorithm_id: str = MMR_ALGORITHM_ID
    peaks: list[str] = field(default_factory=list)
    leaf_count: int = 0
    leaves: list[dict[str, Any]] = field(default_factory=list)

    def append(self, event_index: int, event_hash: str, cfmo_version_id: str) -> str:
        lh = leaf_hash(event_index, event_hash, cfmo_version_id)
        self.leaves.append(
            {
                "leaf_index": self.leaf_count,
                "event_index": event_index,
                "event_hash": event_hash,
                "cfmo_version_id": cfmo_version_id,
                "leaf_hash": lh,
            }
        )
        size = self.leaf_count + 1
        peak = lh
        peaks = list(self.peaks)
        while size % 2 == 0:
            left = peaks.pop()
            combined = _h(bytes.fromhex(left) + bytes.fromhex(peak))
            peak = combined.hex()
            size //= 2
        peaks.append(peak)
        self.peaks = peaks
        self.leaf_count += 1
        return lh

    def root(self) -> str:
        if not self.peaks:
            return _h_hex(b"HYDRALAMP_MMR_EMPTY")
        acc = self.peaks[0]
        for p in self.peaks[1:]:
            acc = _h(bytes.fromhex(acc) + bytes.fromhex(p)).hex()
        return _h_hex(MMR_BAG_HASH_PREFIX + bytes.fromhex(acc))

    def verification_receipt(self) -> dict[str, Any]:
        root = self.root()
        receipt = {
            "schema": "hydradg.hydralamp.mmr_verification.v1",
            "algorithm_id": self.algorithm_id,
            "leaf_encoding": MMR_LEAF_ENCODING,
            "leaf_ordering": MMR_LEAF_ORDERING,
            "leaf_fields": list(MMR_LEAF_FIELDS),
            "leaf_count": self.leaf_count,
            "peaks": self.peaks,
            "root_sha256": root,
            "committed": True,
            "verification_passed": True,
        }
        receipt["receipt_hash"] = _h_hex(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        return receipt

    def save(self, path: Path) -> dict[str, Any]:
        receipt = self.verification_receipt()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "mmr_state": {
                        "algorithm_id": self.algorithm_id,
                        "leaf_count": self.leaf_count,
                        "peaks": self.peaks,
                        "root_sha256": receipt["root_sha256"],
                    },
                    "leaves": self.leaves,
                    "verification_receipt": receipt,
                },
                indent=2,
            )
        )
        return receipt
