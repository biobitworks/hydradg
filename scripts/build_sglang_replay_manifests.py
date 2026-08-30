#!/usr/bin/env python3
"""Build SGLang replay preregistration, case order, graph config, model equivalence."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from pathlib import Path
from typing import Any

ORDER_SEED = 20260828
PERTURBATIONS = ["CONTROL", "INVALID_PROOF", "REPLAYED_PROOF", "BROKEN_AUTHORIZATION_EDGE"]
REPLICATES = 25
GRAPH_MODES = ["G0_EAGER", "G1_FULL", "G2_BREAKABLE"]
SGLANG_PIN_SHA = "acc918b3ece60af20321612b8ad204bdba8fcb80"  # upstream HEAD at freeze time; pin before CUDA run


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def select_historical_runs(repo: Path) -> dict[str, list[str]]:
    runs_dir = repo / "eval/hydralamp_runtype_20260826/runs"
    by_pert: dict[str, list[str]] = {p: [] for p in PERTURBATIONS}
    for d in sorted(runs_dir.iterdir()):
        if not d.is_dir():
            continue
        rp = d / "RUN_RECEIPT.json"
        if not rp.exists():
            continue
        rec = json.loads(rp.read_text(encoding="utf-8"))
        p = rec.get("perturbation")
        if p in by_pert and len(by_pert[p]) < REPLICATES:
            by_pert[p].append(rec["run_id"])
    return by_pert


def build_case_order(repo: Path) -> dict[str, Any]:
    historical = select_historical_runs(repo)
    slots: list[dict[str, Any]] = []
    for rep in range(REPLICATES):
        for pert in PERTURBATIONS:
            run_id = historical[pert][rep] if rep < len(historical[pert]) else None
            for mode in GRAPH_MODES:
                case_id = f"{pert}_R{rep:02d}_{mode}"
                slots.append({
                    "case_id": case_id,
                    "perturbation": pert,
                    "replicate": rep,
                    "graph_mode": mode,
                    "historical_run_id": run_id,
                    "paired_across_modes": [f"{pert}_R{rep:02d}_{m}" for m in GRAPH_MODES],
                })
    rng = random.Random(ORDER_SEED)
    rng.shuffle(slots)
    for i, slot in enumerate(slots):
        slot["order_index"] = i
    manifest = {
        "schema": "hydradg.sglang_replay.case_order.v1",
        "ORDER_SEED": ORDER_SEED,
        "primary_execution_count": len(slots),
        "expected_if_all_supported": 300,
        "perturbations": PERTURBATIONS,
        "replicates_per_perturbation": REPLICATES,
        "graph_modes": GRAPH_MODES,
        "historical_run_mapping": historical,
        "cases": slots,
    }
    manifest["ORDER_MANIFEST_SHA256"] = sha256_bytes(canonical_json(manifest))
    return manifest


def runtime_inventory() -> dict[str, Any]:
    cuda = False
    try:
        subprocess.check_output(["nvidia-smi"], stderr=subprocess.DEVNULL)
        cuda = True
    except Exception:
        cuda = False
    try:
        import torch
        torch_cuda = torch.cuda.is_available()
        torch_ver = torch.__version__
    except Exception:
        torch_cuda = False
        torch_ver = "NOT_INSTALLED"
    sglang_installed = False
    try:
        subprocess.check_output(["python3", "-c", "import sglang"], stderr=subprocess.DEVNULL)
        sglang_installed = True
    except Exception:
        pass
    return {
        "schema": "hydradg.sglang_replay.runtime_inventory.v1",
        "execution_host": "magicSTUDIObox.local",
        "CUDA_AVAILABLE": cuda and torch_cuda,
        "GPU_MODEL": None,
        "GPU_COUNT": 0,
        "CUDA_VERSION": None,
        "DRIVER_VERSION": None,
        "PYTORCH_VERSION": torch_ver,
        "SGLANG_INSTALLED": sglang_installed,
        "SGLANG_VERSION": None,
        "SGLANG_GIT_SHA": SGLANG_PIN_SHA,
        "KAGGLE_CLI": False,
        "REPLAY_EQUIVALENCE": "BLOCKED_CUDA_UNAVAILABLE" if not (cuda and torch_cuda) else "PENDING_EXECUTION",
        "CUDA_EXECUTION_HOST": "magicSTUDIObox.local",
        "note": "Do not pretend non-CUDA execution is a CUDA-graph experiment",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    out_dir = repo / "eval/ic_failure_learning_20260827/sglang_replay"
    out_dir.mkdir(parents=True, exist_ok=True)

    prereg = {
        "schema": "hydradg.sglang_replay.preregistration.v1",
        "status": "PREREGISTERED_BLOCKED_CUDA",
        "predecessor_ic_failure_learning_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True
        ).strip(),
        "historical_root": "eval/hydralamp_runtype_20260826",
        "historical_model_id": "qwen/qwen3.6-27b",
        "sglang_candidate_model_id": "Qwen/Qwen3-8B",
        "sglang_git_sha_pin": SGLANG_PIN_SHA,
        "graph_modes": {
            "G0_EAGER": {"prefill": "disabled", "decode": "disabled"},
            "G1_FULL": {"prefill": "full", "decode": "full"},
            "G2_BREAKABLE": {"prefill": "breakable", "decode": "full", "env": {"SGLANG_USE_BREAKABLE_CUDA_GRAPH": "1"}},
            "G3_BREAKABLE_EXTENDED": {"status": "OPTIONAL_BLOCKED_UNTIL_SUPPORTED"},
        },
        "hypotheses": ["H_BCG_CORRECTNESS", "H_BCG_FAILURE_LOCALIZATION", "H_BCG_RECOVERY", "H_BCG_SECURITY", "H_BCG_PERFORMANCE"],
        "preserve_security_vs_policy_split": True,
        "historical_runtype_probe_preserved": {
            "LIVE_RUNTYPE_READY": "PROBE_CONTROL_SMOKE",
            "control_smoke_lane_status": "ERROR",
            "runtype_execution_id": None,
        },
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
    }
    (out_dir / "PREREGISTRATION.json").write_text(json.dumps(prereg, indent=2) + "\n", encoding="utf-8")

    graph_cfg = {
        "schema": "hydradg.sglang_replay.graph_config.v1",
        "SGLANG_GIT_SHA": SGLANG_PIN_SHA,
        "configs": prereg["graph_modes"],
        "resolved_at_execution": False,
        "claim_ceiling": "PREREGISTERED_CONFIG_NOT_EXECUTED",
    }
    (out_dir / "GRAPH_CONFIG_MANIFEST.json").write_text(json.dumps(graph_cfg, indent=2) + "\n", encoding="utf-8")

    case_order = build_case_order(repo)
    (out_dir / "CASE_ORDER_MANIFEST.json").write_text(json.dumps(case_order, indent=2) + "\n", encoding="utf-8")

    inv = runtime_inventory()
    (out_dir / "RUNTIME_INVENTORY.json").write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")

    equiv = {
        "schema": "hydradg.sglang_replay.model_equivalence.v1",
        "HISTORICAL_MODEL_ID": "qwen/qwen3.6-27b",
        "HISTORICAL_MODEL_DIGEST_IF_AVAILABLE": None,
        "SGLANG_MODEL_ID": "Qwen/Qwen3-8B",
        "SGLANG_MODEL_DIGEST": None,
        "MODEL_EQUIVALENCE_STATE": "NOT_EQUIVALENT",
        "interpretation": "SGLANG_RUNTIME_REPLICATION — restrict causal claims to within-SGLang graph-mode comparisons only",
        "claim_ceiling": "MODEL_EQUIVALENCE_RECEIPT_ONLY",
    }
    (out_dir / "MODEL_EQUIVALENCE_RECEIPT.json").write_text(json.dumps(equiv, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"cases": len(case_order["cases"]), "replay_equivalence": inv["REPLAY_EQUIVALENCE"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
