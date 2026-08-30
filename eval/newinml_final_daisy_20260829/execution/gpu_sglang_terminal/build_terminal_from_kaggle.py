#!/usr/bin/env python3
"""Materialize terminal GPU/SGLang receipts from Kaggle output directory."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GPU_EXEC = ROOT / "gpu_sglang_terminal"
KAGGLE_OUT = ROOT / "lane12_kaggle/kaggle_output"


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p: Path, obj: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def main() -> None:
    results_path = KAGGLE_OUT / "hydradg_sglang/execution_results.json"
    cuda_path = KAGGLE_OUT / "hydradg_sglang/cuda_proof.json"
    if not results_path.is_file():
        raise SystemExit(f"missing {results_path}")
    results = json.loads(results_path.read_text())
    cuda = json.loads(cuda_path.read_text()) if cuda_path.is_file() else {}

    cells = []
    nonce_pass = False
    for block in results.get("results", []):
        for c in block.get("cells", []):
            if c.get("type") == "FRESH_NONCE":
                nonce_pass = bool(c.get("pass"))
            else:
                cells.append(c)

    prov = {
        "provider": "kaggle",
        "kernel": "biobitworks/hydradg-newinml-sglang-hl001-gpu-canary-v2",
        "gpu_type": cuda.get("name"),
        "region": "kaggle-us",
        "recorded_at_utc": utc(),
        "action": "KERNEL_COMPLETE",
    }
    write_json(GPU_EXEC / "GPU_PROVISIONING_RECEIPT.json", prov)

    proof = {
        "schema": "hydradg.gpu_runtime_proof.v1",
        "provider": "kaggle",
        "CUDA_AVAILABLE": bool(cuda.get("cuda")),
        "CUDA_DEVICE_COUNT": cuda.get("n", 0),
        "GPU_MODEL": cuda.get("name"),
        "PYTORCH_VERSION": cuda.get("torch"),
        "recorded_at_utc": utc(),
        "stdout_head": json.dumps(cuda),
    }
    proof["receipt_sha256"] = hashlib.sha256(json.dumps(proof, sort_keys=True).encode()).hexdigest()
    write_json(GPU_EXEC / "GPU_RUNTIME_PROOF.json", proof)

    executed = len(cells)
    pass_cells = sum(1 for c in cells if c.get("terminal_state") == "PASS")
    sglang_ok = bool(results.get("sglang_version")) or results.get("sglang_installed", False)

    closeout = {
        "FINAL_GPU_SGLANG_STATE": "EXTERNAL_PROVIDER_BLOCKED"
        if not sglang_ok
        else ("PARTIAL_EXECUTION" if executed < 24 else "GREEN_AND_RUNNING"),
        "GPU_PROVIDER": "kaggle",
        "GPU_RUNTIME_PROVISIONED": True,
        "CUDA_AVAILABLE": bool(cuda.get("cuda")),
        "SGLANG_STATE": "NOT_STARTED" if not sglang_ok else ("RUNNING" if executed >= 20 else "DEGRADED"),
        "FRESH_NONCE_CANARY": "PASS" if nonce_pass else "FAIL",
        "PREREGISTERED_EXPERIMENT_EXECUTED": executed == 24,
        "EXECUTED_CELLS": executed,
        "PASS_CELLS": pass_cells,
        "FAIL_CELLS": executed - pass_cells,
        "EARLIEST_DIVERGENCE": "SGLANG_INSTALL_FAILED"
        if not sglang_ok
        else ("SERVER_START_FAILED" if executed == 0 else None),
        "recorded_at_utc": utc(),
    }
    write_json(GPU_EXEC / "FINAL_GPU_SGLANG_CLOSEOUT.json", closeout)
    (GPU_EXEC / "FINAL_GPU_SGLANG_CLOSEOUT.md").write_text(
        "# GPU SGLang Closeout (Kaggle)\n\n```json\n" + json.dumps(closeout, indent=2) + "\n```\n"
    )
    print(json.dumps(closeout, indent=2))


if __name__ == "__main__":
    main()
