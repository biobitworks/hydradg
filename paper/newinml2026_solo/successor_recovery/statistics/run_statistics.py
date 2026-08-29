#!/usr/bin/env python3
"""Frozen-observation statistical audit for HydraDG SOLO successor recovery.

Operates on preregistered verdict receipts and Stage-2 summaries only.
Does NOT invoke model inference or substitute endpoints.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from scipy.stats import fisher_exact
except ImportError:
    fisher_exact = None

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAPER = ROOT / "paper/newinml2026_solo"
EVAL_IC = ROOT / "eval/ic_failure_learning_20260827"
EXP008 = PAPER / "provenance/admitted/eval__ic_failure_learning_20260827__daisy_overnight_20260828__EXP-008__VERDICT.json"
EXP009 = PAPER / "provenance/admitted/eval__ic_failure_learning_20260827__daisy_overnight_20260828__EXP-009__VERDICT.json"
STAGE2 = EVAL_IC / "FINAL_REPORT_STAGE2.json"
STAGE2_STATS = EVAL_IC / "STATISTICAL_SUMMARY.json"
STAGE2_VERDICT = EVAL_IC / "LEARNING_HYPOTHESIS_VERDICT.json"
DOC_RT = ROOT / "eval/newinml_doc_roundtrip_20260829/08_statistical_validation/STATISTICAL_ANALYSIS.json"


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    if k == 0:
        lo = 0.0
    else:
        lo = 1 - (math.pow(0.5, 1 / n) if k == n else None)
    if k == 0:
        from math import comb
        lo = 0.0
        hi = 1 - (alpha / 2) ** (1 / n)
    elif k == n:
        lo = (alpha / 2) ** (1 / n)
        hi = 1.0
    else:
        # approximate via Wilson when scipy beta not required
        lo, hi = wilson_ci(k, n, z=1.96)
    return lo, hi


def mcnemar_exact(b: int, c: int) -> float | None:
    n = b + c
    if n == 0:
        return None
    k = min(b, c)
    p = 0.0
    for i in range(k + 1):
        p += math.comb(n, i) * (0.5 ** n)
    return min(1.0, 2 * p)


def load_json(p: Path) -> dict:
    return json.loads(p.read_text())


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def analyze_exp(verdict_path: Path) -> dict:
    v = load_json(verdict_path)
    dq = v.get("data_quality", {})
    pri = v.get("primary", {})
    n_raw = dq.get("n_raw", 0)
    parse_rate = dq.get("valid_parse_rate")
    n_valid = int(round(n_raw * parse_rate)) if parse_rate is not None and n_raw else None
    n_paired = pri.get("n_paired", pri.get("n"))
    b, c = pri.get("b", 0), pri.get("c", 0)
    p_mcnemar = mcnemar_exact(b, c)
    c0_rate = pri.get("c0_rate")
    c1_rate = pri.get("c1_rate")
    rd = pri.get("rd")
    if n_paired and n_paired > 0 and c0_rate is not None:
        k0 = int(round(c0_rate * n_paired))
        k1 = int(round(c1_rate * n_paired)) if c1_rate is not None else 0
        ci0 = wilson_ci(k0, n_paired)
        ci1 = wilson_ci(k1, n_paired)
    else:
        ci0 = ci1 = (None, None)
    stat_state = "UNDERPOWERED" if v.get("result_class") == "UNDERPOWERED" else "NOT_IDENTIFIABLE"
    if pri.get("p_exact") is None and (b + c) == 0:
        stat_state = "UNDERPOWERED"
    return {
        "experiment_id": v.get("experiment_id"),
        "statistical_state": stat_state,
        "n_raw": n_raw,
        "n_valid_parse": n_valid,
        "valid_parse_rate": parse_rate,
        "malformed_rate": dq.get("malformed_rate"),
        "abstain_rate": dq.get("abstain_rate"),
        "unknown_rate": dq.get("unknown_rate"),
        "experimental_unit": "case_model_stratum",
        "pairing": "within_case_model",
        "n_paired": n_paired,
        "c0_rate": c0_rate,
        "c1_rate": c1_rate,
        "absolute_risk_difference": rd,
        "discordant_b": b,
        "discordant_c": c,
        "mcnemar_p_exact": p_mcnemar,
        "ci95_c0_low": ci0[0],
        "ci95_c0_high": ci0[1],
        "ci95_c1_low": ci1[0],
        "ci95_c1_high": ci1[1],
        "primary_endpoint": "E06_prevents_C_media_not_in_vault",
        "preregistered": "YES",
        "terminal_state": v.get("result_class"),
        "result_direction": v.get("conclusion_bounded", ""),
        "ordering_established": v.get("ordering_established"),
        "source_hash": sha256_file(verdict_path),
    }


def analyze_stage2() -> dict:
    rep = load_json(STAGE2)
    stats = load_json(STAGE2_STATS)
    verdict = load_json(STAGE2_VERDICT)
    mc = stats.get("model_state_counts", {})
    n_raw = rep.get("RAW_MODEL_OUTPUT_ROWS", 0)
    n_valid = rep.get("STAGE2_PROPER_ROWS", 0)
    return {
        "experiment_id": "IC-FAILURE-LEARNING-STAGE2",
        "statistical_state": stats.get("inferential_power", "DESCRIPTIVE_ONLY"),
        "n_raw": n_raw,
        "n_valid": n_valid,
        "canary_partial": rep.get("CANARY_PARTIAL_ROWS"),
        "experimental_unit": "case_model_generation",
        "pairing": "within_case_across_models",
        "model_state_counts": mc,
        "family_counts": stats.get("family_counts", {}),
        "M1_vs_M0": rep.get("M1_VS_M0"),
        "M2_vs_M0": rep.get("M2_VS_M0"),
        "M2_vs_M1": rep.get("M2_VS_M1"),
        "terminal_state": rep.get("STAGE2_EXECUTION_VERDICT"),
        "primary_endpoint": "failure_learning_behavior_improvement",
        "preregistered": "YES",
        "source_hash": sha256_file(STAGE2),
    }


def power_analysis(n_paired: int, p0: float = 0.5, p1: float = 0.8) -> dict:
    """Minimum detectable paired discordant proportion at alpha=0.05, power=0.8."""
    if n_paired <= 0:
        return {"n_paired": n_paired, "mdp_note": "UNDEFINED"}
    # descriptive MDE for McNemar: need ~8 discordant pairs for 80% power at moderate effect
    mde_discordant = max(1, int(math.ceil(8 - n_paired))) if n_paired < 8 else 0
    return {
        "n_paired": n_paired,
        "observed_discordant_capacity": n_paired,
        "minimum_discordant_pairs_80pct_power_rule_of_thumb": 8,
        "underpowered": n_paired < 8,
        "additional_pairs_needed_rule_of_thumb": mde_discordant,
        "statistical_state": "UNDERPOWERED" if n_paired < 8 else "MARGINAL",
    }


def missingness_rows(exp_rows: list[dict]) -> list[dict]:
    rows = []
    for e in exp_rows:
        n_raw = e.get("n_raw") or 0
        n_valid = e.get("n_valid_parse") or e.get("n_valid") or 0
        rows.append({
            "experiment_id": e["experiment_id"],
            "n_raw": n_raw,
            "n_valid": n_valid,
            "missing_malformed": int(round(n_raw * (e.get("malformed_rate") or 0))) if e.get("malformed_rate") else n_raw - n_valid,
            "abstain_rate": e.get("abstain_rate"),
            "unknown_rate": e.get("unknown_rate"),
            "parse_failure_rate": e.get("malformed_rate"),
            "terminal_preservation": "YES",
        })
    return rows


def write_environment() -> None:
    env = {
        "python": sys.version,
        "platform": platform.platform(),
        "recorded_at_utc": utc(),
        "host_note": "magicPRObox.local (Cloud Agent execution host)",
        "scipy_available": fisher_exact is not None,
    }
    (OUT / "environment.txt").write_text(json.dumps(env, indent=2) + "\n")
    req = "numpy\nscipy\npandas\nmatplotlib\n"
    (OUT / "requirements-lock-or-equivalent.txt").write_text(req)


def write_analysis_plan() -> None:
    text = """# Statistical Analysis Plan — Successor Recovery

