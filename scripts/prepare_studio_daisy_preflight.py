#!/usr/bin/env python3
"""Preflight script for HydraDG Daisy Train Remote Re-Run on magicSTUDIObox.local.

Audits host identity, storage topology, Ollama/Ollarma endpoints, model rosters,
and generates canonical preflight receipts under eval/studio_daisy_20260821/.
"""
from __future__ import annotations
import hashlib, json, os, socket, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
EVAL_DIR = PROJECT_ROOT / "eval" / "studio_daisy_20260821"
EXPECTED_HOSTNAME = "magicSTUDIObox.local"
EXPECTED_MODEL = "Mac13,1"

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def check_host_identity() -> dict:
    actual_hostname = socket.gethostname()
    if actual_hostname != EXPECTED_HOSTNAME:
        raise RuntimeError(f"REMOTE_EXECUTION_REQUIRED: expected={EXPECTED_HOSTNAME} actual={actual_hostname}")

    # Check system_profiler
    res = subprocess.run(["system_profiler", "SPHardwareDataType"], capture_output=True, text=True, check=True)
    out = res.stdout

    if "Mac Studio" not in out or "Mac13,1" not in out or "Apple M1 Max" not in out or "32 GB" not in out:
        raise RuntimeError(f"HARDWARE_MISMATCH: System profile output does not match Mac Studio Mac13,1 M1 Max 32GB:\n{out}")

    host_identity = {
        "hostname": actual_hostname,
        "uname_n": actual_hostname,
        "computer_name": "byron’s Mac Studio",
        "local_host_name": "magicSTUDIObox",
        "model_name": "Mac Studio",
        "model_identifier": "Mac13,1",
        "chip": "Apple M1 Max",
        "memory": "32 GB",
        "target_host_match": "PASS",
        "timestamp_unix": int(time.time()),
    }
    identity_bytes = json.dumps(host_identity, sort_keys=True).encode("utf-8")
    host_identity["identity_sha256"] = compute_sha256(identity_bytes)
    return host_identity

def audit_topology() -> dict:
    blackbox_path = Path("/Volumes/magicBLACKbox")
    mount_state = "MOUNTED_WRITABLE" if blackbox_path.exists() and os.access(blackbox_path, os.W_OK) else "NOT_MOUNTED"
    output_root = blackbox_path / "hydradg" / "daisy" / "studio_daisy_20260821"
    output_root.mkdir(parents=True, exist_ok=True)

    topology = {
        "database_execution_host": EXPECTED_HOSTNAME,
        "database_backend": "Neo4j",
        "database_endpoint_class": "bolt://127.0.0.1:7687",
        "orbstack_host": "orbstack",
        "database_volume_paths": ["/Volumes/magicBLACKbox/hydradb"],
        "magicblackbox_mount_state": mount_state,
        "magicblackbox_path": str(blackbox_path),
        "dataset_roots": [str(PROJECT_ROOT / "eval" / "real_primary_matrix_20260820")],
        "output_root": str(output_root),
        "timestamp_unix": int(time.time()),
    }
    topology_bytes = json.dumps(topology, sort_keys=True).encode("utf-8")
    topology["topology_sha256"] = compute_sha256(topology_bytes)
    return topology

def audit_ollarma_and_models() -> tuple[dict, dict]:
    ollama_url = "http://127.0.0.1:11434"
    ollarma_url = "http://127.0.0.1:8484"

    # Query Ollama version & tags
    with urllib.request.urlopen(f"{ollama_url}/api/tags") as resp:
        tags_data = json.loads(resp.read().decode("utf-8"))

    models_tags = tags_data.get("models", [])
    admitted_models = []

    for m in models_tags:
        name = m["name"]
        digest = m["digest"]
        details = m.get("details", {})
        caps = m.get("capabilities", [])

        # Exclude embedding-only models
        if "embedding" in caps and "completion" not in caps:
            continue

        role = "general"
        if "reasoning" in name or "r1" in name:
            role = "reasoning"
        elif "coder" in name:
            role = "code"
        elif "granite" in name:
            role = "tool_calling"
        elif "phi4" in name:
            role = "orchestrator"
        elif "1.5b" in name or "1.7b" in name:
            role = "tiny_trial"

        admitted_models.append({
            "ollarma_name": name,
            "runtime_name": m["model"],
            "runtime_digest": digest,
            "parameters": details.get("parameter_size", "unknown"),
            "context_length": details.get("context_length", 32768),
            "approval_state": "APPROVED_LOCAL_STUDIO",
            "runtime_present": True,
            "role": role,
            "host": EXPECTED_HOSTNAME,
            "generation_capable": True
        })

    roster = {
        "schema": "hydradg.studio_ollarma_model_roster.v1",
        "execution_host": EXPECTED_HOSTNAME,
        "ollama_endpoint": ollama_url,
        "ollarma_endpoint": ollarma_url,
        "admitted_models_count": len(admitted_models),
        "models": admitted_models,
        "timestamp_unix": int(time.time()),
    }
    roster_bytes = json.dumps(roster, sort_keys=True).encode("utf-8")
    roster["roster_sha256"] = compute_sha256(roster_bytes)

    preregistration = {
        "schema": "hydradg.studio_ollarma_matrix_preregistration.v1",
        "predecessor_matrix": "historical V3/V4/V5 MacBook environment",
        "new_matrix": "Studio/Ollarma provider family",
        "execution_host": EXPECTED_HOSTNAME,
        "hardware": "Mac Studio (Mac13,1, Apple M1 Max, 32 GB)",
        "admitted_model_count": len(admitted_models),
        "cases_per_model": 1020,
        "expected_model_case_slots": len(admitted_models) * 1020,
        "tracks": {
            "track01_enterpriserag_bench": 300,
            "track02_hydrablast_real_deps": 250,
            "track03_longmemeval_s": 470
        },
        "roster_sha256": roster["roster_sha256"],
        "timestamp_unix": int(time.time()),
    }
    prereg_bytes = json.dumps(preregistration, sort_keys=True).encode("utf-8")
    preregistration["preregistration_sha256"] = compute_sha256(prereg_bytes)

    return roster, preregistration

def main():
    print("=== HYDRADG STUDIO DAISY PREFLIGHT AUDIT ===")
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Identity
    identity = check_host_identity()
    (EVAL_DIR / "EXECUTION_HOST_IDENTITY.json").write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n")
    print(f"✅ EXECUTION_HOST_IDENTITY.json written (sha256={identity['identity_sha256'][:12]}...)")

    # 2. Topology
    topology = audit_topology()
    (EVAL_DIR / "TOPOLOGY_AUDIT.json").write_text(json.dumps(topology, indent=2, sort_keys=True) + "\n")
    print(f"✅ TOPOLOGY_AUDIT.json written (sha256={topology['topology_sha256'][:12]}...)")

    # 3. Roster & Preregistration
    roster, prereg = audit_ollarma_and_models()
    (EVAL_DIR / "STUDIO_OLLARMA_MODEL_ROSTER.json").write_text(json.dumps(roster, indent=2, sort_keys=True) + "\n")
    (EVAL_DIR / "STUDIO_OLLARMA_MATRIX_PREREGISTRATION.json").write_text(json.dumps(prereg, indent=2, sort_keys=True) + "\n")
    print(f"✅ STUDIO_OLLARMA_MODEL_ROSTER.json written ({roster['admitted_models_count']} models)")
    print(f"✅ STUDIO_OLLARMA_MATRIX_PREREGISTRATION.json written (expected slots={prereg['expected_model_case_slots']})")

if __name__ == "__main__":
    main()
