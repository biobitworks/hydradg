#!/usr/bin/env python3
"""Prepares (WITHOUT EXECUTING) the FCG Atom/Seed ablation experiment specification and runner.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def create_ablation_spec(output_path: Path):
    spec = {
        "schema": "hydradg.vithia_ablation_experiment_spec.v1",
        "experiment_id": "FMO-EXP-037-VITHIA-SEEDGRAPH-ABLATION-PREP",
        "execution_status": "PREPARED_UNEXECUTED",
        "preregistration_ts_utc": "2026-08-20T13:15:00Z",
        "objective": "Evaluate Pythia-14m baseline stability and convergence under controlled seed/atom perturbations against the bounded CFMO reference distribution.",
        "parent_reference_basin": "CFMO_REF_DIST_VITHIA_PYTHIA14M_v0.1",
        "ablation_matrices": [
            {
                "matrix_id": "MX-01-SEED-PERTURBATION",
                "description": "Varying random generator seed across 10 trials while holding hyperparameter baseline fixed.",
                "varied_parameter": "seed",
                "values": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
            },
            {
                "matrix_id": "MX-02-TOKEN-ATOM-ABLATION",
                "description": "Injecting single token perturbations at step t=10 and t=20 to measure distance from reference loss basin.",
                "varied_parameter": "token_perturbation",
                "values": [{"step": 10, "delta": 1}, {"step": 20, "delta": 5}]
            }
        ],
        "frozen_baseline_configuration": {
            "model_architecture": "EleutherAI/pythia-14m",
            "lr": 0.0001,
            "adam_eps": 1e-05,
            "grad_clip_norm": 1.0,
            "batch": 2,
            "seq": 128,
            "steps": 24
        },
        "admission_gates": {
            "all_observables_finite_required": True,
            "max_loss_deviation_sigmas": 3.0,
            "reference_basin_comparison_required": True
        },
        "claim_boundary": "PREPARED_UNEXECUTED experiment specification only. DO NOT EXECUTE until human operator issues explicit execution authorization."
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
    print(f"Ablation experiment spec written to {output_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    create_ablation_spec(Path(args.out))

if __name__ == "__main__":
    main()
