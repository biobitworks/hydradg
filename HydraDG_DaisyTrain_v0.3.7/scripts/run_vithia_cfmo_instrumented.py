#!/usr/bin/env python3
"""Fully instrumented Vithia/Pythia training runner for baseline repair, numerical break detection, and CFMO reference basin construction.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, platform, random, sys, time
from pathlib import Path

def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def canonical_tensor_hash(state: dict) -> str:
    import torch
    h = hashlib.sha256()
    for name in sorted(state):
        t = state[name].detach().cpu().contiguous()
        h.update(name.encode("utf-8"))
        h.update(str(t.dtype).encode("ascii"))
        h.update(str(tuple(t.shape)).encode("ascii"))
        h.update(t.numpy().tobytes(order="C"))
    return h.hexdigest()

def environment_receipt() -> dict:
    import torch
    r = {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "torch_num_threads": torch.get_num_threads(),
        "torch_num_interop_threads": torch.get_num_interop_threads(),
        "env": {k: os.environ.get(k) for k in [
            "OMP_NUM_THREADS", "MKL_NUM_THREADS", "CUBLAS_WORKSPACE_CONFIG",
            "CUDA_VISIBLE_DEVICES", "PYTHONHASHSEED"
        ]},
    }
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

def compute_param_metrics(model):
    import torch
    total_sq = 0.0
    max_abs = 0.0
    all_finite = True
    for p in model.parameters():
        if p is None: continue
        val = p.detach().cpu()
        if not torch.isfinite(val).all():
            all_finite = False
        total_sq += float(torch.sum(val ** 2))
        max_abs = max(max_abs, float(torch.max(torch.abs(val))))
    return math.sqrt(total_sq), max_abs, all_finite

def compute_grad_metrics(model):
    import torch
    total_sq = 0.0
    max_abs = 0.0
    all_finite = True
    for p in model.parameters():
        if p is None or p.grad is None: continue
        g = p.grad.detach().cpu()
        if not torch.isfinite(g).all():
            all_finite = False
        total_sq += float(torch.sum(g ** 2))
        max_abs = max(max_abs, float(torch.max(torch.abs(g))))
    return math.sqrt(total_sq), max_abs, all_finite

def train(run_id: str, outdir: Path, seed=314159, steps=24, batch=2, seq=128,
          lr=3e-4, grad_clip_norm=0.0, adam_eps=1e-8, deterministic=True,
          intervention_id: str = None, parent_config: str = None):
    import torch
    outdir.mkdir(parents=True, exist_ok=True)
    set_determinism(seed, deterministic)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(seed).to(device)
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, eps=adam_eps)
    vocab = model.config.vocab_size

    probe_gen = torch.Generator(device="cpu").manual_seed(seed + 777)
    probe = torch.randint(0, vocab, (1, 64), generator=probe_gen).to(device)
    records = []

    earliest_break_step = None
    break_reason = None
    has_break = False

    t_start = time.time()

    for step, ids_cpu in enumerate(synthetic_batches(seed + 1, steps, batch, seq, vocab)):
        step_start = time.time()
        ids = ids_cpu.to(device)
        opt.zero_grad(set_to_none=True)
        
        out = model(input_ids=ids, labels=ids)
        loss_val = float(out.loss.detach().cpu())
        finite_loss = math.isfinite(loss_val)

        out.loss.backward()

        grad_norm, max_abs_grad, finite_grads = compute_grad_metrics(model)

        if grad_clip_norm > 0.0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=grad_clip_norm)

        opt.step()

        param_norm, max_abs_param, finite_params = compute_param_metrics(model)

        with torch.no_grad():
            probe_logits = model(input_ids=probe).logits[:, -1, :].detach().cpu().float()
            finite_logits = torch.isfinite(probe_logits).all().item()
            logit_min = float(torch.min(probe_logits)) if finite_logits else float("nan")
            logit_max = float(torch.max(probe_logits)) if finite_logits else float("nan")
            topv, topi = torch.topk(probe_logits, k=16, dim=-1)

        finite_t = finite_loss and finite_grads and finite_params and finite_logits

        if not finite_t and not has_break:
            has_break = True
            earliest_break_step = step
            break_reason = []
            if not finite_loss: break_reason.append("NON_FINITE_LOSS")
            if not finite_grads: break_reason.append("NON_FINITE_GRADIENTS")
            if not finite_params: break_reason.append("NON_FINITE_PARAMETERS")
            if not finite_logits: break_reason.append("NON_FINITE_LOGITS")
            break_reason = "|".join(break_reason)

        records.append({
            "step": step,
            "loss": loss_val if finite_loss else None,
            "finite_loss": finite_loss,
            "learning_rate": lr,
            "gradient_norm": grad_norm if finite_grads else None,
            "max_abs_gradient": max_abs_grad if finite_grads else None,
            "finite_gradients": finite_grads,
            "parameter_norm": param_norm if finite_params else None,
            "max_abs_parameter": max_abs_param if finite_params else None,
            "finite_parameters": finite_params,
            "logit_min": logit_min if finite_logits else None,
            "logit_max": logit_max if finite_logits else None,
            "finite_logits": finite_logits,
            "finite_t": finite_t,
            "state_hash": canonical_tensor_hash(model.state_dict()),
            "probe_top_ids": topi[0].tolist() if finite_logits else [],
            "probe_top_logits": [float(x) for x in topv[0].tolist()] if finite_logits else [],
            "step_wall_s": time.time() - step_start,
        })

    ckpt = outdir / f"{run_id}.pt"
    torch.save({"model": model.state_dict(), "optimizer": opt.state_dict()}, ckpt)
    
    receipt = {
        "schema": "hydradg.vithia_instrumented_run.v1",
        "run_id": run_id,
        "seed": seed,
        "steps": steps,
        "batch": batch,
        "seq": seq,
        "lr": lr,
        "grad_clip_norm": grad_clip_norm,
        "adam_eps": adam_eps,
        "deterministic_requested": deterministic,
        "intervention_id": intervention_id,
        "parent_config": parent_config,
        "numerical_status": "TRAINING_NUMERICAL_BREAK" if has_break else "FINITE_TRAINING_SUCCESS",
        "earliest_break_step": earliest_break_step,
        "break_reason": break_reason,
        "total_wall_s": time.time() - t_start,
        "environment": environment_receipt(),
        "final_state_hash": canonical_tensor_hash(model.state_dict()),
        "checkpoint_file_sha256": file_sha256(ckpt),
        "records": records,
    }
    rp = outdir / f"{run_id}.receipt.json"
    rp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
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
    ap.add_argument("--grad-clip-norm", type=float, default=0.0)
    ap.add_argument("--adam-eps", type=float, default=1e-8)
    ap.add_argument("--intervention-id", type=str, default=None)
    ap.add_argument("--parent-config", type=str, default=None)
    ap.add_argument("--non-deterministic", action="store_true")
    args = ap.parse_args()

    receipt = train(
        args.run_id, Path(args.outdir), args.seed, args.steps, args.batch, args.seq,
        args.lr, args.grad_clip_norm, args.adam_eps, not args.non_deterministic,
        args.intervention_id, args.parent_config
    )
    print(json.dumps({
        "run_id": receipt["run_id"],
        "numerical_status": receipt["numerical_status"],
        "earliest_break_step": receipt["earliest_break_step"],
        "final_state_hash": receipt["final_state_hash"],
        "checkpoint_file_sha256": receipt["checkpoint_file_sha256"]
    }, indent=2))

if __name__ == "__main__":
    main()
