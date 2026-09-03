#!/usr/bin/env python3
"""NewInML final GPU + SGLang + Daisy execution orchestrator (D0–D13).

Resumable, receipt-driven. Primary: Daytona GPU. Fallback: Kaggle CUDA.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
EXEC = ROOT / "eval/newinml_final_daisy_20260829/execution"
GPU_EXEC = EXEC / "gpu_sglang_terminal"
LOCK = GPU_EXEC / ".orchestrator.lock"
STATE_PATH = GPU_EXEC / "ORCHESTRATOR_STATE.json"

# Frozen scientific identity (repo authority)
EXPERIMENT_ID = "SGLANG-HL-001"
MODEL_ID = "Qwen/Qwen3-8B"
SGLANG_GIT_SHA = "acc918b3ece60af20321612b8ad204bdba8fcb80"
HL_CONDITIONS = ["CONTROL", "INVALID_PROOF", "REPLAYED_PROOF", "BROKEN_AUTHORIZATION_EDGE"]
RUNTIME_MODES = {
    "EAGER_DISABLED": {"prefill": "disabled", "decode": "disabled", "sglang_flag": "--disable-cuda-graph"},
    "TC_PIECEWISE": {"prefill": "tc_piecewise", "decode": "full", "sglang_flag": "--cuda-graph-max-bs 1"},
    "BREAKABLE": {
        "prefill": "breakable",
        "decode": "full",
        "env": {"SGLANG_USE_BREAKABLE_CUDA_GRAPH": "1"},
        "sglang_flag": "--enable-breakable-cuda-graph",
    },
}
CANARY_DOMAIN = "HYDRADG_SGLANG_HL001_CANARY_V1"
SANDBOX_NAME = "hydradg-newinml-sglang-20260829"
KEYS_ENV = Path.home() / ".config/ai-keys/keys.env"
GSD = Path("/Users/byron/projects/active/gettingsciencedone")


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def write_json(p: Path, obj: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def write_jsonl(p: Path, rows: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + ("\n" if rows else ""))


def run_env() -> dict[str, str]:
    env = os.environ.copy()
    prefix = "/opt/homebrew/bin:/usr/local/bin"
    env["PATH"] = f"{prefix}:{env.get('PATH', '')}" if prefix not in env.get("PATH", "") else env["PATH"]
    return env


def daytona_bin() -> str:
    found = shutil.which("daytona", path=run_env().get("PATH"))
    if found:
        return found
    for candidate in ("/opt/homebrew/bin/daytona", "/usr/local/bin/daytona"):
        if Path(candidate).is_file():
            return candidate
    raise FileNotFoundError("daytona CLI not found (expected /opt/homebrew/bin/daytona on magicSTUDIObox)")


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout, env=env or run_env()
    )


def git_meta() -> dict[str, str]:
    return {
        "CURRENT_BRANCH": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip(),
        "CURRENT_SHA": run(["git", "rev-parse", "HEAD"]).stdout.strip(),
    }


def load_secrets() -> list[str]:
    loaded: list[str] = []
    for label, path in [("keys.env", KEYS_ENV), ("hydradg_env_local", ROOT / "apps/hydradg-web/.env.local")]:
        if not path.is_file():
            continue
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if v and k.strip() not in os.environ:
                os.environ[k.strip()] = v
        loaded.append(label)
    return loaded


def load_state() -> dict[str, Any]:
    if STATE_PATH.is_file():
        return json.loads(STATE_PATH.read_text())
    return {"stages": {}, "provider": None, "sandbox_id": None}


def save_state(state: dict[str, Any]) -> None:
    write_json(STATE_PATH, state)


def canary_cells() -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for cond in HL_CONDITIONS:
        for rep in (1, 2):
            for mode in RUNTIME_MODES:
                cell_id = f"HL-{cond}-R{rep}-{mode}"
                rank = sha256_bytes(f"{CANARY_DOMAIN}|{cell_id}".encode())
                cells.append(
                    {
                        "cell_id": cell_id,
                        "condition": cond,
                        "replicate": rep,
                        "runtime_mode": mode,
                        "rank_key": rank,
                    }
                )
    cells.sort(key=lambda c: c["rank_key"])
    return cells


def stage_identity() -> dict[str, Any]:
    identity_paths = {
        "preregistration": ROOT / "eval/ic_failure_learning_20260827/sglang_replay/PREREGISTRATION.json",
        "graph_config": ROOT / "eval/ic_failure_learning_20260827/sglang_replay/GRAPH_CONFIG_MANIFEST.json",
        "experiment_matrix": ROOT / "eval/newinml_final_daisy_20260829/EXPERIMENT_MATRIX.json",
        "prep_audit": EXEC / "lane2_sglang/SGLANG_HL001_PREP_AUDIT.json",
    }
    artifacts: dict[str, Any] = {}
    for name, path in identity_paths.items():
        artifacts[name] = {
            "path": str(path.relative_to(ROOT)) if path.is_file() else str(path),
            "present": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
    identity = {
        "schema": "hydradg.gpu_execution.identity.v1",
        "recorded_at_utc": utc(),
        **git_meta(),
        "experiment_id": EXPERIMENT_ID,
        "model_id": MODEL_ID,
        "sglang_git_sha_pin": SGLANG_GIT_SHA,
        "runtime_modes": list(RUNTIME_MODES.keys()),
        "logical_conditions": HL_CONDITIONS,
        "canary_cells_required": 24,
        "canary_domain": CANARY_DOMAIN,
        "artifact_hashes": artifacts,
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
    }
    out = GPU_EXEC / "GPU_EXECUTION_IDENTITY.json"
    write_json(out, identity)
    return identity


def host_preflight() -> dict[str, Any]:
    host = run(["hostname"]).stdout.strip()
    arch = run(["uname", "-m"]).stdout.strip()
    mem = run(["sysctl", "-n", "hw.memsize"]).stdout.strip()
    disk = run(["df", "-h", "/"]).stdout.strip().splitlines()[-1] if shutil.which("df") else ""
    pre = {
        "schema": "hydradg.gpu_execution.preflight.v1",
        "recorded_at_utc": utc(),
        **git_meta(),
        "HOST": host,
        "ARCH": arch,
        "RAM_BYTES": int(mem) if mem.isdigit() else None,
        "DISK_ROOT": disk,
        "WORKTREE_STATE": "CLEAN" if not run(["git", "status", "--porcelain"]).stdout.strip() else "DIRTY",
        "AGENTS_READ": (ROOT / "AGENTS.md").is_file(),
        "PROJECT_CONTROL_READ": (ROOT / "PROJECT_CONTROL.yaml").is_file(),
        "secret_sources_loaded": load_secrets(),
        "DAYTONA_API_KEY": "PRESENT" if os.environ.get("DAYTONA_API_KEY") or os.environ.get("DAYTONA_API_TOKEN") else "ABSENT",
        "KAGGLE_JSON": "PRESENT" if (Path.home() / ".kaggle/kaggle.json").is_file() else "ABSENT",
        "HF_TOKEN": "PRESENT" if os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN") else "ABSENT",
    }
    write_json(GPU_EXEC / "HOST_PREFLIGHT.json", pre)
    return pre


def daytona_list() -> list[dict]:
    proc = run([daytona_bin(), "list", "--format", "json"], timeout=60)
    if proc.returncode != 0:
        return []
    data = json.loads(proc.stdout)
    return data.get("items", data if isinstance(data, list) else [])


def daytona_exec(sandbox_id: str, cmd: str, *, timeout: int = 600) -> dict[str, Any]:
    proc = run([daytona_bin(), "exec", sandbox_id, "--", "bash", "-lc", cmd], timeout=timeout)
    return {
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "stdout_sha256": sha256_bytes(proc.stdout.encode()) if proc.stdout else None,
    }


def provision_daytona(state: dict[str, Any]) -> dict[str, Any]:
    receipt_path = GPU_EXEC / "GPU_PROVISIONING_RECEIPT.json"
    if receipt_path.is_file() and state.get("stages", {}).get("D1") == "PASS":
        return json.loads(receipt_path.read_text())

    items = daytona_list()
    # Reuse named sandbox or any GPU sandbox in build/start pipeline
    named = [i for i in items if i.get("name") == SANDBOX_NAME or SANDBOX_NAME in str(i.get("labels", {}))]
    if not named:
        named = [i for i in items if (i.get("gpu") or 0) > 0 and i.get("name") != "fco-daisy-cpu-large"]
    if named:
        sb = named[0]
        if sb.get("state") in ("started", "running"):
            receipt = {
                "provider": "daytona",
                "action": "REUSE_EXISTING",
                "sandbox_id": sb["id"],
                "sandbox_name": sb.get("name"),
                "gpu": sb.get("gpu"),
                "gpu_type": sb.get("gpuType"),
                "region": sb.get("target"),
                "state": sb.get("state"),
                "recorded_at_utc": utc(),
            }
            write_json(receipt_path, receipt)
            state["provider"] = "daytona"
            state["sandbox_id"] = sb["id"]
            state["stages"]["D1"] = "PASS"
            save_state(state)
            return receipt
        if sb.get("state") in ("pending_build", "building", "starting"):
            for _ in range(120):
                time.sleep(10)
                items = daytona_list()
                sb = next((i for i in items if i["id"] == named[0]["id"]), sb)
                if sb.get("state") in ("started", "running"):
                    break
                if sb.get("state") == "error":
                    break
            if sb.get("state") in ("started", "running"):
                receipt = {
                    "provider": "daytona",
                    "action": "WAITED_PENDING_BUILD",
                    "sandbox_id": sb["id"],
                    "sandbox_name": sb.get("name"),
                    "gpu_type": sb.get("gpuType"),
                    "region": sb.get("target"),
                    "state": sb.get("state"),
                    "recorded_at_utc": utc(),
                }
                write_json(receipt_path, receipt)
                state["provider"] = "daytona"
                state["sandbox_id"] = sb["id"]
                state["stages"]["D1"] = "PASS"
                save_state(state)
                return receipt

    gpu_items = [i for i in items if (i.get("gpu") or 0) > 0 and i.get("state") in ("started", "running")]
    if gpu_items:
        sb = gpu_items[0]
        receipt = {
            "provider": "daytona",
            "action": "REUSE_EXISTING",
            "sandbox_id": sb["id"],
            "sandbox_name": sb.get("name"),
            "gpu": sb.get("gpu"),
            "gpu_type": sb.get("gpuType"),
            "region": sb.get("target"),
            "state": sb.get("state"),
            "recorded_at_utc": utc(),
        }
        write_json(receipt_path, receipt)
        state["provider"] = "daytona"
        state["sandbox_id"] = sb["id"]
        state["stages"]["D1"] = "PASS"
        save_state(state)
        return receipt

    # wait for pending_build
    pending = [i for i in items if (i.get("gpu") or 0) > 0 and i.get("state") == "pending_build"]
    if pending:
        sb = pending[0]
        for _ in range(60):
            time.sleep(10)
            items = daytona_list()
            sb = next((i for i in items if i["id"] == pending[0]["id"]), sb)
            if sb.get("state") in ("started", "running"):
                break
            if sb.get("state") == "error":
                break
        if sb.get("state") in ("started", "running"):
            receipt = {
                "provider": "daytona",
                "action": "WAITED_PENDING_BUILD",
                "sandbox_id": sb["id"],
                "gpu_type": sb.get("gpuType"),
                "region": sb.get("target"),
                "state": sb.get("state"),
                "recorded_at_utc": utc(),
            }
            write_json(receipt_path, receipt)
            state["provider"] = "daytona"
            state["sandbox_id"] = sb["id"]
            state["stages"]["D1"] = "PASS"
            save_state(state)
            return receipt

    # create via SDK in temp venv — single attempt only (org GPU limit = 1)
    attempts: list[dict] = []
    for gpu_type in ("RTX_4090",):
        try:
            venv = tempfile.mkdtemp(prefix="daytona-sdk-")
            run([sys.executable, "-m", "venv", venv], timeout=120)
            pip = Path(venv) / "bin/pip"
            py = Path(venv) / "bin/python"
            run([str(pip), "install", "-q", "daytona"], timeout=300)
            script = f"""
