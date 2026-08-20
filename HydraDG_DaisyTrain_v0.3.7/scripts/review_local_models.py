#!/usr/bin/env python3
"""Queries local Ollarma models to generate LOCAL_MODEL_HYPOTHESIS review annotations.
Outputs are strictly NON-LOAD-BEARING.
"""
from __future__ import annotations
import argparse, json, urllib.request, urllib.parse
from pathlib import Path

def query_ollama(model_tag: str, prompt: str, endpoint: str = "http://127.0.0.1:11434/api/generate") -> str:
    payload = {
        "model": model_tag,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 512,
        }
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("response", "").strip()

def get_model_metadata(model_tag: str, endpoint: str = "http://127.0.0.1:11434/api/tags") -> dict:
    req = urllib.request.Request(endpoint)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        for m in data.get("models", []):
            if m.get("name") == model_tag:
                return m
    return {"name": model_tag, "details": "unknown"}

def run_review(model_tag: str, role_class: str, ref_dist_path: Path, failure_audit_path: Path, output_path: Path):
    ref_dist = json.loads(ref_dist_path.read_text())
    failure_audit = json.loads(failure_audit_path.read_text())
    meta = get_model_metadata(model_tag)

    prompt = f"""You are acting as a local model reviewer ({role_class}) inspecting Pythia-14m training baseline experiments.

HISTORICAL FAILURE AUDIT:
- Failure ID: {failure_audit['historical_run_id']}
- Classification: {failure_audit['classification']}
- Step 0 Loss: {failure_audit['audit_findings']['initial_loss']}
- First non-finite step: Step 1 (Loss = NaN)
- Failure Cause: {failure_audit['failure_mechanism_summary']}

CFMO REFERENCE DISTRIBUTION:
- Included runs: {ref_dist['num_reference_runs']} reference runs
- Baseline Repair: AdamW lr={ref_dist['configuration']['lr']}, eps={ref_dist['configuration']['adam_eps']}, grad_clip_norm={ref_dist['configuration']['grad_clip_norm']}
- All observables finite: {ref_dist['summary_statistics']['all_observables_finite']}
- Initial Loss Mean: {ref_dist['summary_statistics']['initial_loss_mean']:.4f}
- Final Loss Mean: {ref_dist['summary_statistics']['final_loss_mean']:.4f} (std: {ref_dist['summary_statistics']['final_loss_std']:.4f})

Provide a concise 3-bullet technical evaluation comparing the historical failure with the repaired CFMO reference distribution, and state whether the repaired baseline is suitable for future ablation studies.
"""

    print(f"Querying local model {model_tag} ({role_class})...")
    hypothesis = query_ollama(model_tag, prompt)

    result = {
        "schema": "hydradg.local_model_hypothesis_review.v1",
        "authorship": "LOCAL_MODEL_HYPOTHESIS",
        "load_bearing": False,
        "reviewer_role": role_class,
        "model_metadata": {
            "provider": "ollama",
            "model_tag": model_tag,
            "digest": meta.get("digest"),
            "size_bytes": meta.get("size"),
            "details": meta.get("details"),
            "endpoint": "http://127.0.0.1:11434"
        },
        "hypothesis_text": hypothesis,
        "claim_boundary": "LOCAL_MODEL_HYPOTHESIS only. Strictly non-load-bearing. Cannot declare scientific validity or alter empirical findings."
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Review saved to {output_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-tag", required=True)
    ap.add_argument("--role-class", required=True)
    ap.add_argument("--ref-dist", required=True)
    ap.add_argument("--failure-audit", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    run_review(
        args.model_tag, args.role_class,
        Path(args.ref_dist), Path(args.failure_audit), Path(args.out)
    )

if __name__ == "__main__":
    main()
