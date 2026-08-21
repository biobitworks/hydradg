#!/usr/bin/env python3
"""HydraDG BEAM 1M fail-closed preparation pipeline.

Purpose:
- identify the official BEAM source and expected 1M scope;
- prepare HydraDB-style Routes A-H without fabricating BEAM rows or scores;
- preregister future FCO/FCG multi-session, multi-agent, and economics experiments;
- emit only preparation metadata until official BEAM rows are materialized and hashed.

This script performs ZERO generative inference and ZERO benchmark scoring.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BEAM_DIR = PROJECT_ROOT / "eval" / "beam_1m_20260820"

OFFICIAL_SOURCE = "https://github.com/mohammadtavakoli78/BEAM"
SOURCE_REPO_LICENSE = "MIT"
EXPECTED_CONVERSATIONS_1M = 35
EXPECTED_PROBES_1M = 700
HYDRADB_PUBLISHED_BEAM_1M_OVERALL = 0.82

CATEGORIES = [
    "temporal_reasoning",
    "multi_session_reasoning",
    "event_ordering",
    "information_extraction",
    "contradiction_resolution",
    "summarization",
    "abstention",
    "instruction_following",
    "preference_following",
    "knowledge_update",
]

ROUTES = [
    {"id": "Route A", "description": "Dense content retrieval"},
    {"id": "Route B", "description": "Route A + BM25 sparse lexical retrieval"},
    {"id": "Route C", "description": "Route B + sliding-window contextual enrichment / latent representation"},
    {"id": "Route D", "description": "Route C + adaptive query expansion"},
    {"id": "Route E", "description": "Route D + FCG graph entry and bounded traversal"},
    {"id": "Route F", "description": "Route E + valid-time/current-state/supersession filtering"},
    {"id": "Route G", "description": "Route F + reranking / evidence fusion"},
    {"id": "Route H", "description": "Route G + full FCO/FCG custody and claim-state controls"},
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    BEAM_DIR.mkdir(parents=True, exist_ok=True)
    (BEAM_DIR / "routes").mkdir(parents=True, exist_ok=True)

    source_receipt = {
        "schema": "hydradg.beam_source_receipt.v2",
        "source_url": OFFICIAL_SOURCE,
        "source_repository_license": SOURCE_REPO_LICENSE,
        "dataset_tier": "BEAM_1M",
        "source_state": "OFFICIAL_SOURCE_IDENTIFIED",
        "official_rows_materialized": False,
        "revision_state": "PIN_ON_MATERIALIZATION",
        "claim_ceiling": "SOURCE_IDENTIFIED_ROWS_NOT_YET_MATERIALIZED_OR_HASHED",
    }
    write_json(BEAM_DIR / "SOURCE_RECEIPT.json", source_receipt)

    license_receipt = {
        "schema": "hydradg.beam_license_receipt.v2",
        "source_repository_license": SOURCE_REPO_LICENSE,
        "source_repository_license_verified": True,
        "dataset_rights_status": "VERIFY_ON_OFFICIAL_DATA_MATERIALIZATION",
        "commercial_use_permitted_by_this_receipt": "NOT_ASSERTED",
        "derivatives_permitted_by_this_receipt": "NOT_ASSERTED",
        "claim_ceiling": "SOURCE_REPOSITORY_LICENSE_ONLY",
    }
    write_json(BEAM_DIR / "LICENSE_RECEIPT.json", license_receipt)

    # Do not synthesize benchmark rows. Expected scope comes from the public BEAM 1M definition;
    # observed official rows remain zero until the real dataset is copied/downloaded and hashed.
    manifest = {
        "schema": "hydradg.beam_dataset_manifest.v2",
        "tier": "BEAM_1M",
        "expected_conversations": EXPECTED_CONVERSATIONS_1M,
        "expected_probes": EXPECTED_PROBES_1M,
        "observed_official_conversations": 0,
        "observed_official_probes": 0,
        "categories_expected": CATEGORIES,
        "official_rows_materialized": False,
        "status": "OFFICIAL_ROWS_NOT_MATERIALIZED",
        "synthetic_probe_rows_generated": False,
    }
    write_json(BEAM_DIR / "DATASET_MANIFEST.json", manifest)

    # Keep the legacy path but make its state explicit. This is metadata, not a benchmark row.
    registry_marker = {
        "record_type": "REGISTRY_STATE",
        "claim_eligibility": "NOT_A_BEAM_PROBE_ROW",
        "state": "OFFICIAL_ROWS_NOT_MATERIALIZED",
        "expected_conversations": EXPECTED_CONVERSATIONS_1M,
        "expected_probes": EXPECTED_PROBES_1M,
    }
    (BEAM_DIR / "PROBE_REGISTRY.jsonl").write_text(json.dumps(registry_marker, sort_keys=True) + "\n")

    write_json(BEAM_DIR / "routes" / "ROUTES_DEFINITION.json", {
        "schema": "hydradg.beam_architecture_routes.v2",
        "routes": ROUTES,
        "execution_state": "PREPARED_UNEXECUTED",
    })

    future_multi_agent = {
        "schema": "hydradg.future_multi_agent_economics.v1",
        "state": "FUTURE_PREREGISTERED_HYPOTHESIS_NOT_EXECUTED",
        "hypothesis": "Explicit FCO supersession, validity, provenance, claim-state, and agent-decision lineage can improve knowledge-update, contradiction-resolution, and multi-session reasoning while preserving temporal reasoning, event ordering, and multi-session guardrails.",
        "multi_agent_chain": [
            "retrieval_agent",
            "extraction_agent",
            "reasoning_agent",
            "decision_agent",
            "answer_agent"
        ],
        "controlled_perturbations": [
            "extraction_poison",
            "stale_state_poison",
            "contradiction_poison",
            "provenance_loss",
            "downstream_agent_inheritance"
        ],
        "future_quality_metrics": [
            "ErrorPropagationRate",
            "RecoveryRate",
            "FirstDivergenceAccuracy",
            "CurrentStateAccuracy",
            "HistoricalStateRetention",
            "CompleteEvidencePathRecovery"
        ],
        "future_economic_metrics": [
            "SerializedByteReduction",
            "ContextTokenReduction",
            "AvoidedDownstreamInferenceCalls",
            "UsefulComputeRatio",
            "CostPerCorrectGovernedAnswer"
        ],
        "economic_claim_ceiling": "NO_COST_SAVINGS_CLAIM_UNTIL_MEASURED",
        "non_inferiority_guardrails": [
            "temporal_reasoning",
            "event_ordering",
            "multi_session_reasoning"
        ],
        "anticube_role": "CLASSIFICATION_AND_GOVERNANCE_SIGNAL_NOT_ASSUMED_RANKING_BOOST",
        "failure_policy": "WRONG_AGENT_DECISIONS_RETAINED_AS_PERTURBATION_EVIDENCE"
    }
    write_json(BEAM_DIR / "FUTURE_MULTI_AGENT_ECONOMICS.json", future_multi_agent)

    prereg = {
        "schema": "hydradg.beam_preregistration.v2",
        "tier": "BEAM_1M",
        "expected_conversations_count": EXPECTED_CONVERSATIONS_1M,
        "expected_probes_count": EXPECTED_PROBES_1M,
        "official_rows_materialized": False,
        "routes_implemented": [route["id"] for route in ROUTES],
        "primary_route_comparison": "Route H vs Route A after official rows are materialized and frozen",
        "published_hydradb_reference_accuracy": HYDRADB_PUBLISHED_BEAM_1M_OVERALL,
        "published_reference_state": "EXTERNAL_REFERENCE_NOT_HYDRADG_RESULT",
        "generative_inference_started": False,
        "beam_numerical_results_published": False,
        "ready_for_execution": False,
        "blockers": [
            "OFFICIAL_BEAM_1M_ROWS_NOT_MATERIALIZED",
            "OFFICIAL_DATA_REVISION_AND_ROW_HASHES_NOT_FROZEN"
        ],
        "scientific_claim_ceiling": "BEAM_PIPELINE_PREPARED_OFFICIAL_ROWS_NOT_MATERIALIZED",
        "future_multi_agent_experiment": "FUTURE_MULTI_AGENT_ECONOMICS.json",
    }
    prereg_without_hash = json.dumps(prereg, sort_keys=True).encode("utf-8")
    prereg["preregistration_sha256"] = sha256_bytes(prereg_without_hash)
    write_json(BEAM_DIR / "BEAM_PREREGISTRATION.json", prereg)

    # Hash only files generated by this corrected preparation pass.
    manifest_lines = []
    for rel in [
        "SOURCE_RECEIPT.json",
        "LICENSE_RECEIPT.json",
        "DATASET_MANIFEST.json",
        "PROBE_REGISTRY.jsonl",
        "routes/ROUTES_DEFINITION.json",
        "FUTURE_MULTI_AGENT_ECONOMICS.json",
        "BEAM_PREREGISTRATION.json",
    ]:
        path = BEAM_DIR / rel
        manifest_lines.append(f"{sha256_bytes(path.read_bytes())}  {rel}")
    (BEAM_DIR / "SHA256_MANIFEST.txt").write_text("\n".join(manifest_lines) + "\n")

    print(json.dumps({
        "source": OFFICIAL_SOURCE,
        "source_repo_license": SOURCE_REPO_LICENSE,
        "expected_conversations": EXPECTED_CONVERSATIONS_1M,
        "expected_probes": EXPECTED_PROBES_1M,
        "official_rows_materialized": False,
        "hydradb_published_beam_1m_reference": HYDRADB_PUBLISHED_BEAM_1M_OVERALL,
        "future_multi_agent_state": future_multi_agent["state"],
        "ready_for_execution": False,
        "claim_ceiling": prereg["scientific_claim_ceiling"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
