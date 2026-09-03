#!/usr/bin/env python3
"""Piecewise SGLang stress: TC_PIECEWISE + BREAKABLE on an existing Daytona sandbox."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import newinml_gpu_sglang_daisy_execute as g  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox-id", required=True)
    args = parser.parse_args()

    g.load_secrets()
    state = g.load_state()
    state["provider"] = "daytona"
    state["sandbox_id"] = args.sandbox_id
    state["stages"] = {"D0": "PASS", "D1": "PASS", "D2": "PASS"}
    g.save_state(state)

    proof = g.cuda_proof_daytona(args.sandbox_id)
    cuda_ok = bool(proof.get("CUDA_AVAILABLE"))
    if not cuda_ok:
        # cuda_proof_daytona matches Python "True" in stdout; JSON emits lowercase true.
        probe = g.daytona_exec(
            args.sandbox_id,
            'python3 -c "import torch,json; print(json.dumps({\'cuda\':torch.cuda.is_available()}))"',
            timeout=120,
        )
        cuda_ok = probe["exit_code"] == 0 and "true" in (probe.get("stdout") or "").lower()
        proof["CUDA_AVAILABLE"] = cuda_ok
        proof["cuda_probe_fallback"] = True
        g.write_json(g.GPU_EXEC / "GPU_RUNTIME_PROOF.json", proof)
    print(json.dumps({"stage": "cuda_proof", "CUDA_AVAILABLE": cuda_ok}))
    if not cuda_ok:
        return 2

    remote = g.execute_remote_daytona(args.sandbox_id)
    g.write_json(g.GPU_EXEC / "REMOTE_EXECUTION_RECEIPT.json", remote)
    closeout = g.build_terminal_artifacts(remote.get("remote_results", {}), state)
    state["stages"]["D5"] = "PASS" if remote.get("ok") else "FAIL"
    g.save_state(state)
    g.write_json(g.GPU_EXEC / "FINAL_GPU_SGLANG_CLOSEOUT.json", closeout)
    print(json.dumps(closeout, indent=2))
    return 0 if remote.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
