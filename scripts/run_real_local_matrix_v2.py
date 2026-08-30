#!/usr/bin/env python3
"""HydraDG local-model matrix v2 guardrail.

This legacy v2 entry point is intentionally audit-only. Earlier revisions generated
synthetic model receipts and literal retrieval metrics and are preserved in Git history
as development lineage, not empirical evidence.

Current behavior:
- discovers the local Ollama inventory;
- audits optional evaluator package availability;
- writes a fail-closed audit receipt;
- performs NO dataset-row model inference;
- performs NO benchmark scoring;
- emits NO model-benefit conclusion.

Use a separately preregistered real-execution runner for future empirical work.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = PROJECT_ROOT / "eval" / "execution_audit_20260820"
INVENTORY_DIR = PROJECT_ROOT / "eval" / "real_local_matrix_v2_20260820"
PUBLIC_EXECUTION_HOST = "REDACTED_LOCAL_HOST"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def discover_ollama_runtime() -> dict:
    version = "UNKNOWN"
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip() or result.stderr.strip() or "UNKNOWN"
    except Exception as exc:
        return {
            "status": "BLOCKED_OLLAMA_UNAVAILABLE",
            "ollama_version": version,
            "primary_ollama_text_models": [],
            "error_class": type(exc).__name__,
        }

    models = []
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        rows = [line.split() for line in result.stdout.splitlines()[1:] if line.strip()]
        for parts in rows:
            if not parts:
                continue
            name = parts[0]
            if name.startswith("nomic-embed"):
                continue
            models.append({
                "model_name": name,
                "digest": parts[1] if len(parts) > 1 else None,
                "runtime_availability": "AVAILABLE_LOCAL",
            })
    except Exception as exc:
        return {
            "status": "BLOCKED_MODEL_LIST_UNAVAILABLE",
            "ollama_version": version,
            "primary_ollama_text_models": [],
            "error_class": type(exc).__name__,
        }

    return {
        "status": "INVENTORY_DISCOVERED",
        "ollama_version": version,
        "primary_ollama_text_models": models,
    }


def audit_package(name: str) -> dict:
    result = subprocess.run([sys.executable, "-m", "pip", "show", name], capture_output=True, text=True)
    if result.returncode != 0:
        return {"installed": False, "status": "BLOCKED_PACKAGE_NOT_INSTALLED"}
    version = None
    for line in result.stdout.splitlines():
        if line.startswith("Version:"):
            version = line.split(":", 1)[1].strip()
            break
    return {"installed": True, "version": version, "status": "INSTALLED_RUNTIME"}


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    INVENTORY_DIR.mkdir(parents=True, exist_ok=True)

    inventory = discover_ollama_runtime()
    inventory_bytes = json.dumps(inventory, indent=2, sort_keys=True).encode("utf-8")
    inventory["inventory_sha256"] = sha256_bytes(inventory_bytes)
    (INVENTORY_DIR / "MODEL_INVENTORY.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")

    package_names = ["deepeval", "ragas", "inspect_ai", "beir", "mteb", "lm_eval"]
    package_audit = {name: audit_package(name) for name in package_names}
    (INVENTORY_DIR / "PACKAGE_RUNTIME_AUDIT.json").write_text(json.dumps(package_audit, indent=2, sort_keys=True) + "\n")

    gate = {
        "schema": "hydradg.final_audit_gate.correction.v2",
        "execution_host": PUBLIC_EXECUTION_HOST,
        "host_disclosure_state": "PUBLIC_RELEASE_MINIMIZATION",
        "models_discovered": len(inventory.get("primary_ollama_text_models", [])),
        "models_actually_called": 0,
        "model_responses_receipted": 0,
        "dataset_cases_actually_executed": 0,
        "real_retrieval_score_rows": 0,
        "real_dataset_row_execution_started": False,
        "synthetic_development_scores_promoted": False,
        "evidence_audit_gate": "FAIL_DEVELOPMENT_RECEIPTS_NOT_REAL_EXECUTION",
        "primary_claim_ceiling": "EXPANDED_MODEL_MATRIX_NOT_ESTABLISHED_FROM_REAL_CASE_EXECUTION",
        "historical_track03_evidence_state": "EXECUTED_PRESERVED",
        "vithia_execution_evidence": "NOT_ESTABLISHED_FROM_EXECUTION_RECEIPT",
        "production_deployed": "NO",
        "main_merged": "NO",
    }
    (AUDIT_DIR / "FINAL_AUDIT_GATE.json").write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n")

    print(json.dumps(gate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
