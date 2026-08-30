#!/usr/bin/env python3
"""Atomize dataset cases into FCO/FCG structures and compute Merkle lineage deltas.

Executes structural atomization on EnterpriseRAG-Bench (300 cases),
HydraBlast-Real-Deps (250 cases), and LongMemEval-S (470 cases).
Outputs FCO nodes, FCG edges, and lineage receipts into eval/studio_daisy_20260821/atomized/.
"""
from __future__ import annotations

import hashlib
import json
import os
import socket
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")
EVAL_DIR = PROJECT_ROOT / "eval" / "studio_daisy_20260821"
ATOMIZED_DIR = EVAL_DIR / "atomized"

EXPECTED_HOSTNAME = "magicSTUDIObox.local"


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(val: object) -> str:
    return json.dumps(
        val, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def merkle_root_hex(leaves: list[str]) -> str:
    level = [bytes.fromhex(x) for x in leaves]
    if not level:
        return compute_sha256(b"hydradg.empty_merkle.v1")
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(
                hashlib.sha256(
                    b"hydradg.merkle.node.v1\0" + level[i] + level[i + 1]
                ).digest()
            )
        level = nxt
    return level[0].hex()


def atomize_source_datasets():
    actual_hostname = socket.gethostname()
    if actual_hostname != EXPECTED_HOSTNAME:
        raise RuntimeError(
            f"REMOTE_EXECUTION_REQUIRED: expected={EXPECTED_HOSTNAME} actual={actual_hostname}"
        )

    ATOMIZED_DIR.mkdir(parents=True, exist_ok=True)

    manifest_file = (
        PROJECT_ROOT
        / "eval"
        / "real_primary_matrix_20260820"
        / "DATASET_CASE_MANIFEST.jsonl"
    )
    if not manifest_file.exists():
        raise RuntimeError(f"DATASET_CASE_MANIFEST missing at {manifest_file}")

    cases = []
    with manifest_file.open() as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    fco_nodes = []
    fcg_edges = []
    fco_hashes = []

    # 1. Root FCO for dataset manifest
    manifest_bytes = manifest_file.read_bytes()
    manifest_sha = compute_sha256(manifest_bytes)
    root_fco_id = f"fco:{manifest_sha}"

    fco_nodes.append(
        {
            "id": root_fco_id,
            "object_sha256": manifest_sha,
            "type": "DatasetManifestFCO",
            "payload": {
                "dataset_id": "studio_daisy_primary_datasets",
                "cases_count": len(cases),
                "manifest_sha256": manifest_sha,
                "claim_ceiling": "PRIMARY_DATASET_ATOMIZATION_CUSTODY_ONLY",
            },
        }
    )
    fco_hashes.append(manifest_sha)

    # 2. Atomize cases into case FCOs
    prev_fco_id = root_fco_id
    for idx, c in enumerate(cases):
        c_bytes = canonical_json(c).encode("utf-8")
        c_sha = compute_sha256(c_bytes)
        c_fco_id = f"fco:{c_sha}"

        fco_nodes.append(
            {
                "id": c_fco_id,
                "object_sha256": c_sha,
                "type": "DatasetCaseFCO",
                "payload": {
                    "case_id": c["case_id"],
                    "dataset": c["dataset"],
                    "track": c["track"],
                    "case_payload_sha256": c["case_payload_sha256"],
                    "evaluation_role": c["evaluation_role"],
                },
            }
        )
        fco_hashes.append(c_sha)

        # FCG Lineage Edge
        fcg_edges.append(
            {
                "source": c_fco_id,
                "target": root_fco_id,
                "relation": "MEMBER_OF",
                "edge_sha256": compute_sha256(
                    f"{c_fco_id}:MEMBER_OF:{root_fco_id}".encode("utf-8")
                ),
            }
        )

        if prev_fco_id != root_fco_id:
            fcg_edges.append(
                {
                    "source": c_fco_id,
                    "target": prev_fco_id,
                    "relation": "NEXT",
                    "edge_sha256": compute_sha256(
                        f"{c_fco_id}:NEXT:{prev_fco_id}".encode("utf-8")
                    ),
                }
            )
        prev_fco_id = c_fco_id

    # Write FCO / FCG Lineage Files
    (ATOMIZED_DIR / "fco_nodes.jsonl").write_text(
        "\n".join(canonical_json(n) for n in fco_nodes) + "\n"
    )
    (ATOMIZED_DIR / "fcg_edges.jsonl").write_text(
        "\n".join(canonical_json(e) for e in fcg_edges) + "\n"
    )

    merkle_root = merkle_root_hex(sorted(fco_hashes))

    receipt = {
        "schema": "hydradg.studio_dataset_atomization_receipt.v1",
        "execution_host": EXPECTED_HOSTNAME,
        "dataset_manifest_sha256": manifest_sha,
        "total_cases_atomized": len(cases),
        "fco_nodes_count": len(fco_nodes),
        "fcg_edges_count": len(fcg_edges),
        "merkle_root_sha256": merkle_root,
        "tracks": {
            "track01_enterpriserag_bench": sum(
                1 for c in cases if c["track"] == "track01"
            ),
            "track02_hydrablast_real_deps": sum(
                1 for c in cases if c["track"] == "track02"
            ),
            "track03_longmemeval_s": sum(
                1 for c in cases if c["track"] == "track03"
            ),
        },
        "timestamp_unix": int(time.time()),
    }

    rec_bytes = canonical_json(receipt).encode("utf-8")
    rec_sha = compute_sha256(rec_bytes)
    receipt["receipt_sha256"] = rec_sha

    (ATOMIZED_DIR / "ATOMIZATION_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )

    print("=== HYDRADG STUDIO ATOMIZATION COMPLETED ===")
    print(f"Total Cases Atomized : {len(cases)}")
    print(f"FCO Nodes Created    : {len(fco_nodes)}")
    print(f"FCG Edges Created    : {len(fcg_edges)}")
    print(f"Merkle Root SHA256   : {merkle_root}")
    print(f"Receipt SHA256       : {rec_sha}")


if __name__ == "__main__":
    atomize_source_datasets()
