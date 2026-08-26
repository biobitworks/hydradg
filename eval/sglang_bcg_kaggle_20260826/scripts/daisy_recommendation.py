#!/usr/bin/env python3
"""Emit DAISY_RUNTIME_SUCCESSOR_RECOMMENDATION.json from recomputed summary."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", required=True)
    args = ap.parse_args()
    rd = Path(args.results_dir)
    summary_path = rd / "RECOMPUTED_SUMMARY.json"
    if not summary_path.exists():
        found = list(rd.rglob("RECOMPUTED_SUMMARY.json"))
        summary_path = found[0] if found else summary_path
    if not summary_path.exists():
        raise SystemExit("RECOMPUTED_SUMMARY.json missing")
    s = json.loads(summary_path.read_text(encoding="utf-8"))
    pc = s.get("per_condition") or {}
    comps = s.get("comparisons") or {}

    phenotypes = set()
    for cid, block in pc.items():
        phenotypes.update((block.get("failure_counts") or {}).keys())

    c2 = pc.get("C2") or {}
    c0 = pc.get("C0") or {}
    c1 = pc.get("C1") or {}

    interpretations = []
    if not c2:
        interpretations.append("INCONCLUSIVE")
        recommendation = "PRESERVE_NULL_OR_FAILED_RUNTIME_EVIDENCE"
        detail = "C2 absent from recomputed summary"
    else:
        # Stability
        c2_ok = (c2.get("success_rate") or 0) >= 0.8
        fail_heavy = any(
            k in phenotypes
            for k in (
                "OOM",
                "SERVER_CRASH",
                "CUDA_GRAPH_CAPTURE_FAILURE",
                "CUDA_GRAPH_REPLAY_FAILURE",
                "UNSUPPORTED_CONFIGURATION",
            )
        )
        ttft_vs_c0 = ((comps.get("C2_vs_C0") or {}).get("median_ttft_s") or {})
        ttft_vs_c1 = ((comps.get("C2_vs_C1") or {}).get("median_ttft_s") or {})
        in_vs_c0 = ((comps.get("C2_vs_C0") or {}).get("median_input_tokens_per_s") or {})
        vram_vs_c0 = ((comps.get("C2_vs_C0") or {}).get("peak_vram_mib") or {})

        # Lower TTFT is faster; higher input tok/s is faster
        faster = False
        slower = False
        if ttft_vs_c0.get("pct") is not None and ttft_vs_c0["pct"] < -5:
            faster = True
            interpretations.append("BREAKABLE_FASTER")
        if ttft_vs_c0.get("pct") is not None and ttft_vs_c0["pct"] > 5:
            slower = True
            interpretations.append("BREAKABLE_SLOWER")
        if in_vs_c0.get("pct") is not None and in_vs_c0["pct"] > 5:
            faster = True
            if "BREAKABLE_FASTER" not in interpretations:
                interpretations.append("BREAKABLE_FASTER")
        if vram_vs_c0.get("pct") is not None and vram_vs_c0["pct"] > 5:
            interpretations.append("BREAKABLE_MORE_MEMORY")
        if vram_vs_c0.get("pct") is not None and vram_vs_c0["pct"] < -5:
            interpretations.append("BREAKABLE_LESS_MEMORY")
        if fail_heavy and (c2.get("success_rate") or 0) < 0.5:
            interpretations.append("CONFIGURATION_FAILURE")
        if faster and slower:
            interpretations.append("MIXED")
        if not interpretations:
            interpretations.append("NO_MATERIAL_DIFFERENCE")

        if c2_ok and "BREAKABLE_FASTER" in interpretations and "CONFIGURATION_FAILURE" not in interpretations:
            recommendation = "RECOMMEND_FUTURE_DAISY_RUNTIME_SUCCESSOR_PREREGISTRATION"
            detail = "Breakable prefill appeared stable and faster on at least one preregistered endpoint"
        elif "CONFIGURATION_FAILURE" in interpretations or not c2_ok:
            recommendation = "PRESERVE_NEGATIVE_OR_FAILURE_RUNTIME_EVIDENCE"
            detail = "Breakable condition unstable or failure-heavy"
        elif "BREAKABLE_SLOWER" in interpretations:
            recommendation = "PRESERVE_NEGATIVE_RUNTIME_EVIDENCE"
            detail = "Breakable slower on median TTFT vs control"
        else:
            recommendation = "PRESERVE_NULL_RUNTIME_EVIDENCE"
            detail = "No material runtime difference under claim ceiling"

    out = {
        "document": "DAISY_RUNTIME_SUCCESSOR_RECOMMENDATION",
        "experiment_id": "SGLANG-BCG-KAGGLE-20260826",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "NOT_DAISY_LABELS": ["T00", "T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09", "T10", "T11", "T12"],
        "interpretations": interpretations,
        "recommendation": recommendation,
        "detail": detail,
        "failure_phenotypes_observed": sorted(phenotypes),
        "c0_success_rate": c0.get("success_rate"),
        "c1_success_rate": c1.get("success_rate"),
        "c2_success_rate": c2.get("success_rate"),
        "comparisons": comps,
        "future_daisy_requires": [
            "NEW_PLAN_CHECK",
            "HOST_CHANGED",
            "RUNTIME_CHANGED",
            "SERVING_FRAMEWORK_CHANGED",
        ],
        "claim_ceiling": "ONE_MODEL_ONE_KAGGLE_GPU_RUNTIME_STRESS_ONLY",
        "evidence_state": "ENGINEERING_RUNTIME_EVIDENCE_PROVISIONAL",
    }
    path = rd / "DAISY_RUNTIME_SUCCESSOR_RECOMMENDATION.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # also copy to experiment root results pointer
    print(json.dumps({"wrote": str(path), "recommendation": recommendation, "interpretations": interpretations}, indent=2))


if __name__ == "__main__":
    main()
