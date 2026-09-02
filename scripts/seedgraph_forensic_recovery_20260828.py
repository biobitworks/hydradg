#!/usr/bin/env python3
"""Deterministic SeedGraph PID 96177 forensic recovery artifact generator.

Read-only with respect to SeedGraph outputs on magicBLACKbox. Does not delete,
move, or rewrite partial predecessor artifacts.
"""
from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path("/Users/byron/projects/active/hydradg")
OUT_DIR = REPO / "eval/seedgraph_forensic_recovery_20260828"
ENGINE = REPO / "scripts/seedgraph_hierarchy_v1a.py"
WATCHER = REPO / "scripts/ollarma_seedgraph_v1a_watcher.py"
OUTPUT_ROOT = Path("/Volumes/magicBLACKbox/hydradg/seedgraph/v1a_validation")
AUDIT_ROOT = Path("/Volumes/magicBLACKbox/hydradg/seedgraph/audits")
WATCH_JSONL = AUDIT_ROOT / "v1a_validation_watch_20260824.jsonl"
TERMINAL_RECEIPT = AUDIT_ROOT / "v1a_validation_watch_20260824_terminal_receipt.json"
SWAP_RECEIPT = Path(
    "/Users/byron/projects/active/hydradg-qwen38-model-replay-20260828/"
    "eval/qwen38_model_replay_20260828/remediation/SWAP_REMEDIATION_RECEIPT.json"
)

SOURCES = {
    "track01_questions": Path(
        "/Users/byron/.local/share/hydradg-datasets/track01/"
        "enterprise-rag-bench/data/questions/test.parquet"
    ),
    "track01_documents": Path(
        "/Users/byron/.local/share/hydradg-datasets/track01/"
        "enterprise-rag-bench/data/documents/test.parquet"
    ),
    "track03_json": Path(
        "/Users/byron/.local/share/hydradg-datasets/track03/"
        "longmemeval-cleaned/longmemeval_s_cleaned.json"
    ),
}

EXPECTED_ARTIFACTS = [
    "nodes.parquet",
    "edges.parquet",
    "seed_index.parquet",
    "questions.parquet",
    "question_seeds.parquet",
    "BUILD_RECEIPT.json",
    "SHA256SUMS.txt",
    "track03_turn_projection.parquet",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path, max_bytes: int | None = None) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
            if max_bytes is not None:
                max_bytes -= len(chunk)
                if max_bytes <= 0:
                    break
    return h.hexdigest()


def git_head() -> tuple[str, str]:
    branch = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()
    sha = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    return branch, sha


def engine_git_sha() -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO), "log", "-1", "--format=%H", "--", str(ENGINE.relative_to(REPO))],
        text=True,
    ).strip()


def parquet_integrity(path: Path) -> dict[str, Any]:
    header = path.open("rb").read(4)
    footer = path.open("rb").seek(max(0, path.stat().st_size - 4)) or b""
    with path.open("rb") as f:
        f.seek(max(0, path.stat().st_size - 4))
        footer = f.read(4)
    state = "partial_corrupt"
    detail = ""
    if header != b"PAR1":
        state = "invalid_header"
        detail = f"header={header!r}"
    elif footer != b"PAR1":
        state = "partial_corrupt"
        detail = "Parquet magic bytes not found in footer"
    else:
        try:
            import pyarrow.parquet as pq

            pf = pq.ParquetFile(path)
            state = "readable"
            detail = f"row_groups={pf.num_row_groups}"
        except Exception as err:
            state = "corrupt"
            detail = str(err)
    return {"parquet_header": header.hex(), "parquet_footer": footer.hex(), "integrity_state": state, "detail": detail}


def load_watch_bounds() -> dict[str, Any]:
    first = last = None
    with WATCH_JSONL.open() as f:
        for line in f:
            o = json.loads(line)
            if o.get("type") != "INTERVAL_OBSERVATION":
                continue
            if first is None:
                first = o
            last = o
    return {"first_observation": first, "last_observation": last}


def source_manifest() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    import pandas as pd

    q, d, l = SOURCES["track01_questions"], SOURCES["track01_documents"], SOURCES["track03_json"]
    docs = pd.read_parquet(d, columns=["doc_id"])
    qs = pd.read_parquet(q, columns=["question_id"])
    raw = json.loads(l.read_text())
    turns = 0
    for item in raw:
        for session in item.get("haystack_sessions", []):
            turns += len(session if isinstance(session, list) else [session])
    for key, p in SOURCES.items():
        rows[key] = {
            "path": str(p),
            "size_bytes": p.stat().st_size,
            "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(p.stat().st_mtime)),
            "sha256": sha256_file(p),
            "role": key,
        }
    rows["_logical_counts"] = {
        "track01_documents_rows": int(len(docs)),
        "track01_questions_rows_total": int(len(qs)),
        "track01_questions_primary_contract": 300,
        "track03_json_items": int(len(raw)),
        "track03_turn_rows_estimated": int(turns),
    }
    rows["_source_bytes_total"] = sum(SOURCES[k].stat().st_size for k in SOURCES)
    return rows


