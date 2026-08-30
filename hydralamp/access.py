"""HydraLamp access levels and capability authorization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class AccessLevel(str, Enum):
    PUBLIC_METADATA = "PUBLIC_METADATA"
    PUBLIC_PAYLOAD = "PUBLIC_PAYLOAD"
    PRIVATE_METADATA = "PRIVATE_METADATA"
    PRIVATE_PAYLOAD = "PRIVATE_PAYLOAD"
    PROPOSE_ONLY = "PROPOSE_ONLY"
    VERIFY = "VERIFY"
    PROMOTE = "PROMOTE"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class Capability:
    capability_id: str
    actor_id: str
    object_scope: str
    access_levels: tuple[AccessLevel, ...]
    fcg_root: str
    nonce: str
    expires_event_index: int
    issuer: str = "AUTHORITY"
    revoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "actor_id": self.actor_id,
            "object_scope": self.object_scope,
            "access_levels": [a.value for a in self.access_levels],
            "fcg_root": self.fcg_root,
            "nonce": self.nonce,
            "expires_event_index": self.expires_event_index,
            "issuer": self.issuer,
            "revoked": self.revoked,
        }


@dataclass
class AccessDecision:
    allowed: bool
    access_level: AccessLevel
    reason: str
    connect: bool = False
    read_private: bool = False
    decrypt_private: bool = False
    propose: bool = False
    promote: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "access_level": self.access_level.value,
            "reason": self.reason,
            "connect": self.connect,
            "read_private": self.read_private,
            "decrypt_private": self.decrypt_private,
            "propose": self.propose,
            "promote": self.promote,
        }


def evaluate_access(
    capability: Capability | None,
    requested: AccessLevel,
    actor_id: str,
    actor_revoked: bool,
    event_index: int,
    fcg_root: str,
) -> AccessDecision:
    if actor_revoked:
        return AccessDecision(
            allowed=False,
            access_level=AccessLevel.REVOKED,
            reason="ACTOR_REVOKED",
        )

    if capability is None:
        if requested in (AccessLevel.PUBLIC_METADATA, AccessLevel.PUBLIC_PAYLOAD):
            return AccessDecision(
                allowed=True,
                access_level=requested,
                reason="PUBLIC_ACCESS",
                connect=True,
            )
        return AccessDecision(
            allowed=False,
            access_level=requested,
            reason="NO_CAPABILITY",
            connect=True,
        )

    if capability.revoked:
        return AccessDecision(
            allowed=False,
            access_level=AccessLevel.REVOKED,
            reason="CAPABILITY_REVOKED",
            connect=True,
        )

    if capability.actor_id != actor_id:
        return AccessDecision(
            allowed=False,
            access_level=requested,
            reason="CAPABILITY_ACTOR_MISMATCH",
            connect=True,
        )

    if capability.fcg_root != fcg_root:
        return AccessDecision(
            allowed=False,
            access_level=requested,
            reason="STALE_FCG_ROOT",
            connect=True,
        )

    if event_index > capability.expires_event_index:
        return AccessDecision(
            allowed=False,
            access_level=requested,
            reason="CAPABILITY_EXPIRED",
            connect=True,
            propose=AccessLevel.PROPOSE_ONLY in capability.access_levels,
        )

    if requested not in capability.access_levels:
        return AccessDecision(
            allowed=False,
            access_level=requested,
            reason="CAPABILITY_DENIED",
            connect=True,
            propose=AccessLevel.PROPOSE_ONLY in capability.access_levels,
            read_private=AccessLevel.PRIVATE_METADATA in capability.access_levels,
            decrypt_private=AccessLevel.PRIVATE_PAYLOAD in capability.access_levels,
            promote=AccessLevel.PROMOTE in capability.access_levels,
        )

    return AccessDecision(
        allowed=True,
        access_level=requested,
        reason="CAPABILITY_GRANTED",
        connect=True,
        read_private=requested in (AccessLevel.PRIVATE_METADATA, AccessLevel.PRIVATE_PAYLOAD),
        decrypt_private=requested == AccessLevel.PRIVATE_PAYLOAD,
        propose=AccessLevel.PROPOSE_ONLY in capability.access_levels,
        promote=AccessLevel.PROMOTE in capability.access_levels,
    )
