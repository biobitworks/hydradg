"""SELF_SAFE — proof of possession + current authorization state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hydralamp.crypto import canonical_json, sign_message, sha256_text, verify_signature


@dataclass
class SelfSafeVerdict:
    self_safe: bool
    proof_of_possession: bool
    authorization_current: bool
    context_score_assigned: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "self_safe": self.self_safe,
            "proof_of_possession": self.proof_of_possession,
            "authorization_current": self.authorization_current,
            "context_score_assigned": self.context_score_assigned,
            "reason": self.reason,
            "note": "SELF_SAFE requires PoP + authorization; context score alone is insufficient",
        }


def evaluate_self_safe(
    *,
    actor_id: str,
    private_key,
    public_key,
    challenge: bytes,
    signature: bytes,
    capability_valid: bool,
    actor_revoked: bool,
    context_score: float | None,
) -> SelfSafeVerdict:
    pop = verify_signature(public_key, challenge, signature)
    auth = capability_valid and not actor_revoked
    # Context score is recorded but never sufficient
    self_safe = pop and auth
    reason = "SELF_SAFE_ESTABLISHED" if self_safe else "SELF_SAFE_DENIED"
    if not pop:
        reason = "PROOF_OF_POSSESSION_FAILED"
    elif actor_revoked:
        reason = "ACTOR_REVOKED"
    elif not auth:
        reason = "AUTHORIZATION_NOT_CURRENT"
    return SelfSafeVerdict(
        self_safe=self_safe,
        proof_of_possession=pop,
        authorization_current=auth,
        context_score_assigned=context_score is not None,
        reason=reason,
    )


def build_challenge(actor_id: str, nonce: str) -> bytes:
    return canonical_json({"actor_id": actor_id, "nonce": nonce, "purpose": "self_safe_pop"}).encode()
