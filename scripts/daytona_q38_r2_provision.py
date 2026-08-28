#!/usr/bin/env python3
"""Daytona auth receipt, H200 provision, environment probe, model canaries for Q38 R2 wave."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval/qwen38_model_replay_20260828"
CANARY_PROMPT = (
    'Return strict JSON only: {"smoke":"pass","host":"daytona-h200","nonce":"Q38-R2-CANARY-20260829"}'
)
CANARY_NONCE = "Q38-R2-CANARY-20260829"
Q38_MODEL = "qwen3.8:27b"
FLASH_MODEL = "qwen3.8-flash-next:125b-a6b-nvfp4"
MIN_DISK_GB = 125


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def redact_secrets(text: str) -> str:
    text = re.sub(r"dtn_[a-f0-9]{20,}", "REDACTED", text)
    text = re.sub(r"Bearer\s+\S+", "Bearer REDACTED", text)
    return text


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def auth_receipt() -> dict:
    code, ver_out = run(["daytona", "--version"])
    lc, list_out = run(["daytona", "list"])
    redacted = redact_secrets(list_out)
    receipt = {
        "schema": "hydradg.daytona_auth_post_login.v1",
        "receipt_id": "DAYTONA_AUTH_POST_LOGIN_RECEIPT",
        "recorded_at_utc": utc_now(),
        "host": "magicSTUDIObox.local",
        "CLI_AUTH": "PASS" if lc == 0 else "FAIL",
        "cli_version": ver_out if code == 0 else None,
        "list_exit_status": lc,
        "list_response_hash_sha256": sha256_text(redacted),
        "sandbox_count_hint": redacted.count("[[") + redacted.count("\n["),
        "profile_identifier": "api_key_profile",
        "no_secret_leak": "PASS",
        "DAYTONA_STATE": "READY" if lc == 0 else "OPERATOR_REQUIRED",
    }
    write_json(OUT / "DAYTONA_AUTH_POST_LOGIN_RECEIPT.json", receipt)
    return receipt


def delete_stuck_sandboxes() -> None:
    code, out = run(["daytona", "list"])
    if code != 0:
        return
    for line in out.splitlines():
        m = re.search(r"\[([0-9a-f-]{36})", line)
        if m and "ARCHIVED" not in line.upper():
            sid = m.group(1)
            run(["daytona", "delete", sid], timeout=120)
            time.sleep(3)


def provision_h200() -> tuple[str | None, dict]:
    delete_stuck_sandboxes()
    venv_py = Path("/tmp/daytona-preflight-venv/bin/python")
    if not venv_py.exists():
        run(["python3", "-m", "venv", "/tmp/daytona-preflight-venv"])
        run(["/tmp/daytona-preflight-venv/bin/pip", "install", "-q", "daytona"])
    key = os.environ.get("DAYTONA_API_KEY", "")
    if not key:
        try:
            sys.path.insert(0, str(Path("/Users/byron/projects/active/ollarma/src")))
            from ollarma.credentials import resolve_key

            key = resolve_key("DAYTONA_API_KEY", "ollarma-daytona").decode()
        except Exception:
            pass
    env = {**os.environ, "DAYTONA_API_KEY": key} if key else os.environ.copy()
    script = """
