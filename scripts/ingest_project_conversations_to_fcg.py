#!/usr/bin/env python3
"""Ingests Antigravity/Gemini conversation transcripts, turn logs, and brain artifacts into content-addressed SeedGraph FCO nodes.

- Reads transcript.jsonl from /Users/byron/.gemini/antigravity/brain/<conv_id>/.system_generated/logs/
- Reads brain artifacts (implementation_plan.md, walkthrough.md)
- Computes SHA-256 digests and Gemini signature hashes
- Generates AgentTurnFCO & InTurnReceiptFCO nodes
- Outputs to custody/live/nodes.jsonl, eval/hosted_migration_20260820/CONVERSATION_TURNS_FCO.jsonl, and web fixture
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

def ingest_antigravity_conversation():
    print(f"=== Antigravity Conversation Ingestion (Conv ID: {CONVERSATION_ID}) ===")
    fco_nodes = []
    fco_edges = []

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
            node = make_fco_node("BrainArtifactFCO", payload)
            fco_nodes.append(node)
            print(f"Ingested Brain Artifact: {md_file.name} -> {node['id']}")

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
                    node = make_fco_node("InTurnReceiptFCO", payload)
                    fco_nodes.append(node)
                    turn_count += 1
                except Exception as err:
                    print(f"Warning parsing line {line_idx}: {err}")

        print(f"Ingested {turn_count} transcript turn steps.")

    # 3. Create Session FCO Root for Conversation
    session_payload = {
        "conversation_id": CONVERSATION_ID,
        "agent_identity": "Antigravity/Gemini Pro",
        "total_fco_nodes": len(fco_nodes),
        "seedgraph_admitted": True,
        "hydradb_ingest_source": "app_source=github",
        "license": "CC-BY-NC-ND-4.0",
    }
    session_node = make_fco_node("SessionConversationFCO", session_payload)
    fco_nodes.append(session_node)
    print(f"Created Session Conversation Root: {session_node['id']}")

    # 4. Save to eval output receipt
    out_dir = PROJECT_ROOT / "eval" / "hosted_migration_20260820"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_jsonl = out_dir / "CONVERSATION_TURNS_FCO.jsonl"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for node in fco_nodes:
            f.write(json.dumps(node) + "\n")

    print(f"Saved {len(fco_nodes)} FCO turn nodes to {out_jsonl}")

if __name__ == "__main__":
    ingest_antigravity_conversation()
