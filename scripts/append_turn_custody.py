#!/usr/bin/env python3
"""Append one visible human/assistant turn to HydraDG custody.

Convention: HYDRADG-TURN-RESUME-v1

This is deliberately a new post-fork convention. It does not pretend to recreate
missing pre-resume receipts or hidden model reasoning. Input files must contain
only the exact visible bytes intended for custody.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

CONVENTION = "HYDRADG-TURN-RESUME-v1"


def normalize(value: Any) -> Any:
    if isinstance(value, dict): return {key: normalize(value[key]) for key in sorted(value)}
    if isinstance(value, list): return [normalize(item) for item in value]
    return value


def canonical(value: Any) -> bytes:
    return json.dumps(normalize(value), ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()


def fco(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    digest = sha(canonical({"type": kind, "payload": payload}))
    return {"id": f"fco:{digest}", "object_sha256": digest, "payload": payload, "type": kind}


def edge(src: str, rel: str, dst: str) -> dict[str, Any]:
    body = {"src": src, "rel": rel, "dst": dst, "payload": {}}
    digest = sha(canonical(body))
    return {"dst": dst, "id": f"fcg:{digest}", "object_sha256": digest, "payload": {}, "rel": rel, "src": src}


def append_unique(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_ids: set[str] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip(): existing_ids.add(str(json.loads(line)["id"]))
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            if row["id"] in existing_ids: continue
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            existing_ids.add(row["id"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human-file", required=True)
    parser.add_argument("--assistant-file", required=True)
    parser.add_argument("--model", default="unspecified-visible-output-producer")
    parser.add_argument("--agent", default="ChatGPT")
    parser.add_argument("--custody-dir", default="custody/live")
    parser.add_argument("--date", default="2026-08-18")
    parser.add_argument("--no-sign", action="store_true")
    args = parser.parse_args()

    human_bytes = Path(args.human_file).read_bytes()
    assistant_bytes = Path(args.assistant_file).read_bytes()
    custody = Path(args.custody_dir)
    state_path = custody / "turn_chain_state.json"
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    parent_chain = str(previous.get("turn_chain_sha256") or "RESUME_ANCHOR_2026-08-18")
    previous_receipt_id = previous.get("turn_receipt_fco_id")

    human_sha = sha(human_bytes)
    assistant_sha = sha(assistant_bytes)
    turn_preimage = b"\x00".join([
        CONVENTION.encode(),
        parent_chain.encode(),
        human_sha.encode(),
        assistant_sha.encode(),
    ])
    turn_chain_sha = sha(turn_preimage)

    human = fco("HumanInput", {
        "role": "user",
        "recorded_date": args.date,
        "text_sha256": human_sha,
        "bytes": len(human_bytes),
        "text_scope": "exact visible UTF-8/input bytes supplied to append_turn_custody.py",
        "evidence_class": "DIRECTLY_SUPPLIED",
        "custody_state": "HASHED",
        "claim_ceiling": "AUTHOR_ORIGIN_INPUT",
    })
    assistant = fco("AssistantOutput", {
        "role": "assistant",
        "agent": args.agent,
        "model": args.model,
        "recorded_date": args.date,
        "text_sha256": assistant_sha,
        "bytes": len(assistant_bytes),
        "text_scope": "exact visible assistant/output bytes supplied to append_turn_custody.py; hidden reasoning excluded",
        "evidence_class": "AI_GENERATED_OUTPUT",
        "custody_state": "HASHED",
        "claim_ceiling": "VISIBLE_OUTPUT_PROVENANCE_ONLY",
    })
    receipt = fco("TurnReceipt", {
        "convention": CONVENTION,
        "parent_chain_sha256": parent_chain,
        "human_sha256": human_sha,
        "assistant_body_sha256": assistant_sha,
        "turn_chain_sha256": turn_chain_sha,
        "human_fco_id": human["id"],
        "assistant_fco_id": assistant["id"],
        "previous_turn_receipt_fco_id": previous_receipt_id,
        "custody_state": "HASHED",
        "evidence_class": "DETERMINISTIC_TRANSFORM",
        "claim_ceiling": "TURN_BYTE_CUSTODY_NOT_SEMANTIC_CORRECTNESS",
    })

    edges = [edge(receipt["id"], "BINDS_INPUT", human["id"]), edge(receipt["id"], "BINDS_OUTPUT", assistant["id"])]
    if previous_receipt_id: edges.append(edge(receipt["id"], "CONTINUES_FROM", str(previous_receipt_id)))

    append_unique(custody / "nodes.turns.jsonl", [human, assistant, receipt])
    append_unique(custody / "edges.turns.jsonl", edges)
    state_path.write_text(json.dumps({
        "convention": CONVENTION,
        "turn_chain_sha256": turn_chain_sha,
        "turn_receipt_fco_id": receipt["id"],
        "parent_chain_sha256": parent_chain,
    }, indent=2) + "\n")

    subprocess.run(["python3", "scripts/build_fcg_root.py", "--custody-dir", str(custody)], check=True)

    signature_state = "AUTHOR_SIGNING_NOT_REQUESTED_OR_KEY_UNAVAILABLE"
    key = os.environ.get("FCO_SIGNING_KEY")
    public_key = custody / "PUBLIC_KEY.ed25519.pub"
    if not args.no_sign and key and public_key.exists():
        subprocess.run(["bash", "scripts/sign_fcg_root.sh"], env={**os.environ, "CUSTODY_DIR": str(custody)}, check=True)
        signature_state = "AUTHOR_SIGNATURE_COMMAND_EXECUTED_AND_VERIFIED_BY_SIGN_SCRIPT"

    print(json.dumps({
        "convention": CONVENTION,
        "human_fco_id": human["id"],
        "assistant_fco_id": assistant["id"],
        "turn_receipt_fco_id": receipt["id"],
        "turn_chain_sha256": turn_chain_sha,
        "signature_state": signature_state,
    }))
    return 0


if __name__ == "__main__": raise SystemExit(main())
