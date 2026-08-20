"""Small GPT-NeoX/Pythia-compatible training fixture for divergence experiments.

Purpose:
- bounded reproducibility experiment, not competitive language modeling
- deterministic synthetic token stream by default
- checkpoint tensor custody and fixed-probe logits
- export enough state to compare runs across execution environments

The fixture uses the public EleutherAI/pythia-14m config and initializes from scratch.
It does NOT reproduce the user's historical Vithia corpus unless a future adapter supplies it.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, subprocess, sys, time
from pathlib import Path

def file_sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(8*1024*1024), b""):
            h.update(b)
    return h.hexdigest()

def canonical_tensor_hash(state):
    import torch
    h = hashlib.sha256()
    for name in sorted(state):
        t = state[name].detach().cpu().contiguous()
        h.update(name.encode("utf-8"))
        h.update(str(t.dtype).encode("ascii"))
        h.update(str(tuple(t.shape)).encode("ascii"))
        h.update(t.numpy().tobytes(order="C"))
    return h.hexdigest()

def environment_receipt():
    import torch
    r = {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "torch_num_threads": torch.get_num_threads(),
        "torch_num_interop_threads": torch.get_num_interop_threads(),
        "env": {k:os.environ.get(k) for k in [
            "OMP_NUM_THREADS","MKL_NUM_THREADS","CUBLAS_WORKSPACE_CONFIG",
            "CUDA_VISIBLE_DEVICES","PYTHONHASHSEED"
        ]},
    }
    if torch.cuda.is_available():
        r["cuda"] = torch.version.cuda
        r["cudnn"] = torch.backends.cudnn.version()
        r["gpu_name"] = torch.cuda.get_device_name(0)
        try:
            q = subprocess.check_output(
                ["nvidia-smi","--query-gpu=uuid,name,driver_version","--format=csv,noheader"],
                text=True,
            ).strip()
            r["nvidia_smi"] = q
        except Exception as e:
            r["nvidia_smi_error"] = repr(e)
    return r

def set_determinism(seed: int, deterministic: bool):
    import numpy as np, torch
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        torch.use_deterministic_algorithms(True)
        if torch.backends.cudnn.is_available():
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True

def build_model(seed: int):
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    torch.manual_seed(seed)
    config = AutoConfig.from_pretrained("EleutherAI/pythia-14m")
    return AutoModelForCausalLM.from_config(config)

def synthetic_batches(seed: int, steps: int, batch: int, seq: int, vocab: int):
    import torch
    g = torch.Generator(device="cpu").manual_seed(seed)
    for _ in range(steps):
        yield torch.randint(0, vocab, (batch, seq), generator=g, dtype=torch.long)

def train(run_id: str, outdir: Path, seed=314159, steps=24, batch=2, seq=128,
          lr=3e-4, deterministic=True, perturb_step=-1, perturb_token_delta=0):
    import torch
    outdir.mkdir(parents=True, exist_ok=True)
    set_determinism(seed, deterministic)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(seed).to(device)
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    vocab = model.config.vocab_size

    probe_gen = torch.Generator(device="cpu").manual_seed(seed + 777)
    probe = torch.randint(0, vocab, (1, 64), generator=probe_gen).to(device)
    records = []

    for step, ids_cpu in enumerate(synthetic_batches(seed+1, steps, batch, seq, vocab)):
        if step == perturb_step and perturb_token_delta:
            ids_cpu = ids_cpu.clone()
            ids_cpu[0,0] = (ids_cpu[0,0] + int(perturb_token_delta)) % vocab
        ids = ids_cpu.to(device)
        opt.zero_grad(set_to_none=True)
        out = model(input_ids=ids, labels=ids)
        out.loss.backward()
        opt.step()

        with torch.no_grad():
            logits = model(input_ids=probe).logits[:, -1, :].detach().cpu().float()
            topv, topi = torch.topk(logits, k=16, dim=-1)
        records.append({
            "step": step,
            "loss": float(out.loss.detach().cpu()),
            "state_hash": canonical_tensor_hash(model.state_dict()),
            "probe_top_ids": topi[0].tolist(),
            "probe_top_logits": topv[0].tolist(),
        })

    ckpt = outdir / f"{run_id}.pt"
    torch.save({"model":model.state_dict(),"optimizer":opt.state_dict()}, ckpt)
    receipt = {
        "run_id": run_id,
        "seed": seed,
        "steps": steps,
        "batch": batch,
        "seq": seq,
        "lr": lr,
        "deterministic_requested": deterministic,
        "perturb_step": perturb_step,
        "perturb_token_delta": perturb_token_delta,
        "environment": environment_receipt(),
        "final_state_hash": canonical_tensor_hash(model.state_dict()),
        "checkpoint_file_sha256": file_sha256(ckpt),
        "records": records,
    }
    rp = outdir / f"{run_id}.receipt.json"
    rp.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    return receipt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--outdir", default="runs")
    ap.add_argument("--seed", type=int, default=314159)
    ap.add_argument("--steps", type=int, default=24)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--seq", type=int, default=128)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--non-deterministic", action="store_true")
    ap.add_argument("--perturb-step", type=int, default=-1)
    ap.add_argument("--perturb-token-delta", type=int, default=0)
    args = ap.parse_args()
    receipt = train(
        args.run_id, Path(args.outdir), args.seed, args.steps, args.batch, args.seq,
        args.lr, not args.non_deterministic, args.perturb_step, args.perturb_token_delta,
    )
    print(json.dumps({k:receipt[k] for k in ["run_id","final_state_hash","checkpoint_file_sha256","environment"]}, indent=2))

if __name__ == "__main__":
    main()