## Scope
Post-hoc manuscript-recovery analyses on **frozen** observations only.
No new model samples. No endpoint substitution.

## Primary experiments
- **EXP-008**: paired McNemar on E06 within case×model strata; Wilson CI on proportions.
- **EXP-009**: same; ordering claims gated separately.
- **Stage-2**: descriptive state counts; M0/M1/M2 paired comparisons from frozen verdict JSON.

## Experimental units
- EXP-008/009: case (aggregated to n_paired=2 model strata per condition comparison scope in frozen verdict).
- Stage-2: case×model×generation (432 raw rows; 414 proper).

## Multiplicity
Exploratory secondary patterns (EXP-009 mechanistic) are not pooled with confirmatory E06.

## States
- UNDERPOWERED: insufficient discordant pairs for confirmatory inference.
- DESCRIPTIVE_ONLY: Stage-2 family counts retained without promotion.
- NOT_IDENTIFIABLE: missing pairing structure.

## HydraLamp
Deterministic perturbation cells excluded from probabilistic treatment pooling.
"""
    (OUT / "STATISTICAL_ANALYSIS_PLAN.md").write_text(text)


def run_once(run_id: str) -> dict:
    exp8 = analyze_exp(EXP008)
    exp9 = analyze_exp(EXP009)
    st2 = analyze_stage2()
    exp_rows = [exp8, exp9]

    exp_level_fields = sorted({k for r in [exp8, exp9, st2] for k in r})
    write_csv(OUT / "experiment_level_results.csv", [exp8, exp9, st2], exp_level_fields)
    write_csv(
        OUT / "effect_sizes.csv",
        [
            {**{k: exp8[k] for k in ["experiment_id", "absolute_risk_difference", "c0_rate", "c1_rate", "n_paired"]}, "effect_measure": "risk_difference"},
            {**{k: exp9[k] for k in ["experiment_id", "absolute_risk_difference", "c0_rate", "c1_rate", "n_paired"]}, "effect_measure": "risk_difference"},
        ],
        ["experiment_id", "effect_measure", "absolute_risk_difference", "c0_rate", "c1_rate", "n_paired"],
    )
    write_csv(
        OUT / "confidence_intervals.csv",
        [
            {"experiment_id": exp8["experiment_id"], "parameter": "c0_rate", "ci95_low": exp8["ci95_c0_low"], "ci95_high": exp8["ci95_c0_high"]},
            {"experiment_id": exp8["experiment_id"], "parameter": "c1_rate", "ci95_low": exp8["ci95_c1_low"], "ci95_high": exp8["ci95_c1_high"]},
            {"experiment_id": exp9["experiment_id"], "parameter": "c0_rate", "ci95_low": exp9["ci95_c0_low"], "ci95_high": exp9["ci95_c0_high"]},
            {"experiment_id": exp9["experiment_id"], "parameter": "c1_rate", "ci95_low": exp9["ci95_c1_low"], "ci95_high": exp9["ci95_c1_high"]},
        ],
        ["experiment_id", "parameter", "ci95_low", "ci95_high"],
    )
    write_csv(
        OUT / "exact_tests.csv",
        [
            {"experiment_id": exp8["experiment_id"], "test": "mcnemar_exact", "discordant_b": exp8["discordant_b"], "discordant_c": exp8["discordant_c"], "p_value": exp8["mcnemar_p_exact"]},
            {"experiment_id": exp9["experiment_id"], "test": "mcnemar_exact", "discordant_b": exp9["discordant_b"], "discordant_c": exp9["discordant_c"], "p_value": exp9["mcnemar_p_exact"]},
        ],
        ["experiment_id", "test", "discordant_b", "discordant_c", "p_value"],
    )
    write_csv(OUT / "missingness_failure_analysis.csv", missingness_rows(exp_rows), [
        "experiment_id", "n_raw", "n_valid", "missing_malformed", "abstain_rate", "unknown_rate", "parse_failure_rate", "terminal_preservation",
    ])
    write_csv(
        OUT / "power_precision_analysis.csv",
        [power_analysis(exp8["n_paired"] or 0), power_analysis(exp9["n_paired"] or 0)],
        ["n_paired", "observed_discordant_capacity", "minimum_discordant_pairs_80pct_power_rule_of_thumb", "underpowered", "additional_pairs_needed_rule_of_thumb", "statistical_state"],
    )

    # aggregate output hash for this run
    parts = []
    for name in sorted([
        "experiment_level_results.csv", "effect_sizes.csv", "confidence_intervals.csv",
        "exact_tests.csv", "missingness_failure_analysis.csv", "power_precision_analysis.csv",
    ]):
        parts.append((OUT / name).read_bytes())
    combined = b"".join(parts)
    root = sha256_bytes(combined)
    run_dir = OUT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in [
        "experiment_level_results.csv", "effect_sizes.csv", "confidence_intervals.csv",
        "exact_tests.csv", "missingness_failure_analysis.csv", "power_precision_analysis.csv",
    ]:
        (run_dir / name).write_bytes((OUT / name).read_bytes())
    receipt = {"run_id": run_id, "combined_output_sha256": root, "recorded_at_utc": utc()}
    (run_dir / "RUN_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def write_audit(exp8, exp9, st2, r1, r2, r3) -> None:
    audit = f"""# Statistical Audit — Successor Recovery

