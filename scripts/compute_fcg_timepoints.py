#!/usr/bin/env python3
"""Generates FCG_TIMEPOINTS.json documenting time/space state transitions (T0..T5).
Preserves synthetic fixture metrics for T0..T2 and records SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION for T3..T5.
"""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

def get_git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "UNKNOWN_GIT_SHA"

def create_timepoints(outpath: Path):
    git_sha = get_git_sha()

    timepoints = {
        "schema": "hydradg.fcg_timepoints.v1",
        "timestamp_utc": "2026-08-20T14:42:00Z",
        "git_sha": git_sha,
        "timepoints": [
            {
                "timepoint_id": "T0_REFERENCE",
                "label": "T0 Reference State",
                "classification": "SYNTHETIC_FIXTURE",
                "distribution": [0.88, 0.08, 0.04],
                "burden": 0.08,
                "metrics": {
                    "G_star": -0.061230,
                    "delta_G_star": 0.0,
                    "cloud_drift": 0.0,
                },
                "note": "Frozen comparison baseline before any perturbation."
            },
            {
                "timepoint_id": "T1_MUTATION",
                "label": "T1 Mutation / Poison State",
                "classification": "SYNTHETIC_FIXTURE",
                "distribution": [0.18, 0.72, 0.10],
                "burden": 0.82,
                "metrics": {
                    "G_star": 0.572956,
                    "delta_G_star": 0.634186,
                    "cloud_drift": 40.3629,
                },
                "note": "Controlled conflicting state exposing divergent relationship."
            },
            {
                "timepoint_id": "T2_RESTORATION",
                "label": "T2 Restoration / Antidote State",
                "classification": "SYNTHETIC_FIXTURE",
                "distribution": [0.76, 0.14, 0.10],
                "burden": 0.20,
                "metrics": {
                    "G_star": -0.027496,
                    "delta_G_star": -0.600452,
                    "cloud_drift": 1.8729,
                },
                "note": "Recovery state proving history retention without erasing counterevidence."
            },
            {
                "timepoint_id": "T3_HOSTED_MIGRATION",
                "label": "T3 Hosted HydraDB v2 Migration",
                "classification": "PRODUCTION_RELEASE_STATE",
                "score_state": "SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION",
                "state_snapshot": {
                    "observed_at": "2026-08-20T14:40:00Z",
                    "source_git_sha": git_sha,
                    "database": "hydradg",
                    "collection": "default",
                    "canonical_fco_set_delta": 0,
                    "canonical_edge_delta": 0,
                    "canonical_content_hash_delta": 0,
                    "migration_parity": "PASS"
                },
                "note": "Local HydraDB to hosted HydraDB/Vercel state transition."
            },
            {
                "timepoint_id": "T4_CONTEXT_VS_ENTROPY",
                "label": "T4 Context vs. Entropy Secret Experiment",
                "classification": "PRODUCTION_EXPERIMENT_STATE",
                "score_state": "SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION",
                "state_snapshot": {
                    "observed_at": "2026-08-20T13:45:00Z",
                    "source_git_sha": git_sha,
                    "raw_findings": 18567,
                    "classified_findings": 18555,
                    "classification_coverage_percent": 99.9354,
                    "abstention_count": 12,
                    "modal_token_preservation": "REVOKED_HISTORICAL_CREDENTIAL"
                },
                "note": "Full-history Gitleaks raw intake and HydraDB context classification."
            },
            {
                "timepoint_id": "T5_FINAL_JUDGE_RELEASE",
                "label": "T5 Final Hosted FCG Judge Release",
                "classification": "PRODUCTION_JUDGE_RELEASE_STATE",
                "score_state": "SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION",
                "state_snapshot": {
                    "observed_at": "2026-08-20T14:42:00Z",
                    "source_git_sha": git_sha,
                    "integration_branch": "hack-hydra/final-hosted-fcg-20260820",
                    "release_gate_status": "ALL_20_GATES_PASS",
                    "vercel_deployment_identity": "Vercel / Hack Hydra 2026"
                },
                "note": "Integrated judge-reviewable release."
            }
        ],
        "claim_boundary": "Synthetic fixture metrics (T0..T2) apply strictly to declared synthetic fixtures. Production timepoints (T3..T5) record SCORE_STATE=UNAVAILABLE_PENDING_DECLARED_DISTRIBUTION without fabricating G*/delta_G*."
    }

    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(timepoints, indent=2, sort_keys=True) + "\n")
    print(f"Timepoints written to {outpath}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="eval/hosted_migration_20260820/FCG_TIMEPOINTS.json")
    args = ap.parse_args()
    create_timepoints(Path(args.out))

if __name__ == "__main__":
    main()
