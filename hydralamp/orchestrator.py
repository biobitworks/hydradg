"""HydraLamp orchestrator — CFMO, ContextScoreFCO, MMR, SELF_SAFE integration."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hydralamp.anticube import run_dual_world_anticube
from hydralamp.cfmo import CFMOStore
from hydralamp.context_score import score_leaf
from hydralamp.gateway import HydraLampGateway
from hydralamp.mmr import MMRAccumulator
from hydralamp.self_safe import build_challenge, evaluate_self_safe
from hydralamp.toy_key import public_fcg_key_metadata, CLAIM_CEILING as TOY_CLAIM
from hydralamp.crypto import sign_message


@dataclass
class HydraLampOrchestrator:
    eval_root: Path
    gateway: HydraLampGateway
    cfmo: CFMOStore = field(default_factory=lambda: CFMOStore(Path("/dev/null")))
    mmr: MMRAccumulator = field(default_factory=MMRAccumulator)
    context_scores: list[dict[str, Any]] = field(default_factory=list)
    self_safe_verdicts: list[dict[str, Any]] = field(default_factory=list)
    toy_key_metadata: dict[str, Any] = field(default_factory=dict)
    variance_records: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.cfmo.path == Path("/dev/null"):
            self.cfmo = CFMOStore(self.eval_root / "CFMO_TRAJECTORY.json")

    @classmethod
    def bootstrap(cls, eval_root: Path, mode: str = "TOY_DISTRIBUTED_PRIVATE_KEY") -> "HydraLampOrchestrator":
        gw = HydraLampGateway.bootstrap(eval_root, mode=mode if mode != "TOY_DISTRIBUTED_PRIVATE_KEY" else "TEST_VECTOR_REPLAY")
        orch = cls(eval_root=eval_root, gateway=gw)
        if mode == "TOY_DISTRIBUTED_PRIVATE_KEY":
            for actor_id in orch.gateway.actors.actors:
                orch.toy_key_metadata[actor_id] = public_fcg_key_metadata(actor_id)
            orch.cfmo.append("TOY_KEY_MODE", {"claim_ceiling": TOY_CLAIM}, actor_id="AUTHORITY", event_index=0)
        return orch

    def record_event(self, event: dict[str, Any]) -> None:
        """Append CFMO version, context score, and MMR leaf for each real event."""
        state_type = event.get("event_type", "UNKNOWN")
        if "POISON" in state_type or "QUARANTINE" in state_type:
            cfmo_type = "POISON" if "POISON" in state_type else "QUARANTINE"
        elif "PROMOTED" in state_type:
            cfmo_type = "CANONICAL"
        elif "DENIED" in state_type or "REJECT" in state_type:
            cfmo_type = "RETAINED_REJECTION"
        else:
            cfmo_type = "TRANSITION"

        cfmo_rec = self.cfmo.append(
            cfmo_type,
            {"event_type": state_type, "actor_id": event.get("actor_id"), "access": event.get("access_decision")},
            actor_id=event.get("actor_id", "UNKNOWN"),
            event_index=event.get("event_index", 0),
        )

        ctx = score_leaf(
            target_fco_id=event.get("fco_ids", ["unknown"])[0] if event.get("fco_ids") else f"fco:event:{event.get('event_index')}",
            event_hash=event.get("event_hash", ""),
            fcg_root=event.get("fcg_root_after", ""),
            msm_state=event.get("msm_state_after", "UNKNOWN"),
            actor_id=event.get("actor_id", "UNKNOWN"),
            poison_proximity=1.0 if cfmo_type in ("POISON", "QUARANTINE") else 0.0,
        )
        self.context_scores.append(ctx.to_dict())

        self.mmr.append(
            event.get("event_index", 0),
            event.get("event_hash", ""),
            cfmo_rec["version_id"],
        )

    def finalize_mmr(self) -> dict[str, Any]:
        receipt = self.mmr.save(self.eval_root / "MMR_COMMITMENT.json")
        self.cfmo.append(
            "MMR_COMMITTED",
            {"root_sha256": receipt["root_sha256"], "leaf_count": receipt["leaf_count"]},
            actor_id="AUTHORITY",
            event_index=self.gateway.event_log._index if self.gateway.event_log else 0,
        )
        return receipt

    def run_self_safe_checks(self) -> list[dict[str, Any]]:
        for actor_id in ["HUMAN_CONTROLLER", "RESEARCH_AGENT"]:
            broker = self.gateway.broker.ed25519(actor_id)
            challenge = build_challenge(actor_id, "self-safe-canary")
            sig = sign_message(broker.private_key, challenge)
            verdict = evaluate_self_safe(
                actor_id=actor_id,
                private_key=broker.private_key,
                public_key=broker.public_key,
                challenge=challenge,
                signature=sig,
                capability_valid=True,
                actor_revoked=False,
                context_score=50.0,
            )
            self.self_safe_verdicts.append(verdict.to_dict())
        return self.self_safe_verdicts

    def save(self) -> dict[str, Any]:
        self.gateway.save()
        self.cfmo.save()
        mmr_receipt = self.finalize_mmr()
        out = {
            "context_scores": self.context_scores,
            "self_safe_verdicts": self.self_safe_verdicts,
            "toy_key_metadata": self.toy_key_metadata,
            "variance_records": self.variance_records,
            "mmr_receipt": mmr_receipt,
            "cfmo_version_count": len(self.cfmo.versions),
        }
        (self.eval_root / "ORCHESTRATOR_STATE.json").write_text(json.dumps(out, indent=2))
        return out

    def sync_events_from_gateway(self) -> None:
        if self.gateway.event_log:
            for ev in self.gateway.event_log.events:
                if ev.get("event_index", 0) > len(self.mmr.leaves):
                    self.record_event(ev)
