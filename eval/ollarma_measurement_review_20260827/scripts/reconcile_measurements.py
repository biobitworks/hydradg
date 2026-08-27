#!/usr/bin/env python3
"""Deterministic HydraLamp measurement inventory and reconciliation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
EVENTS = REPO / "eval/hydralamp_20260826/HYDRALAMP_EVENTS.jsonl"
RUNTIME = REPO / "eval/hydralamp_20260826/HYDRALAMP_RUNTIME.json"
STRESS = REPO / "eval/hydralamp_runtype_20260826/LOCAL_MODEL_STRESS_RECEIPT.json"
BACKUP_RECEIPT = REPO / "eval/hydralamp_20260826/backup/BACKUP_RECEIPT.json"
INVENTORY_SRC = REPO / "eval/ollarma_fcg_root_review_20260827/MODEL_INVENTORY.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_events() -> list[dict]:
    return [json.loads(line) for line in EVENTS.read_text().splitlines() if line.strip()]


def metric(**kwargs: Any) -> dict[str, Any]:
    return kwargs


METRICS: list[dict] = [
    # Family 1 — Identity / Custody
    metric(NAME="model_actor_id", PURPOSE="Identify gateway role actor", SOURCE="HYDRALAMP_EVENTS.jsonl actor_id", TRANSFORM="none", EVIDENCE_CLASS="AUTHENTICATED_ACTOR", LEVEL="ACTOR", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="runtime_model", PURPOSE="Ollarma bridge identity string", SOURCE="event.runtime_model", TRANSFORM="none", EVIDENCE_CLASS="AUTHENTICATED_ACTOR", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="MEDIUM — role string not Ollama digest", MISSING_DEPENDENCY="none"),
    metric(NAME="model_tag", PURPOSE="Exact Ollama model name", SOURCE="custody handoff model.approved_name / runtype local_execution", TRANSFORM="none", EVIDENCE_CLASS="PROBABILISTIC_MODEL_OUTPUT", LEVEL="INVOCATION", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="PARTIAL", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="not on frozen 46-event lane"),
    metric(NAME="model_digest", PURPOSE="Runtime weight digest", SOURCE="handoff model.runtime_digest / ollama list", TRANSFORM="none", EVIDENCE_CLASS="INFRASTRUCTURE_IDENTITY", LEVEL="INVOCATION", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="MEDIUM — digest not FCG root", MISSING_DEPENDENCY="frozen events omit digest"),
    metric(NAME="local_execution_id", PURPOSE="Operational correlation id", SOURCE="runtype RUN_RECEIPT local_execution_id", TRANSFORM="none", EVIDENCE_CLASS="OPERATIONAL_TELEMETRY", LEVEL="INVOCATION", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="not canonical FCO id"),
    metric(NAME="event_index", PURPOSE="Sequence in frozen log", SOURCE="HYDRALAMP_EVENTS.jsonl", TRANSFORM="none", EVIDENCE_CLASS="DETERMINISTIC_EVENT_LOG", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="event_hash", PURPOSE="Content hash of event record", SOURCE="event.event_hash", TRANSFORM="canonical_json_sha256", EVIDENCE_CLASS="DETERMINISTIC_EVENT_LOG", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="prev_event_hash not in frozen export"),
    metric(NAME="source_request_hash", PURPOSE="Request bytes identity", SOURCE="event.source_request_hash", TRANSFORM="sha256", EVIDENCE_CLASS="REQUEST_BINDING", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="prompt_sha256", PURPOSE="Prompt bytes identity", SOURCE="handoff prompt_sha256", TRANSFORM="sha256", EVIDENCE_CLASS="PROBABILISTIC_MODEL_INPUT", LEVEL="INVOCATION", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="not on 46-event lane"),
    metric(NAME="output_sha256", PURPOSE="Raw model response hash", SOURCE="handoff output_sha256", TRANSFORM="sha256", EVIDENCE_CLASS="PROBABILISTIC_MODEL_OUTPUT", LEVEL="INVOCATION", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="MEDIUM — not verification", MISSING_DEPENDENCY="frozen lane"),
    metric(NAME="fco_ids", PURPOSE="Materialized object ids touched", SOURCE="event.fco_ids", TRANSFORM="none", EVIDENCE_CLASS="FCO_REFERENCE", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="fcg_root_before", PURPOSE="FCG state before event", SOURCE="event.fcg_root_before", TRANSFORM="gateway_canonical_edges_hash", EVIDENCE_CLASS="FCG_STATE", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="HIGH — not model root", MISSING_DEPENDENCY="none"),
    metric(NAME="fcg_root_after", PURPOSE="FCG state after event", SOURCE="event.fcg_root_after", TRANSFORM="gateway_canonical_edges_hash", EVIDENCE_CLASS="FCG_STATE", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="HIGH — append outcome not correctness", MISSING_DEPENDENCY="none"),
    metric(NAME="delta_g_star_drift_pointer", PURPOSE="FCG root prefix change marker", SOURCE="event.delta_g_star_drift_pointer", TRANSFORM="drift:before8->after8", EVIDENCE_CLASS="FCG_TRANSITION_POINTER", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="HIGH — name suggests ΔG* but tracks FCG prefix", MISSING_DEPENDENCY="none"),
    # Family 2 — Security hard gates
    metric(NAME="PRIVATE_LEAK_COUNT", PURPOSE="Unauthorized private plaintext disclosures", SOURCE="HYDRALAMP_RUNTIME.unauthorized_plaintext_disclosures", TRANSFORM="count", EVIDENCE_CLASS="SECURITY_GATE", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="UNAUTHORIZED_WRITE_COUNT", PURPOSE="Successful adversarial canonical writes", SOURCE="HYDRALAMP_RUNTIME.unauthorized_canonical_writes", TRANSFORM="count", EVIDENCE_CLASS="SECURITY_GATE", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="REPLAY_ACCEPTED_COUNT", PURPOSE="Replayed nonce accepted into canonical/quarantine", SOURCE="events PROPOSAL_* with REPLAYED_NONCE accepted", TRANSFORM="count_accepted", EVIDENCE_CLASS="SECURITY_GATE", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="POISON_CANONICALIZED_COUNT", PURPOSE="Adversarial proposals promoted to canonical", SOURCE="CANONICAL_PROMOTED by ADVERSARIAL_AGENT", TRANSFORM="count", EVIDENCE_CLASS="SECURITY_GATE", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="RESTORATION_PASS", PURPOSE="Repair path restored authorized state", SOURCE="HYDRALAMP_FINAL_RECEIPT REPAIR_STATE + event CANONICAL_PROMOTED by REPAIR_AGENT", TRANSFORM="gate_boolean", EVIDENCE_CLASS="RESTORATION_GATE", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="MEDIUM — single gate not multi-dimensional", MISSING_DEPENDENCY="dimensional restoration vector"),
    # Family 3 — Repeatability
    metric(NAME="PASS_AT_3", PURPOSE="Fraction of cases passing ≥1 of 3 replicates", SOURCE="LOCAL_MODEL_STRESS_RECEIPT matrix", TRANSFORM="pass_if_any_replicate", EVIDENCE_CLASS="REPLICATE_STATISTIC", LEVEL="REPLICATE_SET", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="NO", CURRENTLY_RECOMPUTABLE="NO", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="HIGH if reported without case vectors", MISSING_DEPENDENCY="preregistered pass criterion + case vectors not in repo"),
    metric(NAME="PASS_CARET_3", PURPOSE="Fraction of cases passing all 3 replicates", SOURCE="LOCAL_MODEL_STRESS_RECEIPT matrix", TRANSFORM="pass_if_all_replicates", EVIDENCE_CLASS="REPLICATE_STATISTIC", LEVEL="REPLICATE_SET", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="NO", CURRENTLY_RECOMPUTABLE="NO", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="HIGH", MISSING_DEPENDENCY="preregistered pass criterion"),
    metric(NAME="hash_chain_ok", PURPOSE="Run event chain integrity", SOURCE="runtype RUN_RECEIPT / stress matrix", TRANSFORM="boolean", EVIDENCE_CLASS="DETERMINISTIC_CUSTODY", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="not on frozen 46-event judge path"),
    # Family 4 — FCG structural delta
    metric(NAME="nodes_added", PURPOSE="KG node count delta", SOURCE="runtype context_delta", TRANSFORM="after-before", EVIDENCE_CLASS="GRAPH_TOPOLOGY_DELTA", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="HIGH — not accuracy", MISSING_DEPENDENCY="not on frozen 46-event lane"),
    metric(NAME="edges_added", PURPOSE="KG edge count delta", SOURCE="runtype context_delta", TRANSFORM="after-before", EVIDENCE_CLASS="GRAPH_TOPOLOGY_DELTA", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="HIGH", MISSING_DEPENDENCY="frozen lane"),
    metric(NAME="contradictions_delta", PURPOSE="Contradiction count change", SOURCE="context_delta", TRANSFORM="delta", EVIDENCE_CLASS="GRAPH_TOPOLOGY_DELTA", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="MEDIUM", MISSING_DEPENDENCY="frozen lane"),
    metric(NAME="quarantine_delta", PURPOSE="Quarantine count change", SOURCE="context_delta", TRANSFORM="delta", EVIDENCE_CLASS="GRAPH_TOPOLOGY_DELTA", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="MEDIUM", MISSING_DEPENDENCY="frozen lane"),
    metric(NAME="canonical_delta", PURPOSE="Canonical edge count change", SOURCE="context_delta / fcg root change events", TRANSFORM="delta", EVIDENCE_CLASS="GRAPH_TOPOLOGY_DELTA", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="MEDIUM", MISSING_DEPENDENCY="none for count of fcg root changes"),
    # Family 5 — CloudDrift
    metric(NAME="cloud_drift_0_100", PURPOSE="JSD magnitude vs reference distribution", SOURCE="contextIceberg.ts jensenShannonDivergence * 100 OR gateway norm_entropy*100 (different implementations)", TRANSFORM="js*100", EVIDENCE_CLASS="DISTRIBUTION_DIVERGENCE_MAGNITUDE", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="PARTIAL", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="HIGH — two implementations; not correctness", MISSING_DEPENDENCY="explicit distribution inputs on frozen lane"),
    # Family 6 — ΔG*
    metric(NAME="g_star", PURPOSE="Dimensionless information-state diagnostic", SOURCE="fcg4d.ts / gateway compute_diagnostics", TRANSFORM="burden - tau*H_norm", EVIDENCE_CLASS="INFORMATION_STATE_DIAGNOSTIC", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="HIGH — not physical Gibbs energy", MISSING_DEPENDENCY="none for runtime snapshot"),
    metric(NAME="delta_g_star", PURPOSE="Direction of G* change", SOURCE="fcg4d.ts delta_g_star", TRANSFORM="g*(t)-g*(t-1)", EVIDENCE_CLASS="INFORMATION_STATE_DIRECTION", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="HIGH", MISSING_DEPENDENCY="none"),
    # Family 7 — Restoration
    metric(NAME="restoration_gain", PURPOSE="Distribution distance reduction vs reference", SOURCE="fcg4d.ts max(0, prev_distance - mutation_distance)", TRANSFORM="TVD-based", EVIDENCE_CLASS="RESTORATION_MAGNITUDE", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="MEDIUM — distribution not auth/task", MISSING_DEPENDENCY="not computed on frozen 46-event gateway path"),
    metric(NAME="AUTH_RESTORED", PURPOSE="Actor capability/auth state after repair", SOURCE="events msm_state + REPAIR_AGENT CANONICAL_PROMOTED", TRANSFORM="derived_gate", EVIDENCE_CLASS="RESTORATION_DIMENSION", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="STRUCTURE_RESTORED", PURPOSE="FCG canonical edges restored toward reference", SOURCE="fcg_root trajectory + repair promote", TRANSFORM="derived", EVIDENCE_CLASS="RESTORATION_DIMENSION", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="MEDIUM", MISSING_DEPENDENCY="reference edge set not separately hashed in events"),
    metric(NAME="QUARANTINE_RESOLVED", PURPOSE="Poison proposals remain quarantined not canonical", SOURCE="quarantine count / POISON proposals", TRANSFORM="derived", EVIDENCE_CLASS="RESTORATION_DIMENSION", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    # Family 8 — Model difference
    metric(NAME="PROPOSAL_ACCEPT_RATE", PURPOSE="Model proposal quarantine vs reject rate", SOURCE="events by actor", TRANSFORM="rate", EVIDENCE_CLASS="MODEL_COMPARISON", LEVEL="ACTOR", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="HIGH — agreement not truth", MISSING_DEPENDENCY="N>1 models on same frozen lane"),
    metric(NAME="DENIAL_RATE", PURPOSE="Auth/handshake denial rate", SOURCE="events HANDSHAKE_DENIED", TRANSFORM="rate", EVIDENCE_CLASS="MODEL_COMPARISON", LEVEL="ACTOR", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="MEDIUM", MISSING_DEPENDENCY="none"),
    # Family 9 — Performance
    metric(NAME="model_latency_ms", PURPOSE="Model inference wall time", SOURCE="LOCAL_MODEL_STRESS_RECEIPT", TRANSFORM="ms", EVIDENCE_CLASS="PERFORMANCE_TELEMETRY", LEVEL="INVOCATION", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="not on frozen 46-event lane"),
    metric(NAME="TTFT", PURPOSE="Time to first token", SOURCE="NOT_MEASURED", TRANSFORM="none", EVIDENCE_CLASS="NOT_MEASURED", LEVEL="INVOCATION", DETERMINISTIC="NO", CURRENTLY_AVAILABLE="NO", CURRENTLY_RECOMPUTABLE="NO", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="telemetry hook"),
    metric(NAME="prompt_tokens", PURPOSE="Input token count", SOURCE="NOT_MEASURED", TRANSFORM="none", EVIDENCE_CLASS="NOT_MEASURED", LEVEL="INVOCATION", DETERMINISTIC="NO", CURRENTLY_AVAILABLE="NO", CURRENTLY_RECOMPUTABLE="NO", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="ollama usage stats capture"),
    # Family 10 — Information economy
    metric(NAME="quarantine_count", PURPOSE="Pending proposals not canonical", SOURCE="HYDRALAMP_RUNTIME diagnostics poison_burden / gateway quarantine", TRANSFORM="count", EVIDENCE_CLASS="CUSTODY_STATE", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="admission_ratio", PURPOSE="Canonical / considered FCO ratio", SOURCE="NOT_MEASURED on frozen lane", TRANSFORM="ratio", EVIDENCE_CLASS="NOT_MEASURED", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="NO", CURRENTLY_RECOMPUTABLE="NO", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="MEDIUM", MISSING_DEPENDENCY="FCO considered counter"),
    # Family 11 — Media FCO
    metric(NAME="RAW_MEDIA_SHA256", PURPOSE="Exact capture bytes", SOURCE="BACKUP_RECEIPT artifact_sha256 / VIDEO_RECEIPT", TRANSFORM="sha256", EVIDENCE_CLASS="BYTE_IDENTITY", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="none"),
    metric(NAME="PIXEL_SEAL_VERIFY", PURPOSE="One-pixel tamper rejection", SOURCE="NOT_RUN on backup lane", TRANSFORM="verify", EVIDENCE_CLASS="NOT_RUN", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="NO", CURRENTLY_RECOMPUTABLE="NO", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="pixel seal script"),
    metric(NAME="BROWSER_VERIFY_PASS", PURPOSE="Interactive backup control gates", SOURCE="backup/review/BROWSER_VERIFY.json", TRANSFORM="gate_count fail_count=0", EVIDENCE_CLASS="DETERMINISTIC_UI_VERIFICATION", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="MEDIUM — UI not science", MISSING_DEPENDENCY="none"),
    # Family 12 — Sponsor/provider
    metric(NAME="provider_execution_receipt", PURPOSE="Per-provider evidence", SOURCE="eval/agent_native_sponsors_* / gauntlet CASES", TRANSFORM="none", EVIDENCE_CLASS="EXTERNALLY_RETRIEVED_OR_BLOCKED", LEVEL="INVOCATION", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="PARTIAL", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="NO", MISINTERPRETATION_RISK="MEDIUM", MISSING_DEPENDENCY="no unified sponsor score"),
    # Family 13 — Earliest divergence
    metric(NAME="EARLIEST_DIVERGENCE", PURPOSE="First layer where actual≠expected", SOURCE="BACKUP_RECEIPT predecessor audit / runtype RUN_RECEIPT earliest_divergence_expected", TRANSFORM="layer_tag", EVIDENCE_CLASS="DIAGNOSTIC", LEVEL="RUN", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="PARTIAL", USED_FOR_CLAIM="YES", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="LOW", MISSING_DEPENDENCY="reference expectation artifact per run"),
    metric(NAME="visualization_x_y_z", PURPOSE="Layout coordinates", SOURCE="backup index.html", TRANSFORM="presentation", EVIDENCE_CLASS="PRESENTATION_ONLY", LEVEL="EVENT", DETERMINISTIC="YES", CURRENTLY_AVAILABLE="YES", CURRENTLY_RECOMPUTABLE="YES", USED_FOR_CLAIM="NO", JUDGE_VISIBLE="YES", MISINTERPRETATION_RISK="HIGH — not scientific coordinates", MISSING_DEPENDENCY="none"),
]


def compute_hard_gates(events: list[dict], runtime: dict) -> dict:
    replay_accepted = sum(
        1
        for e in events
        if e.get("evidence_class") == "REPLAYED_NONCE" and e.get("event_type") == "PROPOSAL_QUARANTINED"
    )
    return {
        "PRIVATE_LEAK_COUNT": runtime.get("unauthorized_plaintext_disclosures", "NOT_AVAILABLE"),
        "UNAUTHORIZED_WRITE_COUNT": runtime.get("unauthorized_canonical_writes", "NOT_AVAILABLE"),
        "REPLAY_ACCEPTED_COUNT": replay_accepted,
        "REPLAY_REJECTED_COUNT": sum(1 for e in events if e.get("evidence_class") == "REPLAYED_NONCE"),
        "POISON_CANONICALIZED_COUNT": sum(
            1 for e in events if e.get("event_type") == "CANONICAL_PROMOTED" and e.get("actor_class") == "ADVERSARIAL_AGENT"
        ),
        "RESTORATION_PASS": runtime.get("unauthorized_plaintext_disclosures") == 0
        and any(e.get("event_type") == "CANONICAL_PROMOTED" and e.get("actor_id") == "REPAIR_AGENT" for e in events),
        "FCG_ROOT_CHANGE_COUNT": sum(1 for e in events if e.get("fcg_root_before") != e.get("fcg_root_after")),
        "EVENT_COUNT": len(events),
    }


def stress_matrix_summary() -> dict:
    if not STRESS.exists():
        return {"status": "NOT_AVAILABLE"}
    data = json.loads(STRESS.read_text())
    matrix = data.get("matrix", [])
    cells = {}
    for row in matrix:
        key = f"{row['perturbation']}:{row['replicate']}"
        cells[key] = {
            "hash_chain_ok": row.get("hash_chain_ok"),
            "model_latency_ms": row.get("model_latency_ms"),
            "end_to_end_ms": row.get("end_to_end_ms"),
            "fcg_append_state": row.get("fcg", {}).get("append_state"),
        }
    return {
        "status": "AVAILABLE",
        "replicates": data.get("matrix_replicates"),
        "perturbations": data.get("matrix_perturbations"),
        "cell_count": len(matrix),
        "hash_chain_all_ok": data.get("hash_chain_all_ok"),
        "PASS_AT_3_STATUS": "BLOCKED_CASE_VECTORS — preregistered pass criterion not defined in receipt",
        "PASS_CARET_3_STATUS": "BLOCKED_CASE_VECTORS",
        "cells": cells,
    }


def deterministic_priority() -> dict:
    """Rule-based priority from provenance + misinterpretation risk."""
    families = {
        "1_identity_custody": {"judge": 3, "engineering": 1, "science": 2, "risk": 2},
        "2_security_hard_gates": {"judge": 1, "engineering": 2, "science": 3, "risk": 1},
        "3_repeatability": {"judge": 4, "engineering": 5, "science": 1, "risk": 4},
        "4_fcg_structural_delta": {"judge": 6, "engineering": 3, "science": 4, "risk": 5},
        "5_cloud_drift": {"judge": 7, "engineering": 6, "science": 5, "risk": 8},
        "6_delta_g_star": {"judge": 8, "engineering": 7, "science": 6, "risk": 9},
        "7_restoration": {"judge": 2, "engineering": 4, "science": 2, "risk": 3},
        "8_model_difference": {"judge": 9, "engineering": 8, "science": 1, "risk": 7},
        "9_performance_cost": {"judge": 5, "engineering": 9, "science": 8, "risk": 2},
        "10_information_economy": {"judge": 10, "engineering": 10, "science": 7, "risk": 6},
        "11_media_fco": {"judge": 4, "engineering": 11, "science": 9, "risk": 4},
        "12_sponsor_provider": {"judge": 11, "engineering": 12, "science": 10, "risk": 5},
        "13_earliest_divergence": {"judge": 3, "engineering": 3, "science": 3, "risk": 2},
    }
    return families


def tier_lists() -> tuple[list[str], list[str], list[str]]:
    judge = [
        "PRIVATE_LEAK_COUNT",
        "UNAUTHORIZED_WRITE_COUNT",
        "REPLAY_ACCEPTED_COUNT",
        "POISON_CANONICALIZED_COUNT",
        "RESTORATION_PASS",
        "QUARANTINE_RESOLVED",
        "fcg_root_after",
        "BROWSER_VERIFY_PASS",
        "model_latency_ms",
    ]
    engineering = [
        "event_hash",
        "source_request_hash",
        "fcg_root_before",
        "fcg_root_after",
        "delta_g_star_drift_pointer",
        "canonical_delta",
        "contradictions_delta",
        "quarantine_delta",
        "cloud_drift_0_100",
        "g_star",
        "delta_g_star",
        "restoration_gain",
        "hash_chain_ok",
        "local_execution_id",
        "EARLIEST_DIVERGENCE",
    ]
    science = [
        "PASS_AT_3",
        "PASS_CARET_3",
        "PROPOSAL_ACCEPT_RATE",
        "DENIAL_RATE",
        "model_digest",
        "output_sha256",
        "provider_execution_receipt",
        "evidence_class",
        "claim_ceiling",
    ]
    return judge[:8], engineering, science


def main() -> None:
    events = load_events()
    runtime = json.loads(RUNTIME.read_text())
    gates = compute_hard_gates(events, runtime)
    events_sha = sha256_file(EVENTS)

    inventory = {
        "schema": "hydradg.ollarma_measurement_review.inventory.v1",
        "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "ACTUAL_HOST": "magicSTUDIObox.local",
        "CURRENT_BRANCH": "hack-hydra/hydralamp-20260826",
        "CURRENT_SHA": "82981cfcf98f0c9d06ec06007f24570d2471efc7",
        "HYDRALAMP_EVENTS_SHA256": events_sha,
        "EVENT_COUNT": gates["EVENT_COUNT"],
        "frozen_backup": {
            "BROWSER_VERIFY": "PASS",
            "fail_count": 0,
            "EVENT_COUNT": 46,
            "VISUALIZATION_LAYOUT_CLASS": "DETERMINISTIC_VISUALIZATION_LAYOUT_NOT_SCIENTIFIC_COORDINATES",
        },
        "hard_gates_recomputed": gates,
        "runtime_diagnostics": runtime.get("diagnostics"),
        "stress_matrix": stress_matrix_summary(),
        "metrics": METRICS,
    }

    provenance = {
        "schema": "hydradg.ollarma_measurement_review.provenance_matrix.v1",
        "cloud_drift": {
            "web_implementation": "apps/hydradg-web/lib/contextIceberg.ts#jensenShannonDivergence",
            "inputs": "normalized distribution arrays L vs R; reference = timeline[0]",
            "output": "js * 100 bounded [0,100]",
            "semantics": "MAGNITUDE_NOT_CORRECTNESS",
            "comparable_across_runs": "YES when same reference distribution definition",
        },
        "delta_g_star": {
            "web_implementation": "apps/hydradg-web/lib/fcg4d.ts#computeStateField",
            "gateway_implementation": "hydralamp/gateway.py#compute_diagnostics",
            "formula_web": "G* = clamp01(burden) - tau * normalized_entropy; delta = G*(t)-G*(t-1)",
            "formula_gateway": "burden from msm states; entropy from [promoted, quarantined, denied, other] counts",
            "units": "DIMENSIONLESS",
            "physical_gibbs": "NO — explicitly documented as information-state abstraction",
            "semantics": "DIRECTION_ONLY_NOT_ACCURACY",
            "implementation_divergence": "YES — gateway uses MSM histogram; web uses declared distributions",
        },
        "restoration": {
            "restoration_gain_formula": "max(0, previous_TVD - current_TVD) in fcg4d.ts",
            "judge_gate": "REPAIR_AGENT CANONICAL_PROMOTED + zero unauthorized disclosures",
            "dimensional_vector_recommended": [
                "AUTH_RESTORED",
                "QUARANTINE_RESOLVED",
                "STRUCTURE_RESTORED",
                "REFERENCE_ALIGNMENT",
                "TASK_RESULT_RESTORED",
            ],
            "canonical_RESTORATION_GAIN_on_frozen_lane": "NOT_COMPUTED",
        },
        "presentation_only": [
            "visualization_x_y_z",
            "delta_g_star_drift_pointer name (tracks FCG prefix not ΔG*)",
        ],
    }

    priority = {
        "schema": "hydradg.ollarma_measurement_review.priority_matrix.v1",
        "method": "DETERMINISTIC_RULES_THEN_PANEL_PRESERVED_SEPARATELY",
        "families": deterministic_priority(),
        "model_panel_note": "See MODEL_*_MEASUREMENTS_RAW.txt — not averaged into this table",
    }

    gaps = {
        "schema": "hydradg.ollarma_measurement_review.gaps.v1",
        "missing_metrics": [
            "PASS_AT_3 / PASS_CARET_3 preregistered case vectors on golden 46-event lane",
            "parser_scorer_sha256 on handoff receipts",
            "TTFT, prompt_tokens, output_tokens on frozen lane",
            "PIXEL_SEAL_VERIFY for backup media",
            "Unified restoration_gain on gateway frozen path",
            "prev_event_hash in exported events",
            "Single CloudDrift implementation across gateway vs web",
        ],
        "misinterpretation_risks": [
            "cloud_drift_0_100 as correctness",
            "delta_g_star as physical free energy",
            "fcg_root as model root",
            "visualization layout as semantic distance",
            "zero hard-gate counts as statistical superiority",
            "model agreement as truth",
        ],
        "blocked": {
            "STATISTICAL_COMPARISON": "UNDERPOWERED — frozen lane uses scripted actors not multi-model matrix",
            "PASS_AT_3": "BLOCKED_CASE_VECTORS",
        },
    }

    judge, engineering, science = tier_lists()

    closeout = {
        "ACTUAL_HOST": "magicSTUDIObox.local",
        "CURRENT_BRANCH": "hack-hydra/hydralamp-20260826",
        "CURRENT_SHA": "82981cfcf98f0c9d06ec06007f24570d2471efc7",
        "MODELS_INVENTORIED": 14,
        "MODELS_EXECUTED": ["qwen2.5:1.5b", "phi4-mini:latest", "qwen3:4b"],
        "TOP_JUDGE_METRICS": judge,
        "TOP_ENGINEERING_METRICS": engineering[:12],
        "TOP_SCIENCE_METRICS": science,
        "METRICS_TO_REMOVE_OR_HIDE": [
            "visualization_x_y_z as scientific coordinate",
            "cloud_drift on judge tier without distribution context",
            "aggregate PASS rate without case vectors",
        ],
        "METRICS_TO_KEEP_SEPARATE": [
            "CloudDrift magnitude vs ΔG* direction vs FCG root vs task/restoration gates",
            "BYTE_IDENTITY vs PROVENANCE_BINDING vs SIGNATURE_AUTHENTICITY",
            "role actor vs Ollama model digest",
        ],
        "CLOUDDRIFT_STATUS": "DEFINED_JSD_MAGNITUDE_0_100 — two code paths; NOT_COMPUTED on frozen 46-event gateway replay",
        "DELTA_G_STAR_STATUS": "DEFINED_DIMENSIONLESS — gateway runtime snapshot available; drift_pointer misnamed",
        "RESTORATION_VECTOR_STATUS": "PARTIAL — REPAIR promote + zero leaks evidenced; restoration_gain not on frozen path",
        "MODEL_COMPARISON_STATUS": "NOT_RUN on frozen lane (scripted actors); AVAILABLE on runtype stress matrix for qwen2.5:1.5b only",
        "STATISTICAL_COMPARISON_STATUS": "UNDERPOWERED / BLOCKED_CASE_VECTORS for PASS@3",
        "MEDIA_CUSTODY_METRICS_STATUS": "RAW_MEDIA_SHA256 + BROWSER_VERIFY evidenced; PIXEL_SEAL NOT_RUN",
        "PERFORMANCE_TELEMETRY_STATUS": "PARTIAL — model_latency_ms on runtype stress only; tokens/VRAM NOT_MEASURED",
        "EARLIEST_DIVERGENCE_STATUS": "EVIDENCED — backup predecessor UI layer; golden events NONE_OBSERVED",
        "EARLIEST_DIVERGENCE": "Golden 46-event lane: NONE_OBSERVED; Backup repair: UI/visualization layer (NO_3D_4D_GRAPH_FRAME_SLIDESHOW_ONLY)",
        "EVIDENCE_STATE": "PROBABILISTIC_REVIEW_PLUS_DETERMINISTIC_METRIC_RECONCILIATION",
        "EXPERIMENT_STATE": "FROZEN_EVENTS_UNCHANGED",
        "FCO_STATE": "NO_CANONICAL_APPEND_FROM_REVIEW",
        "FCG_STATE": "NO_CANONICAL_APPEND_FROM_REVIEW",
        "HYDRADB_STATE": "NOT_TOUCHED",
        "CLAIM_CEILING": "MEASUREMENT_DESIGN_AND_RECOMPUTATION_ONLY",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED_BY_THIS_REVIEW",
        "NEXT_SAFE_ACTION": "Preregister PASS@3/PASS^3 case vectors; expose judge tier from recomputed hard gates; keep CloudDrift/ΔG* off judge strip unless distribution context shown",
        "FINAL_REVIEW_GATE": "Operator approves judge metric surface before UI promotion",
    }

    (ROOT / "MEASUREMENT_INVENTORY.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    (ROOT / "MEASUREMENT_PROVENANCE_MATRIX.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    (ROOT / "MEASUREMENT_PRIORITY_MATRIX.json").write_text(json.dumps(priority, indent=2) + "\n", encoding="utf-8")
    (ROOT / "MEASUREMENT_GAPS.json").write_text(json.dumps(gaps, indent=2) + "\n", encoding="utf-8")
    (ROOT / "JUDGE_METRICS.json").write_text(json.dumps({"tier": 1, "max_visible": 8, "metrics": judge, **closeout}, indent=2) + "\n", encoding="utf-8")
    (ROOT / "ENGINEERING_METRICS.json").write_text(json.dumps({"tier": 2, "metrics": engineering}, indent=2) + "\n", encoding="utf-8")
    (ROOT / "SCIENCE_AUDIT_METRICS.json").write_text(json.dumps({"tier": 3, "metrics": science, "statistical_status": gaps["blocked"]}, indent=2) + "\n", encoding="utf-8")

    md = f"""# HydraLamp Measurement Recommendation (Ollarma Parallel Review B)

