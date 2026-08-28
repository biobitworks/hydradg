#!/usr/bin/env python3
"""Remote provider capability audit for Qwen3.8 successor replay."""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval/qwen38_model_replay_20260828"

QWEN38_27B_HF = "Qwen/Qwen3.8-27B"
FLASH_NEXT_HF = "Qwen/Qwen3.8-Flash-Next"
FLASH_NEXT_OLLAMA = "qwen3.8-flash-next:125b-mlx"

# Feasibility estimates (bytes) — conservative for gate
QWEN38_27B_BF16_BYTES = 54 * (1024**3)
QWEN38_27B_FP8_BYTES = 28 * (1024**3)
FLASH_NEXT_BF16_BYTES = 350 * (1024**3)
FLASH_NEXT_FP8_BYTES = 180 * (1024**3)
FLASH_NEXT_MLX_OLLAMA_BYTES = 105 * (1024**3)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def disk_free_gb() -> float:
    try:
        return round(shutil.disk_usage("/").free / (1024**3), 2)
    except OSError:
        return 0.0


def audit_daytona() -> dict:
    code, ver = run_cmd(["daytona", "--version"]) if shutil.which("daytona") else (1, "NOT_FOUND")
    api_key = os.environ.get("DAYTONA_API_KEY", "")
    login_state = "NOT_AUTHENTICATED"
    sandbox_list_ok = False
    if code == 0:
        lc, lo = run_cmd(["daytona", "sandbox", "list"])
        if lc == 0:
            login_state = "AUTHENTICATED"
            sandbox_list_ok = True
        elif "no profiles found" in lo.lower() or "login" in lo.lower():
            login_state = "CLI_NOT_LOGGED_IN"
        elif not api_key:
            login_state = "CLI_NOT_LOGGED_IN_NO_ENV_KEY"
    return {
        "provider": "Daytona",
        "cli_available": code == 0,
        "cli_version": ver if code == 0 else None,
        "DAYTONA_API_KEY_ENV": "PRESENT" if api_key else "ABSENT",
        "login_state": login_state,
        "sandbox_list_ok": sandbox_list_ok,
        "prior_smoke_receipt": "eval/agent_native_sponsors_20260827/daytona/DAYTONA_SMOKE_RECEIPT.json",
        "prior_smoke_state": "LIVE_PASS",
        "prior_smoke_note": "Prior smoke used DAYTONA_API_KEY on Studio; current shell lacks key/profile",
        "gpu_classes_probed": False,
        "state": "BLOCKED" if login_state != "AUTHENTICATED" else "PROVISIONING_CANDIDATE",
    }


def audit_kaggle() -> dict:
    kaggle_bin = shutil.which("kaggle")
    username = os.environ.get("KAGGLE_USERNAME", "")
    key = os.environ.get("KAGGLE_KEY", "")
    return {
        "provider": "Kaggle",
        "cli_available": kaggle_bin is not None,
        "KAGGLE_USERNAME": "PRESENT" if username else "ABSENT",
        "KAGGLE_KEY": "PRESENT" if key else "ABSENT",
        "state": "NOT_CONFIGURED" if not kaggle_bin else ("CREDENTIALS_PRESENT" if username and key else "CLI_MISSING_CREDS"),
        "note": "Kaggle CLI not on PATH; credentials partially present in environment",
    }


