"""HydraLamp canonical event log."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hydralamp.crypto import canonical_json, sha256_text


@dataclass
class EventLog:
    path: Path
    events: list[dict[str, Any]] = field(default_factory=list)
    _index: int = 0

    def append(
        self,
        event_type: str,
        actor_id: str,
        actor_class: str,
        region: str,
        runtime_model: str,
        request_hash: str,
        capability_state: str,
        access_decision: dict[str, Any],
        fco_ids: list[str],
        fcg_root_before: str,
        fcg_root_after: str,
        msm_before: str,
        msm_after: str,
        drift_pointer: str,
        evidence_class: str,
        claim_ceiling: str,
        signature_state: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._index += 1
        event = {
            "event_index": self._index,
            "event_type": event_type,
            "actor_id": actor_id,
            "actor_class": actor_class,
            "region": region,
            "runtime_model": runtime_model,
            "source_request_hash": request_hash,
            "capability_state": capability_state,
            "access_decision": access_decision,
            "fco_ids": fco_ids,
            "fcg_root_before": fcg_root_before,
            "fcg_root_after": fcg_root_after,
            "msm_state_before": msm_before,
            "msm_state_after": msm_after,
            "delta_g_star_drift_pointer": drift_pointer,
            "evidence_class": evidence_class,
            "claim_ceiling": claim_ceiling,
            "signature_state": signature_state,
        }
        if extra:
            event.update(extra)
        event["event_hash"] = sha256_text(canonical_json(event))
        self.events.append(event)
        return event

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            for ev in self.events:
                f.write(json.dumps(ev, sort_keys=True) + "\n")

    @classmethod
    def load(cls, path: Path) -> "EventLog":
        log = cls(path=path)
        if path.exists():
            for line in path.read_text(encoding="utf-8").strip().splitlines():
                if line.strip():
                    ev = json.loads(line)
                    log.events.append(ev)
                    log._index = max(log._index, ev.get("event_index", 0))
        return log

    @property
    def fcg_root(self) -> str:
        if not self.events:
            return sha256_text("HYDRALAMP_EMPTY_FCG")
        return self.events[-1]["fcg_root_after"]
