#!/usr/bin/env python3
"""Gum AI Stack Doctor v2 — successor to NOT_LOCATED gum_ai_stack_doctor.zsh.

Inspects host/tooling capabilities, applies safe local repairs, emits structured receipts.
Does NOT reconstruct or claim to be the historical implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXEC = ROOT / "eval/newinml_final_daisy_20260829/execution/lane0_gum"
GOVERNED_CFOS = Path("/Users/byron/projects/active/cloudflare-os")
EXTERNAL_CFOS = Path("/Users/byron/projects/external/cloudflare-os")
SEEDGRAPH_REPO = Path("/Users/byron/projects/active/seedgraph")
Q38_DIGEST = "22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643"
PREDECESSOR_RECEIPTS = [
    "eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_BEFORE.json",
    "eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_REPAIR_PLAN.json",
    "eval/newinml_final_daisy_20260829/execution/lane0_gum/GUM_DOCTOR_AFTER.json",
]
HISTORICAL_TOOL = "scripts/gum_ai_stack_doctor.zsh"


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str | None:
    if not p.is_file():
        return None
    return sha256_bytes(p.read_bytes())


def write_json(p: Path, obj: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        cwd=cwd or ROOT,
        timeout=timeout,
    )


def git_meta() -> dict[str, str]:
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    sha = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    dirty = bool(run(["git", "status", "--porcelain"]).stdout.strip())
    origin = run(["git", "rev-parse", "@{u}"]).stdout.strip() if run(["git", "rev-parse", "@{u}"]).returncode == 0 else None
    return {
        "CURRENT_BRANCH": branch,
        "CURRENT_SHA": sha,
        "GIT_DIRTY": dirty,
        "ORIGIN_SHA": origin,
    }


def swap_info() -> dict[str, Any]:
    used_gb = None
    r = run(["sysctl", "vm.swapusage"])
    if r.returncode == 0 and "used = " in r.stdout:
        try:
            used_gb = float(r.stdout.split("used = ")[1].split()[0].replace("M", "")) / 1024
        except ValueError:
            pass
    mem = run(["sysctl", "hw.memsize"])
    ram_gb = int(mem.stdout.split(":")[1].strip()) // (1024**3) if mem.returncode == 0 else None
    return {
        "host": platform.node(),
        "arch": platform.machine(),
        "ram_gb": ram_gb,
        "swap_used_gb": used_gb,
        "disk_free_gb": shutil.disk_usage(ROOT).free // (1024**3),
    }


def secret_presence(name: str) -> str:
    return "PRESENT" if os.environ.get(name) else "ABSENT"


def kaggle_state() -> dict[str, str]:
    cfg = Path.home() / ".kaggle" / "kaggle.json"
    env_user = secret_presence("KAGGLE_USERNAME")
    env_key = secret_presence("KAGGLE_KEY")
    if env_user == "PRESENT" and env_key == "PRESENT":
        state = "ENV_CONFIGURED"
    elif cfg.is_file():
        state = "CONFIG_FILE_PRESENT_ENV_ABSENT"
    else:
        state = "BLOCKED_HUMAN_SECRET_REQUIRED"
    return {
        "KAGGLE_USERNAME": env_user,
        "KAGGLE_KEY": env_key,
        "KAGGLE_CONFIG_FILE": "PRESENT" if cfg.is_file() else "ABSENT",
        "KAGGLE_STATE": state,
    }


def daytona_state() -> dict[str, str]:
    key = secret_presence("DAYTONA_API_KEY")
    token = secret_presence("DAYTONA_API_TOKEN")
    cli = shutil.which("daytona")
    if key == "PRESENT" or token == "PRESENT":
        state = "ENV_CONFIGURED"
    elif cli:
        state = "BLOCKED_HUMAN_SECRET_REQUIRED"
    else:
        state = "CLI_ABSENT"
    return {
        "DAYTONA_CLI": cli or None,
        "DAYTONA_API_KEY": key,
        "DAYTONA_API_TOKEN": token,
        "DAYTONA_STATE": state,
    }


def ollama_qwen38() -> dict[str, Any]:
    digest = None
    gate = "FAIL"
    if shutil.which("ollama"):
        r = run(["ollama", "list"])
        for line in r.stdout.splitlines():
            if "qwen3.8:27b" in line:
                parts = line.split()
                digest = parts[1] if len(parts) > 1 else None
                gate = "PASS" if digest and digest.startswith(Q38_DIGEST[:12]) else "FAIL"
    return {
        "ollama": shutil.which("ollama"),
        "qwen38_model": "qwen3.8:27b",
        "qwen38_digest_observed": digest,
        "qwen38_digest_expected_prefix": Q38_DIGEST[:12],
        "qwen38_digest_gate": gate,
    }


def ollarma_probe() -> dict[str, Any]:
    curl = shutil.which("curl")
    if not curl:
        return {"ollarma_state": "CURL_ABSENT"}
    r = run([curl, "-sS", "-o", "/dev/null", "-w", "%{http_code}", "http://127.0.0.1:8484/health"], timeout=10)
    code = r.stdout.strip()
    return {
        "ollarma_endpoint": "http://127.0.0.1:8484/health",
        "ollarma_http_code": code,
        "ollarma_state": "REACHABLE" if code.startswith("2") else "DEGRADED_OR_DOWN",
    }


def cfos_checkout() -> dict[str, Any]:
    governed = GOVERNED_CFOS
    external = EXTERNAL_CFOS
    path = governed if governed.exists() else external if external.exists() else None
    sha = None
    if path and (path / ".git").exists():
        sha = run(["git", "-C", str(path), "rev-parse", "HEAD"]).stdout.strip()
    wrangler = shutil.which("wrangler")
    workerd = shutil.which("workerd")
    wrangler_via_pnpm = None
    if path and not wrangler and (path / "node_modules").exists():
        r = run(["pnpm", "exec", "wrangler", "--version"], cwd=path, timeout=60)
        if r.returncode == 0:
            wrangler_via_pnpm = r.stdout.strip().splitlines()[0] if r.stdout else "OK"
    return {
        "governed_path": str(governed),
        "governed_exists": governed.exists(),
        "external_path": str(external),
        "external_exists": external.exists(),
        "active_checkout": str(path) if path else None,
        "cloudflare_os_sha": sha,
        "wrangler": wrangler,
        "wrangler_via_pnpm": wrangler_via_pnpm,
        "workerd": workerd,
        "pnpm": shutil.which("pnpm"),
    }


def seedgraph_check() -> dict[str, Any]:
    if not SEEDGRAPH_REPO.exists():
        return {"seedgraph_repo": str(SEEDGRAPH_REPO), "seedgraph_present": False}
    sha = run(["git", "-C", str(SEEDGRAPH_REPO), "rev-parse", "HEAD"]).stdout.strip()
    batch_manifest = EXEC.parent / "lane6_seedgraph/BATCH_MANIFEST_BATCH003.json"
    latest_verified = None
    if batch_manifest.is_file():
        latest_verified = json.loads(batch_manifest.read_text()).get("BATCH_ROOT")
    return {
        "seedgraph_repo": str(SEEDGRAPH_REPO),
        "seedgraph_present": True,
        "seedgraph_sha": sha,
        "latest_verified_batch_root": latest_verified,
    }


def cuda_state() -> dict[str, Any]:
    nvidia = shutil.which("nvidia-smi")
    pytorch_cuda = None
    try:
        r = run([sys.executable, "-c", "import torch; print(torch.cuda.is_available())"], timeout=30)
        if r.returncode == 0:
            pytorch_cuda = r.stdout.strip()
    except Exception:
        pytorch_cuda = "IMPORT_FAILED"
    return {
        "nvidia_smi": nvidia,
        "LOCAL_CUDA_STATE": "UNAVAILABLE_EXPECTED" if not nvidia else "AVAILABLE",
        "pytorch_cuda_available": pytorch_cuda,
        "SGLANG_EXECUTION_TARGET": "REMOTE_AUTHORIZED_CUDA" if not nvidia else "LOCAL_CUDA",
    }


def inspect_all() -> dict[str, Any]:
    gm = git_meta()
    return {
        "schema": "hydradg.gum_doctor_v2.before.v1",
        "recorded_at_utc": utc(),
        "HISTORICAL_TOOL_STATE": "NOT_LOCATED",
        "HISTORICAL_TOOL_PATH": HISTORICAL_TOOL,
        "PREDECESSOR_RECEIPTS": PREDECESSOR_RECEIPTS,
        "doctor_version": "gum_ai_stack_doctor_v2",
        **gm,
        **swap_info(),
        "python": sys.version.split()[0],
        "uv": shutil.which("uv"),
        "snakemake": shutil.which("snakemake"),
        "node": shutil.which("node"),
        "pnpm": shutil.which("pnpm"),
        **ollama_qwen38(),
        **ollarma_probe(),
        **cfos_checkout(),
        **cuda_state(),
        **daytona_state(),
        **kaggle_state(),
        **seedgraph_check(),
    }


def capability_matrix(before: dict[str, Any]) -> dict[str, Any]:
    rows = []
    checks = [
        ("host", before.get("host"), "OBSERVED"),
        ("git_clean", not before.get("GIT_DIRTY"), "INFO"),
        ("python", bool(before.get("python")), "REQUIRED"),
        ("uv", bool(before.get("uv")), "OPTIONAL"),
        ("ollama", bool(before.get("ollama")), "REQUIRED_Q38"),
        ("qwen38_digest", before.get("qwen38_digest_gate") == "PASS", "REQUIRED_Q38"),
        ("cloudflare_os", bool(before.get("active_checkout")), "REQUIRED_CFOS"),
        ("wrangler", bool(before.get("wrangler") or before.get("wrangler_via_pnpm")), "REQUIRED_CFOS"),
        ("local_cuda", before.get("LOCAL_CUDA_STATE") == "AVAILABLE", "OPTIONAL_LOCAL"),
        ("daytona_auth", before.get("DAYTONA_STATE") == "ENV_CONFIGURED", "REMOTE_OPTIONAL"),
        ("kaggle_auth", before.get("KAGGLE_STATE") == "ENV_CONFIGURED", "REMOTE_OPTIONAL"),
        ("seedgraph", before.get("seedgraph_present"), "OPTIONAL"),
    ]
    for name, ok, tier in checks:
        rows.append({
            "capability": name,
            "ok": bool(ok),
            "tier": tier,
            "state": "PASS" if ok else "BLOCKED",
        })
    return {
        "schema": "hydradg.gum_doctor_v2.capability_matrix.v1",
        "recorded_at_utc": utc(),
        "rows": rows,
        "blocked_remote": [
            r["capability"]
            for r in rows
            if not r["ok"] and r["tier"] in ("REMOTE_OPTIONAL",)
        ],
    }


def apply_repairs(before: dict[str, Any]) -> tuple[dict[str, Any], list[dict], list[dict]]:
    applied: list[dict] = []
    blocked: list[dict] = []

    if not GOVERNED_CFOS.exists() and EXTERNAL_CFOS.exists():
        try:
            GOVERNED_CFOS.parent.mkdir(parents=True, exist_ok=True)
            GOVERNED_CFOS.symlink_to(EXTERNAL_CFOS)
            applied.append({
                "action": "symlink_governed_cloudflare_os",
                "target": str(GOVERNED_CFOS),
                "source": str(EXTERNAL_CFOS),
            })
        except OSError as exc:
            blocked.append({"item": "cloudflare_os_symlink", "reason": str(exc)})

    cfos_path = GOVERNED_CFOS if GOVERNED_CFOS.exists() else EXTERNAL_CFOS
    if cfos_path.exists() and shutil.which("pnpm"):
        if not (cfos_path / "node_modules").exists():
            r = run(["pnpm", "install", "--frozen-lockfile"], cwd=cfos_path, timeout=600)
            if r.returncode == 0:
                applied.append({"action": "pnpm_install_cloudflare_os", "cwd": str(cfos_path)})
            else:
                blocked.append({
                    "item": "pnpm_install",
                    "reason": (r.stderr or r.stdout or "failed")[:500],
                })

    if not shutil.which("wrangler") and cfos_path.exists() and shutil.which("npm"):
        tools = ROOT / ".tools" / "npm-global"
        tools.mkdir(parents=True, exist_ok=True)
        r = run(["npm", "install", "wrangler@4", "--prefix", str(tools)], timeout=300)
        if r.returncode == 0:
            bin_dir = tools / "bin"
            os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"
            applied.append({"action": "npm_install_wrangler_local", "prefix": str(tools)})
        else:
            blocked.append({"item": "wrangler_install", "reason": (r.stderr or "")[:300]})

    if before.get("DAYTONA_STATE") == "BLOCKED_HUMAN_SECRET_REQUIRED":
        blocked.append({"item": "daytona", "reason": "HUMAN_SECRET_REQUIRED", "policy": "REMOTE_COMPUTE_REQUIRED"})
    if before.get("KAGGLE_STATE") in ("BLOCKED_HUMAN_SECRET_REQUIRED", "CONFIG_FILE_PRESENT_ENV_ABSENT"):
        blocked.append({
            "item": "kaggle",
            "reason": "HUMAN_SECRET_REQUIRED" if before.get("KAGGLE_STATE") == "BLOCKED_HUMAN_SECRET_REQUIRED" else "ENV_EXPORT_REQUIRED",
            "policy": "REMOTE_COMPUTE_REQUIRED",
        })
    if before.get("LOCAL_CUDA_STATE") == "UNAVAILABLE_EXPECTED":
        blocked.append({"item": "local_cuda", "reason": "UNSUPPORTED_LOCAL_HARDWARE", "policy": "REMOTE_AUTHORIZED_CUDA"})

    plan = {
        "schema": "hydradg.gum_doctor_v2.repair_plan.v1",
        "recorded_at_utc": utc(),
        "repairs_applied": applied,
        "repairs_blocked": blocked,
        "scientific_variables_frozen": True,
        "repair_policy": "LOCAL_DETERMINISTIC_ONLY",
    }
    return plan, applied, blocked


def after_snapshot(before: dict[str, Any], repairs: dict[str, Any]) -> dict[str, Any]:
    fresh = inspect_all()
    fresh["schema"] = "hydradg.gum_doctor_v2.after.v1"
    fresh["repairs_applied_count"] = len(repairs.get("repairs_applied", []))
    fresh["repairs_blocked_count"] = len(repairs.get("repairs_blocked", []))
    fresh["lane_state"] = "V2_INVENTORY_AND_SAFE_REPAIR_COMPLETE"
    return fresh


def main() -> int:
    parser = argparse.ArgumentParser(description="Gum AI Stack Doctor v2")
    parser.add_argument("--out-dir", type=Path, default=EXEC)
    parser.add_argument("--repair", action="store_true", help="Apply safe local repairs")
    args = parser.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    before = inspect_all()
    write_json(out / "GUM_DOCTOR_V2_BEFORE.json", before)
    matrix = capability_matrix(before)
    write_json(out / "GUM_DOCTOR_V2_CAPABILITY_MATRIX.json", matrix)

    if args.repair:
        repair_plan, _, _ = apply_repairs(before)
    else:
        repair_plan = {
            "schema": "hydradg.gum_doctor_v2.repair_plan.v1",
            "recorded_at_utc": utc(),
            "repairs_applied": [],
            "repairs_blocked": [{"item": "repair_skipped", "reason": "pass --repair to apply"}],
            "scientific_variables_frozen": True,
        }
    write_json(out / "GUM_DOCTOR_V2_REPAIR_PLAN.json", repair_plan)

    if args.repair:
        after = after_snapshot(before, repair_plan)
    else:
        after = dict(before)
        after["schema"] = "hydradg.gum_doctor_v2.after.v1"
        after["lane_state"] = "READ_ONLY_V2_INVENTORY"
    write_json(out / "GUM_DOCTOR_V2_AFTER.json", after)

    receipt = {
        "schema": "hydradg.gum_doctor_v2.receipt.v1",
        "recorded_at_utc": utc(),
        "HISTORICAL_TOOL_STATE": "NOT_LOCATED",
        "PREDECESSOR_RECEIPTS": PREDECESSOR_RECEIPTS,
        "GUM_DOCTOR_V2_STATE": after.get("lane_state"),
        "repairs_applied": len(repair_plan.get("repairs_applied", [])),
        "repairs_blocked": len(repair_plan.get("repairs_blocked", [])),
        "claim_ceiling": "ENVIRONMENT_CAPABILITY_EVIDENCE_ONLY",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MMR_STATE": "NOT_COMMITTED",
    }
    write_json(out / "GUM_DOCTOR_V2_RECEIPT.json", receipt)
    print(json.dumps({"ok": True, "out": str(out), "state": after.get("lane_state")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
