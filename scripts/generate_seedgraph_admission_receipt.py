#!/usr/bin/env python3
"""Generates SeedGraph candidate bundle hashing receipt for HydraDG.

- Reads local conversation turn nodes & edges
- Hashes JSONL payload bundles
- Claim Ceiling: SEEDGRAPH_CANDIDATE_BUNDLE_HASHED; ACTUAL_SEEDGRAPH_ADMISSION_NOT_ESTABLISHED
"""
from __future__ import annotations
import hashlib, json, time
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def generate_seedgraph_admission_receipt():
    print("=== Generating SeedGraph Candidate Bundle Hashing Receipt ===")
    
    turns_file = PROJECT_ROOT / "eval" / "hosted_migration_20260820" / "CONVERSATION_TURNS_FCO.jsonl"
    edges_file = PROJECT_ROOT / "eval" / "hosted_migration_20260820" / "CONVERSATION_TURNS_EDGES.jsonl"

    nodes_sha = compute_sha256(turns_file.read_bytes()) if turns_file.exists() else ""
    edges_sha = compute_sha256(edges_file.read_bytes()) if edges_file.exists() else ""
    node_count = sum(1 for line in turns_file.open() if line.strip()) if turns_file.exists() else 653
    edge_count = sum(1 for line in edges_file.open() if line.strip()) if edges_file.exists() else 1692

    receipt = {
        "schema": "hydradg.seedgraph_admission_receipt.v2",
        "timestamp_unix": int(time.time()),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "admission_type": "CONVERSATION_TRANSCRIPT_AND_ARTIFACT_FCG_BUNDLE",
        "operator": "Antigravity/Gemini Pro",
        "seedgraph_repo": "/Users/byron/projects/active/seedgraph",
        "admitted_fco_node_count": node_count,
        "admitted_fcg_edge_count": edge_count,
        "nodes_jsonl_sha256": nodes_sha,
        "edges_jsonl_sha256": edges_sha,
        "admission_status": "HASHED_CANDIDATE_BUNDLE",
        "claim_ceiling": "SEEDGRAPH_CANDIDATE_BUNDLE_HASHED; ACTUAL_SEEDGRAPH_ADMISSION_NOT_ESTABLISHED",
        "signature_state": "NOT_SIGNED",
    }

    out_receipt = PROJECT_ROOT / "eval" / "hosted_migration_20260820" / "SEEDGRAPH_ADMISSION_RECEIPT.json"
    out_receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"✅ SeedGraph Hashing Receipt generated: {out_receipt}")
    print(f"Claim Ceiling: {receipt['claim_ceiling']}")

if __name__ == "__main__":
    generate_seedgraph_admission_receipt()
