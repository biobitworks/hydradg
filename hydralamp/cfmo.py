"""CFMO — append-only evolving version/state ledger. Never overwrite poison/quarantine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hydralamp.crypto import canonical_json, sha256_text


IMMUTABLE_STATE_TYPES = frozenset({
    "POISON",
    "QUARANTINE",
    "FAILED_REPAIR",
    "CONTRADICTION",
    "CANONICAL",
    "RETAINED_REJECTION",
})


@dataclass
class CFMOStore:
    """Continuous Federation Metadata Oracle — versioned state trajectory."""

    path: Path
    versions: list[dict[str, Any]] = field(default_factory=list)
    _seq: int = 0

    def append(
        self,
        state_type: str,
        payload: dict[str, Any],
        *,
        actor_id: str,
        event_index: int,
        parent_version_id: str | None = None,
    ) -> dict[str, Any]:
        self._seq += 1
        version_id = f"cfmo:v{self._seq:06d}:{sha256_text(canonical_json(payload))[:12]}"
        record = {
            "version_id": version_id,
            "sequence": self._seq,
            "state_type": state_type,
            "payload": payload,
            "actor_id": actor_id,
            "event_index": event_index,
            "parent_version_id": parent_version_id,
            "supersedes": None,
            "immutable": state_type in IMMUTABLE_STATE_TYPES,
        }
        record["version_hash"] = sha256_text(canonical_json(record))
        self.versions.append(record)
        return record

    def get_latest(self, state_type: str | None = None) -> dict[str, Any] | None:
        for v in reversed(self.versions):
            if state_type is None or v["state_type"] == state_type:
                return v
        return None

    def trajectory(self) -> list[dict[str, Any]]:
        return list(self.versions)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "schema": "hydradg.hydralamp.cfmo.v1",
                    "version_count": len(self.versions),
                    "versions": self.versions,
                },
                indent=2,
            )
        )

    @classmethod
    def load(cls, path: Path) -> "CFMOStore":
        store = cls(path=path)
        if path.exists():
            data = json.loads(path.read_text())
            store.versions = data.get("versions", [])
            store._seq = max((v.get("sequence", 0) for v in store.versions), default=0)
        return store
