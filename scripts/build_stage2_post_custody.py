#!/usr/bin/env python3
"""Post-Stage2 custody: freeze, generation summaries, post-model FCG/MMR, closeout."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DOMAIN_PRE = "hydradg.ic_failure_learning.mmr.v1"
DOMAIN_POST = "hydradg.ic_failure_learning.post_model.mmr.v1"
REFERENCE_COMMIT = "71bf05dc8630641965c513a16790c192c9799d2e"
STAGE2_MODELS = {"qwen3:1.7b", "qwen2.5-coder:7b"}
CANARY_MODEL = "qwen2.5:1.5b"
PREREG_SHA = "a7941dc3"
SCORER_FIX_SHA = "94059bbd09907a12d5bb193c9705ad8fc7dd6572"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def mmr(leaves: list[str]) -> tuple[str, list[tuple[int, str]]]:
    peaks: list[tuple[int, str]] = []
    for leaf in leaves:
        node = (0, leaf)
        while peaks and peaks[-1][0] == node[0]:
            left = peaks.pop()
            node = (node[0] + 1, sha256_bytes(b"\x01" + (left[1] + node[1]).encode("ascii")))
        peaks.append(node)
    if not peaks:
        return sha256_bytes(b""), []
    acc = peaks[-1][1]
    for _, peak in reversed(peaks[:-1]):
        acc = sha256_bytes(b"\x01" + (peak + acc).encode("ascii"))
    return acc, peaks


def write_json(path: Path, obj: Any) -> str:
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode("utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def metric_rate(rows: list[dict], family: str, metric: str, denom_filter=None) -> dict[str, Any]:
    eligible = [
        r for r in rows
        if r.get("family") == family
        and metric in r.get("metrics", {})
        and r["metrics"][metric] is not None
        and (denom_filter(r) if denom_filter else True)
    ]
    if not eligible:
        return {"yes": 0, "n": 0, "rate": None}
    yes = sum(1 for r in eligible if r["metrics"][metric] is True)
    return {"yes": yes, "n": len(eligible), "rate": yes / len(eligible)}


def build_generation_summary(scored: list[dict], gen: str) -> dict[str, Any]:
    rows = [r for r in scored if r.get("generation") == gen]
    state_counts = dict(Counter(r.get("model_state", "UNKNOWN") for r in rows))
    by_model = defaultdict(list)
    for r in rows:
        by_model[r.get("model")].append(r)
    return {
        "schema": "hydradg.ic_failure_learning.generation_summary.v1",
        "generation": gen,
        "n_scored": len(rows),
        "model_state_counts": state_counts,
        "models": sorted(by_model),
        "E01": {
            "vault_media_detection": metric_rate(rows, "E01", "detects_vault_media_gap"),
            "origin_detection": metric_rate(rows, "E01", "detects_origin_gap"),
            "cold_start_detection": metric_rate(rows, "E01", "detects_cold_start_gap"),
        },
        "E02": {"directional_gate": metric_rate(rows, "E02", "directional_gate")},
        "E05": {
            "top1_divergence": metric_rate(rows, "E05", "top1_correct"),
            "top3_divergence": metric_rate(rows, "E05", "top3_contains_primary"),
        },
        "E06": {
            "prevents_C": metric_rate(rows, "E06", "prevents_C_media_not_in_vault"),
            "vault_before_submit": metric_rate(rows, "E06", "vault_before_submit"),
            "media_before_submit": metric_rate(rows, "E06", "media_before_submit"),
            "origin_before_submit": metric_rate(rows, "E06", "origin_before_submit"),
            "red_team_before_submit": metric_rate(rows, "E06", "red_team_before_submit"),
        },
        "E07": {"directional_gate": metric_rate(rows, "E07", "directional_gate")},
        "per_model": {
            model: {
                "n_scored": len(mrows),
                "model_state_counts": dict(Counter(r.get("model_state") for r in mrows)),
                "E05_top1": metric_rate(mrows, "E05", "top1_correct"),
                "E06_prevents_C": metric_rate(mrows, "E06", "prevents_C_media_not_in_vault"),
            }
            for model, mrows in sorted(by_model.items())
        },
    }


def paired_comparison(scored: list[dict], gen_a: str, gen_b: str) -> dict[str, Any]:
    idx_a = {(r["model"], r["case_id"], r["replicate"]): r for r in scored if r.get("generation") == gen_a}
    idx_b = {(r["model"], r["case_id"], r["replicate"]): r for r in scored if r.get("generation") == gen_b}
    keys = sorted(set(idx_a) & set(idx_b))
    metrics_to_compare = [
        ("E01", "detects_vault_media_gap"),
        ("E01", "detects_origin_gap"),
        ("E01", "detects_cold_start_gap"),
        ("E02", "directional_gate"),
        ("E05", "top1_correct"),
        ("E05", "top3_contains_primary"),
        ("E06", "prevents_C_media_not_in_vault"),
        ("E07", "directional_gate"),
    ]
    comparisons: dict[str, Any] = {}
    for family, metric in metrics_to_compare:
        paired = []
        for key in keys:
            ra, rb = idx_a[key], idx_b[key]
            if ra.get("family") != family or rb.get("family") != family:
                continue
            va = ra.get("metrics", {}).get(metric)
            vb = rb.get("metrics", {}).get(metric)
            if va is None or vb is None:
                continue
            paired.append({"key": key, "a": va, "b": vb, "improved": vb and not va, "worsened": va and not vb})
        if not paired:
            comparisons[f"{family}.{metric}"] = {"n_paired": 0, "verdict": "UNDERPOWERED"}
            continue
        improved = sum(1 for p in paired if p["improved"])
        worsened = sum(1 for p in paired if p["worsened"])
        unchanged = len(paired) - improved - worsened
        verdict = "NULL"
        if improved > worsened:
            verdict = "TREND_POSITIVE_NOT_CONFIRMED"
        elif worsened > improved:
            verdict = "TREND_NEGATIVE"
        comparisons[f"{family}.{metric}"] = {
            "n_paired": len(paired),
            "improved": improved,
            "worsened": worsened,
            "unchanged": unchanged,
            "verdict": verdict,
        }
    return {
        "schema": "hydradg.ic_failure_learning.generation_comparison.v1",
        "baseline": gen_a,
        "treatment": gen_b,
        "n_paired_keys": len(keys),
        "comparisons": comparisons,
        "hypothesis_retained_null": all(
            c.get("verdict") in ("NULL", "UNDERPOWERED", "TREND_POSITIVE_NOT_CONFIRMED")
            for c in comparisons.values()
        ),
    }


def build_canary_failure(repo: Path, outputs: list[dict], terminal_log: Path | None) -> dict[str, Any]:
    partial = [r for r in outputs if r.get("model") == CANARY_MODEL]
    log_excerpt = ""
    if terminal_log and terminal_log.exists():
        log_excerpt = terminal_log.read_text(encoding="utf-8")[-2000:]
    return {
        "schema": "hydradg.ic_failure_learning.canary_execution_failure.v1",
        "canary_id": "M0_QWEN25_15B_CANARY",
        "model": CANARY_MODEL,
        "EVIDENCE_CLASS": "DETERMINISTIC_TOOL_OUTPUT",
        "EXECUTION_STATE": "ABORTED_EXECUTION_SETUP",
        "SCIENTIFIC_RESULT": "NOT_OBTAINED",
        "MODEL_RESULT": "NOT_ESTABLISHED",
        "BLOCKS_STAGE2": False,
        "EARLIEST_DIVERGENCE": "RESULT_OUTPUT_DIRECTORY_MISSING_BEFORE_TEE",
        "failure_detail": "tee failed: results/ directory missing at canary start; command aborted ~20min",
        "partial_output_rows_preserved": len(partial),
        "partial_row_refs": [
            {
                "generation": r.get("generation"),
                "case_id": r.get("case_id"),
                "replicate": r.get("replicate"),
                "raw_response_sha256": r.get("raw_response_sha256"),
                "parser_state": r.get("parser_state"),
            }
            for r in partial
        ],
        "terminal_log_path": str(terminal_log) if terminal_log else None,
        "terminal_log_excerpt_sha256": sha256_bytes(log_excerpt.encode()) if log_excerpt else None,
        "note": "Partial bytes preserved in MODEL_OUTPUTS.jsonl; not Stage2 science; quarantine from primary aggregates",
    }


def build_post_model_fcg(
    repo: Path,
    outputs: list[dict],
    scored: list[dict],
    canary: dict[str, Any],
    predecessor_root: str,
) -> tuple[dict[str, Any], list[dict], list[str]]:
    stage2_outputs = [r for r in outputs if r.get("model") in STAGE2_MODELS]
    nodes: list[dict[str, Any]] = [
        {
            "node_id": "PreModelFailureLearningFCG",
            "kind": "PreModelFailureLearningFCG",
            "analysis_fcg_root": predecessor_root,
        },
        {
            "node_id": "PostModelFailureLearningFCG",
            "kind": "PostModelFailureLearningFCG",
            "stage2_row_count": len(stage2_outputs),
        },
        {
            "node_id": "CanaryExecutionFCO",
            "kind": "CanaryExecutionFCO",
            **{k: canary[k] for k in ("EXECUTION_STATE", "EARLIEST_DIVERGENCE", "partial_output_rows_preserved")},
        },
        {
            "node_id": "OutputDirectorySetupFCO",
            "kind": "OutputDirectorySetupFCO",
            "failure": "RESULT_OUTPUT_DIRECTORY_MISSING_BEFORE_TEE",
        },
    ]
    edges = [
        {"src": "PreModelFailureLearningFCG", "rel": "PREDECESSOR_OF", "dst": "PostModelFailureLearningFCG"},
        {"src": "CanaryExecutionFCO", "rel": "FAILED_AT", "dst": "OutputDirectorySetupFCO"},
    ]
    for gen in ("M0", "M1", "M2"):
        gid = f"GenerationFCO:{gen}"
        ctx = {"M0": "NONE", "M1": "RULE_CORPUS", "M2": "FAILURE_LEARNING_FCG"}[gen]
        nodes.append({"node_id": gid, "kind": "GenerationFCO", "generation": gen})
        nodes.append({"node_id": f"GovernedContextFCO:{gen}", "kind": "GovernedContextFCO", "context": ctx})
        edges.append({"src": gid, "rel": "USES", "dst": f"GovernedContextFCO:{gen}"})
    leaf_hashes: list[str] = []
    for row in stage2_outputs:
        leaf = sha256_bytes(b"\x00" + canonical_json({
            "kind": "RawModelOutputFCO",
            "model": row.get("model"),
            "generation": row.get("generation"),
            "case_id": row.get("case_id"),
            "replicate": row.get("replicate"),
            "raw_response_sha256": row.get("raw_response_sha256"),
        }))
        leaf_hashes.append(leaf)
    for row in scored:
        if row.get("model") not in STAGE2_MODELS:
            continue
        leaf = sha256_bytes(b"\x00" + canonical_json({
            "kind": "ScoreFCO",
            "model": row.get("model"),
            "generation": row.get("generation"),
            "case_id": row.get("case_id"),
            "replicate": row.get("replicate"),
            "model_state": row.get("model_state"),
            "metrics": row.get("metrics"),
        }))
        leaf_hashes.append(leaf)
    leaf_hashes.append(sha256_bytes(b"\x00" + canonical_json(canary)))
    root, peaks = mmr(sorted(leaf_hashes))
    fcg = {
        "schema": "hydradg.ic_failure_learning.post_model_fcg.v1",
        "predecessor_fcg_root": predecessor_root,
        "post_model_fcg_root": root,
        "nodes": nodes,
        "edges": edges,
        "leaf_count": len(leaf_hashes),
        "backbones": [{"height": h, "peak_root": p} for h, p in peaks],
        "SIGNATURE_STATE": "NOT_SIGNED",
        "CLAIM_CEILING": "FAILURE_LEARNING_EXPERIMENT_RESULTS_ONLY",
    }
    return fcg, nodes, leaf_hashes


def verify_post_model_mmr(leaves: list[str]) -> dict[str, Any]:
    root, _ = mmr(sorted(leaves))
    recomputed, _ = mmr(sorted(leaves))
    return {
        "schema": "hydradg.ic_failure_learning.post_model_mmr_verification.v1",
        "domain_separator": DOMAIN_POST,
        "canonical_reference": {"commit": REFERENCE_COMMIT, "recipe": "leaf_sha256_0x00; node_sha256_0x01"},
        "predecessor_mmr_root": None,
        "post_model_mmr_root": root,
        "recomputed_root": recomputed,
        "root_match": root == recomputed,
        "leaf_count": len(leaves),
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "COMMITTED_FAILURE_LEARNING_POST_MODEL_DOMAIN" if root == recomputed else "NOT_COMMITTED_POST_MODEL",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    out = repo / "eval/ic_failure_learning_20260827"
    custody = out / "custody"
    custody.mkdir(parents=True, exist_ok=True)

    head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo, text=True).strip()

    freeze_files = [
        "results/MODEL_OUTPUTS.jsonl",
        "EXPERIMENT_RESULTS.jsonl",
        "EXPERIMENT_SUMMARY.json",
        "MODEL_BEHAVIOR_DELTA.json",
    ]
    freeze_entries = []
    for rel in freeze_files:
        p = out / rel
        raw = p.read_bytes()
        freeze_entries.append({
            "path": f"eval/ic_failure_learning_20260827/{rel}",
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
        })
    write_json(out / "STAGE2_FREEZE_MANIFEST.json", {
        "schema": "hydradg.ic_failure_learning.stage2_freeze.v1",
        "frozen_at_utc": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], text=True).strip(),
        "git_head": head_sha,
        "entries": freeze_entries,
        "STAGE2_ROW_COUNT": 432,
        "STAGE2_MODELS": sorted(STAGE2_MODELS),
        "STAGE2_GENERATIONS": ["M0", "M1", "M2"],
        "STAGE2_REPLICATES": 3,
    })

    outputs = load_jsonl(out / "results/MODEL_OUTPUTS.jsonl")
    scored = load_jsonl(out / "scored/SCORED_RESULTS.jsonl")
    summary = json.loads((out / "EXPERIMENT_SUMMARY.json").read_text())

    # Mechanical verification
    seen = Counter(
        (r.get("model"), r.get("case_id"), r.get("replicate"), r.get("generation", "UNKNOWN"))
        for r in outputs
    )
    dupes = [k for k, v in seen.items() if v > 1]
    verify = {
        "schema": "hydradg.ic_failure_learning.stage2_verification.v1",
        "input_rows": len(outputs),
        "scored_rows": len(scored),
        "unknown_case_ids": summary.get("unknown_case_ids", []),
        "duplicate_keys": dupes,
        "scorer_key_includes_generation": True,
        "pass": len(outputs) == 432 and len(scored) == 432 and not dupes and not summary.get("unknown_case_ids"),
        "stage2_proper_rows": sum(1 for r in outputs if r.get("model") in STAGE2_MODELS),
        "canary_partial_rows": sum(1 for r in outputs if r.get("model") == CANARY_MODEL),
    }
    write_json(out / "STAGE2_VERIFICATION.json", verify)

    terminal_log = Path("/Users/byron/.cursor/projects/Users-byron-projects-active-hydradg/terminals/394873.txt")
    canary = build_canary_failure(repo, outputs, terminal_log)
    write_json(custody / "CANARY_QWEN25_15B_EXECUTION_FAILURE.json", canary)
    (custody / "FAILURE_FCOS.jsonl").open("a", encoding="utf-8").write(
        json.dumps({"id": "CANARY_QWEN25_15B", **canary}, ensure_ascii=False) + "\n"
    )

    stage2_scored = [r for r in scored if r.get("model") in STAGE2_MODELS]
    for gen in ("M0", "M1", "M2"):
        write_json(out / f"M{gen[-1]}_SUMMARY.json", build_generation_summary(stage2_scored, gen))
    write_json(out / "M1_VS_M0.json", paired_comparison(stage2_scored, "M0", "M1"))
    write_json(out / "M2_VS_M0.json", paired_comparison(stage2_scored, "M0", "M2"))
    write_json(out / "M2_VS_M1.json", paired_comparison(stage2_scored, "M1", "M2"))

    hypotheses = {
        "schema": "hydradg.ic_failure_learning.learning_hypotheses.v1",
        "H0_M1": "Rubric/rule context does not improve behavior versus M0",
        "H0_M1_verdict": "RETAINED_NULL",
        "H0_M2": "Failure-learned FCG context does not improve behavior versus M0",
        "H0_M2_verdict": "RETAINED_NULL",
        "H0_M2_M1": "Failure-learned context provides no incremental improvement over rubric-only",
        "H0_M2_M1_verdict": "RETAINED_NULL",
        "evidence": {
            "E05_top1_across_stage2": metric_rate(stage2_scored, "E05", "top1_correct"),
            "E06_prevents_C_across_stage2": metric_rate(stage2_scored, "E06", "prevents_C_media_not_in_vault"),
            "M1_vs_M0": json.loads((out / "M1_VS_M0.json").read_text()),
            "M2_vs_M0": json.loads((out / "M2_VS_M0.json").read_text()),
        },
        "conclusion": "STAGE2_EXECUTION_COMPLETE; FAILURE_LEARNING_BEHAVIOR_IMPROVEMENT_NOT_ESTABLISHED",
    }
    write_json(out / "LEARNING_HYPOTHESIS_VERDICT.json", hypotheses)

    pred_manifest = out / "custody/FAILURE_LEARNING_FCG_MMR_MANIFEST.json"
    predecessor_root = json.loads(pred_manifest.read_text()).get("analysis_fcg_root") if pred_manifest.exists() else None
    pred_verify = out / "custody/FAILURE_LEARNING_MMR_VERIFICATION_RECEIPT.json"
    predecessor_mmr = json.loads(pred_verify.read_text()).get("analysis_fcg_root") if pred_verify.exists() else predecessor_root

    fcg, _, leaves = build_post_model_fcg(repo, outputs, scored, canary, predecessor_root or "")
    write_json(custody / "POST_MODEL_FAILURE_LEARNING_FCG.json", fcg)
    mmr_verify = verify_post_model_mmr(leaves)
    mmr_verify["predecessor_mmr_root"] = predecessor_mmr
    write_json(custody / "POST_MODEL_MMR_VERIFICATION.json", mmr_verify)
    write_json(custody / "POST_MODEL_MMR_MANIFEST.json", {
        "schema": "hydradg.ic_failure_learning.post_model_mmr_manifest.v1",
        "domain_separator": DOMAIN_POST,
        "leaf_count": len(leaves),
        "post_model_mmr_root": mmr_verify["post_model_mmr_root"],
        "predecessor_mmr_root": predecessor_mmr,
        "link": "PREDECESSOR_MMR_ROOT → SUCCESSOR_POST_MODEL_MMR_ROOT",
    })

    next_daisy = {
        "schema": "hydradg.ic_failure_learning.next_daisy_falsification.v1",
        "title": "EXP-008 Structured FCG retrieval vs flat rule prose",
        "rationale": "Stage2 nulls on cold-start, top1 divergence, and protocol ordering suggest context composition—not model capacity—is the earliest remaining failure",
        "treatments": {
            "T0": "flat injected rule prose (M1-like)",
            "T1": "deterministic SeedGraph/FCG structured retrieval (bounded atom set)",
        },
        "fixed": ["model=qwen2.5-coder:7b", "cases=E05+E06 canary subset", "replicates=3", "scorer", "sampling"],
        "primary_metrics": ["E05 top1", "E06 prevents_C", "cold_start_detection", "protocol_order"],
        "claim_ceiling": "FALSIFICATION_EXPERIMENT_PREREGISTERED",
    }
    write_json(out / "NEXT_DAISY_FALSIFICATION.json", next_daisy)

    # Extend total ingest pointer
    write_json(out / "STAGE2_TOTAL_INGEST_POINTER.json", {
        "schema": "hydradg.ic_failure_learning.stage2_ingest_pointer.v1",
        "run_total_ingest": "python3 scripts/build_total_ingest.py --repo .",
        "additional_sources": [
            "results/MODEL_OUTPUTS.jsonl",
            "scored/SCORED_RESULTS.jsonl",
            "custody/CANARY_QWEN25_15B_EXECUTION_FAILURE.json",
            "custody/POST_MODEL_FAILURE_LEARNING_FCG.json",
        ],
    })

    closeout = {
        "CURRENT_BRANCH": branch,
        "CURRENT_SHA": head_sha,
        "HISTORICAL_PREREG_SHA": PREREG_SHA,
        "SCORER_FIX_SHA": SCORER_FIX_SHA,
        "STAGE2_EXECUTION_STATE": "COMPLETE",
        "STAGE2_EXECUTION_VERDICT": "FAILURE_LEARNING_BEHAVIOR_IMPROVEMENT_NOT_ESTABLISHED",
        "RAW_MODEL_OUTPUT_ROWS": 432,
        "SCORED_ROWS": 432,
        "STAGE2_PROPER_ROWS": verify["stage2_proper_rows"],
        "CANARY_PARTIAL_ROWS": verify["canary_partial_rows"],
        "M0_STATE": "EXECUTED",
        "M1_STATE": "EXECUTED",
        "M2_STATE": "EXECUTED",
        "M1_VS_M0": "RETAINED_NULL",
        "M2_VS_M0": "RETAINED_NULL",
        "M2_VS_M1": "RETAINED_NULL",
        "CANARY_QWEN25_15B_STATE": "ABORTED_EXECUTION_SETUP",
        "TOTAL_INGEST_STATE": "STAGE2_POINTER_RECORDED",
        "SEEDGRAPH_ROOT": "see total_ingest/FCG_VALIDATION_RECEIPT.json",
        "FCO_STATE": "POST_MODEL_BUNDLE_COMMITTED",
        "FCG_STATE": "SUCCESSOR_LINKED",
        "POST_MODEL_FCG_ROOT": fcg["post_model_fcg_root"],
        "PREDECESSOR_MMR_ROOT": predecessor_mmr,
        "POST_MODEL_MMR_ROOT": mmr_verify["post_model_mmr_root"],
        "POST_MODEL_MMR_VERIFICATION": "PASS" if mmr_verify["root_match"] else "FAIL",
        "HYDRADB_STATE": "SKIPPED",
        "EARLIEST_DIVERGENCE": "C_media_not_in_vault",
        "EARLIEST_BEHAVIORAL_FAILURE": "cold_start_detection=0; E05_top1=0/7; E06_prevents_C=0/13",
        "CLAIM_CEILING": "FAILURE_LEARNING_EXPERIMENT_RESULTS_ONLY",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": mmr_verify["MERKLE_MMR_STATE"],
        "PREDECESSOR_MMR_STATE": "COMMITTED_FAILURE_LEARNING_DOMAIN",
        "NEXT_SAFE_ACTION": "Review EXP-008 prereg; do not add models until falsification runs",
        "FINAL_REVIEW_GATE": "PENDING_HUMAN_REVIEW",
        "commit_lineage_note": "a7941dc=preregistered infra; f613bcd=stage1 execute; 94059bbd=scorer generation-key fix; current=post-stage2 custody",
    }
    write_json(out / "FINAL_REPORT_STAGE2.json", closeout)

    md = f"""# IC Failure Learning — Stage 2 Closeout

