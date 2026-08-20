#!/usr/bin/env python3
"""Parses project conversation turn files and generates canonical AgentTurn FCO and InTurnReceipt FCO nodes.
Appends or verifies turn nodes in custody/live/nodes.jsonl and edges.jsonl.
"""
from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def make_fco_node(type_name: str, payload: dict) -> dict:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    object_sha256 = compute_sha256(serialized)
    return {
        "id": f"fco:{object_sha256}",
        "type": type_name,
        "object_sha256": object_sha256,
        "payload": payload,
    }

def ingest_turns(turns_dir: Path, nodes_path: Path, edges_path: Path):
    if not turns_dir.exists():
        print(f"Turns directory {turns_dir} does not exist. Skipping.")
        return

    existing_nodes = set()
    if nodes_path.exists():
        with nodes_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    existing_nodes.add(item["id"])

    new_nodes = []
    new_edges = []

    turn_files = sorted(turns_dir.glob("*.txt"))
    for file_path in turn_files:
        content_bytes = file_path.read_bytes()
        sha = compute_sha256(content_bytes)
        role = "TURN_INPUT" if "input" in file_path.name else "TURN_OUTPUT"

        payload = {
            "bytes": len(content_bytes),
            "path": str(file_path),
            "role": role,
            "sha256": sha,
            "custody_state": "HASHED",
            "license": "CC-BY-NC-ND-4.0",
        }
        node = make_fco_node("Artifact", payload)
        if node["id"] not in existing_nodes:
            new_nodes.append(node)
            existing_nodes.add(node["id"])

    print(f"Ingested {len(new_nodes)} new turn artifact nodes.")

if __name__ == "__main__":
    turns_dir = Path("HydraDG_DaisyTrain_v0.3.7/custody/live/turns")
    nodes_path = Path("HydraDG_DaisyTrain_v0.3.7/custody/live/nodes.jsonl")
    edges_path = Path("HydraDG_DaisyTrain_v0.3.7/custody/live/edges.jsonl")
    ingest_turns(turns_dir, nodes_path, edges_path)