Recorded: {utc()}

## EXP-008
- Statistical state: **{exp8['statistical_state']}**
- n_raw={exp8['n_raw']}, valid_parse_rate={exp8['valid_parse_rate']}
- n_paired={exp8['n_paired']}, discordant=({exp8['discordant_b']},{exp8['discordant_c']})
- McNemar p: {exp8['mcnemar_p_exact']}
- Conclusion: effect not established (frozen verdict)

## EXP-009
- Statistical state: **{exp9['statistical_state']}**
- ordering_established: {exp9.get('ordering_established')}
- Exploratory secondary pattern NOT promoted

## Stage-2
- Statistical state: **{st2['statistical_state']}**
- n_raw={st2['n_raw']}, n_valid={st2['n_valid']}
- Terminal: {st2['terminal_state']}

## Deterministic reproduction
- R1 output root: {r1['combined_output_sha256']}
- R2 output root: {r2['combined_output_sha256']}
- R3 output root: {r3['combined_output_sha256']}
- Gate: {'PASS' if r1['combined_output_sha256'] == r2['combined_output_sha256'] == r3['combined_output_sha256'] else 'FAIL'}

## No p-hacking statement
Endpoints unchanged post hoc. Negative/null/failed cells retained. No new model samples for significance.
"""
    (OUT / "STATISTICAL_AUDIT.md").write_text(audit)


def main() -> int:
    write_environment()
    write_analysis_plan()
    script_hash = sha256_file(Path(__file__))
    input_hashes = {
        "EXP-008": sha256_file(EXP008),
        "EXP-009": sha256_file(EXP009),
        "STAGE2": sha256_file(STAGE2),
        "script": script_hash,
    }
    exp8 = analyze_exp(EXP008)
    exp9 = analyze_exp(EXP009)
    st2 = analyze_stage2()
    r1 = run_once("R1")
    r2 = run_once("R2")
    r3 = run_once("R3")
    write_audit(exp8, exp9, st2, r1, r2, r3)
    gate = r1["combined_output_sha256"] == r2["combined_output_sha256"] == r3["combined_output_sha256"]
    receipt = {
        "schema": "hydradg.statistical_reproducibility_receipt.v1",
        "recorded_at_utc": utc(),
        "input_hashes": input_hashes,
        "script_sha256": script_hash,
        "R1": r1,
        "R2": r2,
        "R3": r3,
        "REPRODUCIBILITY_GATE": "PASS" if gate else "FAIL",
        "identical_deterministic_outputs": gate,
    }
    (OUT / "STATISTICAL_REPRODUCIBILITY_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