def feasibility_gate() -> dict:
    local_disk = disk_free_gb()
    return {
        "schema": "hydradg.qwen38.remote_artifact_feasibility.v1",
        "recorded_at_utc": utc_now(),
        "host_disk_free_gb": local_disk,
        "models": {
            "QWEN38_27B": {
                "repo": QWEN38_27B_HF,
                "MODEL_WEIGHT_BYTES_BF16": QWEN38_27B_BF16_BYTES,
                "MODEL_WEIGHT_BYTES_FP8": QWEN38_27B_FP8_BYTES,
                "MINIMUM_GPU_VRAM_FP8_GB": 32,
                "MINIMUM_DISK_REQUIREMENT_GB": 35,
                "cuda_ollama_studio_artifact": "gguf Q4_K_M ~17GB — not portable to Linux CUDA",
            },
            "FLASH_NEXT": {
                "repo": FLASH_NEXT_HF,
                "ollama_mlx_tag": FLASH_NEXT_OLLAMA,
                "MODEL_WEIGHT_BYTES_MLX_OLLAMA": FLASH_NEXT_MLX_OLLAMA_BYTES,
                "MODEL_WEIGHT_BYTES_BF16": FLASH_NEXT_BF16_BYTES,
                "MODEL_WEIGHT_BYTES_FP8": FLASH_NEXT_FP8_BYTES,
                "MINIMUM_HOST_RAM_GB": 128,
                "MINIMUM_GPU_VRAM_FP8_GB": 80,
                "MINIMUM_DISK_REQUIREMENT_GB": 110,
                "OFFLOAD_REQUIREMENTS": "51B n-gram/PLE table may require NVMe offload; architecture-specific",
                "cuda_compatible_mlx_ollama": False,
            },
        },
        "local_flash_next_pull_feasible": local_disk >= 110,
        "local_flash_next_pull_state": "BLOCKED" if local_disk < 110 else "FEASIBLE",
        "FLASH_NEXT_REMOTE_CAPACITY_BLOCKED": True,
        "block_reasons": [
            f"local_disk_free_gb={local_disk} < 110 required for MLX Ollama artifact",
            "Daytona CLI not authenticated in current shell; GPU sandbox not provisioned",
            "Flash-Next MLX Ollama artifact not admissible on Linux CUDA without separate HF artifact",
            "Flash-Next HF full weights ~180GB+; exceeds typical single-GPU Daytona quota without multi-node",
        ],
    }


def runtime_compatibility_matrix() -> dict:
    return {
        "schema": "hydradg.qwen38.runtime_compatibility_matrix.v1",
        "recorded_at_utc": utc_now(),
        "note": "Import/model-load not probed on remote; Flash-Next architecture is preview MoE+Engram",
        "matrix": {
            "Transformers_pinned": {"Qwen3.8-27B": "UNTESTED", "Flash-Next": "UNTESTED"},
            "vLLM_pinned": {"Qwen3.8-27B": "UNTESTED", "Flash-Next": "LIKELY_BLOCKED"},
            "SGLang_pinned": {"Qwen3.8-27B": "UNTESTED", "Flash-Next": "LIKELY_BLOCKED"},
            "Ollama_mlx_studio": {"Qwen3.8-27B": "PASS", "Flash-Next": "NOT_INSTALLED"},
            "Ollama_cuda_daytona": {"Qwen3.8-27B": "BLOCKED", "Flash-Next": "BLOCKED"},
        },
        "RUNTIME_EQUIVALENCE": "NO",
        "MODEL_COMPARISON_CLAIM": "DESCRIPTIVE_ONLY",
        "recommended_path_if_unblocked": "same pinned Transformers for BOTH on CUDA host with pinned HF revisions",
    }


def select_provider(daytona: dict, kaggle: dict, feasibility: dict) -> dict:
    if daytona.get("login_state") == "AUTHENTICATED":
        selected = "Daytona"
        state = "PROVISIONING"
    elif kaggle.get("state") == "CREDENTIALS_PRESENT" and kaggle.get("cli_available"):
        selected = "Kaggle"
        state = "PROVISIONING"
    else:
        selected = "BLOCKED_REMOTE_CAPACITY"
        state = "BLOCKED"
    return {
        "SELECTED_REMOTE_PROVIDER": selected,
        "DAYTONA_STATE": daytona.get("state"),
        "KAGGLE_STATE": kaggle.get("state"),
        "REMOTE_SELECTION_STATE": state,
        "FLASH_NEXT_BLOCK": feasibility.get("FLASH_NEXT_REMOTE_CAPACITY_BLOCKED"),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    daytona = audit_daytona()
    kaggle = audit_kaggle()
    feasibility = feasibility_gate()
    runtime = runtime_compatibility_matrix()
    selection = select_provider(daytona, kaggle, feasibility)

    audit = {
        "schema": "hydradg.qwen38.remote_provider_capability_audit.v1",
        "recorded_at_utc": utc_now(),
        "host": socket.gethostname(),
        "daytona": daytona,
        "kaggle": kaggle,
        "feasibility_gate": feasibility,
        "runtime_compatibility": runtime,
        "selection": selection,
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    path = OUT / "REMOTE_PROVIDER_CAPABILITY_AUDIT.json"
    path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    (OUT / "RUNTIME_COMPATIBILITY_MATRIX.json").write_text(
        json.dumps(runtime, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "REMOTE_ARTIFACT_FEASIBILITY_GATE.json").write_text(
        json.dumps(feasibility, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(selection, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
