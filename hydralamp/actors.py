"""HydraLamp actor registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


ACTOR_CLASSES = {
    "HUMAN_CONTROLLER": "HUMAN",
    "RESEARCH_AGENT": "MODEL_AGENT",
    "VERIFIER_AGENT": "MODEL_AGENT",
    "REPAIR_AGENT": "MODEL_AGENT",
    "POISON_AGENT": "ADVERSARIAL_AGENT",
}

DEFAULT_CAPABILITIES: dict[str, list[str]] = {
    "HUMAN_CONTROLLER": ["PUBLIC_METADATA", "PUBLIC_PAYLOAD", "PRIVATE_METADATA", "PRIVATE_PAYLOAD", "PROPOSE_ONLY", "VERIFY", "PROMOTE"],
    "RESEARCH_AGENT": ["PUBLIC_METADATA", "PUBLIC_PAYLOAD", "PRIVATE_METADATA", "PROPOSE_ONLY"],
    "VERIFIER_AGENT": ["PUBLIC_METADATA", "PUBLIC_PAYLOAD", "PRIVATE_METADATA", "VERIFY"],
    "REPAIR_AGENT": ["PUBLIC_METADATA", "PUBLIC_PAYLOAD", "PRIVATE_METADATA", "PRIVATE_PAYLOAD", "PROPOSE_ONLY", "VERIFY", "PROMOTE"],
    "POISON_AGENT": ["PUBLIC_METADATA", "PUBLIC_PAYLOAD", "PROPOSE_ONLY"],
}


@dataclass
class ActorFCO:
    actor_id: str
    actor_class: str
    public_signing_key_b64: str
    public_encryption_key_b64: str
    runtime_model_identity: str
    execution_region: str
    capabilities: list[str]
    revoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "actor_class": self.actor_class,
            "public_signing_key_b64": self.public_signing_key_b64,
            "public_encryption_key_b64": self.public_encryption_key_b64,
            "runtime_model_identity": self.runtime_model_identity,
            "execution_region": self.execution_region,
            "capabilities": self.capabilities,
            "revoked": self.revoked,
            "fco_type": "ActorFCO",
        }


@dataclass
class ActorRegistry:
    actors: dict[str, ActorFCO] = field(default_factory=dict)

    def register(self, actor: ActorFCO) -> None:
        self.actors[actor.actor_id] = actor

    def get(self, actor_id: str) -> ActorFCO | None:
        return self.actors.get(actor_id)

    def revoke(self, actor_id: str) -> None:
        if actor_id in self.actors:
            self.actors[actor_id].revoked = True

    def to_fco_list(self) -> list[dict[str, Any]]:
        return [a.to_dict() for a in self.actors.values()]
