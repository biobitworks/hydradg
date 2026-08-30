#!/usr/bin/env python3
"""Deterministically score HydraLamp × IC failure-learning model outputs.

Input results are JSONL rows with at minimum:
  model, model_identity, case_id, replicate, raw_response_sha256, parsed
where parsed is the strict JSON object returned by the Cloudflare OS Agent Skill.

This scorer never calls a model and never fabricates missing cells.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

GROUND_TRUTH_EARLIEST = "C"
GROUND_TRUTH_TOP3 = ["C", "D", "B"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def contains_any(text: str, needles: list[str]) -> bool:
    return any(needle.lower() in text for needle in needles)


def score_e01(parsed: dict[str, Any]) -> dict[str, Any]:
    text = norm(parsed)
    return {
        "detects_vault_media_gap": contains_any(text, ["folder_id", "vault", "video", "media", "screenshot"]),
        "detects_origin_gap": contains_any(text, ["origin", "prior work", "preexisting", "pre-existing", "hack hydra", "reuse", "branch"]),
        "detects_cold_start_gap": contains_any(text, ["cold-start", "cold start", "start_here", "start here", "discover", "well-known", "credential"]),
        "invented_capability_count": len(parsed.get("invented_capabilities") or []),
    }


def score_e02(condition: str, parsed: dict[str, Any]) -> dict[str, Any]:
    classification = parsed.get("origin_classification", "")
    expected_direction = {
        "T0_ACTUAL": {"PREEXISTING_PROJECT", "AMBIGUOUS"},
        "T4_ALL_ORIGIN_FIXES": {"DISTINCT_HACKATHON_DELTA"},
    }.get(condition)
    return {
        "origin_classification": classification,
        "directional_gate": None if expected_direction is None else classification in expected_direction,
        "invented_capability_count": len(parsed.get("invented_capabilities") or []),
    }


def score_e03(condition: str, parsed: dict[str, Any]) -> dict[str, Any]:
    missing = [norm(x) for x in (parsed.get("missing_evidence_classes") or [])]
    joined = " | ".join(missing)
    return {
        "reported_missing_count": len(missing),
        "still_reports_video_missing": contains_any(joined, ["video", "demo"]),
        "still_reports_origin_missing": contains_any(joined, ["origin", "prior work", "provenance"]),
        "still_reports_vault_missing": contains_any(joined, ["vault", "folder", "attachment"]),
        "condition": condition,
    }


def score_e04(condition: str, parsed: dict[str, Any]) -> dict[str, Any]:
    actions = [norm(x) for x in (parsed.get("first_three_machine_actions") or [])]
    joined = " | ".join(actions)
    discovery = contains_any(joined, ["/.well-known/ai-agent.json", "well-known", "discover"])
    auth = contains_any(joined, ["credential", "authenticate", "auth"])
    run = contains_any(joined, ["/api/hydralamp/run", "post /api/hydralamp/run", "start governed run"])
    status = contains_any(joined, ["/api/hydralamp/status", "verify receipt", "status?run_id"])
    return {
        "action_count": len(actions),
        "discovery_action_present": discovery,
        "authentication_action_present": auth,
        "consequential_run_action_present": run,
        "receipt_or_status_action_present": status,
        "invented_capability_count": len(parsed.get("invented_capabilities") or []),
        "legibility_components_present": sum([discovery, auth, run, status]),
        "condition": condition,
    }


def score_e07(condition: str, parsed: dict[str, Any]) -> dict[str, Any]:
    classification = parsed.get("origin_classification", "")
    expected_direction = {
        "T0_ACTUAL_REPO_ACTUAL_README": {"PREEXISTING_PROJECT", "AMBIGUOUS"},
        "T1_ACTUAL_REPO_BANNER_README": {"DISTINCT_HACKATHON_DELTA", "AMBIGUOUS"},
        "T3_BRANCH_REPO_EXPLICIT_SHAS": {"DISTINCT_HACKATHON_DELTA"},
        "T4_STANDALONE_HYDRALAMP_REPO": {"DISTINCT_HACKATHON_DELTA", "AMBIGUOUS"},
    }.get(condition)
    weak_dims = parsed.get("predicted_weak_dimensions") or []
    return {
        "origin_classification": classification,
        "directional_gate": None if expected_direction is None else classification in expected_direction,
        "confidence_0_1": parsed.get("confidence_0_1"),
        "rubric_concern_count": len(weak_dims),
        "invented_capability_count": len(parsed.get("invented_capabilities") or []),
        "condition": condition,
    }


def score_e05(parsed: dict[str, Any]) -> dict[str, Any]:
    top1 = str(parsed.get("earliest_divergence_candidate", "UNKNOWN")).upper()
    ranking = [str(x).upper() for x in (parsed.get("causal_ranking") or [])]
    return {
        "top1": top1,
        "top1_correct": top1 == GROUND_TRUTH_EARLIEST,
        "top3_contains_primary": GROUND_TRUTH_EARLIEST in ranking[:3],
        "ordered_cdb_exact": ranking[:3] == GROUND_TRUTH_TOP3,
        "ranking": ranking,
    }


def protocol_gate(workflow: list[str]) -> dict[str, Any]:
    steps = [norm(x) for x in workflow]
    joined = "\n".join(steps)

    required = {
        "rubric_frozen": ["rubric", "ic_hack_get"],
        "track_declared": ["track"],
        "evidence_requirement_graph": ["evidence requirement", "evidence graph"],
        "origin_comparison": ["origin", "prior work", "what is new"],
        "media_capture": ["media", "video", "screenshot", "contact sheet"],
        "red_team_90s": ["90-second", "90 second", "red team"],
        "vault_populated": ["vault", "folder_id", "folder id"],
        "start_here": ["00_start_here", "start_here", "start here"],
        "branch_origin_disclosure": ["branch", "origin date", "repo url"],
        "video_contact_sheet": ["video", "contact sheet"],
        "payload_hash": ["payload sha", "sha-256", "sha256"],
    }
    present = {key: contains_any(joined, needles) for key, needles in required.items()}

    submit_index = next((i for i, step in enumerate(steps) if contains_any(step, ["submit", "ic_hack_submit"])), None)
    vault_index = next((i for i, step in enumerate(steps) if contains_any(step, ["vault", "folder_id", "folder id"])), None)
    media_index = next((i for i, step in enumerate(steps) if contains_any(step, ["media", "video", "contact sheet", "screenshot"])), None)
    origin_index = next((i for i, step in enumerate(steps) if contains_any(step, ["origin", "prior work", "what is new"])), None)
    redteam_index = next((i for i, step in enumerate(steps) if contains_any(step, ["90-second", "90 second", "red team"])), None)

    def before_submit(index: int | None) -> bool:
        return submit_index is not None and index is not None and index < submit_index

    prevents_c = before_submit(vault_index) and before_submit(media_index)
    return {
        "required_gates_present": present,
        "required_gate_count": sum(present.values()),
        "required_gate_total": len(required),
        "submit_step_present": submit_index is not None,
        "vault_before_submit": before_submit(vault_index),
        "media_before_submit": before_submit(media_index),
        "origin_before_submit": before_submit(origin_index),
        "red_team_before_submit": before_submit(redteam_index),
        "prevents_C_media_not_in_vault": prevents_c,
    }


def score_row(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    parsed = result.get("parsed")
    if not isinstance(parsed, dict):
        return {
            "case_id": case["case_id"],
            "family": case["experiment_family"],
            "condition": case["condition"],
            "generation": result.get("generation", "UNKNOWN"),
            "model": result.get("model"),
            "replicate": result.get("replicate"),
            "state": "MALFORMED_RESULT_ENVELOPE",
            "model_state": "MALFORMED",
            "metrics": {},
        }

    family = case["experiment_family"]
    if family == "E01":
        metrics = score_e01(parsed)
    elif family == "E02":
        metrics = score_e02(case["condition"], parsed)
    elif family == "E03":
        metrics = score_e03(case["condition"], parsed)
    elif family == "E04":
        metrics = score_e04(case["condition"], parsed)
    elif family == "E05":
        metrics = score_e05(parsed)
    elif family == "E06":
        metrics = protocol_gate(parsed.get("ordered_workflow") or [])
    elif family == "E07":
        metrics = score_e07(case["condition"], parsed)
    else:
        metrics = {}

    return {
        "case_id": case["case_id"],
        "family": family,
        "condition": case["condition"],
        "generation": result.get("generation", "UNKNOWN"),
        "model": result.get("model"),
        "model_identity": result.get("model_identity"),
        "replicate": result.get("replicate"),
        "model_state": parsed.get("state", "UNKNOWN"),
        "raw_response_sha256": result.get("raw_response_sha256"),
        "metrics": metrics,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="eval/ic_failure_learning_20260827/cases/CASES.jsonl")
    ap.add_argument("--results", default="eval/ic_failure_learning_20260827/results/MODEL_OUTPUTS.jsonl")
    ap.add_argument("--out", default="eval/ic_failure_learning_20260827/scored")
    args = ap.parse_args()

    cases_path = Path(args.cases)
    results_path = Path(args.results)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    cases = {row["case_id"]: row for row in (json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip())}
    result_rows = [json.loads(line) for line in results_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    seen_keys: Counter[tuple[Any, Any, Any]] = Counter()
    scored: list[dict[str, Any]] = []
    unknown_cases: list[str] = []
    for result in result_rows:
        case_id = result.get("case_id")
        if case_id not in cases:
            unknown_cases.append(str(case_id))
            continue
        key = (result.get("model"), case_id, result.get("replicate"), result.get("generation", "UNKNOWN"))
        seen_keys[key] += 1
        scored.append(score_row(cases[case_id], result))

    duplicates = [list(key) + [count] for key, count in seen_keys.items() if count > 1]

    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        by_family[row["family"]].append(row)

    def count_metric(rows: list[dict[str, Any]], metric: str, value: Any = True) -> tuple[int, int]:
        eligible = [row for row in rows if metric in row["metrics"] and row["metrics"][metric] is not None]
        return sum(row["metrics"][metric] == value for row in eligible), len(eligible)

    aggregates: dict[str, Any] = {}
    for family, rows in sorted(by_family.items()):
        state_counts = Counter(row.get("model_state", "UNKNOWN") for row in rows)
        block: dict[str, Any] = {"n": len(rows), "model_state_counts": dict(state_counts)}
        if family == "E01":
            for metric in ["detects_vault_media_gap", "detects_origin_gap", "detects_cold_start_gap"]:
                yes, n = count_metric(rows, metric)
                block[metric] = {"yes": yes, "n": n}
        elif family == "E02":
            eligible = [r for r in rows if r["metrics"].get("directional_gate") is not None]
            block["directional_gate"] = {
                "pass": sum(bool(r["metrics"].get("directional_gate")) for r in eligible),
                "n": len(eligible),
            }
        elif family == "E04":
            for metric in ["discovery_action_present", "authentication_action_present", "consequential_run_action_present", "receipt_or_status_action_present"]:
                yes, n = count_metric(rows, metric)
                block[metric] = {"yes": yes, "n": n}
        elif family == "E05":
            for metric in ["top1_correct", "top3_contains_primary", "ordered_cdb_exact"]:
                yes, n = count_metric(rows, metric)
                block[metric] = {"yes": yes, "n": n}
        elif family == "E06":
            for metric in ["prevents_C_media_not_in_vault", "vault_before_submit", "media_before_submit", "origin_before_submit", "red_team_before_submit"]:
                yes, n = count_metric(rows, metric)
                block[metric] = {"yes": yes, "n": n}
        elif family == "E07":
            eligible = [r for r in rows if r["metrics"].get("directional_gate") is not None]
            block["directional_gate"] = {
                "pass": sum(bool(r["metrics"].get("directional_gate")) for r in eligible),
                "n": len(eligible),
            }
        aggregates[family] = block

    scored_path = out / "SCORED_RESULTS.jsonl"
    with scored_path.open("w", encoding="utf-8") as fh:
        for row in scored:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    summary = {
        "schema": "hydradg.ic_failure_learning.score_summary.v1",
        "case_manifest_sha256": sha(cases_path.read_bytes()),
        "model_outputs_sha256": sha(results_path.read_bytes()),
        "scored_results_sha256": sha(scored_path.read_bytes()),
        "input_result_rows": len(result_rows),
        "scored_rows": len(scored),
        "unknown_case_ids": unknown_cases,
        "duplicate_model_case_replicate_keys": duplicates,
        "aggregates": aggregates,
        "evidence_class": "RECOMPUTED_RESULT",
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED_BY_SCORER",
        "claim_ceiling": "FAILURE_LEARNING_EXPERIMENT_RESULTS_ONLY_NOT_ACTUAL_JUDGE_SCORE"
    }
    summary_path = out / "SCORE_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 2 if duplicates or unknown_cases else 0


if __name__ == "__main__":
    raise SystemExit(main())
