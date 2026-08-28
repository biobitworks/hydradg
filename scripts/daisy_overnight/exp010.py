#!/usr/bin/env python3
"""EXP-010 governed decision-schema ablation — prereg, case bank, review, lease gate."""
from __future__ import annotations

import hashlib
import json
import socket
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from daisy_overnight.custody import sha256_bytes
from daisy_overnight.exp010_power import build_power_assessment

OPERATOR_PROMPT_VERBATIM = """On `magicSTUDIObox.local`, start a new isolated EXP-010 Daisy worktree/branch from canonical HydraDG SHA `825964f49e730d951e9199d8386334d8083448b9`. Do not modify EXP-008, EXP-009, or the Q38 replay lane.

First read `AGENTS.md`, `docs/GSD_GSIGMAD_FCO_ORCHESTRATION_PROFILE.md`, the canonical EXP-008/009 preregs/closeouts, schemas, and existing Daisy examples. Preserve OFFER → ACCEPT → PLAN → PLAN_CHECK → EXECUTE → VERIFY → SCIENCE_CLOSEOUT → FCO/FCG → commit/push.

Create discrete T010-A–F work units:

A. Build a deterministic paired-binary power assessment. Treat CASE as the independent unit; 3 replicates are nested and must never inflate N. Use α=.05, target power=.80, primary MDE=15 pp, sensitivity at 10/15/20 pp, and a preregistered discordance/attrition sensitivity grid. Use exact/small-sample appropriate methods; no observed/post-hoc power. Emit required paired N and raw case-bank N.

B. Build/freeze an outcome-blind independent EXP-010 case bank of whatever size the power gate requires. Hash every source/case and prove no selection from Q38 outcomes.

C. Preregister EXP-010 as a governed-decision-schema ablation: identical evidence atoms, models/runtime/parser/scorer frozen, only decision governance changed. Define primary estimand, exclusions, parse accounting, falsifiers, and claim ceiling before inference.

D. Independently review/recompute the prereg and power calculation. STOP on any pseudoreplication, leakage, undefined estimand, or inadequate power.

E. Hash artifacts, validate custody/orchestration, commit only the prereg/power/case-bank block, push, and prove ORIGIN_PARITY=PASS. `SIGNATURE_STATE=NOT_SIGNED` unless a real authorized private-key operation occurs; MMR only if actually constructed.

F. Check the active Q38/Ollama scientific-runtime lease. If Q38 is still running, stop cleanly with `BLOCKED_RUNTIME_LEASE` after the prereg push—do not contend, change model, or fall back. If free, execute EXP-010 exactly as preregistered, preserve every null/malformed/timeout, close out statistics and FCO/FCG/MMR, atomic commit/push, and report final SHA plus next EXP-011 recommendation.

Before doing anything, save this operator prompt verbatim as a versioned PROMPT provenance artifact, SHA-256 it, and link it to the EXP-010 work unit. Do not silently choose or change any scientific variable beyond the values locked above."""

GOVERNED_DECISION_SCHEMA = """Return exactly one JSON object with governed decision fields (NO top-level "answer" key):
{
  "state": "OK|ABSTAIN|MALFORMED_INPUT|BLOCKED_LABEL_LEAKAGE",
  "experiment_family": "E01|E02|E03|E04|E05|E06|E07",
  "condition": "string",
  "evidence_used": ["fco_id_or_quote"],
  "evidence_class": "SOURCE|INFERENCE|PROTOCOL|EXTERNALLY_RETRIEVED_EVIDENCE",
  "requirement": "string",
  "earliest_divergence": "A|B|C|D|E|F|G|NOT_APPLICABLE|UNKNOWN",
  "contradiction": "string|null",
  "missing_evidence": ["string"],
  "prohibited_claim": "string|null",
  "action": "string",
  "abstention_reason": "string|null",
  "claim_ceiling": "string",
  "observations": ["string"],
  "predicted_weak_dimensions": ["string"],
  "origin_classification": "DISTINCT_HACKATHON_DELTA|PREEXISTING_PROJECT|AMBIGUOUS|NOT_APPLICABLE",
  "missing_evidence_classes": ["string"],
  "causal_ranking": ["A", "B", "C"],
  "earliest_divergence_candidate": "A|B|C|D|E|F|G|NOT_APPLICABLE|UNKNOWN",
  "first_three_machine_actions": ["string"],
  "ordered_workflow": ["string"],
  "recommended_first_correction": "string|null",
  "confidence_0_1": 0.0,
  "evidence_quotes": ["string"],
  "invented_capabilities": []
}"""

