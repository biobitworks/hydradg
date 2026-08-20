#!/usr/bin/env python3
"""Complete Repository & Conversation Ingestion Script into SeedGraph FCO nodes with Merkle Root computation.

Gaps Resolved:
1. Renamed gemini_signature_hash -> gemini_provenance_hash with signature_state = "NOT_SIGNED"
2. Turn role separation (USER_INPUT, MODEL/PLANNER_RESPONSE, SYSTEM/TOOL_CALL)
3. Session Root Commitment (ordered_turn_fco_root_sha256, artifact_fco_root_sha256, turn_count, artifact_count, atomization_state = "PENDING")
4. FCG Edge Topology generation (HAS_TURN, NEXT, DERIVED_FROM, HAS_ARTIFACT) written to CONVERSATION_TURNS_EDGES.jsonl
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

def merkle_root_hex(leaves: list[str]) -> str:
    level = [bytes.fromhex(x) for x in leaves if len(x) == 64]
    if not level:
        return compute_sha256(b"hydradg.empty_merkle.v1")
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(hashlib.sha256(b"hydradg.merkle.node.v1\0" + level[i] + level[i + 1]).digest())
        level = nxt
    return level[0].hex()

def determine_turn_role(step_type: str, step_data: dict) -> tuple[str, str]:
    if step_type == "USER_INPUT":
        return "HUMAN_USER", "USER_INPUT"
    elif step_type in ("PLANNER_RESPONSE", "MODEL"):
        return "AI_AGENT", "MODEL"
    else:
        return "SYSTEM", "TOOL_CALL"

def ingest_complete_repository():
    print(f"=== Complete SeedGraph FCO Repository Ingestion (Conv ID: {CONVERSATION_ID}) ===")
    fco_nodes = []
    fcg_edges = []
    seen_ids = set()

    def add_node(node: dict):
        if node["id"] not in seen_ids:
            seen_ids.add(node["id"])
            fco_nodes.append(node)

    def add_edge(src: str, rel: str, dst: str):
        fcg_edges.append({"src": src, "rel": rel, "dst": dst})

    # Master Conversation Source Node
    source_payload = {
        "conversation_id": CONVERSATION_ID,
        "agent_identity": "Antigravity/Gemini Pro",
        "provenance": "Antigravity Local Brain Logs",
        "license": "CC-BY-NC-ND-4.0",
    }
    source_fco = make_fco_node("ConversationSourceFCO", source_payload)
    add_node(source_fco)

    # 1. Parse Brain Artifacts
    artifact_ids = []
    if ANTIGRAVITY_BRAIN_DIR.exists():
        for md_file in sorted(ANTIGRAVITY_BRAIN_DIR.glob("*.md")):
            content_bytes = md_file.read_bytes()
            sha256_hash = compute_sha256(content_bytes)
            gemini_prov = compute_sha256(f"Gemini-Pro:{CONVERSATION_ID}:{md_file.name}:{sha256_hash}".encode("utf-8"))

            payload = {
                "artifact_name": md_file.name,
                "conversation_id": CONVERSATION_ID,
                "agent_identity": "Antigravity/Gemini Pro",
                "content_sha256": sha256_hash,
                "gemini_provenance_hash": gemini_prov,
                "signature_state": "NOT_SIGNED",
                "seedgraph_admitted": True,
                "custody_state": "HASHED_SEEDGRAPH_ADMITTED",
                "license": "CC-BY-NC-ND-4.0",
                "bytes": len(content_bytes),
            }
            art_node = make_fco_node("BrainArtifactFCO", payload)
            add_node(art_node)
            artifact_ids.append(art_node["id"])
            add_edge(art_node["id"], "DERIVED_FROM", source_fco["id"])
            print(f"Ingested Brain Artifact: {md_file.name}")

    # 2. Parse Transcript Logs
    turn_ids = []
    prev_turn_id = None
    if TRANSCRIPT_LOG.exists():
        print(f"Reading transcript log from {TRANSCRIPT_LOG}...")
        with TRANSCRIPT_LOG.open("r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                if not line.strip():
                    continue
                try:
                    step_data = json.loads(line)
                    step_bytes = line.encode("utf-8")
                    sha256_hash = compute_sha256(step_bytes)
                    step_type = step_data.get("type", "UNKNOWN")
                    actor_role, role_kind = determine_turn_role(step_type, step_data)
                    gemini_prov = compute_sha256(f"Gemini:{CONVERSATION_ID}:step_{line_idx}:{sha256_hash}".encode("utf-8"))

                    payload = {
                        "step_index": line_idx,
                        "conversation_id": CONVERSATION_ID,
                        "step_type": step_type,
                        "actor_role": actor_role,
                        "role_kind": role_kind,
                        "agent_identity": "Antigravity/Gemini Pro" if actor_role == "AI_AGENT" else actor_role,
                        "content_sha256": sha256_hash,
                        "gemini_provenance_hash": gemini_prov,
                        "signature_state": "NOT_SIGNED",
                        "seedgraph_admitted": True,
                        "custody_state": "HASHED_SEEDGRAPH_ADMITTED",
                        "license": "CC-BY-NC-ND-4.0",
                    }
                    turn_node = make_fco_node("InTurnReceiptFCO", payload)
                    add_node(turn_node)
                    turn_ids.append(turn_node["id"])
                    
                    add_edge(turn_node["id"], "DERIVED_FROM", source_fco["id"])
                    if prev_turn_id:
                        add_edge(prev_turn_id, "NEXT", turn_node["id"])
                    prev_turn_id = turn_node["id"]
                except Exception as err:
                    print(f"Warning parsing line {line_idx}: {err}")
        print(f"Ingested {len(turn_ids)} transcript turn steps.")

    # Compute Root Commitments over Ordered Turns & Artifacts
    ordered_turn_fco_root_sha256 = compute_sha256("\n".join(turn_ids).encode("utf-8"))
    artifact_fco_root_sha256 = compute_sha256("\n".join(artifact_ids).encode("utf-8"))

    # 3. Parse Evaluation Receipts & Manifests
    eval_dirs = [
        PROJECT_ROOT / "eval" / "hosted_migration_20260820",
        PROJECT_ROOT / "HydraDG_DaisyTrain_v0.3.7" / "eval",
    ]
    eval_count = 0
    for edir in eval_dirs:
        if edir.exists():
            for json_file in sorted(edir.rglob("*.json")):
                if json_file.name in ("CONVERSATION_TURNS_FCO.jsonl", "CONVERSATION_TURNS_EDGES.jsonl", "UPDATED_FCG_MERKLE_ROOT.json"):
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

    # 4. Create Session Master Root with Root Commitment
    leaf_shas = sorted([node["object_sha256"] for node in fco_nodes])
    updated_fcg_merkle_root = merkle_root_hex(leaf_shas)

    session_payload = {
        "conversation_id": CONVERSATION_ID,
        "agent_identity": "Antigravity/Gemini Pro",
        "total_fco_nodes": len(fco_nodes),
        "turn_count": len(turn_ids),
        "artifact_count": len(artifact_ids),
        "ordered_turn_fco_root_sha256": ordered_turn_fco_root_sha256,
        "artifact_fco_root_sha256": artifact_fco_root_sha256,
        "atomization_state": "PENDING",
        "signature_state": "NOT_SIGNED",
        "seedgraph_admitted": True,
        "hydradb_ingest_source": "app_source=github",
        "fcg_merkle_root": updated_fcg_merkle_root,
        "license": "CC-BY-NC-ND-4.0",
    }
    session_node = make_fco_node("SessionConversationFCO", session_payload)
    add_node(session_node)

    for tid in turn_ids:
        add_edge(session_node["id"], "HAS_TURN", tid)
    for aid in artifact_ids:
        add_edge(session_node["id"], "HAS_ARTIFACT", aid)

    final_shas = sorted([node["object_sha256"] for node in fco_nodes])
    final_fcg_root = merkle_root_hex(final_shas)

    print(f"\n=======================================================")
    print(f"UPDATED FCG MERKLE ROOT: {final_fcg_root}")
    print(f"Ordered Turn FCO Root SHA: {ordered_turn_fco_root_sha256}")
    print(f"=======================================================\n")

    merkle_receipt = {
        "schema": "hydradg.updated_fcg_merkle_root.v1",
        "conversation_id": CONVERSATION_ID,
        "total_fco_nodes": len(fco_nodes),
        "total_fcg_edges": len(fcg_edges),
        "updated_fcg_merkle_root": final_fcg_root,
        "ordered_turn_fco_root_sha256": ordered_turn_fco_root_sha256,
        "artifact_fco_root_sha256": artifact_fco_root_sha256,
        "baseline_t3_root": "d38c6cd8318fbfd1eb47d2064b0b2d72e5c5018ef69c1c90e3d5688ab1429ec1",
        "merkle_evolution_state": "UPDATED_UPON_NEW_TURN_INGESTION",
        "license": "CC-BY-NC-ND-4.0",
    }

    out_dir = PROJECT_ROOT / "eval" / "hosted_migration_20260820"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_jsonl = out_dir / "CONVERSATION_TURNS_FCO.jsonl"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for node in fco_nodes:
            f.write(json.dumps(node) + "\n")

    out_edges = out_dir / "CONVERSATION_TURNS_EDGES.jsonl"
    with out_edges.open("w", encoding="utf-8") as f:
        for edge in fcg_edges:
            f.write(json.dumps(edge) + "\n")

    out_merkle = out_dir / "UPDATED_FCG_MERKLE_ROOT.json"
    out_merkle.write_text(json.dumps(merkle_receipt, indent=2, sort_keys=True) + "\n")
    print(f"Saved nodes to {out_jsonl}")
    print(f"Saved edges ({len(fcg_edges)} edges) to {out_edges}")
    print(f"Saved receipt to {out_merkle}")

if __name__ == "__main__":
    ingest_complete_repository()
