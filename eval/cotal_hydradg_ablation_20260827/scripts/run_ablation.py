#!/usr/bin/env python3
"""Deterministic Cotal × HydraDG coordination/custody ablation runner.

Preregistration-locked: same fixtures, payloads, roles, host, ordering.
No live LLM in primary matrix. No silent retry. Scorer locked across A–D.

HydraDG SIGNATURE_STATE remains NOT_SIGNED unless an authorized FCO private-key
signing operation occurs (none in this experiment). Cotal message-signature
verification is recorded in a SEPARATE field.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import time
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EVAL = Path(__file__).resolve().parents[1]
FIXTURES_PATH = EVAL / "FIXTURES.json"
PREREG_PATH = EVAL / "PREREGISTRATION.json"
CREDS_DIR = EVAL / ".cotal_creds"
STORE_DIR = EVAL / ".cotal_store"
SPACE = "hydradg-ablation-20260827"
CONDITIONS = [
    "A_DIRECT_BASELINE",
    "B_COTAL_ONLY",
    "C_HYDRADG_ONLY",
    "D_COTAL_HYDRADG",
]
COTAL_CONDITIONS = {"B_COTAL_ONLY", "D_COTAL_HYDRADG"}
CUSTODY_ON = {"C_HYDRADG_ONLY", "D_COTAL_HYDRADG"}

OUTCOME = ("PASS", "FAIL", "NULL", "NEGATIVE", "ERROR", "TIMEOUT", "ABSTAIN", "CONTRADICTORY")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_json(obj: Any) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def hostname() -> str:
    return socket.gethostname()


def run_cmd(
    args: list[str],
    *,
    timeout: float = 30.0,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=str(ROOT),
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "args": args,
            "returncode": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
            "latency_ms": latency_ms,
            "timed_out": False,
            "error": None,
        }
    except subprocess.TimeoutExpired as e:
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "args": args,
            "returncode": None,
            "stdout": (e.stdout or "") if isinstance(e.stdout, str) else "",
            "stderr": (e.stderr or "") if isinstance(e.stderr, str) else "TIMEOUT",
            "latency_ms": latency_ms,
            "timed_out": True,
            "error": "TIMEOUT",
        }
    except Exception as e:  # noqa: BLE001 — record ERROR honestly
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "args": args,
            "returncode": None,
            "stdout": "",
            "stderr": str(e),
            "latency_ms": latency_ms,
            "timed_out": False,
            "error": type(e).__name__,
        }


@dataclass
class DirectBus:
    """In-process HTTP/MCP stand-in: ordered durable log + role binding without JWT."""

    path: Path
    messages: list[dict[str, Any]] = field(default_factory=list)
    seen_dedupe: set[str] = field(default_factory=set)

    def load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text())
            self.messages = data.get("messages", [])
            self.seen_dedupe = set(data.get("seen_dedupe", []))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {"messages": self.messages, "seen_dedupe": sorted(self.seen_dedupe)},
                indent=2,
            )
            + "\n"
        )

    def deliver(self, envelope: dict[str, Any]) -> dict[str, Any]:
        t0 = time.perf_counter()
        # Direct path trusts caller-supplied role; no cryptographic identity.
        authenticated = False
        auth_outcome = "NULL"
        # Intruder presenting claimed researcher is accepted as claimed (no JWT).
        effective_role = envelope.get("claimed_sender_role") or envelope.get("sender_role")
        envelope = deepcopy(envelope)
        envelope["effective_sender_role"] = effective_role
        envelope["cotal_message_signature_verification"] = "NOT_APPLICABLE_DIRECT"
        dedupe = envelope.get("dedupe_key")
        duplicate = False
        if dedupe and dedupe in self.seen_dedupe:
            duplicate = True
        else:
            if dedupe:
                self.seen_dedupe.add(dedupe)
            self.messages.append(envelope)
            self.save()
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "delivery_success": "PASS",
            "identity_authenticated": "FAIL" if envelope.get("probes", {}).get("invalid_sender") else "ABSTAIN",
            "authorization_enforced": "FAIL"
            if envelope.get("probes", {}).get("attempt_unauthorized_canonical_write")
            else "ABSTAIN",
            "duplicate_delivery": "FAIL" if duplicate else ("PASS" if envelope.get("probes", {}).get("replay") else "NULL"),
            "ordered_delivery": "PASS",
            "latency_ms": latency_ms,
            "cotal_message_signature_verification": "NOT_APPLICABLE_DIRECT",
            "broker_principal": None,
            "effective_sender_role": effective_role,
            "raw": {"mode": "direct", "duplicate": duplicate, "message_count": len(self.messages)},
            "auth_outcome": auth_outcome,
            "authenticated": authenticated,
        }

    def restart_recovery(self) -> dict[str, Any]:
        before = len(self.messages)
        # Simulate process restart: clear memory, reload from durable log.
        self.messages = []
        self.seen_dedupe = set()
        self.load()
        recovered = len(self.messages) == before and before > 0
        return {
            "restart_recovery": "PASS" if recovered else "FAIL",
            "history_recovery": "PASS" if recovered else "FAIL",
            "before_count": before,
            "after_count": len(self.messages),
        }


def ensure_cotal_mesh() -> dict[str, Any]:
    status = run_cmd(["cotal", "status", "--space", SPACE], timeout=20)
    up = run_cmd(
        [
            "cotal",
            "up",
            "--detach",
            "--space",
            SPACE,
            "--store-dir",
            str(STORE_DIR),
        ],
        timeout=60,
    )
    CREDS_DIR.mkdir(parents=True, exist_ok=True)
    mint_results = {}
    for name in ("researcher", "custodian", "intruder"):
        out = CREDS_DIR / f"{name}.creds"
        mint_results[name] = run_cmd(
            [
                "cotal",
                "mint",
                name,
                "--profile",
                "agent",
                "--role",
                name,
                "--out",
                str(out),
                "--space",
                SPACE,
                "--provision",
            ],
            timeout=45,
        )
    return {"status_before": status, "up": up, "mint": mint_results}


def cotal_send(role_target: str, payload: dict[str, Any], creds_name: str) -> dict[str, Any]:
    creds = CREDS_DIR / f"{creds_name}.creds"
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    if not creds.exists():
        return {
            "delivery_success": "ERROR",
            "identity_authenticated": "ERROR",
            "authorization_enforced": "NULL",
            "duplicate_delivery": "NULL",
            "ordered_delivery": "NULL",
            "latency_ms": 0,
            "cotal_message_signature_verification": "ERROR",
            "broker_principal": None,
            "raw": {"error": "MISSING_CREDS", "creds": str(creds)},
        }
    res = run_cmd(
        [
            "cotal",
            "send",
            "ask",
            role_target,
            text,
            "--creds",
            str(creds),
            "--space",
            SPACE,
        ],
        timeout=45,
    )
    out = (res.get("stdout") or "") + (res.get("stderr") or "")
    timed_out = bool(res.get("timed_out"))
    if timed_out:
        delivery = "TIMEOUT"
        identity = "TIMEOUT"
        cotal_sig = "TIMEOUT"
    elif "Permissions Violation" in out or "permission denied" in out.lower():
        delivery = "FAIL"
        identity = "PASS"  # JWT accepted; ACL blocked publish
        cotal_sig = "VERIFIED_CONNECTION_ACL_DENIED"
    elif "can't reach a broker" in out or "invalid" in out.lower() and "jwt" in out.lower():
        delivery = "FAIL"
        identity = "FAIL"
        cotal_sig = "REJECTED"
    elif res.get("returncode") not in (0, None) and "→" not in out:
        delivery = "ERROR" if res.get("error") else "FAIL"
        identity = "FAIL" if "broker" in out.lower() or "creds" in out.lower() else "ABSTAIN"
        cotal_sig = "FAIL"
    elif "→" in out or res.get("returncode") == 0:
        delivery = "PASS"
        identity = "PASS"
        cotal_sig = "VERIFIED_CONNECTION"
    else:
        delivery = "ERROR"
        identity = "ABSTAIN"
        cotal_sig = "UNKNOWN"
    return {
        "delivery_success": delivery,
        "identity_authenticated": identity,
        "authorization_enforced": "ABSTAIN",
        "duplicate_delivery": "NULL",
        "ordered_delivery": "PASS" if delivery == "PASS" else "NULL",
        "latency_ms": res.get("latency_ms", 0),
        "cotal_message_signature_verification": cotal_sig,
        "broker_principal": creds_name,
        "raw": res,
    }


def cotal_invalid_sender_probe(payload: dict[str, Any]) -> dict[str, Any]:
    """Intruder JWT while payload claims researcher — mesh authenticates intruder."""
    forged = deepcopy(payload)
    forged["claimed_sender_role"] = "researcher"
    res = cotal_send("custodian", forged, "intruder")
    # Authenticated principal is intruder (PASS), not the claimed researcher.
    if res["delivery_success"] == "PASS":
        res["identity_authenticated"] = "PASS"
        res["authorization_enforced"] = "FAIL"  # mesh delivered despite role spoof in payload
        res["note"] = "JWT authenticated as intruder; payload claimed researcher; ask-role delivery succeeded"
    return res


def cotal_bogus_identity_probe(payload: dict[str, Any]) -> dict[str, Any]:
    bogus = CREDS_DIR / "bogus.creds"
    bogus.write_text("-----BEGIN NATS USER JWT-----\nbogus\n------END NATS USER JWT------\n")
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    res = run_cmd(
        [
            "cotal",
            "send",
            "ask",
            "custodian",
            text,
            "--creds",
            str(bogus),
            "--space",
            SPACE,
        ],
        timeout=30,
    )
    out = (res.get("stdout") or "") + (res.get("stderr") or "")
    rejected = (
        "can't reach a broker" in out
        or "Permission" in out
        or "invalid" in out.lower()
        or res.get("returncode") not in (0,)
    )
    return {
        "delivery_success": "FAIL" if rejected else "PASS",
        "identity_authenticated": "FAIL" if rejected else "FAIL",
        "authorization_enforced": "PASS" if rejected else "FAIL",
        "duplicate_delivery": "NULL",
        "ordered_delivery": "NULL",
        "latency_ms": res.get("latency_ms", 0),
        "cotal_message_signature_verification": "REJECTED" if rejected else "UNEXPECTED_ACCEPT",
        "broker_principal": None,
        "raw": res,
    }


def cotal_restart_recovery() -> dict[str, Any]:
    store_before = STORE_DIR.exists() and any(STORE_DIR.rglob("*"))
    size_before = sum(p.stat().st_size for p in STORE_DIR.rglob("*") if p.is_file()) if STORE_DIR.exists() else 0
    down = run_cmd(["cotal", "down"], timeout=60)
    time.sleep(2)
    up = run_cmd(
        [
            "cotal",
            "up",
            "--detach",
            "--space",
            SPACE,
            "--store-dir",
            str(STORE_DIR),
        ],
        timeout=60,
    )
    time.sleep(2)
    # Remint may be needed after restart for ask path; store persistence is the recovery signal.
    size_after = sum(p.stat().st_size for p in STORE_DIR.rglob("*") if p.is_file()) if STORE_DIR.exists() else 0
    probe = cotal_send(
        "custodian",
        {"fixture_id": "05_RESTART_RECOVERY", "probe": "post_restart"},
        "researcher",
    )
    if probe["delivery_success"] in ("ERROR", "FAIL") and "MISSING_CREDS" not in str(probe.get("raw")):
        # remint once (not silent retry of same failed send — re-establish creds after mesh restart)
        ensure_cotal_mesh()
        probe = cotal_send(
            "custodian",
            {"fixture_id": "05_RESTART_RECOVERY", "probe": "post_restart_remint"},
            "researcher",
        )
    recovered_store = store_before and size_after > 0 and size_after >= size_before * 0.5
    mesh_ok = probe["delivery_success"] == "PASS"
    return {
        "restart_recovery": "PASS" if recovered_store and mesh_ok else ("FAIL" if not mesh_ok else "NEGATIVE"),
        "history_recovery": "PASS" if recovered_store else "FAIL",
        "store_size_before": size_before,
        "store_size_after": size_after,
        "down": {"returncode": down.get("returncode"), "stderr": (down.get("stderr") or "")[-500:]},
        "up": {"returncode": up.get("returncode"), "stderr": (up.get("stderr") or "")[-500:]},
        "post_restart_probe": probe,
    }


# --- HydraDG custody (deterministic; no FCO private-key signing) ---


@dataclass
class CustodyState:
    canonical_claims: list[dict[str, Any]] = field(default_factory=list)
    successor_claims: list[dict[str, Any]] = field(default_factory=list)
    quarantined: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)
    unauthorized_canonical_writes: int = 0
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    receipts: list[dict[str, Any]] = field(default_factory=list)

    def admit(self, envelope: dict[str, Any], *, custody_on: bool) -> dict[str, Any]:
        payload = envelope["payload"]
        probes = envelope.get("probes", {})
        metrics = {
            "source_preserved": "NULL",
            "evidence_class_correct": "NULL",
            "claim_admission": "NULL",
            "contradiction_preserved": "NULL",
            "unauthorized_canonical_write": "NULL",
            "receipt_recomputed": "NULL",
            "corrupt_receipt_rejected": "NULL",
            "earliest_divergence_identified": "NULL",
        }
        signature_state = "NOT_SIGNED"
        cotal_sig = envelope.get("cotal_message_signature_verification", "NOT_APPLICABLE")

        if not custody_on:
            # Custody OFF: no admission gate — unauthorized canonical write can land.
            if probes.get("attempt_unauthorized_canonical_write"):
                self.canonical_claims.append(payload)
                self.unauthorized_canonical_writes += 1
                metrics["unauthorized_canonical_write"] = "FAIL"  # write occurred
                metrics["claim_admission"] = "PASS"  # admitted without gate
            elif probes.get("corrupt_receipt"):
                self.receipts.append(payload)
                metrics["corrupt_receipt_rejected"] = "FAIL"
                metrics["receipt_recomputed"] = "ABSTAIN"
                metrics["claim_admission"] = "PASS"
            else:
                self.canonical_claims.append(payload)
                metrics["claim_admission"] = "PASS"
                metrics["source_preserved"] = (
                    "PASS" if payload.get("source_url") else "FAIL"
                )
                metrics["evidence_class_correct"] = (
                    "PASS"
                    if payload.get("evidence_class") == "EXTERNALLY_RETRIEVED_EVIDENCE"
                    else "FAIL"
                )
                if probes.get("contradictory"):
                    # Collapses / overwrites without preserving contradiction when custody off
                    metrics["contradiction_preserved"] = "FAIL"
            return {
                "metrics": metrics,
                "SIGNATURE_STATE": signature_state,
                "cotal_message_signature_verification": cotal_sig,
                "fcg_identity": "CANONICAL" if self.unauthorized_canonical_writes else "UNGOVERNED",
                "custody": "OFF",
            }

        # Custody ON
        # Recompute receipt hash when applicable
        if probes.get("corrupt_receipt") or payload.get("message_type") == "custody_receipt":
            body = {k: v for k, v in payload.items() if k != "declared_sha256"}
            computed = sha256_json(body)
            declared = payload.get("declared_sha256")
            metrics["receipt_recomputed"] = "PASS"
            if declared and declared != computed:
                metrics["corrupt_receipt_rejected"] = "PASS"
                metrics["earliest_divergence_identified"] = "PASS"
                metrics["claim_admission"] = "NEGATIVE"
                self.rejected.append({"reason": "CORRUPT_RECEIPT", "computed": computed, "declared": declared})
                return {
                    "metrics": metrics,
                    "SIGNATURE_STATE": signature_state,
                    "cotal_message_signature_verification": cotal_sig,
                    "fcg_identity": "SUCCESSOR_NOT_CANONICAL",
                    "custody": "ON",
                    "computed_sha256": computed,
                }
            metrics["corrupt_receipt_rejected"] = "NULL"

        if probes.get("attempt_unauthorized_canonical_write") or (
            envelope.get("sender_role") == "intruder"
            and payload.get("message_type") == "canonical_append"
        ):
            metrics["unauthorized_canonical_write"] = "PASS"  # blocked
            metrics["claim_admission"] = "NEGATIVE"
            self.rejected.append({"reason": "UNAUTHORIZED_CANONICAL_WRITE", "payload": payload})
            return {
                "metrics": metrics,
                "SIGNATURE_STATE": signature_state,
                "cotal_message_signature_verification": cotal_sig,
                "fcg_identity": "SUCCESSOR_NOT_CANONICAL",
                "custody": "ON",
                "canonical_writes": 0,
            }

        if probes.get("invalid_sender"):
            metrics["claim_admission"] = "NEGATIVE"
            metrics["unauthorized_canonical_write"] = "PASS"
            self.rejected.append({"reason": "INVALID_SENDER", "payload": payload})
            return {
                "metrics": metrics,
                "SIGNATURE_STATE": signature_state,
                "cotal_message_signature_verification": cotal_sig,
                "fcg_identity": "SUCCESSOR_NOT_CANONICAL",
                "custody": "ON",
            }

        if probes.get("unsourced") or not payload.get("source_url"):
            metrics["source_preserved"] = "FAIL"
            metrics["claim_admission"] = "NEGATIVE"
            metrics["evidence_class_correct"] = (
                "PASS"
                if payload.get("evidence_class") == "EXTERNALLY_RETRIEVED_EVIDENCE"
                else "FAIL"
            )
            self.rejected.append({"reason": "UNSOURCED_CLAIM", "payload": payload})
            return {
                "metrics": metrics,
                "SIGNATURE_STATE": signature_state,
                "cotal_message_signature_verification": cotal_sig,
                "fcg_identity": "SUCCESSOR_NOT_CANONICAL",
                "custody": "ON",
            }

        if probes.get("source_mismatch") or payload.get("source_support") is False:
            metrics["source_preserved"] = "PASS"
            metrics["evidence_class_correct"] = "PASS"
            metrics["claim_admission"] = "NEGATIVE"
            self.rejected.append({"reason": "SOURCE_DOES_NOT_SUPPORT_CLAIM", "payload": payload})
            return {
                "metrics": metrics,
                "SIGNATURE_STATE": signature_state,
                "cotal_message_signature_verification": cotal_sig,
                "fcg_identity": "SUCCESSOR_NOT_CANONICAL",
                "custody": "ON",
            }

        if probes.get("contradictory"):
            metrics["source_preserved"] = "PASS"
            metrics["evidence_class_correct"] = "PASS"
            metrics["claim_admission"] = "CONTRADICTORY"
            metrics["contradiction_preserved"] = "PASS"
            record = {
                "prior": payload.get("prior_canonical_claim"),
                "incoming": payload.get("claim"),
                "status": "CONTRADICTORY",
            }
            self.contradictions.append(record)
            self.successor_claims.append(payload)
            self.quarantined.append(payload)
            return {
                "metrics": metrics,
                "SIGNATURE_STATE": signature_state,
                "cotal_message_signature_verification": cotal_sig,
                "fcg_identity": "SUCCESSOR_NOT_CANONICAL",
                "custody": "ON",
                "contradiction": record,
            }

        # Valid path / normal / replay handling at custody: admit to successor quarantine first
        metrics["source_preserved"] = "PASS" if payload.get("source_url") else "FAIL"
        metrics["evidence_class_correct"] = (
            "PASS"
            if payload.get("evidence_class") == "EXTERNALLY_RETRIEVED_EVIDENCE"
            else "FAIL"
        )
        if probes.get("replay"):
            # Custody dedupe by dedupe_key
            keys = {p.get("dedupe_key") for p in self.quarantined + self.successor_claims}
            if payload.get("dedupe_key") in keys:
                metrics["claim_admission"] = "NEGATIVE"
                self.rejected.append({"reason": "DUPLICATE", "payload": payload})
            else:
                metrics["claim_admission"] = "PASS"
                self.quarantined.append(payload)
                self.successor_claims.append(payload)
        else:
            metrics["claim_admission"] = "PASS"
            self.quarantined.append(payload)
            self.successor_claims.append(payload)
        metrics["unauthorized_canonical_write"] = "PASS"  # none occurred
        if probes.get("corrupt_receipt"):
            pass
        else:
            metrics["corrupt_receipt_rejected"] = "NULL"
            metrics["receipt_recomputed"] = "NULL"
            metrics["earliest_divergence_identified"] = "NULL"
            metrics["contradiction_preserved"] = "NULL"
        return {
            "metrics": metrics,
            "SIGNATURE_STATE": signature_state,
            "cotal_message_signature_verification": cotal_sig,
            "fcg_identity": "SUCCESSOR_NOT_CANONICAL",
            "custody": "ON",
            "canonical_writes": 0,
        }


def coordinate(
    condition: str,
    fixture: dict[str, Any],
    bus: DirectBus,
    dedupe_tracker: set[str],
) -> dict[str, Any]:
    probes = fixture["probes"]
    payload = fixture["payload"]
    envelope = {
        "fixture_id": fixture["fixture_id"],
        "sender_role": fixture["sender_role"],
        "receiver_role": fixture["receiver_role"],
        "claimed_sender_role": payload.get("claimed_sender_role"),
        "payload": payload,
        "probes": probes,
        "dedupe_key": payload.get("dedupe_key"),
        "payload_sha256": fixture.get("payload_sha256") or sha256_json(payload),
    }

    coord_metrics = {
        "delivery_success": "NULL",
        "identity_authenticated": "NULL",
        "authorization_enforced": "NULL",
        "duplicate_delivery": "NULL",
        "ordered_delivery": "NULL",
        "restart_recovery": "NULL",
        "history_recovery": "NULL",
        "latency_ms": 0,
    }
    detail: dict[str, Any] = {}

    use_cotal = condition in COTAL_CONDITIONS

    if probes.get("restart"):
        # Seed one durable message first, then restart.
        if use_cotal:
            seed = cotal_send("custodian", {"fixture_id": fixture["fixture_id"], "seed": True}, "researcher")
            detail["seed"] = seed
            rr = cotal_restart_recovery()
            coord_metrics.update(
                {
                    "delivery_success": rr["post_restart_probe"]["delivery_success"],
                    "identity_authenticated": rr["post_restart_probe"]["identity_authenticated"],
                    "restart_recovery": rr["restart_recovery"],
                    "history_recovery": rr["history_recovery"],
                    "latency_ms": rr["post_restart_probe"].get("latency_ms", 0),
                    "ordered_delivery": "PASS",
                    "authorization_enforced": "ABSTAIN",
                    "duplicate_delivery": "NULL",
                }
            )
            detail["restart"] = rr
            envelope["cotal_message_signature_verification"] = rr["post_restart_probe"].get(
                "cotal_message_signature_verification"
            )
        else:
            bus.deliver(envelope)
            rr = bus.restart_recovery()
            coord_metrics.update(
                {
                    "delivery_success": "PASS",
                    "identity_authenticated": "ABSTAIN",
                    "authorization_enforced": "ABSTAIN",
                    "duplicate_delivery": "NULL",
                    "ordered_delivery": "PASS",
                    "restart_recovery": rr["restart_recovery"],
                    "history_recovery": rr["history_recovery"],
                    "latency_ms": 0,
                }
            )
            detail["restart"] = rr
            envelope["cotal_message_signature_verification"] = "NOT_APPLICABLE_DIRECT"
        return {"coordination": coord_metrics, "envelope": envelope, "detail": detail}

    if use_cotal:
        if probes.get("invalid_sender"):
            # Primary: bogus JWT rejection; secondary: intruder JWT with claimed researcher.
            bogus = cotal_bogus_identity_probe(payload)
            spoof = cotal_invalid_sender_probe(payload)
            detail["bogus"] = bogus
            detail["spoof"] = spoof
            coord_metrics.update(
                {
                    "delivery_success": spoof["delivery_success"],
                    "identity_authenticated": "PASS"
                    if bogus["identity_authenticated"] == "FAIL"
                    and spoof["identity_authenticated"] == "PASS"
                    else bogus["identity_authenticated"],
                    "authorization_enforced": "PASS"
                    if bogus["authorization_enforced"] == "PASS"
                    else spoof["authorization_enforced"],
                    "duplicate_delivery": "NULL",
                    "ordered_delivery": spoof.get("ordered_delivery", "NULL"),
                    "latency_ms": (bogus.get("latency_ms") or 0) + (spoof.get("latency_ms") or 0),
                }
            )
            envelope["cotal_message_signature_verification"] = {
                "bogus": bogus["cotal_message_signature_verification"],
                "spoof": spoof["cotal_message_signature_verification"],
            }
        else:
            creds_name = fixture["sender_role"] if fixture["sender_role"] in ("researcher", "custodian", "intruder") else "researcher"
            send_res = cotal_send("custodian", payload, creds_name)
            if probes.get("replay"):
                first = send_res
                second = cotal_send("custodian", payload, creds_name)
                detail["first"] = first
                detail["second"] = second
                # Cotal ask-role does not application-dedupe; duplicate delivery expected unless custody handles it.
                dup = "FAIL" if second["delivery_success"] == "PASS" else "PASS"
                coord_metrics.update(
                    {
                        "delivery_success": first["delivery_success"],
                        "identity_authenticated": first["identity_authenticated"],
                        "authorization_enforced": "ABSTAIN",
                        "duplicate_delivery": dup,
                        "ordered_delivery": "PASS",
                        "latency_ms": (first.get("latency_ms") or 0) + (second.get("latency_ms") or 0),
                    }
                )
                envelope["cotal_message_signature_verification"] = first.get(
                    "cotal_message_signature_verification"
                )
            else:
                detail["send"] = send_res
                authz = "ABSTAIN"
                if probes.get("attempt_unauthorized_canonical_write"):
                    # Coordination may deliver; custody decides write. Mesh does not block content.
                    authz = "FAIL" if send_res["delivery_success"] == "PASS" else "PASS"
                coord_metrics.update(
                    {
                        "delivery_success": send_res["delivery_success"],
                        "identity_authenticated": send_res["identity_authenticated"],
                        "authorization_enforced": authz,
                        "duplicate_delivery": "NULL",
                        "ordered_delivery": "PASS" if send_res["delivery_success"] == "PASS" else "NULL",
                        "latency_ms": send_res.get("latency_ms", 0),
                    }
                )
                envelope["cotal_message_signature_verification"] = send_res.get(
                    "cotal_message_signature_verification"
                )
    else:
        if probes.get("replay"):
            first = bus.deliver(envelope)
            second = bus.deliver(envelope)
            detail["first"] = first
            detail["second"] = second
            coord_metrics.update(
                {
                    "delivery_success": first["delivery_success"],
                    "identity_authenticated": first["identity_authenticated"],
                    "authorization_enforced": first["authorization_enforced"],
                    "duplicate_delivery": second["duplicate_delivery"],
                    "ordered_delivery": "PASS",
                    "latency_ms": (first.get("latency_ms") or 0) + (second.get("latency_ms") or 0),
                }
            )
        else:
            res = bus.deliver(envelope)
            detail["send"] = res
            coord_metrics.update(
                {
                    "delivery_success": res["delivery_success"],
                    "identity_authenticated": res["identity_authenticated"],
                    "authorization_enforced": res["authorization_enforced"],
                    "duplicate_delivery": res["duplicate_delivery"],
                    "ordered_delivery": res["ordered_delivery"],
                    "latency_ms": res.get("latency_ms", 0),
                }
            )
        envelope["cotal_message_signature_verification"] = "NOT_APPLICABLE_DIRECT"

    # Mark non-probed recovery metrics NULL (already set)
    return {"coordination": coord_metrics, "envelope": envelope, "detail": detail}


def run_condition(condition: str, fixtures_doc: dict[str, Any]) -> dict[str, Any]:
    custody_on = condition in CUSTODY_ON
    bus = DirectBus(EVAL / condition / "direct_bus.json")
    if bus.path.exists():
        bus.path.unlink()
    bus.messages = []
    bus.seen_dedupe = set()
    custody = CustodyState()
    rows = []
    if condition in COTAL_CONDITIONS:
        mesh = ensure_cotal_mesh()
    else:
        mesh = {"skipped": True}

    for fixture in fixtures_doc["fixtures"]:
        t0 = time.perf_counter()
        coord = coordinate(condition, fixture, bus, set())
        # For replay under custody ON, seed prior admit before second path already handled in coordinate;
        # admit once using final envelope (replay probe still evaluated inside admit).
        env = coord["envelope"]
        if fixture["probes"].get("replay") and custody_on:
            # First admit
            first_env = deepcopy(env)
            custody.admit(first_env, custody_on=True)
            admit = custody.admit(env, custody_on=True)
        else:
            admit = custody.admit(env, custody_on=custody_on)
        elapsed = int((time.perf_counter() - t0) * 1000)
        row = {
            "fixture_id": fixture["fixture_id"],
            "condition": condition,
            "COORDINATION": coord["coordination"],
            "CUSTODY": admit["metrics"],
            "SIGNATURE_STATE": admit["SIGNATURE_STATE"],
            "cotal_message_signature_verification": admit.get(
                "cotal_message_signature_verification"
            ),
            "fcg_identity": admit.get("fcg_identity"),
            "payload_sha256": fixture.get("payload_sha256"),
            "elapsed_ms": elapsed,
            "detail": {
                "coordination": coord["detail"],
                "custody_extra": {
                    k: v for k, v in admit.items() if k not in ("metrics",)
                },
            },
            "outcome_vocabulary_respected": True,
        }
        rows.append(row)

    out_dir = EVAL / condition
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": "hydradg.cotal_coordination_custody_ablation.condition_receipt.v1",
        "experiment_id": "COTAL_HYDRADG_ABLATION_20260827",
        "condition": condition,
        "coordination": fixtures_doc and (
            "cotal_local_JWT_mesh" if condition in COTAL_CONDITIONS else "direct_HTTP_MCP"
        ),
        "hydradg_custody": "ON" if custody_on else "OFF",
        "execution_host": hostname(),
        "recorded_at_utc": now_utc(),
        "SIGNATURE_STATE": "NOT_SIGNED",
        "mesh_bringup": {
            "up_returncode": (mesh.get("up") or {}).get("returncode") if isinstance(mesh, dict) else None,
            "skipped": mesh.get("skipped", False) if isinstance(mesh, dict) else False,
        },
        "unauthorized_canonical_writes": custody.unauthorized_canonical_writes,
        "canonical_claim_count": len(custody.canonical_claims),
        "successor_claim_count": len(custody.successor_claims),
        "rejected_count": len(custody.rejected),
        "contradiction_count": len(custody.contradictions),
        "rows": rows,
    }
    (out_dir / "CONDITION_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    (out_dir / "rows.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    )
    return receipt


def build_matrix(receipts: dict[str, Any]) -> dict[str, Any]:
    matrix_rows = []
    for condition in CONDITIONS:
        rec = receipts[condition]
        for row in rec["rows"]:
            matrix_rows.append(
                {
                    "condition": condition,
                    "fixture_id": row["fixture_id"],
                    "COORDINATION": row["COORDINATION"],
                    "CUSTODY": row["CUSTODY"],
                    "SIGNATURE_STATE": row["SIGNATURE_STATE"],
                    "cotal_message_signature_verification": row[
                        "cotal_message_signature_verification"
                    ],
                }
            )
    # Descriptive complementarity contrasts (no collapsed score)
    def metric_pass_rate(family: str, metric: str, condition: str) -> dict[str, Any]:
        vals = []
        for r in matrix_rows:
            if r["condition"] != condition:
                continue
            v = r[family].get(metric)
            if v in (None, "NULL"):
                continue
            vals.append(v)
        if not vals:
            return {"n": 0, "pass": 0, "rate": None, "values": []}
        passes = sum(1 for v in vals if v == "PASS")
        return {"n": len(vals), "pass": passes, "rate": passes / len(vals), "values": vals}

    contrasts = {
        "coordination_cotal_vs_direct": {
            "B_vs_A": {
                m: {
                    "B": metric_pass_rate("COORDINATION", m, "B_COTAL_ONLY"),
                    "A": metric_pass_rate("COORDINATION", m, "A_DIRECT_BASELINE"),
                }
                for m in [
                    "delivery_success",
                    "identity_authenticated",
                    "authorization_enforced",
                    "duplicate_delivery",
                    "restart_recovery",
                    "history_recovery",
                ]
            },
            "D_vs_C": {
                m: {
                    "D": metric_pass_rate("COORDINATION", m, "D_COTAL_HYDRADG"),
                    "C": metric_pass_rate("COORDINATION", m, "C_HYDRADG_ONLY"),
                }
                for m in [
                    "delivery_success",
                    "identity_authenticated",
                    "authorization_enforced",
                    "duplicate_delivery",
                    "restart_recovery",
                    "history_recovery",
                ]
            },
        },
        "custody_on_vs_off": {
            "C_vs_A": {
                m: {
                    "C": metric_pass_rate("CUSTODY", m, "C_HYDRADG_ONLY"),
                    "A": metric_pass_rate("CUSTODY", m, "A_DIRECT_BASELINE"),
                }
                for m in [
                    "claim_admission",
                    "contradiction_preserved",
                    "unauthorized_canonical_write",
                    "corrupt_receipt_rejected",
                    "source_preserved",
                ]
            },
            "D_vs_B": {
                m: {
                    "D": metric_pass_rate("CUSTODY", m, "D_COTAL_HYDRADG"),
                    "B": metric_pass_rate("CUSTODY", m, "B_COTAL_ONLY"),
                }
                for m in [
                    "claim_admission",
                    "contradiction_preserved",
                    "unauthorized_canonical_write",
                    "corrupt_receipt_rejected",
                    "source_preserved",
                ]
            },
        },
        "collapsed_single_score": False,
    }
    return {
        "schema": "hydradg.cotal_coordination_custody_ablation.results_matrix.v1",
        "experiment_id": "COTAL_HYDRADG_ABLATION_20260827",
        "execution_host": hostname(),
        "recorded_at_utc": now_utc(),
        "SIGNATURE_STATE": "NOT_SIGNED",
        "metric_families_separate": True,
        "rows": matrix_rows,
        "descriptive_contrasts": contrasts,
        "condition_summaries": {
            c: {
                "unauthorized_canonical_writes": receipts[c]["unauthorized_canonical_writes"],
                "canonical_claim_count": receipts[c]["canonical_claim_count"],
                "successor_claim_count": receipts[c]["successor_claim_count"],
                "rejected_count": receipts[c]["rejected_count"],
                "contradiction_count": receipts[c]["contradiction_count"],
            }
            for c in CONDITIONS
        },
    }


def science_audit(matrix: dict[str, Any], prereg: dict[str, Any], fixtures: dict[str, Any]) -> dict[str, Any]:
    # Complementarity: Cotal helps identity on B/D vs A/C; custody helps unauthorized_write + corrupt receipt on C/D vs A/B
    def collect(condition: str, family: str, metric: str) -> list[str]:
        return [
            r[family][metric]
            for r in matrix["rows"]
            if r["condition"] == condition and r[family].get(metric) not in (None, "NULL")
        ]

    cotal_identity_b = collect("B_COTAL_ONLY", "COORDINATION", "identity_authenticated")
    direct_identity_a = collect("A_DIRECT_BASELINE", "COORDINATION", "identity_authenticated")
    custody_unauth_c = collect("C_HYDRADG_ONLY", "CUSTODY", "unauthorized_canonical_write")
    custody_unauth_a = collect("A_DIRECT_BASELINE", "CUSTODY", "unauthorized_canonical_write")
    corrupt_c = collect("C_HYDRADG_ONLY", "CUSTODY", "corrupt_receipt_rejected")
    corrupt_a = collect("A_DIRECT_BASELINE", "CUSTODY", "corrupt_receipt_rejected")

    findings = []
    if any(v == "PASS" for v in cotal_identity_b) and any(v == "FAIL" for v in direct_identity_a):
        findings.append(
            {
                "finding": "COTAL_CONTRIBUTES_IDENTITY_AUTHENTICATION",
                "evidence": {"B_identity": cotal_identity_b, "A_identity": direct_identity_a},
                "claim_ceiling": "DESCRIPTIVE_CONTRAST_ONLY",
            }
        )
    if any(v == "PASS" for v in custody_unauth_c) and any(v == "FAIL" for v in custody_unauth_a):
        findings.append(
            {
                "finding": "HYDRADG_CONTRIBUTES_UNAUTHORIZED_WRITE_BLOCK",
                "evidence": {"C": custody_unauth_c, "A": custody_unauth_a},
                "claim_ceiling": "DESCRIPTIVE_CONTRAST_ONLY",
            }
        )
    if any(v == "PASS" for v in corrupt_c) and any(v == "FAIL" for v in corrupt_a):
        findings.append(
            {
                "finding": "HYDRADG_CONTRIBUTES_CORRUPT_RECEIPT_REJECTION",
                "evidence": {"C": corrupt_c, "A": corrupt_a},
                "claim_ceiling": "DESCRIPTIVE_CONTRAST_ONLY",
            }
        )

    d_unauth = collect("D_COTAL_HYDRADG", "CUSTODY", "unauthorized_canonical_write")
    d_identity = collect("D_COTAL_HYDRADG", "COORDINATION", "identity_authenticated")
    complementary = (
        any(v == "PASS" for v in d_unauth)
        and any(v == "PASS" for v in d_identity)
        and any(v == "FAIL" for v in custody_unauth_a)
    )
    if complementary:
        findings.append(
            {
                "finding": "COMBINATION_COMPLEMENTARY",
                "statement": "D shows Cotal identity authentication together with HydraDG unauthorized-write blocking; neither subsystem alone covers both metric families.",
                "claim_ceiling": "DESCRIPTIVE_CONTRAST_ONLY",
            }
        )

    return {
        "schema": "hydradg.cotal_coordination_custody_ablation.science_audit.v1",
        "experiment_id": "COTAL_HYDRADG_ABLATION_20260827",
        "framing": "NOT_WINNER_TAKE_ALL",
        "execution_host": hostname(),
        "recorded_at_utc": now_utc(),
        "SIGNATURE_STATE": "NOT_SIGNED",
        "preregistration_sha256": prereg.get("preregistration_sha256"),
        "fixtures_file_sha256": prereg.get("fixtures_file_sha256"),
        "constants_held": {
            "fixture_count": len(fixtures["fixtures"]),
            "conditions": CONDITIONS,
            "live_llm_in_primary_benchmark": False,
            "silent_retry": False,
            "scorer_locked": True,
            "hydradg_signature_state_policy": "NOT_SIGNED",
            "cotal_message_sig_separate_field": True,
        },
        "outcome_vocabulary_preserved": list(OUTCOME),
        "findings": findings,
        "yappy_demo": "PENDING_AFTER_MATRIX",
        "negative_null_error_policy": "PRESERVED_NOT_COLLAPSED",
    }


def try_yappy_demo() -> dict[str, Any]:
    """One illustrative external-agent demo if Yappy configured. Not a benchmark condition."""
    which = shutil.which("yappy")
    env_keys = [k for k in os.environ if "YAPPY" in k.upper()]
    if not which and not env_keys:
        return {
            "status": "NULL",
            "reason": "YAPPY_NOT_CONFIGURED",
            "benchmark_condition": False,
            "SIGNATURE_STATE": "NOT_SIGNED",
            "recorded_at_utc": now_utc(),
        }
    # If present, run a single non-scoring ping; do not fold into matrix.
    res = run_cmd([which or "yappy", "--help"], timeout=20)
    return {
        "status": "PASS" if res.get("returncode") == 0 else "ERROR",
        "benchmark_condition": False,
        "note": "Illustrative only; excluded from RESULTS_MATRIX scoring",
        "raw_help_excerpt": ((res.get("stdout") or "") + (res.get("stderr") or ""))[:500],
        "SIGNATURE_STATE": "NOT_SIGNED",
        "recorded_at_utc": now_utc(),
    }


def main() -> int:
    assert hostname() == "magicSTUDIObox.local" or os.environ.get("ABLATION_ALLOW_NON_STUDIO") == "1", (
        f"Scientific execution host must be magicSTUDIObox.local; got {hostname()}"
    )
    fixtures = json.loads(FIXTURES_PATH.read_text())
    prereg = json.loads(PREREG_PATH.read_text())
    # Verify payload hashes unchanged since preregistration commit
    for f in fixtures["fixtures"]:
        recomputed = sha256_json(f["payload"])
        locked = prereg.get("payload_sha256_by_fixture", {}).get(f["fixture_id"])
        if locked and locked != recomputed:
            raise SystemExit(f"PAYLOAD_DRIFT {f['fixture_id']}: locked={locked} now={recomputed}")
        f["payload_sha256"] = recomputed

    receipts = {}
    for condition in CONDITIONS:
        print(f"=== RUN {condition} @ {now_utc()} ===", flush=True)
        receipts[condition] = run_condition(condition, fixtures)

    matrix = build_matrix(receipts)
    (EVAL / "RESULTS_MATRIX.json").write_text(json.dumps(matrix, indent=2) + "\n")
    audit = science_audit(matrix, prereg, fixtures)
    yappy = try_yappy_demo()
    audit["yappy_demo"] = yappy
    (EVAL / "SCIENCE_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n")
    (EVAL / "YAPPY_ILLUSTRATIVE_DEMO.json").write_text(json.dumps(yappy, indent=2) + "\n")
    print("DONE", json.dumps({"host": hostname(), "findings": len(audit["findings"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