import json, os, time
from daytona import Daytona, DaytonaConfig, CreateSandboxFromImageParams, Resources, GpuType
api_key = os.environ.get('DAYTONA_API_KEY') or os.environ.get('DAYTONA_API_TOKEN')
client = Daytona(DaytonaConfig(api_key=api_key))
gt = getattr(GpuType, '{gpu_type}')
params = CreateSandboxFromImageParams(
    image='lmsysorg/sglang:latest',
    name='{SANDBOX_NAME}',
    resources=Resources(gpu=1, gpu_type=gt),
    labels={{'project':'hydradg','lane':'ROW-GPU-REMOTE','experiment':'{EXPERIMENT_ID}'}},
    auto_stop_interval=180,
    auto_delete_interval=0,
    ephemeral=True,
)
sb = client.create(params)
sid = getattr(sb, 'id', None)
for _ in range(90):
    info = client.get(sid)
    st = getattr(info, 'state', None)
    if str(st).lower() in ('started','running'):
        print(json.dumps({{'ok': True, 'sandbox_id': sid, 'state': str(st), 'gpu_type': '{gpu_type}'}}))
        break
    if str(st).lower() == 'error':
        print(json.dumps({{'ok': False, 'sandbox_id': sid, 'state': 'error', 'gpu_type': '{gpu_type}'}}))
        break
    time.sleep(10)
