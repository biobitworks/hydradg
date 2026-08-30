"""ContextScoreFCO — routing/diagnostic evidence only; never authorizes access."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hydralamp.crypto import canonical_json, sha256_text

SCORER_ID = "hydralamp-context-scorer-v1"
SCORER_CONFIG = {
    "version": "1.0.0",
    "features": ["access_pattern", "provenance_completeness", "poison_proximity"],
    "weights": {"access_pattern": 0.4, "provenance": 0.35, "poison_proximity": 0.25},
}
SCORER_CONFIG_HASH = sha256_text(canonical_json(SCORER_CONFIG))


@dataclass(frozen=True)
class ContextScoreFCO:
    """Versioned context score bound to an FCO or knowledge leaf."""

    target_fco_id: str
    input_hashes: dict[str, str]
    score_0_100: float
    uncertainty_0_1: float
    evidence_class: str
    scorer_id: str = SCORER_ID
    scorer_config_hash: str = SCORER_CONFIG_HASH
    version: int = 1
    authorizes_access: bool = False  # invariant: always False

    def to_dict(self) -> dict[str, Any]:
        body = {
            "fco_type": "ContextScoreFCO",
            "target_fco_id": self.target_fco_id,
            "input_hashes": self.input_hashes,
            "score_0_100": round(self.score_0_100, 4),
            "uncertainty_0_1": round(self.uncertainty_0_1, 4),
            "evidence_class": self.evidence_class,
            "scorer_id": self.scorer_id,
            "scorer_config_hash": self.scorer_config_hash,
            "version": self.version,
            "authorizes_access": False,
            "routing_only": True,
            "claim_ceiling": "CONTEXT_ROUTING_DIAGNOSTIC_ONLY",
        }
        body["fco_id"] = f"fco:ctxscore:{sha256_text(canonical_json(body))[:32]}"
        body["object_sha256"] = sha256_text(canonical_json(body))
        return body


def score_leaf(
    target_fco_id: str,
    *,
    event_hash: str,
    fcg_root: str,
    msm_state: str,
    actor_id: str,
    poison_proximity: float = 0.0,
) -> ContextScoreFCO:
    """Deterministic scorer — same inputs yield same score."""
    input_hashes = {
        "event_hash": event_hash,
        "fcg_root": fcg_root,
        "msm_state": msm_state,
        "actor_id_hash": sha256_text(actor_id),
    }
    access_component = 30.0 if msm_state in ("AUTHENTICATED", "CAPABILITY_GRANTED") else 10.0
    provenance_component = 40.0 if fcg_root else 5.0
    poison_component = max(0.0, 100.0 - poison_proximity * 100.0)
    w = SCORER_CONFIG["weights"]
    score = (
        w["access_pattern"] * access_component
        + w["provenance"] * provenance_component
        + w["poison_proximity"] * poison_component
    )
    uncertainty = min(1.0, 0.15 + poison_proximity * 0.5 + (0.1 if msm_state == "UNKNOWN" else 0.0))
    evidence_class = "DETERMINISTIC_CONTEXT_SCORE"
    if poison_proximity > 0.5:
        evidence_class = "ELEVATED_POISON_PROXIMITY_DIAGNOSTIC"
    return ContextScoreFCO(
        target_fco_id=target_fco_id,
        input_hashes=input_hashes,
        score_0_100=min(100.0, score),
        uncertainty_0_1=uncertainty,
        evidence_class=evidence_class,
    )