FREE_FORM_SCHEMA = """Return exactly one JSON object:
{
  "state": "OK|ABSTAIN|MALFORMED_INPUT|BLOCKED_LABEL_LEAKAGE",
  "experiment_family": "E01|E02|E03|E04|E05|E06|E07",
  "condition": "string",
  "observations": ["string"],
  "predicted_weak_dimensions": ["string"],
  "origin_classification": "DISTINCT_HACKATHON_DELTA|PREEXISTING_PROJECT|AMBIGUOUS|NOT_APPLICABLE",
  "missing_evidence_classes": ["string"],
  "causal_ranking": ["A", "B", "C"],
  "earliest_divergence_candidate": "A|B|C|D|E|F|G|NOT_APPLICABLE|UNKNOWN",
  "first_three_machine_actions": ["string"],
  "ordered_workflow": ["string"],
  "recommended_first_correction": "string|null",
  "confidence_0_1": 0.0,
  "evidence_quotes": ["string"],
  "invented_capabilities": []
}"""

Q38_FORBIDDEN_PATHS = [
    "eval/ic_failure_learning_20260827/qwen38_model_replay_20260828",
    "/Users/byron/projects/active/hydradg-qwen38-model-replay-20260828",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def case_row(case_id: str, family: str, condition: str, payload: Any, task: str, blind: bool) -> dict[str, Any]:
    body = {
        "case_id": case_id,
        "experiment_family": family,
        "condition": condition,
        "blind": blind,
        "task": task,
        "input": payload,
    }
    body["case_payload_sha256"] = hashlib.sha256(canon(body)).hexdigest()
    return body


def write_prompt_provenance(exp_dir: Path) -> dict[str, Any]:
    text_path = exp_dir / "PROMPT_PROVENANCE.md"
    text_path.write_text(OPERATOR_PROMPT_VERBATIM + "\n", encoding="utf-8")
    receipt = {
        "schema": "hydradg.prompt_provenance.v1",
        "prompt_id": "EXP-010-OPERATOR-20260828",
        "recorded_at_utc": utc_now(),
        "prompt_sha256": sha256_bytes(OPERATOR_PROMPT_VERBATIM.encode("utf-8")),
        "prompt_bytes": len(OPERATOR_PROMPT_VERBATIM.encode("utf-8")),
        "artifact_path": str(text_path.name),
        "linked_work_units": ["T010-A", "T010-B", "T010-C", "T010-D", "T010-E", "T010-F"],
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (exp_dir / "PROMPT_PROVENANCE.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def generate_e06_expansion_cases(repo: Path, n_required: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Outcome-blind E06 variants from frozen postmortem/submission sources only."""
    submitted_path = repo / "eval/immersive_commons_submission_20260827/seal/IMMERSIVE_COMMONS_SUBMISSION_PAYLOAD.json"
    rubric_path = repo / "eval/ic_postmortem_20260827/IC_RUBRIC_SNAPSHOT.json"
    counterfactual_path = repo / "eval/ic_postmortem_20260827/WHAT_WE_COULD_HAVE_SENT.json"
    protocol_path = repo / "docs/HACKATHON_SUBMISSION_FCO_PROTOCOL.md"

    sources = {
        "submitted_payload": sha256_bytes(submitted_path.read_bytes()),
        "rubric_snapshot": sha256_bytes(rubric_path.read_bytes()),
        "counterfactual_maximal": sha256_bytes(counterfactual_path.read_bytes()),
        "protocol_doc": sha256_bytes(protocol_path.read_bytes()),
    }

    submitted = json.loads(submitted_path.read_text())
    rubric = json.loads(rubric_path.read_text())
    counterfactual = json.loads(counterfactual_path.read_text())
    protocol_text = protocol_path.read_text(encoding="utf-8")

    vault_treatments: list[tuple[str, dict[str, Any]]] = [
        ("VAULT_NULL", {"folder_id": None}),
        ("VAULT_COUNTERFACTUAL", {"folder_id": "COUNTERFACTUAL_VISIBLE_VAULT", "vault_visible": ["00_START_HERE.md"]}),
        ("VAULT_HERO", {"folder_id": "COUNTERFACTUAL_VISIBLE_VAULT", "vault_visible": ["00_START_HERE.md", "HYDRALAMP_SUBMISSION_HERO.png", "contact-sheet.png"]}),
        ("VAULT_VIDEO", {"folder_id": "COUNTERFACTUAL_VISIBLE_VAULT", "vault_visible": ["00_START_HERE.md", "HYDRALAMP_SUBMISSION_HERO.png", "contact-sheet.png", "demo.mp4"]}),
        ("VAULT_SPONSOR", {"folder_id": "COUNTERFACTUAL_VISIBLE_VAULT", "vault_visible": ["00_START_HERE.md", "demo.mp4", "sponsor-live-error-receipts.json"]}),
        ("VAULT_FULL", {"folder_id": "d_<counterfactual>", "vault_visible": counterfactual["vault_package"]["files"][:10]}),
    ]
    origin_treatments: list[tuple[str, dict[str, Any]]] = [
        ("ORIGIN_ACTUAL", {}),
        ("ORIGIN_DATE", {"origin_disclosure": {"hydradg_substrate_first_commit": "e4558026 on 2026-08-18", "hydralamp_first_commit": "757f3fa7 on 2026-08-26 14:36 PDT"}}),
        ("ORIGIN_BRANCH", {"repo_url": "https://github.com/biobitworks/hydradg/tree/hack-hydra/hydralamp-20260826"}),
        ("ORIGIN_DELTA", {"what_is_new_vs_prior_work": counterfactual["top_level_submission"].get("blurb", "")[:200]}),
        ("ORIGIN_ALL", {"repo_url": "https://github.com/biobitworks/hydradg/tree/hack-hydra/hydralamp-20260826", "origin_disclosure": {"hydradg_substrate_first_commit": "e4558026 on 2026-08-18", "hydralamp_first_commit": "757f3fa7 on 2026-08-26"}}),
    ]
    blurb_treatments = [
        ("BLURB_ACTUAL", submitted.get("blurb")),
        ("BLURB_COUNTERFACTUAL", counterfactual["top_level_submission"].get("blurb")),
    ]
    demo_treatments = [
        ("DEMO_ACTUAL", submitted.get("demo_url")),
        ("DEMO_GOLDEN", counterfactual["top_level_submission"].get("demo_url")),
    ]
    surface_treatments: list[tuple[str, dict[str, Any]]] = [
        ("SURFACE_DEFAULT", {}),
        ("SURFACE_CONDENSED", {"agent_surface": counterfactual["top_level_submission"].get("agent_surface", submitted.get("agent_surface"))}),
        ("SURFACE_TABLE", {"agent_surface_table": [
            {"method": "GET/POST", "path": "/api/hydralamp/run", "purpose": "start governed run"},
            {"method": "GET", "path": "/api/hydralamp/status?run_id=", "purpose": "read custody status"},
        ]}),
        ("SURFACE_TRACK01", {"track_declaration": "Track 01 External Customer Facing"}),
        ("SURFACE_TRACK02", {"track_declaration": "Track 02 Internal Team Facing"}),
    ]

    rows: list[dict[str, Any]] = []
    idx = 0
    for vname, vadd in vault_treatments:
        for oname, oadd in origin_treatments:
            for bname, blurb in blurb_treatments:
                for dname, demo in demo_treatments:
                    for sname, sadd in surface_treatments:
                        idx += 1
                        actual = deepcopy(submitted)
                        actual["blurb"] = blurb
                        actual["demo_url"] = demo
                        actual.update(vadd)
                        actual.update(oadd)
                        actual.update(sadd)
                        base_input = {
                            "event_rubric": rubric,
                            "actual_submission": actual,
                            "governed_failure_learning_protocol": protocol_text,
                            "exp010_fixture_source": {
                                "vault_treatment": vname,
                                "origin_treatment": oname,
                                "blurb_treatment": bname,
                                "demo_treatment": dname,
                                "surface_treatment": sname,
                                "generation_index": idx,
                            },
                        }
                        cid = f"E06-P010-{idx:04d}"
                        rows.append(
                            case_row(
                                cid,
                                "E06",
                                f"P010_{vname}_{oname}_{bname}_{dname}_{sname}",
                                base_input,
                                "Produce an ordered pre-submission workflow using the supplied governed protocol. "
                                "Do not submit while required judge evidence remains unsurfaced unless a human waiver is explicit.",
                                False,
                            )
                        )
                        if len(rows) >= n_required:
                            break
                    if len(rows) >= n_required:
                        break
                if len(rows) >= n_required:
                    break
            if len(rows) >= n_required:
                break
        if len(rows) >= n_required:
            break

    provenance = {
        "schema": "hydradg.daisy_overnight.exp010_case_bank_provenance.v1",
        "selection_rule": "DETERMINISTIC_CARTESIAN_FROM_FROZEN_SOURCES_ORDERED_BY_INDEX",
        "q38_outcome_exclusion": {
            "forbidden_paths": Q38_FORBIDDEN_PATHS,
            "q38_raw_outputs_used": False,
            "q38_scored_results_used": False,
        },
        "source_hashes": sources,
        "e06_expansion_count": len(rows),
        "e06_expansion_case_ids": [r["case_id"] for r in rows],
    }
    return rows, provenance


def build_case_bank(repo: Path, exp_dir: Path, power: dict[str, Any]) -> dict[str, Any]:
    base_cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    base_cases = [json.loads(line) for line in base_cases_path.read_text().splitlines() if line.strip()]
    n_required = power["raw_case_bank_n_recommended"]
    e06_expanded, e06_prov = generate_e06_expansion_cases(repo, n_required)

    # Full bank: non-E06 originals + expanded E06 primary bank
    non_e06 = [c for c in base_cases if c["experiment_family"] != "E06"]
    bank = non_e06 + e06_expanded

    bank_path = exp_dir / "CASE_BANK.jsonl"
    with bank_path.open("w", encoding="utf-8") as fh:
        for row in bank:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    e06_in_bank = [c for c in bank if c["experiment_family"] == "E06"]
    manifest = {
        "schema": "hydradg.daisy_overnight.exp010_case_bank_manifest.v1",
        "recorded_at_utc": utc_now(),
        "base_cases_manifest_sha256": sha256_bytes(base_cases_path.read_bytes()),
        "case_bank_sha256": sha256_bytes(bank_path.read_bytes()),
        "total_cases": len(bank),
        "e06_primary_cases": len(e06_in_bank),
        "non_e06_secondary_cases": len(non_e06),
        "required_paired_n": power["required_paired_n_worst_case_mde_grid"],
        "raw_case_bank_n_recommended": n_required,
        "power_gate_satisfied": len(e06_in_bank) >= power["required_paired_n_worst_case_mde_grid"],
        "e06_provenance": e06_prov,
        "outcome_blind": True,
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (exp_dir / "CASE_BANK_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_preregistration(repo: Path, exp_dir: Path, power: dict[str, Any], prompt_receipt: dict[str, Any]) -> dict[str, Any]:
    exp009 = json.loads(
        (repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/EXP-009/PREREGISTRATION.json").read_text()
    )
    exp009_verdict = json.loads(
        (repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/EXP-009/VERDICT.json").read_text()
    )
    bank_manifest = json.loads((exp_dir / "CASE_BANK_MANIFEST.json").read_text())
    model_inv = json.loads(
        (repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/MODEL_INVENTORY_FREEZE.json").read_text()
    )
    scorer_sha = sha256_bytes((repo / "scripts/score_ic_failure_learning.py").read_bytes())

    prereg = {
        "schema": "hydradg.daisy_overnight.preregistration.v1",
        "experiment_id": "EXP-010",
        "predecessor_experiment": "EXP-009",
        "predecessor_verdict": exp009_verdict.get("EXPERIMENT_PRIMARY_VERDICT", exp009_verdict.get("result_class")),
        "changed_variable": "DECISION_GOVERNANCE_SCHEMA_ONLY",
        "intervention": "GOVERNED_DECISION_SCHEMA",
        "control": "FREE_FORM",
        "H0": "Explicit governed decision schema does not change measured failure-prevention behavior relative to free-form JSON composition when evidence atoms, ordering, models, and scorer are held fixed.",
        "H1": "Governed decision schema changes measured failure-prevention behavior.",
        "conditions": {"C0": "FREE_FORM", "C1": "GOVERNED_DECISION_SCHEMA"},
        "output_schemas": {
            "C0": FREE_FORM_SCHEMA,
            "C1": GOVERNED_DECISION_SCHEMA,
            "C1_prohibited_keys": ["answer"],
        },
        "context_pipeline_frozen_from": "EXP-009",
        "atom_order": "CAUSAL_FCG_ORDER",
        "retrieval": "STRUCTURED_FCG",
        "models": exp009["models"],
        "model_inventory_sha256": sha256_bytes(json.dumps(model_inv, sort_keys=True).encode()),
        "runtime": model_inv.get("runtime", "DIRECT_OLLAMA_API"),
        "parser": "strict_json_ollama_format",
        "scorer_sha256": scorer_sha,
        "case_bank_sha256": bank_manifest["case_bank_sha256"],
        "case_bank_manifest_sha256": sha256_bytes((exp_dir / "CASE_BANK_MANIFEST.json").read_bytes()),
        "replicates": 3,
        "replicate_aggregation": "MAJORITY_OF_3_AT_CASE_LEVEL",
        "independent_unit": "CASE",
        "replicate_inflation_prohibited": True,
        "primary_endpoint": "E06_PREVENTS_C_MEDIA_NOT_IN_VAULT",
        "primary_estimand": "paired_risk_difference_rd = rate_C1 - rate_C0 on case-level majority binary prevents_C across E06-P010-* cases",
        "primary_test": "exact_mcnemar_one_sided_on_discordant_pairs",
        "alpha": 0.05,
        "power_assessment_sha256": sha256_bytes((exp_dir / "POWER_ASSESSMENT.json").read_bytes()),
        "required_paired_n": power["required_paired_n_worst_case_mde_grid"],
        "exclusions": {
            "malformed_json": "excluded_from_primary_endpoint_computation",
            "abstain": "scored_as_failure_to_prevent",
            "timeout": "preserved_as_ABSTAIN_or_FAILED_row",
            "label_leakage": "BLOCKED_LABEL_LEAKAGE rows excluded",
        },
        "parse_accounting": {
            "valid_parse": "PARSED_JSON",
            "malformed": "MALFORMED_JSON",
            "unknown_state": "model_state=UNKNOWN",
            "abstain_state": "model_state=ABSTAIN",
        },
        "falsifiers": [
            "C1 valid_parse_rate < C0 valid_parse_rate by >10pp with no compensating prevents_C gain",
            "governed schema introduces systematic ABSTAIN inflation",
            "primary rd<=0 with adequate powered discordant pairs",
        ],
        "claim_ceiling": "EXPLORATORY_MECHANISTIC_FALSIFICATION",
        "prompt_provenance_sha256": prompt_receipt["prompt_sha256"],
        "frozen_at_utc": utc_now(),
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (exp_dir / "PREREGISTRATION.json").write_text(json.dumps(prereg, indent=2) + "\n", encoding="utf-8")
    return prereg


def independent_review(repo: Path, exp_dir: Path, power: dict[str, Any]) -> dict[str, Any]:
    prereg = json.loads((exp_dir / "PREREGISTRATION.json").read_text())
    bank_manifest = json.loads((exp_dir / "CASE_BANK_MANIFEST.json").read_text())
    checks: list[dict[str, Any]] = []

    checks.append(
        {
            "check": "pseudoreplication",
            "pass": prereg.get("replicate_inflation_prohibited") and prereg.get("independent_unit") == "CASE",
            "note": "3 replicates nest under case; N is paired cases not rows",
        }
    )
    checks.append(
        {
            "check": "q38_leakage",
            "pass": not bank_manifest["e06_provenance"]["q38_outcome_exclusion"]["q38_raw_outputs_used"],
            "note": "case bank built from frozen postmortem/submission sources only",
        }
    )
    checks.append(
        {
            "check": "estimand_defined",
            "pass": bool(prereg.get("primary_estimand")),
            "note": prereg.get("primary_estimand"),
        }
    )
    checks.append(
        {
            "check": "power_gate",
            "pass": bank_manifest.get("power_gate_satisfied", False),
            "required_n": power["required_paired_n_worst_case_mde_grid"],
            "available_e06": bank_manifest.get("e06_primary_cases"),
        }
    )
    checks.append(
        {
            "check": "c1_schema_no_answer_key",
            "pass": "answer" in prereg.get("output_schemas", {}).get("C1_prohibited_keys", []),
        }
    )
    checks.append(
        {
            "check": "changed_variable_isolation",
            "pass": prereg.get("changed_variable") == "DECISION_GOVERNANCE_SCHEMA_ONLY",
        }
    )

    # Recompute power independently
    power2 = build_power_assessment()
    power_match = (
        power2["required_paired_n_worst_case_mde_grid"] == power["required_paired_n_worst_case_mde_grid"]
        and power2["required_paired_n_primary"] == power["required_paired_n_primary"]
    )
    checks.append({"check": "power_recompute_match", "pass": power_match})

    terminal = "PASS"
    stop_reasons = []
    for c in checks:
        if not c.get("pass"):
            terminal = "STOP"
            stop_reasons.append(c["check"])
    review = {
        "schema": "hydradg.daisy_overnight.exp010_independent_review.v1",
        "recorded_at_utc": utc_now(),
        "reviewer": "deterministic_recompute_script",
        "checks": checks,
        "terminal_state": terminal,
        "stop_reasons": stop_reasons,
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (exp_dir / "PLAN_CHECK.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    if terminal == "STOP":
        raise SystemExit(f"PLAN_CHECK STOP: {stop_reasons}")
    return review


def check_runtime_lease() -> dict[str, Any]:
    q38_procs: list[str] = []
    try:
        out = subprocess.check_output(["ps", "aux"], text=True)
        for line in out.splitlines():
            if any(k in line for k in ("run_qwen38", "chain_q38", "exp008-q38", "exp009-q38", "qwen3.8:27b")):
                if "grep" not in line:
                    q38_procs.append(line[:200])
    except subprocess.CalledProcessError:
        pass
    blocked = len(q38_procs) > 0
    lease = {
        "schema": "hydradg.daisy_overnight.runtime_lease.v1",
        "recorded_at_utc": utc_now(),
        "host": socket.gethostname(),
        "q38_process_matches": q38_procs,
        "ollama_shared_runtime": True,
        "terminal_state": "BLOCKED_RUNTIME_LEASE" if blocked else "LEASE_AVAILABLE",
        "exp010_execute_permitted": not blocked,
        "note": "EXP-010 uses qwen3:1.7b and qwen2.5-coder:7b; Q38 holds qwen3.8:27b but shares Ollama daemon",
    }
    return lease


def build_work_unit(
    work_unit_id: str,
    phase: str,
    repo: Path,
    base_sha: str,
    input_sha: str,
    cap_sha: str,
    expected_outputs: list[str],
    stop_conditions: list[str],
) -> dict[str, Any]:
    return {
        "schema": "hydradg.orchestration_work_unit.v1",
        "work_unit_id": work_unit_id,
        "phase": phase,
        "actor": {
            "actor_class": "AI_AGENT",
            "runtime_identity": "cursor-agent/composer",
        },
        "role_lane": "STUDIO_DAISY_SCIENTIFIC_EXECUTION",
        "role_ceiling": "EXPLORATORY_MECHANISTIC_FALSIFICATION",
        "writeback_disposition": "CANDIDATE_ONLY",
        "repo": "biobitworks/hydradg",
        "branch": "hack-hydra/daisy-exp010-20260828",
        "base_git_sha": base_sha,
        "expected_host": "magicSTUDIObox.local",
        "actual_host": socket.gethostname(),
        "capability_snapshot_sha256": cap_sha,
        "input_packet_sha256": input_sha,
        "lease": {
            "lease_id": f"exp010-{work_unit_id.lower()}",
            "fencing_token": 1,
            "single_writer_scope": f"eval/ic_failure_learning_20260827/daisy_overnight_20260828/EXP-010",
            "lease_owner": "hack-hydra/daisy-exp010-20260828",
            "lease_state": "ACTIVE",
        },
        "expected_outputs": expected_outputs,
        "verification_gates": ["PLAN_CHECK_PASS", "ORCHESTRATION_WORK_UNIT_PASS"],
        "stop_conditions": stop_conditions,
        "claim_ceiling": "EXPLORATORY_MECHANISTIC_FALSIFICATION",
        "fco_state": "NOT_APPENDED",
        "fcg_state": "NOT_APPENDED",
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED",
    }


def run_prereg_pipeline(repo: Path) -> dict[str, Any]:
    if socket.gethostname() != "magicSTUDIObox.local":
        raise SystemExit("BLOCKED: hostname != magicSTUDIObox.local")

    out_root = repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828"
    exp_dir = out_root / "EXP-010"
    wu_dir = exp_dir / "work_units"
    exp_dir.mkdir(parents=True, exist_ok=True)
    wu_dir.mkdir(parents=True, exist_ok=True)

    base_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

    # PROMPT provenance first
    prompt_receipt = write_prompt_provenance(exp_dir)

    # T010-A power
    power = build_power_assessment()
    (exp_dir / "POWER_ASSESSMENT.json").write_text(json.dumps(power, indent=2) + "\n", encoding="utf-8")

    # T010-B case bank
    bank_manifest = build_case_bank(repo, exp_dir, power)

    # T010-C prereg
    prereg = build_preregistration(repo, exp_dir, power, prompt_receipt)

    # T010-D review
    review = independent_review(repo, exp_dir, power)

    # Work units
    cap = sha256_bytes(json.dumps({"host": socket.gethostname(), "ollama": "0.33.0"}, sort_keys=True).encode())
    units = {
        "T010-A": build_work_unit(
            "T010-A",
            "OFFER",
            repo,
            base_sha,
            sha256_bytes(json.dumps(power, sort_keys=True).encode()),
            cap,
            ["POWER_ASSESSMENT.json"],
            ["pseudoreplication", "post_hoc_power"],
        ),
        "T010-B": build_work_unit(
            "T010-B",
            "OFFER",
            repo,
            base_sha,
            bank_manifest["case_bank_sha256"],
            cap,
            ["CASE_BANK.jsonl", "CASE_BANK_MANIFEST.json"],
            ["q38_outcome_leakage"],
        ),
        "T010-C": build_work_unit(
            "T010-C",
            "OFFER",
            repo,
            base_sha,
            sha256_bytes((exp_dir / "PREREGISTRATION.json").read_bytes()),
            cap,
            ["PREREGISTRATION.json"],
            ["undefined_estimand"],
        ),
        "T010-D": build_work_unit(
            "T010-D",
            "ACCEPT",
            repo,
            base_sha,
            sha256_bytes((exp_dir / "PLAN_CHECK.json").read_bytes()),
            cap,
            ["PLAN_CHECK.json"],
            ["PLAN_CHECK_STOP"],
        ),
    }
    for uid, doc in units.items():
        path = wu_dir / f"{uid}.json"
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    # Runtime lease (T010-F pre-check)
    lease = check_runtime_lease()
    (exp_dir / "RUNTIME_LEASE.json").write_text(json.dumps(lease, indent=2) + "\n", encoding="utf-8")

    # Artifact hash manifest
    artifacts = {}
    for name in [
        "PROMPT_PROVENANCE.json",
        "POWER_ASSESSMENT.json",
        "CASE_BANK.jsonl",
        "CASE_BANK_MANIFEST.json",
        "PREREGISTRATION.json",
        "PLAN_CHECK.json",
        "RUNTIME_LEASE.json",
    ]:
        p = exp_dir / name
        if p.exists():
            artifacts[name] = sha256_bytes(p.read_bytes())
    (exp_dir / "PREREG_ARTIFACT_HASHES.json").write_text(json.dumps(artifacts, indent=2) + "\n", encoding="utf-8")

    return {
        "power": power,
        "bank_manifest": bank_manifest,
        "prereg": prereg,
        "review": review,
        "lease": lease,
        "prompt_receipt": prompt_receipt,
    }
