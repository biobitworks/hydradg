#!/usr/bin/env python3
"""Executes and verifies local HydraDB graph write-back estimation for HydraDG.

- Reads local FCO nodes (turn FCOs, spatiotemporal pointers, container FCOs)
- Sets explicit fail-closed claim ceiling: FULL_LOCAL_HYDRADB_WRITEBACK_NOT_ESTABLISHED
- Outputs receipt to eval/hosted_migration_20260820/LOCAL_HYDRADB_WRITEBACK_RECEIPT.json
"""
from __future__ import annotations
import hashlib, json, os, socket, sys, time
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
HYDRADB_ENDPOINT = os.environ.get("HYDRADB_LOCAL_ENDPOINT", "http://127.0.0.1:8443")

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def probe_socket(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False

def execute_local_hydradb_writeback():
    print("=== Local HydraDB Graph Write-Back Accounting Estimator ===")
    
    turns_file = PROJECT_ROOT / "eval" / "hosted_migration_20260820" / "CONVERSATION_TURNS_FCO.jsonl"
    turn_nodes = 0
    if turns_file.exists():
        with turns_file.open("r", encoding="utf-8") as f:
            turn_nodes = sum(1 for line in f if line.strip())

    dedup_file = PROJECT_ROOT / "eval" / "hosted_migration_20260820" / "DEDUPLICATION_PARQUET_RECEIPT.json"
    spatiotemporal_pointers = 0
    if dedup_file.exists():
        dedup_data = json.loads(dedup_file.read_text(encoding="utf-8"))
        spatiotemporal_pointers = dedup_data.get("spatiotemporal_pointers", {}).get("level_0_word_pointer_nodes", 0) + \
                                 dedup_data.get("spatiotemporal_pointers", {}).get("level_1_sentence_pointer_nodes", 0)

    projected_nodes = turn_nodes + 503 + spatiotemporal_pointers
    projected_relations = turn_nodes * 2 + spatiotemporal_pointers

    is_online = probe_socket("127.0.0.1", 7474) or probe_socket("127.0.0.1", 8443)

    claim_ceiling = "FULL_LOCAL_HYDRADB_WRITEBACK_NOT_ESTABLISHED"
    writeback_state = "PROJECTION_ACCOUNTING_ESTIMATOR_ONLY"
    readback_state = "NOT_ESTABLISHED"
    status = "NOT_ESTABLISHED"

    writeback_receipt = {
        "schema": "hydradg.local_hydradb_writeback_receipt.v3",
        "hydradb_endpoint": HYDRADB_ENDPOINT if not is_online else "http://127.0.0.1:7474",
        "namespace": "hydradg-local-custody",
        "writeback_timestamp_unix": int(time.time()),
        "writeback_timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "writeback_state": writeback_state,
        "readback_verification_state": readback_state,
        "node_counts": {
            "projected_fco_nodes": projected_nodes,
            "mutated_fco_nodes": None,
            "projected_fcg_relations": projected_relations,
            "conversation_turn_fcos": turn_nodes,
            "spatiotemporal_pointer_fcos": spatiotemporal_pointers,
            "container_fcos": 503,
        },
        "writeback_digest_sha256": compute_sha256(f"writeback:{projected_nodes}:{writeback_state}".encode("utf-8")),
        "license": "CC-BY-NC-ND-4.0",
        "claim_ceiling": claim_ceiling,
        "status": status,
    }

    out_receipt = PROJECT_ROOT / "eval" / "hosted_migration_20260820" / "LOCAL_HYDRADB_WRITEBACK_RECEIPT.json"
    out_receipt.write_text(json.dumps(writeback_receipt, indent=2, sort_keys=True) + "\n")
    print(f"✅ Local HydraDB Write-Back Receipt reclassified: {out_receipt}")
    print(f"Claim Ceiling: {claim_ceiling}")

if __name__ == "__main__":
    execute_local_hydradb_writeback()
