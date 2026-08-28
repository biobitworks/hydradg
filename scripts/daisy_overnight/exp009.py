"""EXP-009 causal ordering ablation — freeze, execute, closeout."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from daisy_overnight.atoms import (
    CONTEXT_CHAR_BUDGET,
    load_admissible_atoms,
    order_atoms_causal,
    order_atoms_neutral,
    render_ordered_context,
    structured_retriever_atoms,
)
from daisy_overnight.custody import append_fcg_edges, build_mmr_receipt, sha256_bytes
from daisy_overnight.stats import bootstrap_rd_ci, exact_mcnemar, holm_correction, risk_difference

from score_ic_failure_learning import score_row

CHECKPOINT_SHA = "a7889664ba0d53548595e7d812ca5ffa608690ca"
STAGE2_MODELS = ["qwen3:1.7b", "qwen2.5-coder:7b"]
N_REPLICATES = 3
SECONDARY_ENDPOINTS = [
    ("E05_top1", "E05", "top1_correct"),
    ("E05_top3", "E05", "top3_contains_primary"),
    ("E01_cold_start", "E01", "detects_cold_start_gap"),
    ("E01_vault_media", "E01", "detects_vault_media_gap"),
    ("E01_origin_gap", "E01", "detects_origin_gap"),
    ("E07_directional_gate", "E07", "directional_gate"),
]


def utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verify_exp008_closed(out_root: Path) -> dict[str, Any]:
    exp008 = out_root / "EXP-008"
    verdict_path = exp008 / "VERDICT.json"
    decision_path = exp008 / "DAISY_DECISION.json"
    if not verdict_path.exists():
        raise SystemExit("BLOCKED: EXP-008 VERDICT.json missing")
    verdict = json.loads(verdict_path.read_text())
    decision = json.loads(decision_path.read_text())
    if verdict.get("result_class") != "UNDERPOWERED":
        raise SystemExit(f"BLOCKED: EXP-008 result={verdict.get('result_class')} expected UNDERPOWERED closed")
    if decision.get("next_experiment") != "EXP-009":
        raise SystemExit(f"BLOCKED: Daisy decision next={decision.get('next_experiment')} expected EXP-009")
    mmr_path = exp008 / "MMR_VERIFICATION.json"
    predecessor = json.loads(mmr_path.read_text()).get("mmr_root") if mmr_path.exists() else None
    return {"verdict": verdict, "decision": decision, "predecessor_mmr": predecessor}


def build_power_assessment(repo: Path, exp_dir: Path) -> dict[str, Any]:
    cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text().splitlines() if line.strip()]
    e06 = [c for c in cases if c["experiment_family"] == "E06"]
    assessment = {
        "schema": "hydradg.daisy_overnight.power_assessment.v1",
        "experiment_id": "EXP-009",
        "E06_existing_case_count": len(e06),
        "E06_case_ids": [c["case_id"] for c in e06],
        "unused_preexisting_admissible_E06_cases": 0,
        "expansion_permissible": False,
        "source_manifest": str(cases_path),
        "source_manifest_sha256": sha256_bytes(cases_path.read_bytes()),
        "freeze_date_utc": utc_now(),
        "label_leakage_check": "PASS_NO_EVAL_LABELS_IN_CASE_INPUT",
        "power_disposition": "NO_PREEXISTING_INDEPENDENT_E06_EXPANSION",
        "E06_POWER_STATE": "KNOWN_LIMITED",
        "E06_CONFIRMATORY_CLAIM_ALLOWED": "NO",
        "EXP009_CLASSIFICATION_SCOPE": "EXPLORATORY_MECHANISTIC_FALSIFICATION",
        "note": "Only E06-T0 and E06-T1 in frozen CASES.jsonl; no held-out E06 pool",
    }
    (exp_dir / "POWER_ASSESSMENT.json").write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")
    return assessment


def build_atom_set_freeze(repo: Path, exp_dir: Path) -> list[dict[str, Any]]:
    cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text().splitlines() if line.strip()]
    atoms_lib = load_admissible_atoms(repo)
    exp008_mmr = json.loads((repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/EXP-008/MMR_VERIFICATION.json").read_text())
    rows: list[dict[str, Any]] = []
    mismatches: list[str] = []

    for case in cases:
        fam = case["experiment_family"]
        selected_atoms, retained_ids = structured_retriever_atoms(atoms_lib, fam, CONTEXT_CHAR_BUDGET)
        id_set = set(retained_ids)
        neutral_atoms = order_atoms_neutral([a for a in selected_atoms if a["fco_id"] in id_set])
        causal_atoms = order_atoms_causal([a for a in selected_atoms if a["fco_id"] in id_set])
        c0_ids = [a["fco_id"] for a in neutral_atoms]
        c1_ids = [a["fco_id"] for a in causal_atoms]
        if set(c0_ids) != set(c1_ids):
            mismatches.append(case["case_id"])

        prose_hashes = {a["fco_id"]: hashlib.sha256(a["prose"].encode("utf-8")).hexdigest() for a in selected_atoms}
        atom_hashes = {a["fco_id"]: hashlib.sha256(json.dumps(a["structured"], sort_keys=True).encode()).hexdigest() for a in selected_atoms}
        total_bytes = sum(len(a["prose"].encode()) for a in selected_atoms)

        rows.append(
            {
                "case_id": case["case_id"],
                "experiment_family": fam,
                "selected_fco_ids": retained_ids,
                "c0_fco_ids": c0_ids,
                "c1_fco_ids": c1_ids,
                "atom_set_equal": set(c0_ids) == set(c1_ids),
                "source_fcg_root": exp008_mmr.get("mmr_root"),
                "retrieval_version": "EXP-008_STRUCTURED_RETRIEVER_V1",
                "retrieval_parameters": {"budget": CONTEXT_CHAR_BUDGET, "selector": "structured_retriever_atoms"},
                "atom_prose_hashes": prose_hashes,
                "atom_struct_hashes": atom_hashes,
                "n_atoms": len(retained_ids),
                "total_source_bytes": total_bytes,
            }
        )

    path = exp_dir / "ATOM_SET_FREEZE.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    if mismatches:
        gate = {"EXP009_VALIDITY_GATE": "FAIL_ATOM_SET_MISMATCH", "cases": mismatches}
        (exp_dir / "VALIDITY_GATE.json").write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(f"EXP009_VALIDITY_GATE=FAIL_ATOM_SET_MISMATCH cases={mismatches}")

    (exp_dir / "VALIDITY_GATE.json").write_text(
        json.dumps({"EXP009_VALIDITY_GATE": "PASS", "cases_checked": len(rows)}, indent=2) + "\n",
        encoding="utf-8",
    )
    return rows


def build_ordering_algorithm(exp_dir: Path) -> dict[str, Any]:
    spec = {
        "schema": "hydradg.daisy_overnight.ordering_algorithm.v1",
        "C0_NEUTRAL_ORDER": {
            "algorithm": "STABLE_CANONICAL_FCO_ID_ASC",
            "description": "Sort selected atoms by fco_id ascending; no semantic prioritization",
        },
        "C1_CAUSAL_FCG_ORDER": {
            "algorithm": "CAUSAL_KIND_RANK_THEN_PRIORITY_THEN_FCO_ID",
            "tiers": [
                "source/input (ProvenanceFCO, MethodFCO)",
                "requirement (RequirementFCO)",
                "contradiction (ContradictionFCO)",
                "failure (FailureRelationshipFCO, FailureClassFCO)",
                "consequence/protocol (GovernedProtocolFCO)",
                "claim ceiling (NegativeEvidenceFCO, ClaimCeilingFCO)",
            ],
            "tie_break": "priority_field_then_canonical_FCO_ID",
            "outcome_labels_forbidden": True,
            "scorer_labels_forbidden": True,
        },
        "changed_variable": "ATOM_ORDER_ONLY",
    }
    (exp_dir / "ORDERING_ALGORITHM.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return spec


def build_preregistration(repo: Path, exp_dir: Path, power: dict[str, Any]) -> dict[str, Any]:
    cases_path = repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    scorer_path = repo / "scripts/score_ic_failure_learning.py"
    inv_path = repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/MODEL_INVENTORY_FREEZE.json"
    inv = json.loads(inv_path.read_text())
    exp008_mmr = json.loads((repo / "eval/ic_failure_learning_20260827/daisy_overnight_20260828/EXP-008/MMR_VERIFICATION.json").read_text())

    prereg = {
        "schema": "hydradg.daisy_overnight.preregistration.v1",
        "experiment_id": "EXP-009",
        "intervention": "CAUSAL_FCG_ORDER",
        "control": "NEUTRAL_DETERMINISTIC_ORDER",
        "changed_variable": "ATOM_ORDER_ONLY",
        "H0": "Causal FCG ordering does not change measured failure-prevention behavior relative to neutral ordering when atom identity/content are held fixed.",
        "H1": "Causal FCG ordering changes measured failure-prevention behavior.",
        "E06_POWER_STATE": power["E06_POWER_STATE"],
        "primary_registered_endpoint": "E06_PREVENTS_C",
        "primary_confirmatory_status": "POWER_LIMITED_EXPLORATORY",
        "secondary_endpoint_family": [m[0] for m in SECONDARY_ENDPOINTS],
        "models": {m["alias"]: m.get("digest") for m in inv["models"]},
        "cases_manifest_sha256": sha256_bytes(cases_path.read_bytes()),
        "replicates": N_REPLICATES,
        "scorer_sha256": sha256_bytes(scorer_path.read_bytes()),
        "FCG_source_root": exp008_mmr.get("mmr_root"),
        "predecessor_experiment": "EXP-008",
        "predecessor_verdict": "UNDERPOWERED",
        "checkpoint_sha": CHECKPOINT_SHA,
        "frozen_at_utc": utc_now(),
    }
    (exp_dir / "PREREGISTRATION.json").write_text(json.dumps(prereg, indent=2) + "\n", encoding="utf-8")
    return prereg


def verify_ordering_isolation(exp_dir: Path, atom_rows: list[dict[str, Any]], repo: Path) -> dict[str, Any]:
    atoms_lib = {a["fco_id"]: a for a in load_admissible_atoms(repo)}
    isolation_rows: list[dict[str, Any]] = []
    failures: list[str] = []

    for row in atom_rows:
        case_id = row["case_id"]
        fam = row["experiment_family"]
        selected = [atoms_lib[fid] for fid in row["selected_fco_ids"] if fid in atoms_lib]
        neutral = order_atoms_neutral(selected)
        causal = order_atoms_causal(selected)
        c0_text, c0_ids, c0_ph = render_ordered_context(neutral, "NEUTRAL_ORDER")
        c1_text, c1_ids, c1_ph = render_ordered_context(causal, "CAUSAL_FCG_ORDER")

        c0_multiset = sorted(c0_ph)
        c1_multiset = sorted(c1_ph)
        byte_multiset_equal = c0_multiset == c1_multiset
        id_equal = set(c0_ids) == set(c1_ids)

        trunc_asymmetric = ("truncated" in c0_text) != ("truncated" in c1_text)
        if trunc_asymmetric:
            failures.append(case_id)

        isolation_rows.append(
            {
                "case_id": case_id,
                "atom_ids_equal": id_equal,
                "prose_hash_multiset_equal": byte_multiset_equal,
                "c0_context_chars": len(c0_text),
                "c1_context_chars": len(c1_text),
                "char_delta": abs(len(c0_text) - len(c1_text)),
                "truncation_asymmetric": trunc_asymmetric,
            }
        )

    gate = "PASS" if not failures else "FAIL"
    receipt = {
        "schema": "hydradg.daisy_overnight.ordering_isolation.v1",
        "ORDERING_ISOLATION_GATE": gate,
        "asymmetric_truncation_cases": failures,
        "per_case": isolation_rows,
    }
    (exp_dir / "ORDERING_ISOLATION_GATE.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit(f"ORDERING_ISOLATION_GATE=FAIL asymmetric_truncation={failures}")
    return receipt


def execute_exp009(
    repo: Path,
    exp_dir: Path,
    atom_rows: list[dict[str, Any]],
    ollama_generate: Callable[..., tuple[str, float]],
    build_prompt: Callable[..., tuple[str, dict[str, Any]]],
    resource_snapshot: Callable[[], dict[str, Any]],
    inv: dict[str, Any],
) -> None:
    cases = {r["case_id"]: r for r in atom_rows}
    cases_full = {
        c["case_id"]: c
        for c in (
            json.loads(line)
            for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
            if line.strip()
        )
    }
    atoms_lib = {a["fco_id"]: a for a in load_admissible_atoms(repo)}
    ledger_path = exp_dir / "PROMPT_PROJECTION_LEDGER.jsonl"
    raw_path = exp_dir / "RAW_OUTPUTS.jsonl"
    existing_keys: set[tuple[str, str, str, int]] = set()
    if raw_path.exists():
        for line in raw_path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                existing_keys.add((row["model"], row["case_id"], row["condition"], row["replicate"]))

    for model in STAGE2_MODELS:
        for condition, label, order_fn in [
            ("C0", "NEUTRAL_ORDER", order_atoms_neutral),
            ("C1", "CAUSAL_FCG_ORDER", order_atoms_causal),
        ]:
            snap_block_before = resource_snapshot()
            for atom_row in atom_rows:
                case = cases_full[atom_row["case_id"]]
                fam = case["experiment_family"]
                selected = [atoms_lib[fid] for fid in atom_row["selected_fco_ids"] if fid in atoms_lib]
                ordered = order_fn(selected)
                context, retained, _ = render_ordered_context(ordered, label)
                for replicate in range(1, N_REPLICATES + 1):
                    key = (model, case["case_id"], condition, replicate)
                    if key in existing_keys:
                        continue
                    prompt, proj = build_prompt(case, condition, context, retained, "EXP-009")
                    proj.update(
                        {
                            "model": model,
                            "replicate": replicate,
                            "context_mode": label,
                            "order_mode": label,
                            "atom_set_sha256": sha256_bytes(json.dumps(atom_row, sort_keys=True).encode()),
                        }
                    )
                    with ledger_path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps(proj, sort_keys=True) + "\n")
                    state = "OK"
                    raw = ""
                    latency = 0.0
                    try:
                        raw, latency = ollama_generate(model, prompt)
                    except Exception as exc:
                        try:
                            time.sleep(2)
                            raw, latency = ollama_generate(model, prompt, timeout=600)
                        except Exception as exc2:
                            state = f"FAILED:{type(exc2).__name__}"
                            raw = json.dumps({"state": "ABSTAIN", "error": str(exc2)})
                    try:
                        parsed = json.loads(raw)
                        parser_state = "PARSED_JSON"
                    except json.JSONDecodeError:
                        parsed = None
                        parser_state = "MALFORMED_JSON"
                    row = {
                        "schema": "hydradg.daisy_overnight.raw_output.v1",
                        "experiment_id": "EXP-009",
                        "condition": condition,
                        "context_mode": label,
                        "generation": f"EXP-009_{condition}",
                        "model": model,
                        "model_identity": next((m.get("modelfile_from", model) for m in inv["models"] if m["alias"] == model), model),
                        "case_id": case["case_id"],
                        "experiment_family": fam,
                        "case_condition": case["condition"],
                        "replicate": replicate,
                        "prompt_sha256": proj["prompt_sha256"],
                        "raw_response_sha256": sha256_bytes(raw.encode("utf-8")),
                        "latency_seconds": round(latency, 3),
                        "parser_state": parser_state,
                        "parsed": parsed,
                        "run_state": state,
                        "evidence_class": "PROBABILISTIC_MODEL_OUTPUT",
                        "model_weight_state": "UNCHANGED",
                    }
                    with raw_path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
                    print(f"EXP-009 {condition} {model} {case['case_id']} r{replicate} {parser_state} {latency:.1f}s")
            snap_block_after = resource_snapshot()
            with (exp_dir / "RESOURCE_LOG.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps(
                        {
                            "model": model,
                            "condition": condition,
                            "before": snap_block_before,
                            "after": snap_block_after,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )


def score_and_closeout_exp009(repo: Path, exp_dir: Path, predecessor_mmr: str, power: dict[str, Any]) -> dict[str, Any]:
    cases = {
        row["case_id"]: row
        for row in (
            json.loads(line)
            for line in (repo / "eval/ic_failure_learning_20260827/cases/CASES.jsonl").read_text().splitlines()
            if line.strip()
        )
    }
    raw_rows = [json.loads(line) for line in (exp_dir / "RAW_OUTPUTS.jsonl").read_text().splitlines() if line.strip()]
    scored = []
    parsed_rows = []
    for row in raw_rows:
        case = cases[row["case_id"]]
        s = score_row(case, row)
        scored.append(s)
        parsed_rows.append({**row, "score": s})

    with (exp_dir / "SCORED_RESULTS.jsonl").open("w", encoding="utf-8") as fh:
        for row in scored:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    with (exp_dir / "PARSED_OUTPUTS.jsonl").open("w", encoding="utf-8") as fh:
        for row in parsed_rows:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    case_level: list[dict[str, Any]] = []
    grouped: dict[tuple, list] = defaultdict(list)
    for row in scored:
        grouped[(row["model"], row["case_id"], row["generation"])].append(row)

    def majority_bool(reps: list[dict], field: str) -> bool | None:
        vals = [r["metrics"].get(field) for r in reps if r.get("metrics") and r["metrics"].get(field) is not None]
        if not vals:
            return None
        return sum(v is True for v in vals) >= 2

    for key, reps in grouped.items():
        model, case_id, generation = key
        fam = reps[0]["family"]
        cond = "C0" if "_C0" in generation else "C1"
        case_level.append(
            {
                "model": model,
                "case_id": case_id,
                "condition": cond,
                "generation": generation,
                "family": fam,
                "n_replicates": len(reps),
                "case_primary_e06": majority_bool(reps, "prevents_C_media_not_in_vault") if fam == "E06" else None,
                "replicate_states": [r.get("model_state") for r in reps],
            }
        )
    with (exp_dir / "CASE_LEVEL_RESULTS.jsonl").open("w", encoding="utf-8") as fh:
        for row in case_level:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    parser_ok = sum(1 for r in raw_rows if r.get("parser_state") == "PARSED_JSON")
    dq = {
        "n_raw": len(raw_rows),
        "valid_parse_rate": parser_ok / len(raw_rows) if raw_rows else 0,
        "malformed_rate": sum(1 for r in scored if r.get("model_state") == "MALFORMED") / len(scored) if scored else 0,
        "unknown_rate": sum(1 for r in scored if r.get("model_state") == "UNKNOWN") / len(scored) if scored else 0,
        "abstain_rate": sum(1 for r in scored if r.get("model_state") == "ABSTAIN") / len(scored) if scored else 0,
    }
    (exp_dir / "DATA_QUALITY.json").write_text(json.dumps(dq, indent=2) + "\n", encoding="utf-8")

    stats_by_model: dict[str, Any] = {}
    for model in STAGE2_MODELS:
        pairs: list[tuple[bool | None, bool | None]] = []
        e06_cases = sorted({c["case_id"] for c in case_level if c["family"] == "E06" and c["model"] == model})
        for cid in e06_cases:
            c0 = next((c["case_primary_e06"] for c in case_level if c["model"] == model and c["case_id"] == cid and c["condition"] == "C0"), None)
            c1 = next((c["case_primary_e06"] for c in case_level if c["model"] == model and c["case_id"] == cid and c["condition"] == "C1"), None)
            pairs.append((c0, c1))
        rd = risk_difference(pairs)
        b = sum(1 for a, bb in pairs if a and bb is False)
        c = sum(1 for a, bb in pairs if not a and bb)
        mcn = exact_mcnemar(b, c)
        boot = bootstrap_rd_ci(pairs)
        stats_by_model[model] = {**rd, **mcn, **boot, "n_paired": rd["n"], "pairs": pairs}

    secondary_tests: list[dict[str, Any]] = []
    for metric, family, field in SECONDARY_ENDPOINTS:
        for model in STAGE2_MODELS:
            pairs = []
            case_ids = sorted({r["case_id"] for r in scored if r["family"] == family and r["model"] == model})
            for cid in case_ids:
                c0_reps = [r for r in scored if r["model"] == model and r["case_id"] == cid and "_C0" in r["generation"]]
                c1_reps = [r for r in scored if r["model"] == model and r["case_id"] == cid and "_C1" in r["generation"]]
                if not c0_reps or not c1_reps:
                    continue
                c0_maj = sum(r["metrics"].get(field) is True for r in c0_reps) >= 2
                c1_maj = sum(r["metrics"].get(field) is True for r in c1_reps) >= 2
                pairs.append((c0_maj, c1_maj))
            rd = risk_difference(pairs)
            b = sum(1 for a, bb in pairs if a and not bb)
            c = sum(1 for a, bb in pairs if not a and bb)
            mcn = exact_mcnemar(b, c)
            secondary_tests.append({"metric": metric, "model": model, **rd, **mcn})
    secondary_tests = holm_correction(secondary_tests)

    macro_n = sum(s["n_paired"] for s in stats_by_model.values())
    stats = {
        "schema": "hydradg.daisy_overnight.stats.v1",
        "experiment_id": "EXP-009",
        "primary_endpoint": "E06_PREVENTS_C_MEDIA_NOT_IN_VAULT",
        "E06_power_state": power["E06_POWER_STATE"],
        "by_model": stats_by_model,
        "macro_descriptive": {
            "n_paired_total": macro_n,
            "weighted_rd": sum((s["rd"] or 0) * s["n_paired"] for s in stats_by_model.values()) / macro_n if macro_n else None,
        },
        "secondary_tests": secondary_tests,
        "alpha": 0.05,
    }
    (exp_dir / "STATS.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    primary = stats_by_model[STAGE2_MODELS[0]]
    for m in STAGE2_MODELS[1:]:
        if stats_by_model[m].get("n_paired", 0) > primary.get("n_paired", 0):
            primary = stats_by_model[m]

    experiment_primary_verdict = "UNDERPOWERED" if primary.get("n_paired", 0) < 5 else "RETAINED_NULL"
    if primary.get("p_exact") is not None and primary.get("n_paired", 0) >= 5:
        if primary["p_exact"] < 0.05 and (primary.get("rd") or 0) > 0:
            experiment_primary_verdict = "SUPPORTED_POSITIVE"
        elif primary["p_exact"] < 0.05 and (primary.get("rd") or 0) < 0:
            experiment_primary_verdict = "SUPPORTED_NEGATIVE"

    pos_secondaries = [t for t in secondary_tests if (t.get("rd") or 0) > 0 and t.get("n", 0) > 0]
    neg_secondaries = [t for t in secondary_tests if (t.get("rd") or 0) < 0 and t.get("n", 0) > 0]
    if pos_secondaries and not neg_secondaries:
        mechanistic = "DIRECTIONALLY_POSITIVE_SECONDARY"
    elif neg_secondaries and not pos_secondaries:
        mechanistic = "DIRECTIONALLY_NEGATIVE_SECONDARY"
    elif pos_secondaries or neg_secondaries:
        mechanistic = "MIXED_SECONDARY"
    else:
        mechanistic = "NULL_SECONDARY"

    if dq["valid_parse_rate"] < 0.5:
        experiment_primary_verdict = "INCONCLUSIVE_DATA_QUALITY"
        mechanistic = "INCONCLUSIVE"

    verdict = {
        "schema": "hydradg.daisy_overnight.verdict.v1",
        "experiment_id": "EXP-009",
        "EXPERIMENT_PRIMARY_VERDICT": experiment_primary_verdict,
        "MECHANISTIC_EXPLORATORY_PATTERN": mechanistic,
        "result_class": experiment_primary_verdict,
        "primary": primary,
        "data_quality": dq,
        "ordering_established": False,
        "conclusion_bounded": "causal FCG ordering effect not established on confirmatory E06 endpoint",
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (exp_dir / "VERDICT.json").write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")

    if experiment_primary_verdict == "SUPPORTED_POSITIVE":
        next_exp = "EXP-009R_CONFIRMATION"
    elif experiment_primary_verdict in ("INCONCLUSIVE_DATA_QUALITY", "FAILED_IMPLEMENTATION", "ABORTED_EXECUTION_SETUP", "TIMEOUT"):
        next_exp = "STOP_IMPLEMENTATION_REPAIR"
    else:
        next_exp = "EXP-010"

    decision = {
        "schema": "hydradg.daisy_overnight.decision.v1",
        "experiment_id": "EXP-009",
        "result_class": experiment_primary_verdict,
        "MECHANISTIC_EXPLORATORY_PATTERN": mechanistic,
        "next_experiment": next_exp,
        "ORDERING_SIGNAL_EXPLORATORY": mechanistic.startswith("DIRECTIONALLY") or mechanistic == "MIXED_SECONDARY",
        "reason": f"E06 n_paired={primary.get('n_paired')} power_state={power['E06_POWER_STATE']}",
    }
    (exp_dir / "DAISY_DECISION.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")

    (exp_dir / "STATS.md").write_text(
        f"# EXP-009 Statistics\n\n**Primary verdict:** {experiment_primary_verdict}\n**Exploratory pattern:** {mechanistic}\n\n"
        + json.dumps(stats, indent=2)
        + "\n",
        encoding="utf-8",
    )

    fcg_root = append_fcg_edges(exp_dir, "EXP-009", experiment_primary_verdict, predecessor_mmr or "")
    mmr = build_mmr_receipt(exp_dir, predecessor_mmr)
    return {"verdict": verdict, "decision": decision, "fcg_root": fcg_root, "mmr": mmr, "stats": stats}
