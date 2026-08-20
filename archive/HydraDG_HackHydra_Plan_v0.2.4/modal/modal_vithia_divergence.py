"""Modal launcher for HydraDG/Vithia divergence experiments.

After authenticating locally:
    pip install modal
    python3 -m modal setup
    modal run modal/modal_vithia_divergence.py

Default matrix:
- two fresh T4 containers
- one L4
- one A10
- one controlled T4 perturbation

Each run records the actual GPU UUID/name. A "different computer/device" claim is only
admitted when receipts establish different physical/device identifiers or materially
different declared hardware classes.
"""
from __future__ import annotations
import json, pathlib, modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
app = modal.App("hydradg-vithia-divergence")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .uv_pip_install(
        "torch==2.8.0",
        "transformers==4.55.0",
        "numpy==2.2.6",
    )
    .add_local_file(str(ROOT/"scripts/vithia_divergence_core.py"), "/opt/hydradg/vithia_divergence_core.py")
)

volume = modal.Volume.from_name("hydradg-vithia-runs", create_if_missing=True)
VOL = "/vol"

@app.function(
    image=image,
    gpu="T4",
    timeout=60*60,
    volumes={VOL: volume},
    single_use_containers=True,
)
def train_remote(run_id: str, perturb_step: int = -1, perturb_token_delta: int = 0):
    import importlib.util, pathlib, json
    spec = importlib.util.spec_from_file_location("core", "/opt/hydradg/vithia_divergence_core.py")
    core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
    outdir = pathlib.Path(VOL) / "runs"
    receipt = core.train(
        run_id=run_id,
        outdir=outdir,
        seed=314159,
        steps=24,
        batch=2,
        seq=128,
        lr=3e-4,
        deterministic=True,
        perturb_step=perturb_step,
        perturb_token_delta=perturb_token_delta,
    )
    volume.commit()
    # Do not return the full step history to the caller unnecessarily.
    return {
        "run_id": receipt["run_id"],
        "final_state_hash": receipt["final_state_hash"],
        "checkpoint_file_sha256": receipt["checkpoint_file_sha256"],
        "environment": receipt["environment"],
        "perturb_step": perturb_step,
        "perturb_token_delta": perturb_token_delta,
    }

@app.local_entrypoint()
def main():
    matrix = [
        ("t4_a","T4",-1,0),
        ("t4_b","T4",-1,0),
        ("l4_a","L4",-1,0),
        ("a10_a","A10",-1,0),
        ("t4_perturb","T4",8,1),
    ]
    results = []
    for run_id, gpu, ps, pd in matrix:
        f = train_remote.with_options(gpu=gpu)
        r = f.remote(run_id, ps, pd)
        r["requested_gpu"] = gpu
        results.append(r)
        print(json.dumps(r, indent=2))
    print("\n=== MATRIX SUMMARY ===")
    print(json.dumps(results, indent=2))