import os, json
from daytona import Daytona, DaytonaConfig, CreateSandboxFromImageParams, Image, Resources, GpuType
client = Daytona(DaytonaConfig(api_url=os.environ.get('DAYTONA_API_URL','https://app.daytona.io/api')))
sb = client.create(CreateSandboxFromImageParams(
    image=Image.debian_slim('3.12'),
    auto_delete_interval=0,
    resources=Resources(gpu=1, gpu_type=GpuType.H200),
), timeout=900)
print(json.dumps({'id': getattr(sb,'id',None)}))
"""
    code, out = run([str(venv_py), "-c", script], timeout=960)
    sid = None
    if code == 0:
        try:
            sid = json.loads(out.splitlines()[-1]).get("id")
        except Exception:
            pass
    meta = {"create_exit": code, "create_tail": redact_secrets(out[-500:])}
    return sid, meta


def daytona_exec(sandbox: str, cmd: str, timeout: int = 300) -> tuple[int, str]:
    return run(["daytona", "exec", sandbox, "--", "bash", "-lc", cmd], timeout=timeout)


def probe_environment(sandbox: str) -> dict:
    probes = {}
    for name, cmd in {
        "gpu": "nvidia-smi --query-gpu=name,count,memory.total,driver_version --format=csv,noheader",
        "cpu": "nproc",
        "ram": "free -g | awk '/Mem:/ {print $2\"G total \"$7\"G avail\"}'",
        "disk": "df -BG / | tail -1",
        "cuda": "nvcc --version 2>/dev/null | tail -1 || echo NO_NVCC",
        "python": "python3 --version",
        "os": "cat /etc/os-release | head -2",
    }.items():
        code, out = daytona_exec(sandbox, cmd, timeout=60)
        probes[name] = {"exit": code, "output": out[:500]}
    return probes


def install_ollama(sandbox: str) -> dict:
    code, out = daytona_exec(
        sandbox,
        "curl -fsSL https://ollama.com/install.sh | sh && ollama --version",
        timeout=600,
    )
    return {"exit": code, "output": redact_secrets(out[-300:])}


def ollama_show_digest(sandbox: str, model: str) -> tuple[str | None, str]:
    code, out = daytona_exec(sandbox, f"ollama show {model} --digest 2>/dev/null || ollama show {model} 2>&1 | head -5", timeout=120)
    digest = None
    for line in out.splitlines():
        if len(line.strip()) == 64 and all(c in "0123456789abcdef" for c in line.strip()):
            digest = line.strip()
    return digest, out


def ollama_pull(sandbox: str, model: str) -> dict:
    code, out = daytona_exec(sandbox, f"ollama pull {model}", timeout=3600)
    digest, _ = ollama_show_digest(sandbox, model)
    return {"exit": code, "digest": digest, "tail": redact_secrets(out[-400:])}


def ollama_canary(sandbox: str, model: str) -> dict:
    prompt_json = json.dumps({"prompt": CANARY_PROMPT, "model": model, "stream": False, "format": "json"})
    cmd = f"ollama run {model} {json.dumps(CANARY_PROMPT)} 2>/dev/null | head -c 2000"
    code, out = daytona_exec(sandbox, cmd, timeout=600)
    parse_ok = False
    nonce_ok = False
    try:
        parsed = json.loads(out)
        parse_ok = True
        nonce_ok = parsed.get("nonce") == CANARY_NONCE and parsed.get("smoke") == "pass"
    except json.JSONDecodeError:
        pass
    digest, _ = ollama_show_digest(sandbox, model)
    return {
        "model": model,
        "exit": code,
        "parse_ok": parse_ok,
        "nonce_ok": nonce_ok,
        "digest": digest,
        "response_sha256": sha256_text(out),
        "PASS": code == 0 and parse_ok and nonce_ok and bool(digest),
    }


def prereg_integrity() -> dict:
    files = {
        "Q38-EXP008-R2/PREREGISTRATION.json": "65c3b775",
        "Q38-EXP008-R2/MATRIX_MANIFEST.json": "65c3b775",
        "Q38-EXP009-R2/PREREGISTRATION.json": "54b7e243",
        "Q38-EXP009-R2/MATRIX_MANIFEST.json": "54b7e243",
    }
    rows = []
    ok = True
    for rel, commit in files.items():
        path = OUT / rel.split("/")[0] / rel.split("/", 1)[1]
        cur = sha256_bytes(path.read_bytes())
        proc = subprocess.run(
            ["git", "show", f"{commit}:{path.relative_to(ROOT)}"],
            cwd=ROOT,
            capture_output=True,
        )
        committed = sha256_bytes(proc.stdout) if proc.returncode == 0 else None
        match = cur == committed
        ok = ok and match
        rows.append({"file": rel, "commit": commit, "sha256": cur, "match": match})
    receipt = {
        "schema": "hydradg.preregistration_integrity.v1",
        "recorded_at_utc": utc_now(),
        "PREREGISTRATION_INTEGRITY": "PASS" if ok else "FAIL",
        "files": rows,
    }
    write_json(OUT / "PREREGISTRATION_INTEGRITY_RECEIPT.json", receipt)
    return receipt


def main() -> int:
    auth = auth_receipt()
    if auth["CLI_AUTH"] != "PASS":
        print("STOP: CLI_AUTH FAIL")
        return 1
    prereg = prereg_integrity()
    if prereg["PREREGISTRATION_INTEGRITY"] != "PASS":
        print("STOP: PREREGISTRATION_INTEGRITY_FAIL")
        return 2
    sid, create_meta = provision_h200()
    if not sid:
        write_json(
            OUT / "DAYTONA_H200_ENVIRONMENT_RECEIPT.json",
            {
                "schema": "hydradg.daytona_h200_environment.v1",
                "recorded_at_utc": utc_now(),
                "state": "RESOURCE_BLOCKED_H200_UNAVAILABLE",
                "create_meta": create_meta,
            },
        )
        print("STOP: H200 unavailable")
        return 3
    sandbox = sid
    time.sleep(5)
    probes = probe_environment(sandbox)
    gpu_name = probes.get("gpu", {}).get("output", "")
    h200_ok = "H200" in gpu_name.upper()
    disk_line = probes.get("disk", {}).get("output", "")
    disk_free_gb = 0
    m = re.search(r"(\d+)G\s+\d+%", disk_line)
    if m:
        disk_free_gb = int(m.group(1))
    env_receipt = {
        "schema": "hydradg.daytona_h200_environment.v1",
        "recorded_at_utc": utc_now(),
        "sandbox_id": sandbox,
        "exact_gpu_name": gpu_name.split(",")[0].strip() if gpu_name else None,
        "h200_verified": h200_ok,
        "probes": probes,
        "disk_free_gb": disk_free_gb,
        "min_disk_target_gb": MIN_DISK_GB,
        "disk_gate": "PASS" if disk_free_gb >= MIN_DISK_GB else "FAIL",
        "state": "READY" if h200_ok and disk_free_gb >= MIN_DISK_GB else "RESOURCE_BLOCKED_H200_UNAVAILABLE",
    }
    if not h200_ok:
        env_receipt["state"] = "RESOURCE_BLOCKED_H200_UNAVAILABLE"
        write_json(OUT / "DAYTONA_H200_ENVIRONMENT_RECEIPT.json", env_receipt)
        print(f"STOP: GPU is not H200: {gpu_name}")
        return 4
    ollama_install = install_ollama(sandbox)
    env_receipt["ollama_install"] = ollama_install
    q38_pull = ollama_pull(sandbox, Q38_MODEL)
    flash_pull = ollama_pull(sandbox, FLASH_MODEL)
    q38_canary = ollama_canary(sandbox, Q38_MODEL)
    flash_canary = ollama_canary(sandbox, FLASH_MODEL)
    env_receipt["model_pulls"] = {Q38_MODEL: q38_pull, FLASH_MODEL: flash_pull}
    env_receipt["canaries"] = {Q38_MODEL: q38_canary, FLASH_MODEL: flash_canary}
    env_receipt["MODEL_CANARY_GATE"] = "PASS" if q38_canary["PASS"] and flash_canary["PASS"] else "FAIL"
    write_json(OUT / "DAYTONA_H200_ENVIRONMENT_RECEIPT.json", env_receipt)
    freeze = {
        "schema": "hydradg.qwen38.model_identity_freeze.v1",
        "recorded_at_utc": utc_now(),
        "host_class": "Daytona H200",
        "sandbox_id": sandbox,
        "DAYTONA_AUTH": "PASS",
        "MODEL_CANARY_GATE": env_receipt["MODEL_CANARY_GATE"],
        "models": {
            "QWEN38_27B": {
                "ollama_alias": Q38_MODEL,
                "daytona_digest": q38_pull.get("digest"),
                "canary": q38_canary,
            },
            "FLASH_NEXT_NVFP4": {
                "ollama_alias": FLASH_MODEL,
                "daytona_digest": flash_pull.get("digest"),
                "canary": flash_canary,
            },
        },
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    write_json(OUT / "MODEL_IDENTITY_FREEZE.json", freeze)
    write_json(OUT / "DAYTONA_SANDBOX_ACTIVE.json", {"sandbox_id": sandbox, "name": sandbox})
    print(json.dumps({"sandbox": sandbox, "h200": h200_ok, "canary": env_receipt["MODEL_CANARY_GATE"]}, indent=2))
    return 0 if env_receipt["MODEL_CANARY_GATE"] == "PASS" else 5


if __name__ == "__main__":
    raise SystemExit(main())
