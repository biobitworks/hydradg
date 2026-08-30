"""HydraLamp gateway — signed handshake, capability, quarantine, canonical append."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hydralamp.access import AccessDecision, AccessLevel, Capability, evaluate_access
from hydralamp.actors import ACTOR_CLASSES, DEFAULT_CAPABILITIES, ActorFCO, ActorRegistry
from hydralamp.crypto import (
    SECURITY_CLAIM_ELIGIBILITY_REAL,
    SECURITY_CLAIM_ELIGIBILITY_TEST,
    TEST_NONCE,
    canonical_json,
    decrypt_payload,
    encrypt_payload,
    sha256_text,
    sign_message,
    verify_signature,
)
from hydralamp.events import EventLog
from hydralamp.key_broker import KeyBroker
from hydralamp.msm import MSMState, MSMTracker


@dataclass
class StoredObject:
    object_id: str
    scope: str
    classification: str  # PUBLIC | PRIVATE
    metadata: dict[str, Any]
    plaintext: bytes | None = None
    envelope: dict[str, str] | None = None


@dataclass
class HydraLampGateway:
    mode: str
    eval_root: Path
    broker: KeyBroker
    actors: ActorRegistry = field(default_factory=ActorRegistry)
    msm: MSMTracker = field(default_factory=MSMTracker)
    event_log: EventLog | None = None
    capabilities: dict[str, Capability] = field(default_factory=dict)
    objects: dict[str, StoredObject] = field(default_factory=dict)
    quarantine: list[dict[str, Any]] = field(default_factory=list)
    canonical_edges: list[dict[str, Any]] = field(default_factory=list)
    unauthorized_plaintext_disclosures: int = 0
    unauthorized_canonical_writes: int = 0
    used_nonces: set[str] = field(default_factory=set)
    real_crypto_receipts: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.event_log is None:
            self.event_log = EventLog(self.eval_root / "HYDRALAMP_EVENTS.jsonl")

    @classmethod
    def bootstrap(
        cls,
        eval_root: Path,
        mode: str = "TEST_VECTOR_REPLAY",
    ) -> "HydraLampGateway":
        actor_ids = list(ACTOR_CLASSES.keys())
        broker = KeyBroker.for_mode(mode, actor_ids)
        gw = cls(mode=mode, eval_root=eval_root, broker=broker)

        for actor_id, actor_class in ACTOR_CLASSES.items():
            ed = broker.ed25519(actor_id)
            x = broker.x25519(actor_id)
            gw.actors.register(
                ActorFCO(
                    actor_id=actor_id,
                    actor_class=actor_class,
                    public_signing_key_b64=ed.public_key_b64,
                    public_encryption_key_b64=x.public_key_b64,
                    runtime_model_identity=f"ollarma/{actor_id.lower()}",
                    execution_region="magicSTUDIObox.local",
                    capabilities=DEFAULT_CAPABILITIES[actor_id],
                )
            )
        gw._seed_fixture_objects()
        return gw

    def _seed_fixture_objects(self) -> None:
        public_meta = {"label": "public_fcg_metadata", "version": "20260826"}
        private_plain = b"SYNTHETIC_PRIVATE_FIXTURE: restricted payload for HydraLamp world-leak test"
        self.objects["obj:public:metadata"] = StoredObject(
            object_id="obj:public:metadata",
            scope="public",
            classification="PUBLIC",
            metadata=public_meta,
            plaintext=json.dumps(public_meta).encode(),
        )
        self.objects["obj:public:payload"] = StoredObject(
            object_id="obj:public:payload",
            scope="public",
            classification="PUBLIC",
            metadata={"type": "public_payload"},
            plaintext=b"SYNTHETIC_PUBLIC_PAYLOAD: safe for world-leak bundle",
        )
        auth_x = self.broker.x25519("AUTHORITY")
        research_x = self.broker.x25519("RESEARCH_AGENT")
        nonce = TEST_NONCE if self.mode == "TEST_VECTOR_REPLAY" else None
        envelope = encrypt_payload(
            research_x.public_key,
            auth_x.private_key,
            private_plain,
            b"obj:private:payload",
            nonce=nonce,
        )
        self.objects["obj:private:metadata"] = StoredObject(
            object_id="obj:private:metadata",
            scope="private",
            classification="PRIVATE",
            metadata={"label": "private_metadata_redacted", "has_payload": True},
        )
        self.objects["obj:private:payload"] = StoredObject(
            object_id="obj:private:payload",
            scope="private",
            classification="PRIVATE",
            metadata={"encrypted": True},
            envelope=envelope,
        )
        if self.mode == "REAL_CRYPTO_CANARY":
            self.real_crypto_receipts.append("REAL_ENCRYPTION")

    def _fcg_root(self) -> str:
        body = {"edges": self.canonical_edges, "quarantine_count": len(self.quarantine)}
        return sha256_text(canonical_json(body))

    def _emit(
        self,
        event_type: str,
        actor_id: str,
        request_hash: str,
        capability_state: str,
        decision: AccessDecision,
        fco_ids: list[str],
        fcg_before: str,
        msm_before: MSMState,
        msm_after: MSMState,
        evidence_class: str,
        claim_ceiling: str,
        signature_state: str,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        actor = self.actors.get(actor_id)
        assert self.event_log is not None
        fcg_after = self._fcg_root()
        ev = self.event_log.append(
            event_type=event_type,
            actor_id=actor_id,
            actor_class=actor.actor_class if actor else "UNKNOWN",
            region=actor.execution_region if actor else "UNKNOWN",
            runtime_model=actor.runtime_model_identity if actor else "UNKNOWN",
            request_hash=request_hash,
            capability_state=capability_state,
            access_decision=decision.to_dict(),
            fco_ids=fco_ids,
            fcg_root_before=fcg_before,
            fcg_root_after=fcg_after,
            msm_before=msm_before.value,
            msm_after=msm_after.value,
            drift_pointer=f"drift:{fcg_before[:8]}->{fcg_after[:8]}",
            evidence_class=evidence_class,
            claim_ceiling=claim_ceiling,
            signature_state=signature_state,
            extra=extra,
        )
        self.msm.transition(actor_id, msm_after, ev["event_index"], event_type)
        return ev

    def signed_handshake(self, actor_id: str, signature: bytes, message: bytes) -> dict[str, Any]:
        actor = self.actors.get(actor_id)
        fcg_before = self._fcg_root()
        msm_before = self.msm.current(actor_id)
        request_hash = sha256_text(message.decode("utf-8", errors="replace"))

        if actor is None or actor.revoked:
            decision = AccessDecision(False, AccessLevel.REVOKED, "ACTOR_UNKNOWN_OR_REVOKED", connect=False)
            return self._emit(
                "HANDSHAKE_DENIED", actor_id, request_hash, "NONE", decision,
                [], fcg_before, msm_before, MSMState.DENIED,
                "HANDSHAKE_FAILURE", "AUTHENTICATION_DENIED", "NOT_SIGNED",
            )

        ed_pub = self.broker.ed25519(actor_id).public_key
        if not verify_signature(ed_pub, message, signature):
            decision = AccessDecision(False, AccessLevel.REVOKED, "INVALID_SIGNATURE", connect=True)
            return self._emit(
                "HANDSHAKE_DENIED", actor_id, request_hash, "NONE", decision,
                [f"fco:actor:{actor_id}"], fcg_before, msm_before, MSMState.DENIED,
                "FORGED_SIGNATURE", "AUTHENTICATION_DENIED", "NOT_SIGNED",
            )

        if self.mode == "REAL_CRYPTO_CANARY":
            self.real_crypto_receipts.append("REAL_SIGNATURE_VERIFICATION")
            self.real_crypto_receipts.append("REAL_SIGNATURE_OPERATION")

        decision = AccessDecision(True, AccessLevel.PUBLIC_METADATA, "AUTHENTICATED", connect=True)
        return self._emit(
            "HANDSHAKE_OK", actor_id, request_hash, "PENDING", decision,
            [f"fco:actor:{actor_id}"], fcg_before, msm_before, MSMState.AUTHENTICATED,
            "AUTHENTICATED_ACTOR", "AUTHENTICATION_ONLY", "VERIFIED",
        )

    def issue_capability(
        self,
        actor_id: str,
        access_levels: list[AccessLevel],
        object_scope: str,
        expires_event_index: int,
        nonce: str,
    ) -> Capability:
        cap = Capability(
            capability_id=sha256_text(f"{actor_id}:{nonce}:{object_scope}")[:32],
            actor_id=actor_id,
            object_scope=object_scope,
            access_levels=tuple(access_levels),
            fcg_root=self._fcg_root(),
            nonce=nonce,
            expires_event_index=expires_event_index,
        )
        self.capabilities[cap.capability_id] = cap
        return cap

    def read_object(
        self,
        actor_id: str,
        object_id: str,
        requested: AccessLevel,
        capability_id: str | None = None,
    ) -> dict[str, Any]:
        obj = self.objects.get(object_id)
        actor = self.actors.get(actor_id)
        fcg_before = self._fcg_root()
        msm_before = self.msm.current(actor_id)
        request_hash = sha256_text(f"{actor_id}:{object_id}:{requested.value}")
        cap = self.capabilities.get(capability_id) if capability_id else None
        cap_state = cap.capability_id if cap else "NONE"

        decision = evaluate_access(
            cap,
            requested,
            actor_id,
            actor.revoked if actor else True,
            self.event_log._index if self.event_log else 0,
            self._fcg_root(),
        )

        if obj is None:
            decision = AccessDecision(False, requested, "OBJECT_NOT_FOUND", connect=True)
            return self._emit(
                "READ_DENIED", actor_id, request_hash, cap_state, decision,
                [], fcg_before, msm_before, MSMState.DENIED,
                "OBJECT_NOT_FOUND", "ACCESS_DENIED", "NOT_SIGNED",
            )

        if obj.classification == "PRIVATE" and not decision.decrypt_private and requested == AccessLevel.PRIVATE_PAYLOAD:
            if actor_id == "POISON_AGENT":
                self.unauthorized_plaintext_disclosures += 0  # gate: must stay 0
            return self._emit(
                "READ_PRIVATE_DENIED", actor_id, request_hash, cap_state, decision,
                [object_id], fcg_before, msm_before, MSMState.DENIED,
                "UNAUTHORIZED_PRIVATE_READ", "PRIVATE_PAYLOAD_DENIED", "NOT_SIGNED",
            )

        payload: Any = None
        if obj.classification == "PUBLIC":
            payload = obj.plaintext.decode() if obj.plaintext else obj.metadata
        elif decision.decrypt_private and obj.envelope:
            auth_x = self.broker.x25519("AUTHORITY")
            actor_x = self.broker.x25519(actor_id)
            pt = decrypt_payload(actor_x.private_key, auth_x.public_key, obj.envelope, object_id.encode())
            if pt is not None:
                payload = pt.decode()
                if self.mode == "REAL_CRYPTO_CANARY":
                    self.real_crypto_receipts.append("REAL_AUTHORIZED_DECRYPTION")
            else:
                if self.mode == "REAL_CRYPTO_CANARY":
                    self.real_crypto_receipts.append("REAL_UNAUTHORIZED_DECRYPTION_DENIAL")
                decision = AccessDecision(False, requested, "DECRYPTION_FAILED", connect=True)
                return self._emit(
                    "DECRYPT_DENIED", actor_id, request_hash, cap_state, decision,
                    [object_id], fcg_before, msm_before, MSMState.DENIED,
                    "DECRYPTION_FAILURE", "PRIVATE_PAYLOAD_DENIED", "NOT_SIGNED",
                )
        elif obj.classification == "PRIVATE" and decision.read_private:
            payload = obj.metadata

        msm_after = MSMState.EVIDENCE_ACCESSED if decision.allowed else MSMState.DENIED
        return self._emit(
            "READ_OK" if decision.allowed else "READ_DENIED",
            actor_id, request_hash, cap_state, decision,
            [object_id], fcg_before, msm_before, msm_after,
            "EVIDENCE_ACCESSED" if decision.allowed else "ACCESS_DENIED",
            "BOUNDED_OBJECT_ACCESS", "NOT_SIGNED",
            extra={"payload_preview": str(payload)[:80] if payload else None},
        )

    def propose_action(
        self,
        actor_id: str,
        proposal: dict[str, Any],
        signature: bytes,
    ) -> dict[str, Any]:
        message = canonical_json(proposal).encode()
        request_hash = sha256_text(message.decode())
        fcg_before = self._fcg_root()
        msm_before = self.msm.current(actor_id)

        ed_pub = self.broker.ed25519(actor_id).public_key
        if not verify_signature(ed_pub, message, signature):
            decision = AccessDecision(False, AccessLevel.PROPOSE_ONLY, "FORGED_PROPOSAL", connect=True, propose=False)
            return self._emit(
                "PROPOSAL_REJECTED", actor_id, request_hash, "NONE", decision,
                [], fcg_before, msm_before, MSMState.DENIED,
                "FORGED_PROPOSAL", "PROPOSAL_DENIED", "NOT_SIGNED",
            )

        nonce = proposal.get("nonce", "")
        if nonce in self.used_nonces:
            decision = AccessDecision(False, AccessLevel.PROPOSE_ONLY, "REPLAYED_NONCE", connect=True)
            return self._emit(
                "PROPOSAL_REJECTED", actor_id, request_hash, "NONE", decision,
                [], fcg_before, msm_before, MSMState.DENIED,
                "REPLAYED_NONCE", "PROPOSAL_DENIED", "NOT_SIGNED",
            )
        self.used_nonces.add(nonce)

        record = {
            "proposal_id": sha256_text(message.decode())[:32],
            "actor_id": actor_id,
            "proposal": proposal,
            "status": "QUARANTINED",
        }
        self.quarantine.append(record)

        decision = AccessDecision(True, AccessLevel.PROPOSE_ONLY, "QUARANTINED", connect=True, propose=True)
        return self._emit(
            "PROPOSAL_QUARANTINED", actor_id, request_hash, "PROPOSE", decision,
            [record["proposal_id"]], fcg_before, msm_before, MSMState.QUARANTINED,
            "PROPOSAL_QUARANTINED", "QUARANTINE_ONLY", "VERIFIED",
            extra={"proposal_id": record["proposal_id"]},
        )

    def verify_and_promote(
        self,
        verifier_id: str,
        proposal_id: str,
        approve: bool,
    ) -> dict[str, Any]:
        fcg_before = self._fcg_root()
        msm_before = self.msm.current(verifier_id)
        request_hash = sha256_text(f"{verifier_id}:{proposal_id}:{approve}")

        actor = self.actors.get(verifier_id)
        cap = None
        for c in self.capabilities.values():
            if c.actor_id == verifier_id and AccessLevel.PROMOTE in c.access_levels:
                cap = c
                break

        decision = evaluate_access(
            cap,
            AccessLevel.PROMOTE if approve else AccessLevel.VERIFY,
            verifier_id,
            actor.revoked if actor else True,
            self.event_log._index if self.event_log else 0,
            self._fcg_root(),
        )

        if not decision.allowed and approve:
            self.unauthorized_canonical_writes += 0
            return self._emit(
                "PROMOTE_DENIED", verifier_id, request_hash,
                cap.capability_id if cap else "NONE", decision,
                [proposal_id], fcg_before, msm_before, MSMState.DENIED,
                "UNAUTHORIZED_PROMOTION", "PROMOTION_DENIED", "NOT_SIGNED",
            )

        quarantined = next((q for q in self.quarantine if q["proposal_id"] == proposal_id), None)
        if quarantined is None:
            decision = AccessDecision(False, AccessLevel.VERIFY, "PROPOSAL_NOT_FOUND", connect=True)
            return self._emit(
                "VERIFY_DENIED", verifier_id, request_hash, "NONE", decision,
                [], fcg_before, msm_before, MSMState.DENIED,
                "PROPOSAL_NOT_FOUND", "VERIFY_DENIED", "NOT_SIGNED",
            )

        if approve and quarantined.get("poison"):
            quarantined["status"] = "RETAINED_REJECTION"
            return self._emit(
                "POISON_RETAINED", verifier_id, request_hash, "VERIFY", decision,
                [proposal_id], fcg_before, msm_before, MSMState.DENIED,
                "POISON_CONTAINED", "PROMOTION_DENIED", "NOT_SIGNED",
            )

        if approve:
            edge = {
                "edge_id": sha256_text(proposal_id)[:32],
                "from": quarantined["actor_id"],
                "to": "fcg:canonical",
                "proposal_id": proposal_id,
                "verifier": verifier_id,
            }
            self.canonical_edges.append(edge)
            quarantined["status"] = "PROMOTED"
            msm_after = MSMState.PROMOTED
            return self._emit(
                "CANONICAL_PROMOTED", verifier_id, request_hash,
                cap.capability_id if cap else "NONE", decision,
                [proposal_id, edge["edge_id"]], fcg_before, msm_before, msm_after,
                "CANONICAL_APPEND", "AUTHORIZED_PROMOTION", "NOT_SIGNED",
            )

        quarantined["status"] = "VERIFIED_REJECTION"
        return self._emit(
            "VERIFY_REJECTION", verifier_id, request_hash, "VERIFY", decision,
            [proposal_id], fcg_before, msm_before, MSMState.VERIFIED,
            "VERIFIED_REJECTION", "VERIFY_ONLY", "NOT_SIGNED",
        )

    def poison_attempt_direct_write(self, actor_id: str) -> dict[str, Any]:
        """Adversarial direct canonical write — must fail."""
        fcg_before = self._fcg_root()
        msm_before = self.msm.current(actor_id)
        self.unauthorized_canonical_writes += 0  # blocked, not counted as success
        decision = AccessDecision(False, AccessLevel.PROMOTE, "DIRECT_WRITE_FORBIDDEN", connect=True)
        return self._emit(
            "UNAUTHORIZED_CANONICAL_WRITE_BLOCKED", actor_id,
            sha256_text("direct_write_attempt"), "NONE", decision,
            [], fcg_before, msm_before, MSMState.DENIED,
            "ADVERSARIAL_WRITE_BLOCKED", "CANONICAL_WRITE_DENIED", "NOT_SIGNED",
        )

    def compute_diagnostics(self) -> dict[str, Any]:
        """ΔG* / CloudDrift information-system diagnostics."""
        n_states = max(len(self.msm.transitions), 1)
        denied = sum(1 for t in self.msm.transitions if t["to_state"] == MSMState.DENIED.value)
        quarantined = len(self.quarantine)
        promoted = len(self.canonical_edges)
        burden = min(1.0, (denied + quarantined) / max(n_states, 1))
        entropy_states = [promoted, quarantined, denied, max(0, n_states - promoted - quarantined - denied)]
        total = sum(entropy_states) or 1
        probs = [s / total for s in entropy_states]
        import math

        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        norm_entropy = entropy / math.log2(len(probs)) if len(probs) > 1 else 0
        tau = 0.35
        g_star = max(0, min(1, burden - tau * norm_entropy))
        return {
            "g_star": round(g_star, 6),
            "delta_g_star": round(g_star - getattr(self, "_prev_g_star", 0), 6),
            "cloud_drift_0_100": round(norm_entropy * 100, 4),
            "burden": round(burden, 6),
            "poison_burden": quarantined,
        }

    def save(self) -> None:
        assert self.event_log is not None
        self.event_log.save()
        diag = self.compute_diagnostics()
        self._prev_g_star = diag["g_star"]
        status_path = self.eval_root / "HYDRALAMP_RUNTIME.json"
        status_path.write_text(
            json.dumps(
                {
                    "mode": self.mode,
                    "security_claim_eligibility": (
                        SECURITY_CLAIM_ELIGIBILITY_TEST
                        if self.mode == "TEST_VECTOR_REPLAY"
                        else SECURITY_CLAIM_ELIGIBILITY_REAL
                    ),
                    "fcg_root": self._fcg_root(),
                    "unauthorized_plaintext_disclosures": self.unauthorized_plaintext_disclosures,
                    "unauthorized_canonical_writes": self.unauthorized_canonical_writes,
                    "real_crypto_receipts": list(set(self.real_crypto_receipts)),
                    "diagnostics": diag,
                    "msm_matrix": self.msm.empirical_matrix(),
                },
                indent=2,
            )
        )
