#!/usr/bin/env python3
"""Complete Repository & Conversation Ingestion Script into SeedGraph FCO nodes.

- Ingests Antigravity transcript logs & brain artifacts (implementation_plan.md, walkthrough.md)
- Ingests all evaluation receipts in eval/hosted_migration_20260820/ & HydraDG_DaisyTrain_v0.3.7/eval/
- Ingests all project turn files in HydraDG_DaisyTrain_v0.3.7/custody/live/turns/
- Computes content SHA-256 digests and Gemini signature hashes
- Outputs complete unified FCO index to eval/hosted_migration_20260820/CONVERSATION_TURNS_FCO.jsonl
"""
from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path

CONVERSATION_ID = "eee59322-9ae9-4eb7-a286-acc43ba20a29"
ANTIGRAVITY_BRAIN_DIR = Path(f"/Users/byron/.gemini/antigravity/brain/{CONVERSATION_ID}")
TRANSCRIPT_LOG = ANTIGRAVITY_BRAIN_DIR / ".system_generated" / "logs" / "transcript.jsonl"
PROJECT_ROOT = Path("/Users/byron/projects/active/hydradg")

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

def ingest_complete_repository():
    print(f"=== Complete SeedGraph FCO Repository Ingestion (Conv ID: {CONVERSATION_ID}) ===")
    fco_nodes = []
    seen_ids = set()

    def add_node(node: dict):
        if node["id"] not in seen_ids:
            seen_ids.add(node["id"])
            fco_nodes.append(node)

    # 1. Parse Brain Artifacts
    if ANTIGRAVITY_BRAIN_DIR.exists():
        for md_file in sorted(ANTIGRAVITY_BRAIN_DIR.glob("*.md")):
            content_bytes = md_file.read_bytes()
            sha256_hash = compute_sha256(content_bytes)
            gemini_sig = compute_sha256(f"Gemini-Pro:{CONVERSATION_ID}:{md_file.name}:{sha256_hash}".encode("utf-8"))

            payload = {
                "artifact_name": md_file.name,
                "conversation_id": CONVERSATION_ID,
                "agent_identity": "Antigravity/Gemini Pro",
                "content_sha256": sha256_hash,
                "gemini_signature_hash": gemini_sig,
                "seedgraph_admitted": True,
                "custody_state": "HASHED_SEEDGRAPH_ADMITTED",
                "license": "CC-BY-NC-ND-4.0",
                "bytes": len(content_bytes),
            }
            add_node(make_fco_node("BrainArtifactFCO", payload))
            print(f"Ingested Brain Artifact: {md_file.name}")

    # 2. Parse Transcript Logs
    if TRANSCRIPT_LOG.exists():
        print(f"Reading transcript log from {TRANSCRIPT_LOG}...")
        turn_count = 0
        with TRANSCRIPT_LOG.open("r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                if not line.strip():
                    continue
                try:
                    step_data = json.loads(line)
                    step_bytes = line.encode("utf-8")
                    sha256_hash = compute_sha256(step_bytes)
                    step_type = step_data.get("type", "UNKNOWN")
                    gemini_sig = compute_sha256(f"Gemini:{CONVERSATION_ID}:step_{line_idx}:{sha256_hash}".encode("utf-8"))

                    payload = {
                        "step_index": line_idx,
                        "conversation_id": CONVERSATION_ID,
                        "step_type": step_type,
                        "agent_identity": "Antigravity/Gemini Pro",
                        "content_sha256": sha256_hash,
                        "gemini_signature_hash": gemini_sig,
                        "seedgraph_admitted": True,
                        "custody_state": "HASHED_SEEDGRAPH_ADMITTED",
                        "license": "CC-BY-NC-ND-4.0",
                    }
                    add_node(make_fco_node("InTurnReceiptFCO", payload))
                    turn_count += 1
                except Exception as err:
                    print(f"Warning parsing line {line_idx}: {err}")
        print(f"Ingested {turn_count} transcript turn steps.")

    # 3. Parse Evaluation Receipts & Manifests
    eval_dirs = [
        PROJECT_ROOT / "eval" / "hosted_migration_20260820",
        PROJECT_ROOT / "HydraDG_DaisyTrain_v0.3.7" / "eval",
    ]
    eval_count = 0
    for edir in eval_dirs:
        if edir.exists():
            for json_file in sorted(edir.rglob("*.json")):
                if json_file.name == "CONVERSATION_TURNS_FCO.jsonl":
                    continue
                content_bytes = json_file.read_bytes()
                sha256_hash = compute_sha256(content_bytes)
                payload = {
                    "receipt_name": json_file.name,
                    "relative_path": str(json_file.relative_to(PROJECT_ROOT)),
                    "content_sha256": sha256_hash,
                    "seedgraph_admitted": True,
                    "custody_state": "HASHED_SEEDGRAPH_ADMITTED",
                    "license": "CC-BY-NC-ND-4.0",
                    "bytes": len(content_bytes),
                }
                add_node(make_fco_node("EvaluationReceiptFCO", payload))
                eval_count += 1
    print(f"Ingested {eval_count} evaluation receipt files.")

    # 4. Parse Project Turn Files
    turns_dir = PROJECT_ROOT / "HydraDG_DaisyTrain_v0.3.7" / "custody" / "live" / "turns"
    turns_count = 0
    if turns_dir.exists():
        for turn_file in sorted(turns_dir.glob("*.txt")):
            content_bytes = turn_file.read_bytes()
            sha256_hash = compute_sha256(content_bytes)
            role = "TURN_INPUT" if "input" in turn_file.name else "TURN_OUTPUT"
            payload = {
                "turn_filename": turn_file.name,
                "role": role,
                "content_sha256": sha256_hash,
                "seedgraph_admitted": True,
                "custody_state": "HASHED_SEEDGRAPH_ADMITTED",
                "license": "CC-BY-NC-ND-4.0",
                "bytes": len(content_bytes),
            }
            add_node(make_fco_node("ProjectTurnFCO", payload))
            turns_count += 1
    print(f"Ingested {turns_count} project turn files.")

    # 5. Create Session Master Root
    session_payload = {
        "conversation_id": CONVERSATION_ID,
        "agent_identity": "Antigravity/Gemini Pro",
        "total_fco_nodes": len(fco_nodes),
        "seedgraph_admitted": True,
        "hydradb_ingest_source": "app_source=github",
        "license": "CC-BY-NC-ND-4.0",
    }
    session_node = make_fco_node("SessionConversationFCO", session_payload)
    add_node(session_node)
    print(f"Created Session Master Root FCO: {session_node['id']}")

    # 6. Save Complete Unified Output
    out_dir = PROJECT_ROOT / "eval" / "hosted_migration_20260820"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_jsonl = out_dir / "CONVERSATION_TURNS_FCO.jsonl"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for node in fco_nodes:
            f.write(json.dumps(node) + "\n")

    print(f"Saved total {len(fco_nodes)} FCO nodes to {out_jsonl}")

if __name__ == "__main__":
    ingest_complete_repository()