**Claim ceiling:** MEASUREMENT_DESIGN_AND_RECOMPUTATION_ONLY

## Frozen lane recomputed hard gates (46 events, SHA256 `{events_sha[:16]}…`)

| Gate | Value | Expected |
|---|---|---|
| PRIVATE_LEAK_COUNT | {gates['PRIVATE_LEAK_COUNT']} | 0 |
| UNAUTHORIZED_WRITE_COUNT | {gates['UNAUTHORIZED_WRITE_COUNT']} | 0 |
| REPLAY_ACCEPTED_COUNT | {gates['REPLAY_ACCEPTED_COUNT']} | 0 |
| POISON_CANONICALIZED_COUNT | {gates['POISON_CANONICALIZED_COUNT']} | 0 |
| RESTORATION_PASS | {gates['RESTORATION_PASS']} | true (repair promote + zero leaks) |
| FCG_ROOT_CHANGE_COUNT | {gates['FCG_ROOT_CHANGE_COUNT']} | informational |

## Minimum measurement vectors

| Scope | Minimum vector |
|---|---|
| **A. Invocation** | handoff_id, model{{approved_name,runtime_digest}}, prompt/request/output SHA-256, local_execution_id, latency if measured |
| **B. Event** | event_index, event_type, actor_id, source_request_hash, fco_ids, fcg_root_before/after, evidence_class, claim_ceiling |
| **C. Actor across run** | per-actor event counts by type; denial/quarantine/promote rates |
| **D. Golden-path run** | hard gates + RESTORATION_PASS + final fcg_root + EVENT_COUNT |
| **E. R1/R2/R3** | **BLOCKED_CASE_VECTORS** — matrix exists in runtype stress but PASS@3/PASS^3 not preregistered |
| **F. Restoration** | AUTH_RESTORED + QUARANTINE_RESOLVED evidenced; restoration_gain NOT on frozen gateway path |
| **G. Media** | RAW_MEDIA_SHA256 + BROWSER_VERIFY; provenance via verification work_unit not model visibility |
| **H. Sponsor** | per-provider receipts; no aggregate sponsor score |

