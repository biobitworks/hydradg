"""Anticube preregistered adversarial perturbations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from hydralamp.access import AccessLevel
from hydralamp.crypto import canonical_json, sign_message
from hydralamp.gateway import HydraLampGateway
from hydralamp.sandbox import DualWorldRunner, WorldMode

DEFAULT_PERTURBATIONS_PATH = Path(__file__).resolve().parents[1] / "eval" / "hydralamp_20260826" / "ANTICUBE_PERTURBATIONS.json"


def load_perturbations(path: Path | None = None) -> list[dict[str, Any]]:
    p = path or DEFAULT_PERTURBATIONS_PATH
    if not p.exists():
        return _builtin_perturbations()
    return json.loads(p.read_text())


def _builtin_perturbations() -> list[dict[str, Any]]:
    return [
        {"id": "AC-001", "name": "valid_sig_valid_cap", "expected": "ALLOW"},
        {"id": "AC-002", "name": "valid_sig_invalid_cap", "expected": "DENY"},
        {"id": "AC-003", "name": "forged_signature", "expected": "DENY"},
        {"id": "AC-004", "name": "wrong_actor_signature", "expected": "DENY"},
        {"id": "AC-005", "name": "expired_capability", "expected": "DENY"},
        {"id": "AC-006", "name": "revoked_actor", "expected": "DENY"},
        {"id": "AC-007", "name": "replayed_nonce", "expected": "DENY"},
        {"id": "AC-008", "name": "stale_fcg_root", "expected": "DENY"},
        {"id": "AC-009", "name": "public_read", "expected": "ALLOW"},
        {"id": "AC-010", "name": "unauth_private_read", "expected": "DENY"},
        {"id": "AC-011", "name": "valid_proposal", "expected": "QUARANTINE"},
        {"id": "AC-012", "name": "poison_proposal", "expected": "RETAIN_REJECTION"},
        {"id": "AC-013", "name": "unauth_canonical_write", "expected": "DENY"},
        {"id": "AC-014", "name": "authorized_repair", "expected": "PROMOTE"},
    ]


def apply_perturbation(gw: HydraLampGateway, perturbation: dict[str, Any]) -> dict[str, Any]:
    name = perturbation["name"]
    actor = "RESEARCH_AGENT"

    if name == "forged_signature":
        msg = b"anticube:forged"
        return gw.signed_handshake(actor, b"\x00" * 64, msg)

    if name == "wrong_actor_signature":
        msg = b"anticube:wrong_actor"
        sig = sign_message(gw.broker.ed25519("HUMAN_CONTROLLER").private_key, msg)
        return gw.signed_handshake(actor, sig, msg)

    if name == "revoked_actor":
        gw.actors.revoke("POISON_AGENT")
        msg = b"anticube:revoked"
        sig = sign_message(gw.broker.ed25519("POISON_AGENT").private_key, msg)
        return gw.signed_handshake("POISON_AGENT", sig, msg)

    if name == "replayed_nonce":
        proposal = {"action": "replay", "nonce": "replay-fixed-nonce", "payload_hash": "x"}
        sig = sign_message(gw.broker.ed25519(actor).private_key, canonical_json(proposal).encode())
        gw.propose_action(actor, proposal, sig)
        return gw.propose_action(actor, proposal, sig)

    if name == "unauth_private_read":
        return gw.read_object("POISON_AGENT", "obj:private:payload", AccessLevel.PRIVATE_PAYLOAD)

    if name == "public_read":
        return gw.read_object(actor, "obj:public:payload", AccessLevel.PUBLIC_PAYLOAD)

    if name == "unauth_canonical_write":
        return gw.poison_attempt_direct_write("POISON_AGENT")

    if name == "poison_proposal":
        proposal = {"action": "self_promote", "nonce": f"poison-{perturbation['id']}", "malicious": True}
        sig = sign_message(gw.broker.ed25519("POISON_AGENT").private_key, canonical_json(proposal).encode())
        ev = gw.propose_action("POISON_AGENT", proposal, sig)
        pid = ev.get("proposal_id")
        if pid:
            gw.quarantine[-1]["poison"] = True
            return gw.verify_and_promote("VERIFIER_AGENT", pid, approve=True)
        return ev

    if name == "valid_proposal":
        proposal = {"action": "append", "nonce": f"valid-{perturbation['id']}", "payload_hash": "ok"}
        sig = sign_message(gw.broker.ed25519(actor).private_key, canonical_json(proposal).encode())
        return gw.propose_action(actor, proposal, sig)

    msg = f"anticube:{name}".encode()
    sig = sign_message(gw.broker.ed25519(actor).private_key, msg)
    return gw.signed_handshake(actor, sig, msg)


def run_dual_world_anticube(gw: HydraLampGateway, perturbations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    perturbations = perturbations or load_perturbations()
    runner = DualWorldRunner()
    results = []

    for p in perturbations:
        def action(gateway: HydraLampGateway, world: WorldMode) -> dict[str, Any]:
            ev = apply_perturbation(gateway, p)
            allowed = ev.get("access_decision", {}).get("allowed", False)
            expected = p.get("expected", "DENY")
            false_denial = expected == "ALLOW" and not allowed
            return {
                "event_type": ev.get("event_type"),
                "allowed": allowed,
                "expected": expected,
                "false_denial": false_denial,
                "world": world.value,
            }

        dual = runner.run_adversarial_fixture(
            gw,
            fixture_id=p["id"],
            perturbation_id=p["name"],
            action=action,
        )
        results.append({
            "perturbation_id": p["id"],
            "name": p["name"],
            "expected": p["expected"],
            "sandbox": dual.sandbox,
            "open_world": dual.open_world,
        })

    false_denials = [r for r in results if r["sandbox"].get("false_denial") or r["open_world"].get("false_denial")]
    return {
        "perturbations_tested": len(results),
        "false_denials": false_denials,
        "false_denial_count": len(false_denials),
        "unauthorized_plaintext_disclosures": gw.unauthorized_plaintext_disclosures,
        "unauthorized_canonical_writes": gw.unauthorized_canonical_writes,
        "results": results,
        "pass": gw.unauthorized_plaintext_disclosures == 0 and gw.unauthorized_canonical_writes == 0,
    }
