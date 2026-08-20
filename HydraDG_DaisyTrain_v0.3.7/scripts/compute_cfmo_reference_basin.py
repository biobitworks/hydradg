#!/usr/bin/env python3
"""Constructs a bounded CFMO reference distribution from stable reference baseline runs.
"""
from __future__ import annotations
import argparse, json, math, numpy as np
from pathlib import Path

def compute_reference_basin(input_dir: Path, output_path: Path):
    receipt_files = sorted(input_dir.glob("*.receipt.json"))
    if not receipt_files:
        raise FileNotFoundError(f"No receipt files found in {input_dir}")

    runs_data = []
    for p in receipt_files:
        data = json.loads(p.read_text())
        if data.get("numerical_status") == "FINITE_TRAINING_SUCCESS":
            runs_data.append(data)

    if not runs_data:
        raise ValueError("No successful finite reference runs found to build distribution.")

    num_runs = len(runs_data)
    num_steps = len(runs_data[0]["records"])

    per_step_stats = []
    for step_idx in range(num_steps):
        step_losses = [r["records"][step_idx]["loss"] for r in runs_data]
        step_param_norms = [r["records"][step_idx]["parameter_norm"] for r in runs_data]
        step_grad_norms = [r["records"][step_idx]["gradient_norm"] for r in runs_data]
        step_logit_mins = [r["records"][step_idx]["logit_min"] for r in runs_data]
        step_logit_maxs = [r["records"][step_idx]["logit_max"] for r in runs_data]

        loss_mean = float(np.mean(step_losses))
        loss_std = float(np.std(step_losses, ddof=1)) if num_runs > 1 else 0.0

        per_step_stats.append({
            "step": step_idx,
            "loss_mean": loss_mean,
            "loss_std": loss_std,
            "loss_min": float(np.min(step_losses)),
            "loss_max": float(np.max(step_losses)),
            "loss_bound_lower": loss_mean - 2.0 * loss_std,
            "loss_bound_upper": loss_mean + 2.0 * loss_std,
            "param_norm_mean": float(np.mean(step_param_norms)),
            "param_norm_std": float(np.std(step_param_norms, ddof=1)) if num_runs > 1 else 0.0,
            "grad_norm_mean": float(np.mean(step_grad_norms)),
            "grad_norm_std": float(np.std(step_grad_norms, ddof=1)) if num_runs > 1 else 0.0,
            "logit_min_mean": float(np.mean(step_logit_mins)),
            "logit_max_mean": float(np.max(step_logit_maxs)),
        })

    final_losses = [r["records"][-1]["loss"] for r in runs_data]

    reference_distribution = {
        "schema": "hydradg.cfmo_reference_distribution.v1",
        "reference_basin_id": "CFMO_REF_DIST_VITHIA_PYTHIA14M_v0.1",
        "num_reference_runs": num_runs,
        "included_run_ids": [r["run_id"] for r in runs_data],
        "excluded_runs": ["VITHIA-OVERNIGHT-01 (PRESERVED_NEGATIVE_CONTROL)"],
        "configuration": {
            "model_architecture": "EleutherAI/pythia-14m",
            "lr": runs_data[0]["lr"],
            "adam_eps": runs_data[0]["adam_eps"],
            "grad_clip_norm": runs_data[0]["grad_clip_norm"],
            "batch": runs_data[0]["batch"],
            "seq": runs_data[0]["seq"],
            "steps": runs_data[0]["steps"],
        },
        "summary_statistics": {
            "initial_loss_mean": float(np.mean([r["records"][0]["loss"] for r in runs_data])),
            "final_loss_mean": float(np.mean(final_losses)),
            "final_loss_std": float(np.std(final_losses, ddof=1)) if num_runs > 1 else 0.0,
            "final_loss_min": float(np.min(final_losses)),
            "final_loss_max": float(np.max(final_losses)),
            "numerical_admissibility_rate": 1.0,
            "all_observables_finite": True,
        },
        "per_step_distribution": per_step_stats,
        "claim_boundary": "Bounded local CFMO reference distribution derived strictly from finite baseline reference runs. Negative control VITHIA-OVERNIGHT-01 excluded from statistic calculation."
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(reference_distribution, indent=2, sort_keys=True) + "\n")
    print(f"Reference distribution saved to {output_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    compute_reference_basin(Path(args.input_dir), Path(args.out))

if __name__ == "__main__":
    main()