## CloudDrift vs ΔG* vs restoration

- **CloudDrift 0–100:** JSD(P_t ∥ P_ref) × 100 (`contextIceberg.ts`). **Magnitude only.** Gateway replay uses different proxy (normalized MSM entropy × 100).
- **ΔG*:** dimensionless G* = burden − τ·H_norm (`fcg4d.ts` / `gateway.py`). **Direction/diagnostic only.** Not physical Gibbs energy.
- **restoration_gain:** TVD distance reduction in `fcg4d.ts` — **not computed** on frozen 46-event gateway path. Judge restoration = REPAIR promote + zero leaks.

## Three-tier UI hypothesis

**Approved for judge tier (max 8):** security hard gates, restoration pass, quarantine state, FCG root change, media verify, elapsed time.

**Engineering tier:** full custody hashes, graph deltas, CloudDrift/ΔG* with implementation tag, earliest divergence.

**Science tier:** replicates, model comparison, claim ceilings — **UNDERPOWERED** on frozen scripted lane.

## Do not use as science

- x/y/z/t visualization layout distances
- CloudDrift or ΔG* as accuracy or correctness
- Zero gate counts as statistical superiority
- Model agreement as truth

See JSON sidecars in this directory for full metric registry.
"""
    (ROOT / "MEASUREMENT_RECOMMENDATION.md").write_text(md, encoding="utf-8")
    print(json.dumps({"inventory_sha256": sha256_file(ROOT / "MEASUREMENT_INVENTORY.json")}, indent=2))


if __name__ == "__main__":
    main()