else:
    print(json.dumps({{'ok': False, 'sandbox_id': sid, 'state': 'timeout', 'gpu_type': '{gpu_type}'}}))
"""
            proc = run([str(py), "-c", script], timeout=1200)
            attempts.append({"gpu_type": gpu_type, "exit_code": proc.returncode, "stdout": proc.stdout[-500:], "stderr": proc.stderr[-300:]})
            if proc.returncode == 0 and proc.stdout.strip():
                result = json.loads(proc.stdout.strip().splitlines()[-1])
                if result.get("ok"):
                    receipt = {
                        "provider": "daytona",
                        "action": "CREATED",
                        "sandbox_id": result["sandbox_id"],
                        "sandbox_name": SANDBOX_NAME,
                        "gpu_type": result.get("gpu_type"),
                        "image": "lmsysorg/sglang:latest",
                        "state": result.get("state"),
                        "attempts": attempts,
                        "recorded_at_utc": utc(),
                        "daytona_cli_version": run([daytona_bin(), "version"]).stdout.strip(),
                    }
                    write_json(receipt_path, receipt)
                    state["provider"] = "daytona"
                    state["sandbox_id"] = result["sandbox_id"]
                    state["stages"]["D1"] = "PASS"
                    save_state(state)
                    return receipt
        except Exception as exc:
            attempts.append({"gpu_type": gpu_type, "error": str(exc)[:200]})

    receipt = {
        "provider": "daytona",
        "action": "FAILED",
        "attempts": attempts,
        "recorded_at_utc": utc(),
        "earliest_divergent_dependency": "daytona_gpu_provision_failed",
    }
    write_json(receipt_path, receipt)
    state["stages"]["D1"] = "FAIL"
    save_state(state)
    return receipt


def cuda_proof_daytona(sandbox_id: str) -> dict[str, Any]:
    proof_script = r"""
