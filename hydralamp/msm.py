"""HydraLamp Mechanical Scientific Method — observed state transitions."""

from __future__ import annotations

from collections import defaultdict
from enum import Enum
from typing import Any


class MSMState(str, Enum):
    UNKNOWN = "UNKNOWN"
    AUTHENTICATED = "AUTHENTICATED"
    CAPABILITY_GRANTED = "CAPABILITY_GRANTED"
    EVIDENCE_ACCESSED = "EVIDENCE_ACCESSED"
    PROPOSAL_CREATED = "PROPOSAL_CREATED"
    QUARANTINED = "QUARANTINED"
    VERIFIED = "VERIFIED"
    PROMOTED = "PROMOTED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"


VALID_TRANSITIONS: dict[MSMState, set[MSMState]] = {
    MSMState.UNKNOWN: {MSMState.AUTHENTICATED, MSMState.DENIED, MSMState.REVOKED},
    MSMState.AUTHENTICATED: {
        MSMState.CAPABILITY_GRANTED,
        MSMState.DENIED,
        MSMState.EVIDENCE_ACCESSED,
        MSMState.REVOKED,
    },
    MSMState.CAPABILITY_GRANTED: {
        MSMState.EVIDENCE_ACCESSED,
        MSMState.PROPOSAL_CREATED,
        MSMState.DENIED,
        MSMState.REVOKED,
    },
    MSMState.EVIDENCE_ACCESSED: {
        MSMState.PROPOSAL_CREATED,
        MSMState.DENIED,
        MSMState.QUARANTINED,
    },
    MSMState.PROPOSAL_CREATED: {MSMState.QUARANTINED, MSMState.DENIED},
    MSMState.QUARANTINED: {MSMState.VERIFIED, MSMState.DENIED},
    MSMState.VERIFIED: {MSMState.PROMOTED, MSMState.DENIED},
    MSMState.PROMOTED: set(),
    MSMState.DENIED: set(),
    MSMState.REVOKED: set(),
}


class MSMTracker:
    def __init__(self) -> None:
        self.actor_states: dict[str, MSMState] = {}
        self.transitions: list[dict[str, Any]] = []

    def current(self, actor_id: str) -> MSMState:
        return self.actor_states.get(actor_id, MSMState.UNKNOWN)

    def transition(
        self,
        actor_id: str,
        to_state: MSMState,
        event_index: int,
        event_type: str,
    ) -> dict[str, Any]:
        from_state = self.current(actor_id)
        allowed = to_state in VALID_TRANSITIONS.get(from_state, set()) or from_state == to_state
        record = {
            "event_index": event_index,
            "actor_id": actor_id,
            "from_state": from_state.value,
            "to_state": to_state.value,
            "event_type": event_type,
            "valid_transition": allowed,
        }
        self.transitions.append(record)
        if allowed or from_state == MSMState.UNKNOWN:
            self.actor_states[actor_id] = to_state
        return record

    def empirical_matrix(self) -> dict[str, Any]:
        counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for t in self.transitions:
            counts[t["from_state"]][t["to_state"]] += 1
        return {k: dict(v) for k, v in counts.items()}
