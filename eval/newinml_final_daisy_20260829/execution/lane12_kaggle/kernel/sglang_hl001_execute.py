#!/usr/bin/env python3
"""Kaggle CUDA fallback for SGLANG-HL-001 — frozen identity, 24-cell canary."""
import hashlib
import json
import os
import secrets
import subprocess
import time
import urllib.request

MODEL_ID = "Qwen/Qwen3-8B"
SGLANG_SHA = "acc918b3ece60af20321612b8ad204bdba8fcb80"
CONDITIONS = ["CONTROL", "INVALID_PROOF", "REPLAYED_PROOF", "BROKEN_AUTHORIZATION_EDGE"]
MODES = {
    "EAGER_DISABLED": {"flag": "--disable-cuda-graph"},
    "TC_PIECEWISE": {"flag": "--cuda-graph-max-bs 1"},
    "BREAKABLE": {"flag": "--enable-breakable-cuda-graph", "env": {"SGLANG_USE_BREAKABLE_CUDA_GRAPH": "1"}},
}
PORT = 30000
OUT = "/kaggle/working/hydradg_sglang"
SGLANG_INSTALL_LOG = f"{OUT}/sglang_install.log"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(cmd: str, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)


os.makedirs(OUT, exist_ok=True)

# CUDA proof
run("nvidia-smi -L > /kaggle/working/nvidia_smi.txt")
p = run(
    'python3 -c "import torch,json; print(json.dumps({\'torch\':torch.__version__,\'cuda\':torch.cuda.is_available(),\'n\':torch.cuda.device_count(),\'name\':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}))"'
)
tout = p.stdout
cuda = json.loads(tout.strip()) if tout.strip() else {}
open(f"{OUT}/cuda_proof.json", "w").write(json.dumps(cuda, indent=2))

# HF auth for gated model weights (env names only in receipts; value from Kaggle secrets)
hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
if hf_token:
    run("python3 -m pip install -q huggingface_hub")
    run(f"python3 -c \"from huggingface_hub import login; login(token={json.dumps(hf_token)})\"")

# Install pinned SGLang with logged errors
if run("python3 -c 'import sglang'").returncode != 0:
    run("python3 -m pip install -q --upgrade pip setuptools wheel")
    inst = run(
        f"python3 -m pip install -q 'sglang[all] @ git+https://github.com/sgl-project/sglang.git@{SGLANG_SHA}' "
        f"> {SGLANG_INSTALL_LOG} 2>&1",
        timeout=2400,
    )
    open(f"{OUT}/sglang_install_exit.txt", "w").write(str(inst.returncode))

p = run("python3 -c 'import sglang; print(getattr(sglang,\"__version__\",\"unknown\"))'")
sglang_ver = p.stdout.strip()
sglang_installed = p.returncode == 0
open(f"{OUT}/sglang_import_check.json", "w").write(
    json.dumps({"installed": sglang_installed, "version": sglang_ver, "stderr": p.stderr[:500]}, indent=2)
)

if not sglang_installed:
    summary = {
        "provider": "kaggle",
        "cuda": cuda,
        "sglang_installed": False,
        "sglang_git_sha_pin": SGLANG_SHA,
        "model_id": MODEL_ID,
        "terminal_state": "SGLANG_INSTALL_FAILED",
        "install_log_head": open(SGLANG_INSTALL_LOG).read()[:2000] if os.path.exists(SGLANG_INSTALL_LOG) else None,
        "results": [],
    }
    open(f"{OUT}/execution_results.json", "w").write(json.dumps(summary, indent=2))
    print(json.dumps({"ok": False, "reason": "SGLANG_INSTALL_FAILED", "cuda": cuda.get("cuda")}))
    raise SystemExit(2)


def start_server(mode_name: str, cfg: dict) -> bool:
    env = os.environ.copy()
    env.update(cfg.get("env", {}))
    flag = cfg.get("flag", "")
    run("pkill -f sglang.launch_server 2>/dev/null; sleep 2")
    run(
        f"nohup python3 -m sglang.launch_server --model-path {MODEL_ID} --host 0.0.0.0 --port {PORT} {flag} "
        f"> {OUT}/server_{mode_name}.log 2>&1 &",
        env=env,
    )
    for _ in range(120):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(5)
    return False


def infer(prompt: str, max_tokens: int = 64):
    body = json.dumps({"text": prompt, "sampling_params": {"temperature": 0, "max_new_tokens": max_tokens}}).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/generate", data=body, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = r.read().decode()
    return resp, time.time() - t0


results = []
nonce = f"HYDRADG_SGLANG_CANARY_{int(time.time())}_{secrets.token_hex(4)}"
nonce_prompt = f"Return ONLY JSON with key nonce equal to exactly: {nonce}"

for mode_name, cfg in MODES.items():
    if not start_server(mode_name, cfg):
        results.append({"mode": mode_name, "server_started": False})
        continue
    cells = []
    if mode_name == list(MODES.keys())[0]:
        try:
            resp, lat = infer(nonce_prompt)
            cells.append(
                {
                    "type": "FRESH_NONCE",
                    "nonce_sha256": sha(nonce.encode()),
                    "pass": nonce in resp,
                    "latency_s": lat,
                }
            )
        except Exception as e:
            cells.append({"type": "FRESH_NONCE", "pass": False, "error": str(e)[:200]})
    for cond in CONDITIONS:
        for rep in [1, 2]:
            cell_id = f"HL-{cond}-R{rep}-{mode_name}"
            prompt = f"HydraDG SGLang cell {cell_id}. Return ONLY JSON with keys cell_id,condition,decision. condition={cond}."
            try:
                resp, lat = infer(prompt)
                cells.append(
                    {
                        "cell_id": cell_id,
                        "runtime_mode": mode_name,
                        "prompt_sha256": sha(prompt.encode()),
                        "response_sha256": sha(resp.encode()),
                        "latency_s": lat,
                        "terminal_state": "PASS",
                    }
                )
            except Exception as e:
                cells.append({"cell_id": cell_id, "terminal_state": "FAIL", "error": str(e)[:200]})
    results.append({"mode": mode_name, "server_started": True, "cells": cells})

summary = {
    "provider": "kaggle",
    "cuda": cuda,
    "sglang_version": sglang_ver,
    "sglang_git_sha_pin": SGLANG_SHA,
    "model_id": MODEL_ID,
    "results": results,
}
open(f"{OUT}/execution_results.json", "w").write(json.dumps(summary, indent=2))
print(json.dumps({"ok": True, "out": OUT, "cuda": cuda.get("cuda")}))
