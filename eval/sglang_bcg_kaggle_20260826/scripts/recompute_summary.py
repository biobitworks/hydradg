#!/usr/bin/env python3
"""Recompute engineering summary from raw metrics.jsonl — RECOMPUTED_RESULT."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def median(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def p95(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = sorted(xs)
    idx = min(len(ys) - 1, max(0, math.ceil(0.95 * len(ys)) - 1))
    return ys[idx]


def iqr(xs: list[float]) -> list[float] | None:
    if len(xs) < 2:
        return None
    ys = sorted(xs)
    return [statistics.quantiles(ys, n=4)[0], statistics.quantiles(ys, n=4)[2]]


def find_metrics(results_dir: Path) -> Path:
    direct = results_dir / "metrics.jsonl"
    if direct.exists():
        return direct
    found = list(results_dir.rglob("metrics.jsonl"))
    if not found:
        raise FileNotFoundError("metrics.jsonl not found")
    return found[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", required=True)
    args = ap.parse_args()
    results_dir = Path(args.results_dir)
    metrics_path = find_metrics(results_dir)
    rows = [json.loads(l) for l in metrics_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    by_c: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_c[r.get("condition_id", "?")].append(r)

    def cond_summary(cid: str, items: list[dict]) -> dict:
        passes = [x for x in items if x.get("phenotype") == "PASS" and x.get("completed")]
        fail_counts: dict[str, int] = defaultdict(int)
        for x in items:
            fail_counts[x.get("phenotype") or "UNKNOWN_FAILURE"] += 1
        ttfts = [float(x["ttft_s"]) for x in passes if x.get("ttft_s") is not None]
        in_tps = [float(x["input_tokens_per_s"]) for x in passes if x.get("input_tokens_per_s") is not None]
        tot_tps = [float(x["request_throughput"]) for x in passes if x.get("request_throughput") is not None]
        vrams = [float(x["peak_gpu_memory_mib_sample"]) for x in items if x.get("peak_gpu_memory_mib_sample") is not None]
        startups = [float(x["server_startup_time_s"]) for x in items if x.get("server_startup_time_s") is not None]
        captures = [float(x["cuda_graph_capture_time_s"]) for x in items if x.get("cuda_graph_capture_time_s") is not None]
        # by prompt length / batch
        by_cell: dict[str, dict] = {}
        for x in passes:
            key = f"P{x.get('target_prompt_tokens')}_B{x.get('batch_size')}"
            by_cell.setdefault(key, {"ttft": [], "in_tps": [], "req_tps": []})
            if x.get("ttft_s") is not None:
                by_cell[key]["ttft"].append(float(x["ttft_s"]))
            if x.get("input_tokens_per_s") is not None:
                by_cell[key]["in_tps"].append(float(x["input_tokens_per_s"]))
            if x.get("request_throughput") is not None:
                by_cell[key]["req_tps"].append(float(x["request_throughput"]))
        by_cell_out = {
            k: {
                "median_ttft_s": median(v["ttft"]),
                "median_input_tokens_per_s": median(v["in_tps"]),
                "median_request_throughput": median(v["req_tps"]),
                "n": max(len(v["ttft"]), len(v["in_tps"]), len(v["req_tps"])),
            }
            for k, v in sorted(by_cell.items())
        }
        return {
            "condition_id": cid,
            "n_rows": len(items),
            "n_pass": len(passes),
            "success_rate": (len(passes) / len(items)) if items else 0.0,
            "failure_counts": dict(fail_counts),
            "median_ttft_s": median(ttfts),
            "p95_ttft_s": p95(ttfts),
            "ttft_iqr": iqr(ttfts),
            "median_input_tokens_per_s": median(in_tps),
            "median_request_throughput": median(tot_tps),
            "peak_vram_mib": max(vrams) if vrams else None,
            "median_startup_s": median(startups),
            "median_capture_s": median(captures),
            "by_prompt_batch": by_cell_out,
        }

    per_cond = {cid: cond_summary(cid, items) for cid, items in sorted(by_c.items())}

    # Pairwise deltas C2 vs C0 / C1
    def delta(a: float | None, b: float | None) -> dict | None:
        if a is None or b is None:
            return None
        abs_d = a - b
        pct = (abs_d / b * 100.0) if b != 0 else None
        return {"abs": abs_d, "pct": pct}

    comparisons = {}
    if "C2" in per_cond:
        for other in ("C0", "C1"):
            if other not in per_cond:
                continue
            comparisons[f"C2_vs_{other}"] = {
                "median_ttft_s": delta(per_cond["C2"]["median_ttft_s"], per_cond[other]["median_ttft_s"]),
                "median_input_tokens_per_s": delta(
                    per_cond["C2"]["median_input_tokens_per_s"], per_cond[other]["median_input_tokens_per_s"]
                ),
                "peak_vram_mib": delta(per_cond["C2"]["peak_vram_mib"], per_cond[other]["peak_vram_mib"]),
            }

    equiv_path = results_dir / "output_equivalence_diagnostic.json"
    if not equiv_path.exists():
        found = list(results_dir.rglob("output_equivalence_diagnostic.json"))
        equiv_path = found[0] if found else equiv_path
    mismatches = None
    if equiv_path.exists():
        mismatches = json.loads(equiv_path.read_text(encoding="utf-8")).get("mismatches")

    out = {
        "classification": "RECOMPUTED_RESULT",
        "experiment_id": "SGLANG-BCG-KAGGLE-20260826",
        "recomputed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "metrics_path": str(metrics_path),
        "n_metric_rows": len(rows),
        "per_condition": per_cond,
        "comparisons": comparisons,
        "output_equivalence_mismatches": mismatches,
        "claim_ceiling": "ONE_MODEL_ONE_KAGGLE_GPU_RUNTIME_STRESS_ONLY",
        "evidence_state": "ENGINEERING_RUNTIME_EVIDENCE_PROVISIONAL",
    }
    out_path = results_dir / "RECOMPUTED_SUMMARY.json"
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    out_path.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    (results_dir / "RECOMPUTED_SUMMARY.sha256").write_text(digest + "\n", encoding="utf-8")
    print(json.dumps({"RECOMPUTED_SUMMARY": str(out_path), "sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
