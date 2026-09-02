#!/usr/bin/env python3
"""Forward-only Q38 leaf accounting and remediation artifact generation."""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "eval/qwen38_model_replay_20260828/remediation"
LEAF_DIR = OUT / "leaves"
EXP_ID = "Q38-EXP008-R"
MODEL_DIGEST = "22130167c4c20e20c7b71454612966ca8e8171e9b3cc8ab6ce8aa6cbfec79643"
MODEL_TAG = "qwen3.8:27b"
N_REPLICATES = 3
Q3_CASE = "E01-T0"
Q4_CASES = ["E01-T0", "E02-0", "E02-1", "E02-2", "E02-3"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def canonical_key(case_id: str, condition: str, replicate: int) -> tuple[str, str, str, str, str, int]:
    return (EXP_ID, MODEL_DIGEST, case_id, condition, MODEL_TAG, replicate)


def key_to_dict(k: tuple) -> dict[str, Any]:
    return {
        "experiment_id": k[0],
        "model_digest": k[1],
        "case_id": k[2],
        "condition": k[3],
        "model_tag": k[4],
        "replicate": k[5],
    }


def load_cases() -> list[str]:
    cases_path = ROOT / "eval/ic_failure_learning_20260827/cases/CASES.jsonl"
    return [json.loads(line)["case_id"] for line in cases_path.read_text().splitlines() if line.strip()]


def infer_terminal_state(row: dict[str, Any]) -> str:
    run_state = row.get("run_state", "")
    parser_state = row.get("parser_state", "")
    if run_state.startswith("FAILED:TimeoutError"):
        return "TIMEOUT"
    if run_state.startswith("FAILED:"):
        return "EXECUTION_FAILURE"
    if parser_state == "MALFORMED_JSON":
        return "MALFORMED_JSON"
    if parser_state == "PARSED_JSON":
        # abstention json from timeout path
        if run_state != "OK":
            return "EXECUTION_FAILURE"
        return "SUCCESS"  # custody terminal; scorer may later refine WRONG_ANSWER
    return "UNKNOWN"


def build_expected_leaves(cases: list[str]) -> list[dict[str, Any]]:
    leaves = []
    for case_id in cases:
        for condition in ("C0", "C1"):
            for replicate in range(1, N_REPLICATES + 1):
                k = canonical_key(case_id, condition, replicate)
                leaves.append({**key_to_dict(k), "leaf_id": "|".join(str(x) for x in k)})
    leaves.sort(key=lambda r: (r["case_id"], r["condition"], r["replicate"]))
    return leaves


def load_actual_rows() -> tuple[dict[tuple, dict], list[tuple], list[tuple]]:
    raw_path = ROOT / "eval/ic_failure_learning_20260827/qwen38_model_replay_20260828/EXP-008-Q38/RAW_OUTPUTS.jsonl"
    terminal: dict[tuple, dict] = {}
    duplicates: list[tuple] = []
    invalidated: list[tuple] = []
    expected_digest = MODEL_DIGEST
    for line in raw_path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        k = canonical_key(row["case_id"], row["condition"], row["replicate"])
        if row.get("model_digest") != expected_digest:
            invalidated.append(k)
            continue
        if k in terminal:
            duplicates.append(k)
            continue
        terminal[k] = {
            **key_to_dict(k),
            "leaf_id": "|".join(str(x) for x in k),
            "terminal_state": infer_terminal_state(row),
            "parser_state": row.get("parser_state"),
            "run_state": row.get("run_state"),
            "prompt_sha256": row.get("prompt_sha256"),
            "raw_response_sha256": row.get("raw_response_sha256"),
            "latency_seconds": row.get("latency_seconds"),
            "source_row_sha256": sha256_bytes(line.encode("utf-8")),
        }
    return terminal, duplicates, invalidated


def write_jsonl(path: Path, rows: list[dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    path.write_text(content, encoding="utf-8")
    return sha256_bytes(content.encode("utf-8"))


def stage_subset(keys: set[tuple], terminal: dict[tuple, dict]) -> dict[str, int]:
    present = {k for k in keys if k in terminal}
    return {"expected": len(keys), "terminal": len(present), "missing": len(keys) - len(present)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    LEAF_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_cases()
    expected = build_expected_leaves(cases)
    expected_sha = write_jsonl(LEAF_DIR / "EXPECTED_CELL_LEAVES.jsonl", expected)

    terminal_map, duplicates, invalidated_keys = load_actual_rows()
    actual_rows = sorted(terminal_map.values(), key=lambda r: (r["case_id"], r["condition"], r["replicate"]))
    actual_sha = write_jsonl(LEAF_DIR / "ACTUAL_TERMINAL_LEAVES.jsonl", actual_rows)

    expected_keys = {canonical_key(r["case_id"], r["condition"], r["replicate"]) for r in expected}
    missing_keys = expected_keys - set(terminal_map.keys())
    missing_rows = sorted(
        [{**key_to_dict(k), "leaf_id": "|".join(str(x) for x in k), "reason": "UNRECEIPTED"} for k in missing_keys],
        key=lambda r: (r["case_id"], r["condition"], r["replicate"]),
    )
    missing_sha = write_jsonl(LEAF_DIR / "MISSING_CELL_LEAVES.jsonl", missing_rows)

    invalidated_rows = sorted(
        [{**key_to_dict(k), "leaf_id": "|".join(str(x) for x in k), "reason": "INTEGRITY_INVALIDATED"} for k in invalidated_keys],
        key=lambda r: (r["case_id"], r["condition"], r["replicate"]),
    )
    invalidated_sha = write_jsonl(LEAF_DIR / "INVALIDATED_CELL_LEAVES.jsonl", invalidated_rows)

    # Q3
    q3_keys = {canonical_key(Q3_CASE, c, r) for c in ("C0", "C1") for r in range(1, N_REPLICATES + 1)}
    q3 = stage_subset(q3_keys, terminal_map)

    # Q4 corrected
    q4_keys = {canonical_key(cid, cond, r) for cid in Q4_CASES for cond in ("C0", "C1") for r in range(1, N_REPLICATES + 1)}
    q4 = stage_subset(q4_keys, terminal_map)
    q4_c0_keys = {k for k in q4_keys if k[2] in Q4_CASES and k[3] == "C0"}
    q4_c1_keys = {k for k in q4_keys if k[2] in Q4_CASES and k[3] == "C1"}
    q4_c0 = stage_subset(q4_c0_keys, terminal_map)
    q4_c1 = stage_subset(q4_c1_keys, terminal_map)

    terminal_counts = Counter(r["terminal_state"] for r in actual_rows)
    condition_counts = Counter((r["case_id"], r["condition"]) for r in actual_rows)

    accounting = {
        "schema": "hydradg.qwen38.experiment_leaf_accounting.v1",
        "recorded_at_utc": utc_now(),
        "experiment_id": EXP_ID,
        "model_tag": MODEL_TAG,
        "model_digest": MODEL_DIGEST,
        "case_count": len(cases),
        "expected_local_leaves": len(expected),
        "terminal_local_leaves": len(actual_rows),
        "missing_local_leaves": len(missing_rows),
        "invalidated_local_leaves": len(invalidated_rows),
        "duplicate_canonical_keys": len(duplicates),
        "balance_check": len(expected) == len(actual_rows) + len(missing_rows) + len(invalidated_rows),
        "EXPECTED_CELL_LEAVES_SHA256": expected_sha,
        "ACTUAL_TERMINAL_LEAVES_SHA256": actual_sha,
        "MISSING_CELL_LEAVES_SHA256": missing_sha,
        "INVALIDATED_CELL_LEAVES_SHA256": invalidated_sha,
        "terminal_state_counts": dict(terminal_counts),
        "global_condition_coverage": dict(Counter(r["condition"] for r in actual_rows)),
        "q3": q3,
        "q4_corrected": {
            "expected": q4["expected"],
            "terminal": q4["terminal"],
            "missing": q4["missing"],
            "c0": q4_c0,
            "c1": q4_c1,
            "prior_27_of_30_valid": "NO",
            "prior_receipt_defect": "Counted cells outside Q4 5-case scope (E02-4,E03-*) as Q4 progress",
        },
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (OUT / "EXPERIMENT_LEAF_ACCOUNTING.json").write_text(json.dumps(accounting, indent=2) + "\n", encoding="utf-8")

    q4_correction = {
        "schema": "hydradg.qwen38.q4_accounting_correction.v1",
        "recorded_at_utc": utc_now(),
        "forward_only": True,
        "supersedes_stale_prose_only": True,
        "Q4_EXPECTED": 30,
        "Q4_C0_EXPECTED": 15,
        "Q4_C0_TERMINAL": q4_c0["terminal"],
        "Q4_C1_EXPECTED": 15,
        "Q4_C1_TERMINAL": q4_c1["terminal"],
        "Q4_TOTAL_TERMINAL": q4["terminal"],
        "Q4_MISSING": q4["missing"],
        "Q4_PRIOR_27_OF_30_VALID": "NO",
        "explanation": "Prior staircase counted 27 global C0 cells including out-of-scope cases; valid Q4 intersection is 15/30.",
        "q4_case_set": Q4_CASES,
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (OUT / "Q4_ACCOUNTING_CORRECTION_RECEIPT.json").write_text(json.dumps(q4_correction, indent=2) + "\n", encoding="utf-8")

    # Action matrix: missing leaves grouped
    q3_missing = sorted(
        [key_to_dict(k) | {"stage": "Q3"} for k in q3_keys if k not in terminal_map],
        key=lambda r: (r["condition"], r["replicate"]),
    )
    q4_missing = sorted(
        [key_to_dict(k) | {"stage": "Q4"} for k in q4_keys if k not in terminal_map],
        key=lambda r: (r["case_id"], r["condition"], r["replicate"]),
    )
    q5_missing = sorted(
        [key_to_dict(k) | {"stage": "Q5"} for k in missing_keys],
        key=lambda r: (r["case_id"], r["condition"], r["replicate"]),
    )
    action_matrix = {
        "schema": "hydradg.qwen38.experiment_action_matrix.v1",
        "recorded_at_utc": utc_now(),
        "q3_missing_cells": q3_missing,
        "q4_missing_cells": q4_missing,
        "q5_missing_cells_count": len(q5_missing),
        "next_execution_batch_q3": q3_missing,
        "cells_reused": len(actual_rows),
        "cells_newly_executed": 0,
        "cells_invalidated": len(invalidated_rows),
        "selective_scientific_reruns": 0,
        "SIGNATURE_STATE": "NOT_SIGNED",
    }
    (OUT / "EXPERIMENT_ACTION_MATRIX.json").write_text(json.dumps(action_matrix, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"expected": len(expected), "terminal": len(actual_rows), "missing": len(missing_rows), "q3": q3, "q4": q4}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