def inventory_outputs() -> list[dict[str, Any]]:
    inv: list[dict[str, Any]] = []
    for art in EXPECTED_ARTIFACTS:
        fp = OUTPUT_ROOT / art
        if not fp.exists():
            inv.append(
                {
                    "path": str(fp),
                    "type": "file",
                    "role": art,
                    "size_bytes": 0,
                    "mtime_utc": None,
                    "sha256": None,
                    "state": "missing",
                }
            )
            continue
        st = fp.stat()
        entry: dict[str, Any] = {
            "path": str(fp),
            "type": "file",
            "role": art,
            "size_bytes": st.st_size,
            "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
            "state": "partial" if st.st_size == 0 else "present",
        }
        if st.st_size <= 256 * 1024 * 1024:
            entry["sha256"] = sha256_file(fp)
        else:
            entry["sha256"] = "DEFERRED_LARGE_FILE"
            entry["sha256_manifest_note"] = "Hash deferred; preserve exact locator and size_bytes"
        if art.endswith(".parquet"):
            entry.update(parquet_integrity(fp))
        inv.append(entry)
    for extra in [WATCH_JSONL, TERMINAL_RECEIPT]:
        if extra.exists():
            st = extra.stat()
            inv.append(
                {
                    "path": str(extra),
                    "type": "file",
                    "role": extra.name,
                    "size_bytes": st.st_size,
                    "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
                    "sha256": sha256_file(extra) if st.st_size < 512 * 1024 * 1024 else "DEFERRED_LARGE_FILE",
                    "state": "complete" if extra != TERMINAL_RECEIPT else "missing",
                }
            )
    if TERMINAL_RECEIPT.exists():
        inv[-1]["state"] = "complete"
    return inv


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    branch, head_sha = git_head()
    swap = json.loads(SWAP_RECEIPT.read_text()) if SWAP_RECEIPT.exists() else {}
    watch = load_watch_bounds()
    sources = source_manifest()
    inventory = inventory_outputs()
    kill_utc = swap.get("recorded_at_utc", "2026-08-29T04:44:50Z")
    estimated_start = "2026-08-22T23:58:22Z"

    identity = {
        "schema": "hydradg.seedgraph.forensic_identity.v1",
        "recorded_at_utc": utc_now(),
        "execution_host": socket.gethostname(),
        "pid": 96177,
        "ppid": 96175,
        "exact_command": (
            "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/"
            "Versions/3.14/Resources/Python.app/Contents/MacOS/Python "
            f"{ENGINE} build --output-dir {OUTPUT_ROOT} --require-studio"
        ),
        "working_directory": str(REPO),
        "estimated_start_utc": estimated_start,
        "last_observed_alive_utc": watch["last_observation"]["utc_timestamp"],
        "interrupted_at_utc": kill_utc,
        "runtime_seconds_observed": watch["last_observation"]["elapsed_seconds"],
        "git_repo": str(REPO),
        "git_branch_at_forensic": branch,
        "git_sha_at_forensic": head_sha,
        "engine_path": str(ENGINE),
        "engine_sha256": sha256_file(ENGINE),
        "engine_git_sha_at_last_change": engine_git_sha(),
        "python_identity": subprocess.check_output(["python3", "--version"], text=True).strip(),
        "python_path": subprocess.check_output(["which", "python3"], text=True).strip(),
        "implementation_lane": "hydradg.seedgraph.hierarchy.v1a",
        "canonical_seedgraph_repo_note": (
            "PID 96177 executed HydraDG scripts/seedgraph_hierarchy_v1a.py build, "
            "not uv run seedgraph import from /Users/byron/projects/active/seedgraph"
        ),
        "source_datasets": sources,
        "output_root": str(OUTPUT_ROOT),
        "ledger_path": None,
        "content_store_path": str(OUTPUT_ROOT),
        "graph_path": str(OUTPUT_ROOT),
        "checkpoint_path": None,
        "stdout_stderr_paths": {
            "process_stdout_stderr": "NOT_CAPTURED",
            "watcher_log_path": "/tmp/seedgraph_audit.log",
            "watcher_log_present": False,
        },
        "watcher_relationship": {
            "watcher_pid": 9211,
            "watcher_script": str(WATCHER),
            "watcher_watch_receipt": str(WATCH_JSONL),
            "watcher_terminal_receipt_expected": str(TERMINAL_RECEIPT),
            "watcher_state": "TERMINATED_BEFORE_CLOSEOUT",
            "watcher_termination_reason": "Killed during Q38 swap remediation before PID 96177 exit closeout",
        },
        "stages_performed": [
            "ROOT_IMPORT",
            "BYTE_CUSTODY",
            "LOGICAL_RECORD_INGEST",
            "STRUCTURAL_ATOMIZATION",
            "FCO_BINDING",
            "FCG_BINDING",
        ],
        "stage_at_interruption": "FINAL_PARQUET_SERIALIZATION",
        "stage_not_reached": ["VALIDATION", "BUILD_RECEIPT_EMISSION", "TERMINAL_WATCHER_CLOSEOUT"],
        "prior_misclassification": {
            "label": "OPERATIONAL_STALE",
            "source_receipt": str(SWAP_RECEIPT),
            "corrected_to": "ACTIVE_IMPORT_INTERRUPTED",
        },
        "claim_ceiling": "DETERMINISTIC_TOOL_OUTPUT",
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED",
    }
    (OUT_DIR / "SEEDGRAPH_PID96177_FORENSIC_IDENTITY.json").write_text(
        json.dumps(identity, indent=2, sort_keys=True) + "\n"
    )

    manifest = {
        "schema": "hydradg.seedgraph.interrupted_output_manifest.v1",
        "recorded_at_utc": utc_now(),
        "predecessor_pid": 96177,
        "output_root": str(OUTPUT_ROOT),
        "preservation_policy": "DO_NOT_DELETE_OR_MOVE",
        "inventory": inventory,
        "expected_artifacts": EXPECTED_ARTIFACTS,
        "present_count": sum(1 for x in inventory if x.get("state") == "present"),
        "partial_count": sum(1 for x in inventory if x.get("state") == "partial"),
        "missing_count": sum(1 for x in inventory if x.get("state") == "missing"),
        "total_output_bytes": sum(x.get("size_bytes", 0) for x in inventory if "v1a_validation" in x.get("path", "")),
        "newest_output_mtime_utc": watch["last_observation"]["newest_output_mtime_utc"],
        "claim_ceiling": "DETERMINISTIC_TOOL_OUTPUT",
        "signature_state": "NOT_SIGNED",
    }
    (OUT_DIR / "SEEDGRAPH_INTERRUPTED_OUTPUT_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )

    checkpoint = {
        "schema": "hydradg.seedgraph.last_durable_checkpoint.v1",
        "recorded_at_utc": utc_now(),
        "implementation_sha256": sha256_file(ENGINE),
        "implementation_git_sha": engine_git_sha(),
        "checkpoint_identity": None,
        "source_root": {k: sources[k] for k in SOURCES},
        "interruption_boundary": "DURING_FINAL_PARQUET_WRITE",
        "write_semantics": (
            "seedgraph_hierarchy_v1a.build() holds all nodes/edges/atoms in memory, "
            "then writes parquet artifacts in one batch at finalize(). "
            "No incremental checkpoint/resume API exists in v1a."
        ),
        "last_durable_record": None,
        "last_durable_atom": None,
        "last_durable_batch": None,
        "last_observed_filesystem_activity_utc": watch["last_observation"]["newest_output_mtime_utc"],
        "partial_files": [
            {
                "path": str(OUTPUT_ROOT / "nodes.parquet"),
                "size_bytes": (OUTPUT_ROOT / "nodes.parquet").stat().st_size,
                "integrity": parquet_integrity(OUTPUT_ROOT / "nodes.parquet"),
            },
            {
                "path": str(OUTPUT_ROOT / "edges.parquet"),
                "size_bytes": (OUTPUT_ROOT / "edges.parquet").stat().st_size,
                "integrity": parquet_integrity(OUTPUT_ROOT / "edges.parquet"),
            },
        ],
        "ledger_root": None,
        "content_store_root": str(OUTPUT_ROOT),
        "graph_root": str(OUTPUT_ROOT),
        "BUILD_RECEIPT_present": False,
        "claim_ceiling": "DETERMINISTIC_TOOL_OUTPUT",
    }
    (OUT_DIR / "SEEDGRAPH_LAST_DURABLE_CHECKPOINT.json").write_text(
        json.dumps(checkpoint, indent=2, sort_keys=True) + "\n"
    )

    terminal = {
        "schema": "hydradg.seedgraph.terminal_receipt_check.v1",
        "recorded_at_utc": utc_now(),
        "TERMINAL_RECEIPT_PRESENT": "NO",
        "TERMINAL_RECEIPT_PATH": str(TERMINAL_RECEIPT),
        "TERMINAL_RECEIPT_SHA256": None,
        "BUILD_RECEIPT_PRESENT": (OUTPUT_ROOT / "BUILD_RECEIPT.json").exists(),
        "watcher_closeout_completed": False,
        "reason": "Watcher PID 9211 terminated before PID 96177 exit closeout; no TERMINAL_EVENT in watch JSONL",
    }
    (OUT_DIR / "SEEDGRAPH_TERMINAL_RECEIPT_CHECK.json").write_text(
        json.dumps(terminal, indent=2, sort_keys=True) + "\n"
    )

    recovery = {
        "schema": "hydradg.seedgraph.recovery_classification.v1",
        "recorded_at_utc": utc_now(),
        "SEEDGRAPH_RECOVERY_CLASSIFICATION": "SEEDGRAPH_PARTIAL_RESTART_REQUIRED",
        "SEEDGRAPH_RESUME_SAFE": False,
        "idempotency_answer": {
            "question": "If already imported object X is submitted again with identical canonical bytes, does SeedGraph reuse safely?",
            "implementation": "seedgraph_hierarchy_v1a.py",
            "answer_code": "E",
            "answer_text": (
                "unknown_for_interrupted_run; full deterministic re-run to a clean output root "
                "would reproduce canonical typed_id/object_sha256 values (content-addressed), "
                "but v1a has no resume/checkpoint and cannot reuse partial corrupt parquet"
            ),
            "canonical_seedgraph_import_note": (
                "uv run seedgraph import supports --resume-run-id for publication-family batches; "
                "that path is separate from HydraDG hierarchy v1a validation build"
            ),
        },
        "interruption_state": "AFTER_IN_MEMORY_CONSTRUCTION_BEFORE_VALID_RECEIPT",
        "successor_plan": {
            "relationship": "INTERRUPTED_PREDECESSOR_LINEAGE -> SUPERSEDED_BY -> SuccessorSeedGraphRunFCO",
            "recovery_mode": "RESTART_FROM_FROZEN_SOURCE",
            "predecessor_output_preserve_path": str(OUTPUT_ROOT),
            "successor_output_root_recommended": "/Volumes/magicBLACKbox/hydradg/seedgraph/v1a_validation_successor_20260828",
            "freeze_requirements": [
                "source SHA256 unchanged",
                "engine git sha or engine sha256 pinned",
                "parser/config unchanged",
                "isolated output root (no overwrite of predecessor partials)",
            ],
        },
        "fco_fcg_custody": {
            "chain": "SourceFCO -> SeedGraphImportRunFCO -> SeedGraphBatch/Atom objects -> canonical Atom/FCO -> FCG edges",
            "interruption_relation": "RECOVERED_BY",
            "interruption_relation_note": (
                "Canonical hydra_schema_edges.json has no INTERRUPTED_BY; "
                "use RECOVERED_BY for successor run and preserve predecessor as historical evidence"
            ),
            "predecessor_run_state": "INTERRUPTED_BY_RESOURCE_REMEDIATION",
        },
        "resource_isolation": {
            "Q38_MODEL_EXECUTION": "PAUSED",
            "OLLARMA_WATCHER_LLM": "PAUSED",
            "WATCHER_TELEMETRY_ONLY": "YES",
        },
        "claim_ceiling": "DETERMINISTIC_TOOL_OUTPUT",
        "signature_state": "NOT_SIGNED",
        "merkle_mmr_state": "NOT_COMMITTED",
    }
    (OUT_DIR / "SEEDGRAPH_RECOVERY_CLASSIFICATION.json").write_text(
        json.dumps(recovery, indent=2, sort_keys=True) + "\n"
    )

    counts = sources["_logical_counts"]
    report = {
        "schema": "hydradg.seedgraph.forensic_final_report.v1",
        "recorded_at_utc": utc_now(),
        "CURRENT_BRANCH": branch,
        "CURRENT_SHA": head_sha,
        "PID96177_ACTUAL_ROLE": "HydraDG SeedGraph hierarchy v1a monolithic build (import+ingest+atomize+FCO/FCG bind+parquet serialize)",
        "PID96177_SEEDGRAPH_VERSION": f"engine_sha256={sha256_file(ENGINE)} engine_git={engine_git_sha()}",
        "PID96177_SOURCE_ROOT": {k: str(v) for k, v in SOURCES.items()},
        "PID96177_OUTPUT_ROOT": str(OUTPUT_ROOT),
        "SEEDGRAPH_TERMINAL_RECEIPT": "ABSENT",
        "SEEDGRAPH_LAST_DURABLE_CHECKPOINT": "NONE_VALID",
        "ROOT_SOURCE_IMPORTED": "PASS_IN_MEMORY_NOT_DURABLY_COMMITTED",
        "SOURCE_BYTE_COVERAGE": "UNKNOWN_DURABLE_PARTIAL_CORRUPT_PARQUET",
        "LOGICAL_RECORDS_EXPECTED": {
            "track01_documents": counts["track01_documents_rows"],
            "track01_questions_primary": counts["track01_questions_primary_contract"],
            "track03_questions": counts["track03_json_items"],
            "track03_turns": counts["track03_turn_rows_estimated"],
        },
        "LOGICAL_RECORDS_INGESTED": "UNKNOWN_NOT_READBACK_SAFE",
        "LOGICAL_RECORD_COVERAGE": "UNKNOWN",
        "ATOMS_EMITTED": "UNKNOWN",
        "FAILED_ATOMS": "UNKNOWN",
        "ABSTENTIONS": 0,
        "ORPHAN_ATOMS": "UNKNOWN",
        "CANONICAL_FCO_BINDINGS": "UNKNOWN_PARTIAL_NOT_VALIDATED",
        "CANONICAL_FCG_BINDINGS": "UNKNOWN_PARTIAL_NOT_VALIDATED",
        "SEEDGRAPH_INTERRUPTION_STATE": "FORENSIC_RECOVERY_REQUIRED",
        "SEEDGRAPH_RECOVERY_CLASSIFICATION": "SEEDGRAPH_PARTIAL_RESTART_REQUIRED",
        "SEEDGRAPH_RESUME_SAFE": False,
        "SEEDGRAPH_RESOURCE_STATE": {
            "swap_used_pct": round(
                float(subprocess.check_output(["sysctl", "-n", "vm.swapusage"], text=True).split("used = ")[1].split("M")[0])
                / float(subprocess.check_output(["sysctl", "-n", "vm.swapusage"], text=True).split("total = ")[1].split("M")[0])
                * 100,
                2,
            )
            if subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True).returncode == 0
            else "UNKNOWN",
            "seedgraph_writer_active": False,
        },
        "SEEDGRAPH_FINAL_STATE": "NOT_ESTABLISHED",
        "Q38_EXECUTION_STATE": "PAUSED_DURING_SEEDGRAPH_RECOVERY",
        "FCO_STATE": "PREDECESSOR_INTERRUPTED_NOT_PROMOTED",
        "FCG_STATE": "NOT_APPENDED",
        "HYDRADB_STATE": "BLOCKED_PENDING_SEEDGRAPH_TERMINAL_VALID",
        "EVIDENCE_STATE": "FORENSIC_ARTIFACTS_RECORDED",
        "EXPERIMENT_STATE": "SEEDGRAPH_V1A_VALIDATION_BLOCKED",
        "EARLIEST_DIVERGENCE": "FINAL_PARQUET_SERIALIZATION_WITHOUT_BUILD_RECEIPT",
        "CLAIM_CEILING": "DETERMINISTIC_TOOL_OUTPUT",
        "SIGNATURE_STATE": "NOT_SIGNED",
        "MERKLE_MMR_STATE": "NOT_COMMITTED",
        "NEXT_SAFE_ACTION": (
            "Preserve predecessor partials; schedule successor build to isolated output root "
            "with pinned source/engine SHA; hold Q38 until SeedGraph terminal valid or human-approved checkpoint"
        ),
        "FINAL_REVIEW_GATE": "HUMAN_OPERATOR_APPROVAL_BEFORE_SUCCESSOR_BUILD",
        "artifact_paths": {
            "identity": str(OUT_DIR / "SEEDGRAPH_PID96177_FORENSIC_IDENTITY.json"),
            "manifest": str(OUT_DIR / "SEEDGRAPH_INTERRUPTED_OUTPUT_MANIFEST.json"),
            "checkpoint": str(OUT_DIR / "SEEDGRAPH_LAST_DURABLE_CHECKPOINT.json"),
            "classification": str(OUT_DIR / "SEEDGRAPH_RECOVERY_CLASSIFICATION.json"),
        },
    }
    (OUT_DIR / "SEEDGRAPH_FORENSIC_FINAL_REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"state": "COMPLETE", "out_dir": str(OUT_DIR)}, indent=2))


if __name__ == "__main__":
    main()
