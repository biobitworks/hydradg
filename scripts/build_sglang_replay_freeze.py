#!/usr/bin/env python3
"""Freeze historical HydraLamp/Runtype experiment artifacts for SGLang replay."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HISTORICAL_ROOT = "eval/hydralamp_runtype_20260826"
REQUIRED = [
    "EVAL_SUITE.json",
    "CORE_STRESS_RECEIPT.json",
    "HASH_TAMPER_STRESS_RECEIPT.json",
    "CONCURRENCY_STRESS_RECEIPT.json",
    "CONTEXT_DELTA_RECEIPT.json",
    "SSE_STRESS_RECEIPT.json",
    "RESTART_RECOVERY_RECEIPT.json",
    "LOCAL_MODEL_STRESS_RECEIPT.json",
    "LIVE_RUNTYPE_STRESS_RECEIPT.json",
    "SMOKE_PASS_RECEIPT.json",
    "MODEL_INVENTORY.json",
    "HYDRALAMP_SCIENCE_CLOSEOUT_RECEIPT.json",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(repo: Path, rel: str) -> str | None:
    import subprocess
    try:
        return subprocess.check_output(["git", "hash-object", rel], cwd=repo, text=True).strip()
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="eval/ic_failure_learning_20260827/sglang_replay/HISTORICAL_EXPERIMENT_FREEZE.json")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    hist = repo / HISTORICAL_ROOT
    entries: list[dict[str, Any]] = []
    for name in REQUIRED:
        path = hist / name
        if not path.exists():
            entries.append({"path": f"{HISTORICAL_ROOT}/{name}", "status": "MISSING"})
            continue
        raw = path.read_bytes()
        entries.append({
            "path": f"{HISTORICAL_ROOT}/{name}",
            "status": "FROZEN",
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
            "git_blob_sha": git_blob_sha(repo, f"{HISTORICAL_ROOT}/{name}"),
            "historical_or_successor": "historical",
            "role": name.replace(".json", ""),
            "training_visibility": "EVAL_ONLY",
            "evaluation_visibility": "HISTORICAL_BASELINE",
        })
    manifest = {
        "schema": "hydradg.sglang_replay.historical_freeze.v1",
        "historical_root": HISTORICAL_ROOT,
        "entry_count": len(entries),
        "entries": entries,
        "matrix_contract": {
            "CONTROL": 25,
            "INVALID_PROOF": 25,
            "REPLAYED_PROOF": 25,
            "BROKEN_AUTHORIZATION_EDGE": 25,
            "total": 100,
        },
        "tamper_cases": [
            "TAMPER_01_alter_model_context_byte",
            "TAMPER_02_alter_model_response_byte",
            "TAMPER_03_alter_tool_result",
            "TAMPER_04_remove_fcg_edge",
            "TAMPER_05_reorder_two_events",
            "TAMPER_06_change_prev_event_hash",
            "TAMPER_07_replay_old_proof",
            "TAMPER_08_altered_graph_expected_root",
        ],
        "POISON_MUST_REMAIN_IMMUTABLE": True,
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
    }
    out = (repo / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"frozen": sum(1 for e in entries if e.get("status") == "FROZEN"), "out": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
