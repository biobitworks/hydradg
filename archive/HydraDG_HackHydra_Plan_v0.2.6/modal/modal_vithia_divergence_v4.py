"""Modal 1.5+ self-contained HydraDG/Vithia divergence launcher.

Why this file is self-contained:
- Modal detected live project files changing while the image was building.
- App source auto-inclusion is disabled.
- The remote function is cloudpickle-serialized.
- No add_local_file/add_local_dir mount participates in this run.

Run:
    modal run modal/modal_vithia_divergence_v4.py

The first image build is large because torch includes CUDA libraries. Subsequent runs
should reuse Modal's image cache when the pinned image recipe is unchanged.
"""
from __future__ import annotations

import json
import modal

app = modal.App("hydradg-vithia-divergence-v4", include_source=False)

image = (
    modal.Image.debian_slim(python_version="3.13")
    .uv_pip_install(
        "numpy==2.2.6",
        "torch==2.8.0",
        "transformers==4.55.0",
    )
)

volume = modal.Volume.from_name("hydradg-vithia-runs-v4", create_if_missing=True)
VOL = "/vol"


@app.function(
    image=image,
    gpu="T4",
    timeout=60 * 60,
    volumes={VOL: volume},
    single_use_containers=True,
    include_source=False,
    serialized=True,
)
def train_remote(
    run_id: str,
    perturb_step: int = -1,
    perturb_token_delta: int = 0,
    steps: int = 24,
):
    """Train a bounded Pythia-14M-compatible fixture and return an evidence receipt."""
    import hashlib
    import json
    import os
    import platform
    import random
    import subprocess
    import sys
    from pathlib import Path

    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, GPTNeoXConfig

    SEED = 314159
    BATCH = 2
    SEQ = 128
    LR = 3e-4

    def canonical_tensor_hash(state):
        h = hashlib.sha256()
        for name in sorted(state):
            t = state[name].detach().cpu().contiguous()
            h.update(name.encode("utf-8"))
            h.update(str(t.dtype).encode("ascii"))
            h.update(str(tuple(t.shape)).encode("ascii"))
            h.update(t.numpy().tobytes(order="C"))
        return h.hexdigest()

    def file_sha256(path: Path):
        h = hashlib.sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
                h.update(block)
        return h.hexdigest()

    def environment_receipt():
        r = {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "torch": torch.__version__,
            "transformers": __import__("transformers").__version__,
            "numpy": np.__version__,
            "cuda_available": torch.cuda.is_available(),
            "torch_num_threads": torch.get_num_threads(),
            "torch_num_interop_threads": torch.get_num_interop_threads(),
            "env": {
                k: os.environ.get(k)
                for k in [
                    "OMP_NUM_THREADS",
                    "MKL_NUM_THREADS",
                    "CUBLAS_WORKSPACE_CONFIG",
                    "CUDA_VISIBLE_DEVICES",
                    "PYTHONHASHSEED",
                ]
            },
        }
        if torch.cuda.is_available():
            r["cuda"] = torch.version.cuda
            r["cudnn"] = torch.backends.cudnn.version()
            r["gpu_name"] = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            r["gpu_total_memory"] = props.total_memory
            r["gpu_capability"] = [props.major, props.minor]
            try:
                r["nvidia_smi"] = subprocess.check_output(
                    [
                        "nvidia-smi",
                        "--query-gpu=uuid,name,driver_version",
                        "--format=csv,noheader",
                    ],
                    text=True,
                ).strip()
            except Exception as exc:
                r["nvidia_smi_error"] = repr(exc)
        return r

    # Pin both PyTorch CPU thread pools before any tensor/model work.
    # This removes a confound observed in the completed quick matrix, where
    # inter-op thread counts differed by scheduled GPU environment.
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)

    # Pin randomness before model initialization.
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

    # Required by deterministic CUDA matmul paths when applicable.
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    torch.use_deterministic_algorithms(True)
    if torch.backends.cudnn.is_available():
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Freeze the public Pythia-14M architecture inside the experiment.
    # Source parameters correspond to EleutherAI/pythia-14m config.json as
    # published in Hugging Face commit 94f7c35d5e9f2e9bac8ca839329f505b4d007d5d.
    # We intentionally initialize weights from scratch so network/model-weight
    # downloads cannot become an uncontrolled divergence source.
    frozen_config = {
        "architectures": ["GPTNeoXForCausalLM"],
        "attention_bias": True,
        "attention_dropout": 0.0,
        "bos_token_id": 0,
        "classifier_dropout": 0.1,
        "eos_token_id": 0,
        "hidden_act": "gelu",
        "hidden_dropout": 0.0,
        "hidden_size": 128,
        "initializer_range": 0.02,
        "intermediate_size": 512,
        "layer_norm_eps": 1e-5,
        "max_position_embeddings": 2048,
        "model_type": "gpt_neox",
        "num_attention_heads": 4,
        "num_hidden_layers": 6,
        "rope_scaling": None,
        "rotary_emb_base": 10000,
        "rotary_pct": 0.25,
        "tie_word_embeddings": False,
        "use_cache": False,
        "use_parallel_residual": True,
        "vocab_size": 50304,
    }
    config_source = {
        "repository": "EleutherAI/pythia-14m",
        "source_commit": "94f7c35d5e9f2e9bac8ca839329f505b4d007d5d",
        "source_file": "config.json",
        "mode": "FROZEN_ARCHITECTURE_FROM_PUBLIC_SOURCE",
    }
    config_sha256 = hashlib.sha256(
        json.dumps(frozen_config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    config = GPTNeoXConfig(**frozen_config)
    config_dict = config.to_dict()

    torch.manual_seed(SEED)
    model = AutoModelForCausalLM.from_config(config).to(device=device, dtype=torch.float32)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    vocab = model.config.vocab_size

    data_gen = torch.Generator(device="cpu").manual_seed(SEED + 1)
    probe_gen = torch.Generator(device="cpu").manual_seed(SEED + 777)
    probe = torch.randint(0, vocab, (1, 64), generator=probe_gen).to(device)

    records = []
    first_perturbation_receipt = None

    for step in range(steps):
        ids_cpu = torch.randint(
            0, vocab, (BATCH, SEQ), generator=data_gen, dtype=torch.long
        )

        if step == perturb_step and perturb_token_delta:
            original = int(ids_cpu[0, 0])
            ids_cpu = ids_cpu.clone()
            ids_cpu[0, 0] = (ids_cpu[0, 0] + int(perturb_token_delta)) % vocab
            first_perturbation_receipt = {
                "step": step,
                "coordinate": [0, 0],
                "original_token": original,
                "perturbed_token": int(ids_cpu[0, 0]),
                "token_delta": int(perturb_token_delta),
            }

        ids = ids_cpu.to(device)
        optimizer.zero_grad(set_to_none=True)
        out = model(input_ids=ids, labels=ids)
        out.loss.backward()
        optimizer.step()

        with torch.no_grad():
            logits = (
                model(input_ids=probe)
                .logits[:, -1, :]
                .detach()
                .cpu()
                .float()
            )
            topv, topi = torch.topk(logits, k=16, dim=-1)

        records.append(
            {
                "step": step,
                "loss": float(out.loss.detach().cpu()),
                "state_hash": canonical_tensor_hash(model.state_dict()),
                "probe_top_ids": topi[0].tolist(),
                "probe_top_logits": topv[0].tolist(),
            }
        )

    outdir = Path(VOL) / "runs"
    outdir.mkdir(parents=True, exist_ok=True)

    checkpoint_path = outdir / f"{run_id}.pt"
    torch.save(
        {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "config": config_dict,
        },
        checkpoint_path,
    )

    receipt = {
        "schema": "hydradg.run_receipt.v0.2.5",
        "run_id": run_id,
        "seed": SEED,
        "steps": steps,
        "batch": BATCH,
        "seq": SEQ,
        "lr": LR,
        "deterministic_requested": True,
        "perturb_step": perturb_step,
        "perturb_token_delta": perturb_token_delta,
        "perturbation_receipt": first_perturbation_receipt,
        "environment": environment_receipt(),
        "model_config_sha256": config_sha256,
        "model_config_source": config_source,
        "model_config": config_dict,
        "final_state_hash": canonical_tensor_hash(model.state_dict()),
        "checkpoint_file_sha256": file_sha256(checkpoint_path),
        "records": records,
    }

    receipt_path = outdir / f"{run_id}.receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    volume.commit()

    # Keep the local return small; detailed records live on the Modal Volume.
    return {
        "run_id": run_id,
        "final_state_hash": receipt["final_state_hash"],
        "checkpoint_file_sha256": receipt["checkpoint_file_sha256"],
        "model_config_sha256": receipt["model_config_sha256"],
        "environment": receipt["environment"],
        "perturbation_receipt": first_perturbation_receipt,
        "receipt_volume_path": str(receipt_path),
    }


@app.local_entrypoint()
def main(
    quick: bool = False,
):
    """Run the initial cross-GPU matrix.

    --quick uses 4 steps for an inexpensive build/runtime smoke test.
    Full mode uses 24 steps.
    """
    steps = 4 if quick else 24
    matrix = [
        ("t4_a", "T4", -1, 0),
        ("t4_b", "T4", -1, 0),
        ("l4_a", "L4", -1, 0),
        ("a10_a", "A10", -1, 0),
        ("t4_perturb", "T4", 2 if quick else 8, 1),
    ]

    results = []
    for run_id, gpu, perturb_step, perturb_delta in matrix:
        fn = train_remote.with_options(gpu=gpu)
        result = fn.remote(
            run_id,
            perturb_step,
            perturb_delta,
            steps,
        )
        result["requested_gpu"] = gpu
        results.append(result)
        print(json.dumps(result, indent=2, sort_keys=True))

    print("\n=== MATRIX SUMMARY ===")
    print(json.dumps(results, indent=2, sort_keys=True))