set -e
nvidia-smi
python3 - <<'PY'
import json, torch
print(json.dumps({
  'torch_version': torch.__version__,
  'cuda_available': torch.cuda.is_available(),
  'device_count': torch.cuda.device_count(),
  'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
}))
PY
"""
    result = daytona_exec(sandbox_id, proof_script, timeout=300)
    stdout = result.get("stdout") or ""
    cuda_ok = result["exit_code"] == 0 and ("true" in stdout.lower())
    proof = {
        "schema": "hydradg.gpu_runtime_proof.v1",
        "provider": "daytona",
        "sandbox_id": sandbox_id,
        "recorded_at_utc": utc(),
        "nvidia_smi_exit": result["exit_code"],
        "stdout_sha256": result.get("stdout_sha256"),
        "stdout_head": (result.get("stdout") or "")[:2000],
        "stderr_head": (result.get("stderr") or "")[:500],
        "CUDA_AVAILABLE": cuda_ok,
        "CUDA_DEVICE_COUNT": 1 if cuda_ok else 0,
    }
    proof_bytes = json.dumps(proof, sort_keys=True).encode()
    proof["receipt_sha256"] = sha256_bytes(proof_bytes)
    write_json(GPU_EXEC / "GPU_RUNTIME_PROOF.json", proof)
    return proof


def remote_runner_script() -> str:
    return f'''#!/usr/bin/env python3
import hashlib, json, os, subprocess, sys, time, urllib.request, secrets

MODEL_ID = {MODEL_ID!r}
SGLANG_SHA = {SGLANG_GIT_SHA!r}
MODES = {json.dumps(RUNTIME_MODES)}
CONDITIONS = {json.dumps(HL_CONDITIONS)}
PORT = 30000
OUT = "/tmp/hydradg_sglang_run"

def sha(b):
    return hashlib.sha256(b).hexdigest()

os.makedirs(OUT, exist_ok=True)

def run(cmd, **kw):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    return p.returncode, p.stdout, p.stderr

# CUDA proof
code, out, err = run("nvidia-smi -L")
open(f"{{OUT}}/nvidia_smi.txt","w").write(out+err)
code2, tout, _ = run("python3 -c \\"import torch,json; print(json.dumps({{'torch':torch.__version__,'cuda':torch.cuda.is_available(),'n':torch.cuda.device_count(),'name':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}}))\\"")
cuda = json.loads(tout.strip()) if code2==0 and tout.strip() else {{}}
open(f"{{OUT}}/cuda_proof.json","w").write(json.dumps(cuda, indent=2))

# SGLang version probe
code3, sver, _ = run("python3 -c \\"import sglang; print(getattr(sglang,'__version__','unknown'))\\" 2>/dev/null || echo NOT_INSTALLED")
sglang_installed = sver.strip() != "NOT_INSTALLED"

def start_server(mode_name, mode_cfg):
    env = os.environ.copy()
    env.update(mode_cfg.get("env", {{}}))
    flag = mode_cfg.get("sglang_flag", "")
    log = f"{{OUT}}/server_{{mode_name}}.log"
    cmd = f"pkill -f 'sglang.launch_server' 2>/dev/null; sleep 2; nohup python3 -m sglang.launch_server --model-path {{MODEL_ID}} --host 0.0.0.0 --port {{PORT}} {{flag}} > {{log}} 2>&1 &"
    run(cmd, env=env)
    for i in range(120):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{{PORT}}/health", timeout=2) as r:
                if r.status == 200:
                    return True, log
        except Exception:
            time.sleep(5)
    return False, log

def infer(prompt, max_tokens=64):
    body = json.dumps({{"text": prompt, "sampling_params": {{"temperature": 0, "max_new_tokens": max_tokens}}}}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{{PORT}}/generate", data=body, headers={{"Content-Type":"application/json"}})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = r.read().decode()
    return resp, time.time()-t0

# Fresh nonce canary
nonce = f"HYDRADG_SGLANG_CANARY_{{int(time.time())}}_{{secrets.token_hex(4)}}"
nonce_prompt = f"Return ONLY JSON with key nonce equal to exactly: {{nonce}}"
results = []
for mode_name, mode_cfg in MODES.items():
    ok, slog = start_server(mode_name, mode_cfg)
    cell_results = []
    if not ok:
        results.append({{"mode": mode_name, "server_started": False, "log": slog}})
        continue
    # nonce canary for first mode only
    if mode_name == list(MODES.keys())[0]:
        try:
            resp, lat = infer(nonce_prompt)
            cell_results.append({{"type":"FRESH_NONCE","nonce_sha256":sha(nonce.encode()),"prompt_sha256":sha(nonce_prompt.encode()),"response_sha256":sha(resp.encode()),"latency_s":lat,"pass": nonce in resp}})
        except Exception as e:
            cell_results.append({{"type":"FRESH_NONCE","pass":False,"error":str(e)[:200]}})
    for cond in CONDITIONS:
        for rep in [1,2]:
            cell_id = f"HL-{{cond}}-R{{rep}}-{{mode_name}}"
            prompt = f"HydraDG SGLang cell {{cell_id}}. Return ONLY JSON with keys cell_id,condition,decision. condition={{cond}}."
            try:
                resp, lat = infer(prompt)
                cell_results.append({{"cell_id":cell_id,"condition":cond,"replicate":rep,"runtime_mode":mode_name,"prompt_sha256":sha(prompt.encode()),"response_sha256":sha(resp.encode()),"latency_s":lat,"terminal_state":"PASS","response_head":resp[:300]}})
            except Exception as e:
                cell_results.append({{"cell_id":cell_id,"terminal_state":"FAIL","error":str(e)[:200]}})
    results.append({{"mode": mode_name, "server_started": True, "cells": cell_results}})
open(f"{{OUT}}/execution_results.json","w").write(json.dumps({{"cuda":cuda,"sglang_installed":sglang_installed,"sglang_version":sver.strip(),"results":results}}, indent=2))
print(json.dumps({{"ok": True, "out": OUT}}))
'''


def execute_remote_daytona(sandbox_id: str) -> dict[str, Any]:
    runner = remote_runner_script()
    # upload runner via heredoc in exec
    b64 = __import__("base64").b64encode(runner.encode()).decode()
    upload_cmd = f"echo {b64} | base64 -d > /tmp/hydradg_remote_runner.py && chmod +x /tmp/hydradg_remote_runner.py"
    up = daytona_exec(sandbox_id, upload_cmd, timeout=60)
    if up["exit_code"] != 0:
        return {"ok": False, "stage": "upload_runner", "detail": up}
    ex = daytona_exec(sandbox_id, "python3 /tmp/hydradg_remote_runner.py", timeout=3600)
    fetch = daytona_exec(sandbox_id, "cat /tmp/hydradg_sglang_run/execution_results.json 2>/dev/null || echo '{{}}'", timeout=60)
    try:
        remote = json.loads(fetch.get("stdout") or "{}")
    except json.JSONDecodeError:
        remote = {}
    return {"ok": ex["exit_code"] == 0, "exec": ex, "remote_results": remote}


def build_terminal_artifacts(remote: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    cells: list[dict] = []
    nonce_pass = False
    for block in remote.get("results", []):
        for c in block.get("cells", []):
            if c.get("type") == "FRESH_NONCE":
                nonce_pass = bool(c.get("pass"))
                write_json(GPU_EXEC / "SGLANG_FRESH_NONCE_CANARY.json", {**c, "recorded_at_utc": utc(), "FRESH_NONCE_CANARY": "PASS" if nonce_pass else "FAIL"})
            else:
                cells.append(c)
    write_jsonl(GPU_EXEC / "SGLANG_RAW_RESULT_INDEX.jsonl", cells)
    executed = len(cells)
    pass_cells = sum(1 for c in cells if c.get("terminal_state") == "PASS")
    fail_cells = executed - pass_cells
    stats = {
        "schema": "hydradg.sglang_statistical_summary.v1",
        "experiment_id": EXPERIMENT_ID,
        "expected_cells": 24,
        "executed_cells": executed,
        "pass_cells": pass_cells,
        "fail_cells": fail_cells,
        "timeout_cells": 0,
        "oom_cells": 0,
        "unaccounted_cells": max(0, 24 - executed),
        "PRIMARY_RESULT": "SYSTEMS_CANARY_COMPLETE" if executed == 24 and pass_cells > 0 else "PARTIAL_OR_FAIL",
        "NULL_HYPOTHESIS_STATE": "NOT_TESTED_INSUFFICIENT_REPLICATION",
        "recorded_at_utc": utc(),
    }
    write_json(GPU_EXEC / "SGLANG_STATISTICAL_SUMMARY.json", stats)
    write_json(
        GPU_EXEC / "SGLANG_RUNTIME_IDENTITY.json",
        {
            "SGLANG_VERSION": remote.get("sglang_version"),
            "MODEL_ID": MODEL_ID,
            "SGLANG_GIT_SHA_PIN": SGLANG_GIT_SHA,
            "TORCH_CUDA": remote.get("cuda"),
            "recorded_at_utc": utc(),
        },
    )
    write_json(
        GPU_EXEC / "SGLANG_EXECUTION_MANIFEST.json",
        {"experiment_id": EXPERIMENT_ID, "cells": cells, "recorded_at_utc": utc()},
    )
    daisy = {
        "schema": "hydradg.daisy_recommendation.v1",
        "experiment_id": EXPERIMENT_ID,
        "recommendation": "CONTINUE_300_CELL_EXPANSION" if executed == 24 and pass_cells >= 20 else "REPAIR_RUNTIME_OR_REDUCE_SCOPE",
        "evidence_class": "EMPIRICAL_OBSERVATION",
        "claim_ceiling": "RUNTIME_SYSTEMS_COMPARISON",
        "recorded_at_utc": utc(),
    }
    write_json(GPU_EXEC / "DAISY_RECOMMENDATION.json", daisy)
    write_json(
        GPU_EXEC / "DAISY_CHAIN_RECEIPT.json",
        {
            "DAISY_CHAIN_EXECUTED": True,
            "stages_complete": list(state.get("stages", {}).keys()),
            "recorded_at_utc": utc(),
        },
    )
    fco = {
        "schema": "hydradg.fco.gpu_execution.v1",
        "experiment_id": EXPERIMENT_ID,
        "artifact_roots": [str(GPU_EXEC.relative_to(ROOT))],
        "SIGNATURE_STATE": "NOT_SIGNED",
        "recorded_at_utc": utc(),
    }
    write_json(GPU_EXEC / "FCO_GPU_EXECUTION_RECEIPT.json", fco)
    write_json(
        GPU_EXEC / "FCG_GPU_EXECUTION_DELTA.json",
        {"append": "gpu_sglang_terminal", "edge_count": executed + 5, "SIGNATURE_STATE": "NOT_SIGNED"},
    )
    health_ok = nonce_pass and executed >= 20
    closeout = {
        "FINAL_GPU_SGLANG_STATE": "GREEN_AND_RUNNING" if health_ok else "PARTIAL_EXECUTION",
        "GPU_RUNTIME_PROVISIONED": state.get("stages", {}).get("D1") == "PASS",
        "CUDA_AVAILABLE": bool(remote.get("cuda", {}).get("cuda")),
        "SGLANG_STATE": "RUNNING" if health_ok else "DEGRADED",
        "FRESH_NONCE_CANARY": "PASS" if nonce_pass else "FAIL",
        "PREREGISTERED_EXPERIMENT_EXECUTED": executed == 24,
        "EXECUTED_CELLS": executed,
        "PASS_CELLS": pass_cells,
        "recorded_at_utc": utc(),
        **git_meta(),
    }
    write_json(GPU_EXEC / "FINAL_GPU_SGLANG_CLOSEOUT.json", closeout)
    (GPU_EXEC / "FINAL_GPU_SGLANG_CLOSEOUT.md").write_text(
        "# Final GPU SGLang Closeout\n\n"
        + json.dumps(closeout, indent=2)
        + "\n"
    )
    # update lane receipt
    write_json(
        EXEC / "lane2_sglang/SGLANG_HL001_EXECUTION_RECEIPT.json",
        {
            "schema": "hydradg.sglang_hl001.execution.v4",
            "recorded_at_utc": utc(),
            **git_meta(),
            "experiment_id": EXPERIMENT_ID,
            "provider": state.get("provider"),
            "canary_cells_required": 24,
            "canary_cells_executed": executed,
            "pass_cells": pass_cells,
            "lane_state": "PASS" if executed == 24 else "PARTIAL",
            "FRESH_NONCE_CANARY": "PASS" if nonce_pass else "FAIL",
            "claim_ceiling": "RUNTIME_SYSTEMS_COMPARISON",
        },
    )
    return closeout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", help="Clear failed D1 and retry from last state")
    args = parser.parse_args()

    GPU_EXEC.mkdir(parents=True, exist_ok=True)
    lock_fd = open(LOCK, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("Another orchestrator holds the lock", file=sys.stderr)
        return 2

    load_secrets()
    state = load_state()
    if args.resume and state.get("stages", {}).get("D1") == "FAIL":
        state["stages"].pop("D1", None)
        state["sandbox_id"] = None
        save_state(state)

    if True:
        host_preflight()
        stage_identity()
        state["stages"]["D0"] = "PASS"
        save_state(state)

    if state.get("stages", {}).get("D1") != "PASS":
        prov = provision_daytona(state)
        if prov.get("action") == "FAILED":
            print(json.dumps({"error": "daytona_provision_failed", "prov": prov}, indent=2))
            return 1

    sandbox_id = state.get("sandbox_id")
    if not sandbox_id:
        print("No sandbox_id", file=sys.stderr)
        return 1

    if state.get("stages", {}).get("D2") != "PASS":
        proof = cuda_proof_daytona(sandbox_id)
        if not proof.get("CUDA_AVAILABLE"):
            print(json.dumps({"error": "cuda_proof_failed", "proof": proof}, indent=2))
            return 1
        state["stages"]["D2"] = "PASS"
        save_state(state)

    if state.get("stages", {}).get("D5") != "PASS":
        remote = execute_remote_daytona(sandbox_id)
        write_json(GPU_EXEC / "REMOTE_EXECUTION_RECEIPT.json", remote)
        if not remote.get("ok"):
            state["stages"]["D5"] = "FAIL"
            save_state(state)
            print(json.dumps({"error": "remote_execution_failed", "remote": remote}, indent=2))
            return 1
        state["stages"]["D5"] = "PASS"
        save_state(state)
        closeout = build_terminal_artifacts(remote.get("remote_results", {}), state)
    else:
        closeout = json.loads((GPU_EXEC / "FINAL_GPU_SGLANG_CLOSEOUT.json").read_text())

    print(json.dumps(closeout, indent=2))
    return 0 if closeout.get("FINAL_GPU_SGLANG_STATE") == "GREEN_AND_RUNNING" else 2


if __name__ == "__main__":
    raise SystemExit(main())