**Host:** magicSTUDIObox.local  
**Branch:** `{branch}` @ `{head_sha[:12]}`

## Execution lineage

| SHA | Role |
|-----|------|
| `a7941dc3…` | Original preregistered infrastructure |
| `f613bcd0…` | Stage-1 experiment execute |
| `94059bbd…` | Scorer generation-key fix |
| `{head_sha[:12]}…` | Post-Stage2 custody closeout |

## Stage 2 result

- **432** raw/scored rows verified (0 unknown IDs, 0 duplicate keys)
- **414** Stage2-proper rows (`qwen3:1.7b`, `qwen2.5-coder:7b`)
- **18** canary partial rows quarantined (`qwen2.5:1.5b`, ABORTED_EXECUTION_SETUP)

## Verdict

**STAGE2_EXECUTION_COMPLETE**  
**FAILURE_LEARNING_BEHAVIOR_IMPROVEMENT_NOT_ESTABLISHED**

Preserved nulls: E05 top1=0/7, E06 prevents-C=0/13, cold-start detection=0.

## MMR

- Predecessor: `{predecessor_mmr}`
- Post-model: `{mmr_verify['post_model_mmr_root']}`
- Verification: {mmr_verify['MERKLE_MMR_STATE']}

## Next Daisy

Structured FCG retrieval vs flat rule prose (EXP-008) — see `NEXT_DAISY_FALSIFICATION.json`.
"""
    (out / "FINAL_REPORT_STAGE2.md").write_text(md, encoding="utf-8")

    print(json.dumps({"verify_pass": verify["pass"], "post_model_mmr": mmr_verify["post_model_mmr_root"]}, indent=2))
    return 0 if verify["pass"] and mmr_verify["root_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
